import re
from datetime import datetime


UMBRAL_IMPORTE_MINIMO = 0.01


def normalizar_importe(valor):
    if valor is None:
        return None

    try:
        s = str(valor).strip()

        if not s:
            return None

        s = s.replace("€", "").replace("EUR", "").replace("eur", "")
        s = s.replace("\xa0", " ").replace(" ", "")
        s = s.replace("−", "-").replace("–", "-").replace("—", "-")

        # Caso español: 1.234,56
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        else:
            # Si viniera 1234.56 sin comas, se respeta
            # Si viniera 1.234 y no hay coma, asumimos que el punto es decimal solo si hay 1 bloque
            if s.count(".") > 1:
                s = s.replace(".", "")

        numero = float(s)

        if abs(numero) < UMBRAL_IMPORTE_MINIMO:
            return 0.0

        return numero
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

    texto = str(texto)

    # Acepta:
    # 1.234,56
    # -1.234,56
    # 123,45
    patron = r"(?<!\d)-?\d{1,3}(?:\.\d{3})*,\d{2}(?!\d)"

    montos = re.findall(patron, texto)

    unicos = []
    vistos = set()

    for m in montos:
        limpio = m.strip()
        if limpio not in vistos:
            vistos.add(limpio)
            unicos.append(limpio)

    return unicos[:300]


def extraer_fecha(texto):
    if not texto:
        return "No detectada"

    fechas = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", texto)
    return fechas[0] if fechas else "No detectada"


def normalizar_fecha(fecha_str):
    if not fecha_str or fecha_str == "No detectada":
        return None

    fecha_str = str(fecha_str).strip()

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


def _buscar_importe_en_texto(texto, patrones):
    if not texto:
        return None

    for patron in patrones:
        for m in re.finditer(patron, texto, flags=re.IGNORECASE | re.DOTALL):
            grupos = m.groups()
            for g in grupos:
                if g:
                    valor = normalizar_importe(g)
                    if valor is not None:
                        return g.strip()
    return None


def buscar_importe_por_patrones(texto_lower, patrones):
    return _buscar_importe_en_texto(texto_lower, patrones)


def _extraer_totales_por_linea(texto):
    """
    Busca importes en líneas que parezcan contener el total final de una factura.
    Evita quedarse con base imponible, subtotales o importes intermedios.
    """
    if not texto:
        return []

    candidatos = []
    lineas = texto.splitlines()

    for linea in lineas:
        l = linea.lower().strip()

        if not l:
            continue

        if "base imponible" in l:
            continue
        if "subtotal" in l:
            continue
        if "bruto" in l or "neto" in l:
            continue

        if any(tag in l for tag in ["total factura", "importe total", "total eur", "total"]):
            importes = re.findall(r"-?\d{1,3}(?:\.\d{3})*,\d{2}", linea)
            for imp in importes:
                valor = normalizar_importe(imp)
                if valor is not None:
                    candidatos.append((imp, valor, linea))

    return candidatos


def _extraer_ultimo_total_documento(texto):
    """
    Busca todas las apariciones de total en el documento
    y devuelve la última válida, que suele ser el total final.
    """
    if not texto:
        return None

    patrones_total = [
        r"\btotal factura\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\bimporte total\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal eur\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
    ]

    encontrados = []
    for patron in patrones_total:
        for m in re.finditer(patron, texto, flags=re.IGNORECASE | re.DOTALL):
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
    Busca un bloque tipo:
    base imponible ... IVA ... total
    y devuelve el tercer importe.
    """
    if not texto:
        return None

    patron = (
        r"base imponible.*?"
        r"(-?\d{1,3}(?:\.\d{3})*,\d{2}).*?"
        r"(?:i\.?\s*v\.?\s*a|iva).*?"
        r"(-?\d{1,3}(?:\.\d{3})*,\d{2}).*?"
        r"(-?\d{1,3}(?:\.\d{3})*,\d{2})"
    )

    m = re.search(patron, texto, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None

    candidato = m.group(3)
    if normalizar_importe(candidato) is not None:
        return candidato.strip()

    return None


def _extraer_importe_total_explicito(texto):
    if not texto:
        return None

    patrones_total = [
        r"\btotal factura\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\bimporte total\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal a pagar\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal a abonar\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\bimporte a pagar\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal eur\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
        r"\btotal\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})\b",
    ]

    return _buscar_importe_en_texto(texto, patrones_total)


def extraer_importe_principal(texto, tipo_documento, importes):
    if not importes:
        return None

    importes_numericos = []
    for imp in importes:
        valor = normalizar_importe(imp)
        if valor is not None:
            importes_numericos.append((imp, valor))

    if not importes_numericos:
        return None

    if tipo_documento == "factura_venta":
        candidatos_linea = _extraer_totales_por_linea(texto)
        if candidatos_linea:
            candidatos_linea.sort(key=lambda x: x[1])
            return candidatos_linea[-1][0]

        ultimo_total = _extraer_ultimo_total_documento(texto)
        if ultimo_total:
            return ultimo_total

        total_base_iva = _extraer_total_desde_base_iva_total(texto)
        if total_base_iva:
            return total_base_iva

        return max(importes_numericos, key=lambda x: x[1])[0]

    if tipo_documento == "factura_compra":
        candidatos_linea = _extraer_totales_por_linea(texto)
        if candidatos_linea:
            candidatos_linea.sort(key=lambda x: x[1])
            return candidatos_linea[-1][0]

        ultimo_total = _extraer_ultimo_total_documento(texto)
        if ultimo_total:
            return ultimo_total

        total_base_iva = _extraer_total_desde_base_iva_total(texto)
        if total_base_iva:
            return total_base_iva

        return max(importes_numericos, key=lambda x: x[1])[0]

    return None


def extraer_resumen_extracto(texto):
    texto = texto or ""

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
        "saldo_inicial_disponible": [
            r"saldo inicial disponible\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "saldo_final_disponible": [
            r"saldo final disponible\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "saldo_inicial_retenido": [
            r"saldo inicial retenido\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "saldo_final_retenido": [
            r"saldo final retenido\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "pagos_recibidos": [
            r"pagos recibidos\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "pagos_enviados": [
            r"pagos enviados\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "retiradas_y_cargos": [
            r"retiradas y cargos\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "depositos_y_creditos": [
            r"depósitos y créditos\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
            r"depositos y creditos\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "tarifas": [
            r"tarifas\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "liberaciones": [
            r"liberaciones\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
        "retenido": [
            r"\bretenido\s*[:\-]?\s*€?\s*(-?\d{1,3}(?:\.\d{3})*,\d{2})",
        ],
    }

    for campo, lista_patrones in patrones.items():
        encontrado = _buscar_importe_en_texto(texto, lista_patrones)
        if encontrado is not None:
            campos[campo] = normalizar_importe(encontrado)

    return campos
