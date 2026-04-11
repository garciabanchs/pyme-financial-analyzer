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

    montos = re.findall(r"-?\d{1,3}(?:\.\d{3})*,\d{2}", texto)
    unicos = []
    vistos = set()

    for m in montos:
        if m not in vistos:
            vistos.add(m)
            unicos.append(m)

    return unicos[:200]


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


def buscar_importe_por_patrones(texto_lower, patrones):
    for patron in patrones:
        m = re.search(patron, texto_lower, flags=re.IGNORECASE | re.DOTALL)
        if m:
            candidato = m.group(1)
            valor = normalizar_importe(candidato)
            if valor is not None:
                return candidato
    return None


def _extraer_totales_por_linea(texto):
    """
    Busca importes en líneas que contengan la idea de TOTAL FINAL de factura.
    Esto ayuda a no quedarnos con base imponible o subtotales.
    """
    if not texto:
        return []

    candidatos = []
    lineas = texto.splitlines()

    for linea in lineas:
        l = linea.lower()

        if "base imponible" in l:
            continue
        if "subtotal" in l:
            continue
        if "bruto" in l or "neto" in l:
            continue

        if any(tag in l for tag in ["total factura", "importe total", "total eur", "total"]):
            importes = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}", linea)
            for imp in importes:
                valor = normalizar_importe(imp)
                if valor is not None:
                    candidatos.append((imp, valor, linea))

    return candidatos


def _extraer_ultimo_total_documento(texto):
    """
    Busca todas las apariciones de 'total ... importe' en el documento
    y devuelve la última válida, porque en muchas facturas el total final
    aparece después de base imponible e IVA.
    """
    if not texto:
        return None

    texto_lower = texto.lower()

    patrones_total = [
        r"\btotal factura\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\bimporte total\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal eur\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
    ]

    encontrados = []
    for patron in patrones_total:
        for m in re.finditer(patron, texto_lower, flags=re.IGNORECASE | re.DOTALL):
            candidato = m.group(1)
            valor = normalizar_importe(candidato)
            if valor is not None:
                encontrados.append((m.start(), candidato, valor))

    if not encontrados:
        return None

    encontrados.sort(key=lambda x: x[0])
    return encontrados[-1][1]


def _extraer_total_desde_base_iva_total(texto):
    """
    Busca un bloque típico:
    base imponible ... IVA ... total
    y devuelve el tercer importe, que suele ser el total final.
    """
    if not texto:
        return None

    texto_lower = texto.lower()

    patron = (
        r"base imponible.*?"
        r"(\d{1,3}(?:\.\d{3})*,\d{2}).*?"
        r"(?:i\.?v\.?a|iva).*?"
        r"(\d{1,3}(?:\.\d{3})*,\d{2}).*?"
        r"(\d{1,3}(?:\.\d{3})*,\d{2})"
    )

    m = re.search(patron, texto_lower, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None

    candidato = m.group(3)
    if normalizar_importe(candidato) is not None:
        return candidato

    return None

def extraer_importe_principal(texto, tipo_documento, importes):
    """
    Devuelve el mejor importe principal detectado.

    Reglas:
    - factura_venta: usar el MAYOR importe detectado, porque normalmente el total final
      supera base imponible e IVA por separado.
    - factura_compra: intentar total explícito; si no, usar el mayor.
    - extractos: no devuelven un único importe aquí.
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

    # Venta: aquí queremos total final, no base imponible.
    if tipo_documento == "factura_venta":
        return max(importes_numericos, key=lambda x: x[1])[0]

    # Compra: intentamos total explícito primero.
    if tipo_documento == "factura_compra":
        texto_lower = (texto or "").lower()

        patrones_total = [
            r"\btotal factura\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
            r"\bimporte total\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
            r"\btotal eur\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
            r"\btotal\s*[:\-]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b",
        ]

        for patron in patrones_total:
            m = re.search(patron, texto_lower, flags=re.IGNORECASE | re.DOTALL)
            if m:
                candidato = m.group(1)
                if normalizar_importe(candidato) is not None:
                    return candidato

        return max(importes_numericos, key=lambda x: x[1])[0]

    return None

def extraer_resumen_extracto(texto):
    texto = texto or ""
    t = texto.lower()

    campos = {
        "saldo_inicial_disponible": None,
        "saldo_final_disponible": None,
        "saldo_inicial_retenido": None,
        "saldo_final_retenido": None,
        "pagos_recibidos": None,
        "pagos_enviados": None,
        "retiradas_y_cargos": None,
        "depositos_y_creditos": None,
        "tarifas": None,
        "liberaciones": None,
        "retenido": None,
    }

    patrones = {
        "saldo_inicial_disponible": r"saldo inicial disponible\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "saldo_final_disponible": r"saldo final disponible\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "saldo_inicial_retenido": r"saldo inicial retenido\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "saldo_final_retenido": r"saldo final retenido\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "pagos_recibidos": r"pagos recibidos\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "pagos_enviados": r"pagos enviados\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "retiradas_y_cargos": r"retiradas y cargos\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "depositos_y_creditos": r"depósitos y créditos\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})|depositos y creditos\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "tarifas": r"tarifas\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "liberaciones": r"liberaciones\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        "retenido": r"retenido\s+(-?\d{1,3}(?:\.\d{3})*,\d{2})",
    }

    for campo, patron in patrones.items():
        m = re.search(patron, t, flags=re.IGNORECASE)
        if m:
            grupos = [g for g in m.groups() if g]
            if grupos:
                campos[campo] = normalizar_importe(grupos[0])

    return campos
