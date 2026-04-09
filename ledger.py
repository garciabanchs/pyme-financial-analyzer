import re

from parser_financiero import (
    normalizar_importe,
    extraer_importe_principal,
    obtener_periodo,
)


def clasificar_movimiento_bancario(texto, valor):
    t = (texto or "").lower()

    if "fee" in t or "comisión" in t or "comision" in t:
        return "comision"

    if "retenido" in t or "retención" in t or "retencion" in t or "retention" in t or "hold" in t:
        return "retencion"

    if "transfer" in t or "bank transfer" in t or "transferencia" in t or "retirada" in t:
        return "traspaso"

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
        "from",
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
        "comisión",
        "comision",
        "subscription",
        "payment to",
        "to ",
    ]

    for patron in patrones_entrada:
        if patron in t:
            return "entrada"

    for patron in patrones_salida:
        if patron in t:
            return "salida"

    return None


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
        "historial de transacciones",
        "resumen",
        "totales",
        "subtotal",
        "balance",
        "tipo de cambio",
        "conversión",
        "conversion",
        "autorización abierta",
        "autorizacion abierta",
        "cancelación de retención",
        "cancelacion de retencion",
        "disponible",
        "pendiente",
        "processing",
        "overview",
        "activity summary",
    ]

    return any(fragmento in linea_lower for fragmento in fragmentos_ignorar)


def limpiar_descripcion(linea):
    return " ".join((linea or "").strip().split())


def extraer_movimientos_extracto(texto, archivo, fecha_doc):
    movimientos = []

    if not texto:
        return movimientos

    texto_lower = texto.lower()
    inicio_historial = texto_lower.find("historial de transacciones")
    if inicio_historial != -1:
        texto_trabajo = texto[inicio_historial:]
    else:
        texto_trabajo = texto

    lineas = texto_trabajo.split("\n")

    patron_fecha = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
    patron_importe = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")

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

        # Solo usamos líneas que parezcan realmente una transacción:
        # fecha o contexto cercano a fecha + descripción + importe
        tiene_fecha_en_linea = patron_fecha.search(linea_original) is not None
        linea_anterior = limpiar_descripcion(lineas[i - 1]).lower() if i > 0 else ""
        linea_siguiente = limpiar_descripcion(lineas[i + 1]).lower() if i + 1 < len(lineas) else ""

        contexto_con_fecha = (
            tiene_fecha_en_linea
            or bool(patron_fecha.search(linea_anterior))
            or bool(patron_fecha.search(linea_siguiente))
            or fecha_actual is not None
        )

        if not contexto_con_fecha:
            continue

        # En extractos tipo PayPal o similares, suele servir mejor el último importe de la línea.
        importe_str = importes[-1]
        valor_abs = normalizar_importe(importe_str)

        if valor_abs is None:
            continue

        if valor_abs < 1:
            continue

        # Evitar importes gigantes que suelen ser agregados o resúmenes
        if valor_abs > 100000:
            continue

        naturaleza = inferir_naturaleza_desde_texto(linea_original)

        # Si no pudo inferirse por texto, intentar con contexto de línea vecina
        if naturaleza is None:
            naturaleza = inferir_naturaleza_desde_texto(linea_anterior)
        if naturaleza is None:
            naturaleza = inferir_naturaleza_desde_texto(linea_siguiente)

        # Si sigue sin inferirse, mejor NO inventar
        if naturaleza is None:
            continue

        valor_firmado = valor_abs if naturaleza == "entrada" else -valor_abs
        categoria = clasificar_movimiento_bancario(linea_lower, valor_firmado)

        descripcion_base = linea_original[:200]
        clave = (
            archivo,
            fecha_actual or "sin_fecha",
            naturaleza,
            round(valor_abs, 2),
            descripcion_base[:120],
        )

        if clave in vistos:
            continue

        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": fecha_actual or "No detectada",
            "periodo": obtener_periodo(fecha_actual or "No detectada"),
            "importe": f"{valor_abs:.2f}".replace(".", ","),
            "importe_num": valor_abs,
            "naturaleza": naturaleza,
            "categoria": categoria,
            "descripcion": descripcion_base,
            "soporte": False
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
                    "naturaleza": naturaleza,
                    "categoria": "factura_venta" if tipo_doc == "factura_venta" else "factura_compra",
                    "descripcion": archivo,
                    "soporte": True
                })

        elif tipo_doc == "extracto_bancario":
            movimientos = extraer_movimientos_extracto(
                texto=texto,
                archivo=archivo,
                fecha_doc=fecha,
            )

            for n, movimiento in enumerate(movimientos, start=1):
                movimiento["id"] = f"bank_{idx}_{n}"

            ledger.extend(movimientos)

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
                    "naturaleza": "revisar",
                    "categoria": "otros",
                    "descripcion": archivo,
                    "soporte": True
                })

    return ledger
