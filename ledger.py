import re
from parser_financiero import (
    normalizar_importe,
    extraer_importe_principal,
    obtener_periodo,
)

def clasificar_movimiento_bancario(texto, valor):
    t = (texto or "").lower()

    if "fee" in t or "tarifa" in t or "comisión" in t or "comision" in t:
        return "comision"

    if "retenido" in t or "retención" in t or "retencion" in t or "retention" in t or "hold" in t:
        return "retencion"

    if "transfer" in t or "bank transfer" in t or "transferencia" in t or "retirada" in t or "retirada iniciada por el usuario" in t:
        return "traspaso"

    if "cancelación de retención" in t or "cancelacion de retencion" in t:
        return "ajuste"

    if "depósito" in t or "deposito" in t:
        return "ajuste"

    if valor > 0:
        return "cobro_cliente"

    if valor < 0:
        return "pago_proveedor"

    return "desconocido"


def inferir_naturaleza_desde_texto(linea):
    t = (linea or "").lower()

    patrones_entrada = [
        "pago recibido",
        "pagos recibidos",
        "cobro",
        "abono",
        "ingreso",
        "recibido",
        "received",
        "payment received",
        "bonificación",
        "bonificacion",
        "cancelación de retención",
        "cancelacion de retencion",
        "depósito",
        "deposito",
        "liberación",
        "liberacion",
        "pago en punto de venta",
        "pago estándar",
        "pago general",
    ]

    patrones_salida = [
        "pago enviado",
        "pagos enviados",
        "enviado",
        "enviados",
        "cargo",
        "débito",
        "debito",
        "compra",
        "paid",
        "sent",
        "withdrawal",
        "retirada",
        "fee",
        "tarifa",
        "comisión",
        "comision",
        "subscription",
        "payment to",
        "retención",
        "retencion",
        "retención de cuenta",
        "retencion de cuenta",
        "transacción de la tarjeta de débito",
        "transaccion de la tarjeta de debito",
    ]

    for patron in patrones_entrada:
        if patron in t:
            return "entrada"

    for patron in patrones_salida:
        if patron in t:
            return "salida"

    return "desconocido"


def es_linea_ruido(linea_lower):
    if not linea_lower:
        return True

    fragmentos_ignorar = [
        "saldo inicial",
        "saldo final",
        "pagos recibidos",
        "pagos enviados",
        "importe neto",
        "importe bruto",
        "historial de transacciones - eur",
        "resumen",
        "totales",
        "subtotal",
        "balance",
        "tipo de cambio",
        "conversión",
        "conversion",
        "overview",
        "activity summary",
        "nombre \\ correo electrónico",
        "nombre \\ correo electronico",
        "bruto comisión neto",
        "bruto comision neto",
        "fecha descripción",
        "fecha descripcion",
        "id. de cuenta",
        "página",
        "pagina",
    ]

    return any(fragmento in linea_lower for fragmento in fragmentos_ignorar)


def limpiar_descripcion(linea):
    return " ".join((linea or "").strip().split())


def extraer_movimientos_extracto(texto, archivo, fecha_doc):
    movimientos = []
    if not texto:
        return movimientos

    lineas = texto.split("\n")
    patron_fecha = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
    patron_importe = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")

    fecha_actual = fecha_doc if fecha_doc and fecha_doc != "No detectada" else None
    vistos = set()
    contador = 1

    for i, linea in enumerate(lineas):
        linea_original = limpiar_descripcion(linea)
        linea_lower = linea_original.lower()

        if not linea_original:
            continue

        m_fecha = patron_fecha.search(linea_original)
        if m_fecha:
            fecha_actual = m_fecha.group()

        if es_linea_ruido(linea_lower):
            continue

        importes = patron_importe.findall(linea_original)
        if not importes:
            continue

        # Para historial detallado normalmente tomamos el PRIMER importe firmado de la línea.
        importe_str = importes[0]
        valor = normalizar_importe(importe_str)
        if valor is None:
            continue

        if abs(valor) < 0.01:
            continue

        if abs(valor) > 100000:
            continue

        naturaleza = "entrada" if valor > 0 else "salida"
        categoria = clasificar_movimiento_bancario(linea_lower, valor)

        descripcion_base = linea_original[:250]

        clave = (
            archivo,
            fecha_actual or "sin_fecha",
            round(valor, 2),
            descripcion_base[:150],
        )

        if clave in vistos:
            continue

        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": fecha_actual or "No detectada",
            "periodo": obtener_periodo(fecha_actual or "No detectada"),
            "importe": f"{abs(valor):.2f}".replace(".", ","),
            "importe_num": abs(valor),
            "importe_firmado_num": valor,
            "naturaleza": naturaleza,
            "categoria": categoria,
            "descripcion": descripcion_base,
            "soporte": False,
            "estado_conciliacion": "pendiente"
        })

        vistos.add(clave)
        contador += 1

    return movimientos


def construir_ledger(documentos):
    ledger = []

    for idx, doc in enumerate(documentos, start=1):
        texto = doc.get("texto", "")
        tipo_doc = doc.get("tipo", "otros")
        fecha = doc.get("fecha", "No detectada")
        periodo = obtener_periodo(fecha)
        archivo = doc.get("archivo", f"doc_{idx}")
        importes = doc.get("importes", [])
        resumen_extracto = doc.get("resumen_extracto", {})

        if tipo_doc in ["factura_venta", "factura_compra"]:
            importe_principal = extraer_importe_principal(texto, tipo_doc, importes)

            if importe_principal:
                naturaleza = "entrada" if tipo_doc == "factura_venta" else "salida"

                ledger.append({
                    "id": f"doc_{idx}",
                    "archivo": archivo,
                    "tipo": tipo_doc,
                    "fecha": fecha,
                    "periodo": periodo,
                    "importe": importe_principal,
                    "importe_num": normalizar_importe(importe_principal),
                    "importe_firmado_num": normalizar_importe(importe_principal) if naturaleza == "entrada" else -normalizar_importe(importe_principal),
                    "naturaleza": naturaleza,
                    "categoria": tipo_doc,
                    "descripcion": archivo,
                    "soporte": True,
                    "estado_conciliacion": "pendiente"
                })

        elif tipo_doc == "extracto_bancario":
            if resumen_extracto:
                ledger.append({
                    "id": f"extract_summary_{idx}",
                    "archivo": archivo,
                    "tipo": "extracto_resumen",
                    "fecha": fecha,
                    "periodo": periodo,
                    "importe": "0,00",
                    "importe_num": 0.0,
                    "importe_firmado_num": 0.0,
                    "naturaleza": "resumen",
                    "categoria": "resumen_extracto",
                    "descripcion": archivo,
                    "soporte": True,
                    "resumen_extracto": resumen_extracto,
                    "estado_conciliacion": "no_aplica"
                })

            movimientos = extraer_movimientos_extracto(
                texto=texto,
                archivo=archivo,
                fecha_doc=fecha,
            )

            for n, movimiento in enumerate(movimientos, start=1):
                movimiento["id"] = f"bank_{idx}_{n}"
                ledger.append(movimiento)

        else:
            importe_principal = extraer_importe_principal(texto, tipo_doc, importes)

            if importe_principal:
                ledger.append({
                    "id": f"doc_{idx}",
                    "archivo": archivo,
                    "tipo": tipo_doc,
                    "fecha": fecha,
                    "periodo": periodo,
                    "importe": importe_principal,
                    "importe_num": normalizar_importe(importe_principal),
                    "importe_firmado_num": 0.0,
                    "naturaleza": "revisar",
                    "categoria": "otros",
                    "descripcion": archivo,
                    "soporte": True,
                    "estado_conciliacion": "pendiente"
                })

    return ledger
