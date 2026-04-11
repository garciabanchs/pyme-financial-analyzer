import re
from parser_financiero import (
    normalizar_importe,
    extraer_importe_principal,
    obtener_periodo,
)


PATRON_FECHA = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")
PATRON_IMPORTE = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")


def limpiar_descripcion(linea):
    return " ".join((linea or "").strip().split())


def clasificar_movimiento_bancario(texto, valor):
    t = (texto or "").lower()

    if "fee" in t or "tarifa" in t or "comisión" in t or "comision" in t:
        return "comision"

    if "retenido" in t or "retención" in t or "retencion" in t or "retention" in t or "hold" in t:
        return "retencion"

    if (
        "transfer" in t
        or "bank transfer" in t
        or "transferencia" in t
        or "retirada" in t
        or "retirada iniciada por el usuario" in t
    ):
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


def es_linea_ruido(linea_lower):
    if not linea_lower:
        return True

    fragmentos_ignorar = [
        "historial de transacciones - eur",
        "nombre \\ correo electrónico",
        "nombre \\ correo electronico",
        "bruto comisión neto",
        "bruto comision neto",
        "fecha descripción",
        "fecha descripcion",
        "id. de cuenta",
        "id. de paypal",
        "página",
        "pagina",
        "descripción eur",
        "descripcion eur",
        "paypal (europe)",
        "resumen de actividad",
        "resumen de saldo",
        "saldo inicial disponible",
        "saldo final disponible",
        "saldo inicial retenido",
        "saldo final retenido",
        "pagos recibidos",
        "pagos enviados",
        "retiradas y cargos",
        "depósitos y créditos",
        "depositos y creditos",
        "tarifas",
        "liberaciones",
        "retenido",
        "balance",
        "subtotal",
        "totales",
        "activity summary",
        "overview",
    ]

    return any(fragmento in linea_lower for fragmento in fragmentos_ignorar)


def es_linea_componente_evento(linea_lower):
    patrones_componentes = [
        "fee",
        "tarifa",
        "comisión",
        "comision",
        "retenido",
        "retención",
        "retencion",
        "retention",
        "hold",
        "liberación",
        "liberacion",
        "cancelación de retención",
        "cancelacion de retencion",
        "importe neto",
        "importe bruto",
        "neto",
        "bruto",
    ]
    return any(p in linea_lower for p in patrones_componentes)


def es_linea_evento_principal(linea_lower):
    """
    Solo deja pasar hechos económicos principales.
    """
    patrones_principales = [
        "pago en punto de venta",
        "pago estándar",
        "pago estandar",
        "pago general",
        "pago recibido",
        "payment received",
        "pago enviado",
        "retirada iniciada por el usuario",
        "depósito bancario",
        "deposito bancario",
        "transacción de la tarjeta",
        "transaccion de la tarjeta",
        "compra con tarjeta",
        "reembolso",
        "refund",
    ]

    return any(p in linea_lower for p in patrones_principales)


def parece_linea_agregada(linea_original, linea_lower, importes):
    """
    Detecta líneas que parecen agregados del extracto y no transacciones individuales.
    """
    if not importes:
        return True

    # Si hay demasiados importes en la misma línea, casi seguro es agregado o resumen.
    if len(importes) >= 3:
        return True

    # Si la línea es muy corta y solo muestra números grandes, suele ser subtotal/agregado.
    texto_sin_fechas = PATRON_FECHA.sub("", linea_original)
    texto_sin_importes = PATRON_IMPORTE.sub("", texto_sin_fechas)
    texto_limpio = re.sub(r"[\-\–—:;/|\\]+", " ", texto_sin_importes)
    texto_limpio = " ".join(texto_limpio.split())

    # Muy poco texto descriptivo -> probablemente agregado.
    if len(texto_limpio) < 8:
        return True

    # Términos típicos de agrupación / lote / agregado.
    patrones_agregado = [
        "total",
        "lote",
        "batch",
        "grupo",
        "acumulado",
        "resumen",
        "liquidación",
        "liquidacion",
        "transferencia a banco",
        "bank transfer",
    ]
    if any(p in linea_lower for p in patrones_agregado):
        return True

    return False


def inferir_naturaleza_desde_texto(linea_lower, valor):
    if valor > 0:
        return "entrada"
    if valor < 0:
        return "salida"

    entradas = [
        "pago recibido",
        "payment received",
        "depósito bancario",
        "deposito bancario",
        "reembolso",
        "refund",
        "liberación",
        "liberacion",
    ]
    salidas = [
        "pago enviado",
        "retirada iniciada por el usuario",
        "compra con tarjeta",
        "transacción de la tarjeta",
        "transaccion de la tarjeta",
        "tarifa",
        "fee",
        "comisión",
        "comision",
        "retención",
        "retencion",
    ]

    if any(p in linea_lower for p in entradas):
        return "entrada"
    if any(p in linea_lower for p in salidas):
        return "salida"

    return "desconocido"


def extraer_movimientos_extracto(texto, archivo, fecha_doc):
    """
    Extrae solo eventos principales del historial detallado.
    Excluye:
    - resumen del período
    - subtotales
    - netos/brutos/comisiones/retenciones/liberaciones
    - agregados macro del extracto
    """
    movimientos = []
    if not texto:
        return movimientos

    lineas = texto.split("\n")
    fecha_actual = fecha_doc if fecha_doc and fecha_doc != "No detectada" else None
    vistos = set()
    contador = 1

    for linea in lineas:
        linea_original = limpiar_descripcion(linea)
        if not linea_original:
            continue

        linea_lower = linea_original.lower()

        if es_linea_ruido(linea_lower):
            continue

        if es_linea_componente_evento(linea_lower):
            continue

        # Solo consideramos líneas que parezcan evento principal.
        if not es_linea_evento_principal(linea_lower):
            continue

        importes = PATRON_IMPORTE.findall(linea_original)
        if not importes:
            continue

        if parece_linea_agregada(linea_original, linea_lower, importes):
            continue

        # Exigimos fecha explícita para bajar falsos positivos macro.
        m_fecha = PATRON_FECHA.search(linea_original)
        if m_fecha:
            fecha_actual = m_fecha.group()
        elif not fecha_actual:
            continue

        # En transacción individual, el primer importe firmado suele ser suficiente.
        importe_str = importes[0]
        valor = normalizar_importe(importe_str)
        if valor is None:
            continue

        if abs(valor) < 0.01:
            continue

        if abs(valor) > 100000:
            continue

        naturaleza = inferir_naturaleza_desde_texto(linea_lower, valor)
        if naturaleza == "desconocido":
            naturaleza = "entrada" if valor > 0 else "salida"

        categoria = clasificar_movimiento_bancario(linea_lower, valor)
        descripcion_base = linea_original[:250]

        clave = (
            archivo,
            fecha_actual or "sin_fecha",
            round(valor, 2),
            descripcion_base[:180],
            categoria,
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
            "estado_conciliacion": "pendiente",
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
                importe_num = normalizar_importe(importe_principal) or 0.0

                ledger.append({
                    "id": f"doc_{idx}",
                    "archivo": archivo,
                    "tipo": tipo_doc,
                    "fecha": fecha,
                    "periodo": periodo,
                    "importe": importe_principal,
                    "importe_num": importe_num,
                    "importe_firmado_num": importe_num if naturaleza == "entrada" else -importe_num,
                    "naturaleza": naturaleza,
                    "categoria": tipo_doc,
                    "descripcion": archivo,
                    "soporte": True,
                    "estado_conciliacion": "pendiente",
                })

        elif tipo_doc == "extracto_bancario":
            # Resumen oficial del extracto: sirve para caja macro
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
                    "estado_conciliacion": "no_aplica",
                })

            # Historial detallado: solo eventos principales y transaccionales
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
                    "importe_num": normalizar_importe(importe_principal) or 0.0,
                    "importe_firmado_num": 0.0,
                    "naturaleza": "revisar",
                    "categoria": "otros",
                    "descripcion": archivo,
                    "soporte": True,
                    "estado_conciliacion": "pendiente",
                })

    return ledger
