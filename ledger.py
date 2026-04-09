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
    patron_importe = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")

    fecha_actual = fecha_doc if fecha_doc and fecha_doc != "No detectada" else None
    vistos = set()
    contador = 1

    lineas_ignorar = [
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
    ]

    for linea in lineas:
        linea_original = linea.strip()
        linea_lower = linea_original.lower()

        if not linea_original:
            continue

        m_fecha = patron_fecha.search(linea_original)
        if m_fecha:
            fecha_actual = m_fecha.group()

        if any(fragmento in linea_lower for fragmento in lineas_ignorar):
            continue

        if "cancelación de retención" in linea_lower or "cancelacion de retencion" in linea_lower:
            continue

        if "autorización abierta" in linea_lower or "autorizacion abierta" in linea_lower:
            continue

        if "tipo de cambio" in linea_lower:
            continue

        importes = patron_importe.findall(linea_original)
        if not importes:
            continue

        importe_str = importes[-1]
        valor = normalizar_importe(importe_str)

        if valor is None:
            continue

        if abs(valor) < 1:
            continue

        clave = (
            fecha_actual or "sin_fecha",
            round(abs(valor), 2),
            linea_lower[:120],
        )
        if clave in vistos:
            continue

        naturaleza = "entrada" if valor > 0 else "salida"
        categoria = clasificar_movimiento_bancario(linea_lower, valor)

        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": fecha_actual or "No detectada",
            "periodo": obtener_periodo(fecha_actual or "No detectada"),
            "importe": f"{abs(valor):.2f}".replace(".", ","),
            "importe_num": abs(valor),
            "naturaleza": naturaleza,
            "categoria": categoria,
            "descripcion": linea_original[:200],
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
