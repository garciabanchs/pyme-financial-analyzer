import re
from datetime import datetime


def normalizar_importe(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except Exception:
        return None


def formatear_importe_es(numero):
    try:
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def extraer_importes(texto):
    if not texto:
        return []

    montos = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}", texto)

    unicos = []
    vistos = set()

    for m in montos:
        if m not in vistos:
            vistos.add(m)
            unicos.append(m)

    return unicos[:50]


def extraer_fecha(texto):
    if not texto:
        return "No detectada"

    fechas = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", texto)
    return fechas[0] if fechas else "No detectada"


def normalizar_fecha(fecha_str):
    if not fecha_str or fecha_str == "No detectada":
        return None

    formatos = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y"]

    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str, fmt)
        except Exception:
            pass

    return None


def obtener_periodo(fecha_str):
    fecha = normalizar_fecha(fecha_str)
    if not fecha:
        return "Sin período"
    return fecha.strftime("%Y-%m")


def extraer_importe_principal(texto, tipo_documento, importes):
    """
    Devuelve el mejor importe principal detectado en el documento.
    Regla simple y robusta:
    - Para facturas: prioriza etiquetas tipo total / importe total / total eur
    - Si no encuentra etiqueta fiable: usa el mayor importe
    - Para extractos: no devuelve uno solo, porque ahí interesan varios movimientos
    """
    if not importes:
        return None

    importes_numericos = []
    for imp in importes:
        valor = normalizar_importe(imp)
        if valor is not None:
            importes_numericos.append((imp, valor))

    if not importes_numericos:
        return None

    texto_lower = (texto or "").lower()

    if tipo_documento in ["factura_venta", "factura_compra"]:
        patrones_total = [
            r"total\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"importe total\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"total eur\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
            r"total factura\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})",
        ]

        for patron in patrones_total:
            m = re.search(patron, texto_lower)
            if m:
                candidato = m.group(1)
                valor = normalizar_importe(candidato)
                if valor is not None:
                    return candidato

        # fallback robusto
        return max(importes_numericos, key=lambda x: x[1])[0]

    # para extractos no devolvemos uno único
    return None
