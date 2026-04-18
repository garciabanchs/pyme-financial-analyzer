import re
from datetime import datetime


UMBRAL_IMPORTE_MINIMO = 0.01
PATRON_IMPORTE = r"-?\d{1,3}(?:\.\d{3})*,\d{2}"


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

        if "," in s:
            s = s.replace(".", "").replace(",", ".")
        else:
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
    montos = re.findall(rf"(?<!\d){PATRON_IMPORTE}(?!\d)", texto)

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


def _buscar_importe_despues_de_etiqueta(texto, etiquetas, max_chars=120):
    """
    Busca un importe después de una etiqueta, aunque haya OCR roto,
    espacios, tabulaciones o columnas entre medio.
    """
    if not texto:
        return None

    texto_norm = str(texto).replace("\xa0", " ")
    texto_norm = re.sub(r"[ \t]+", " ", texto_norm)

    for etiqueta in etiquetas:
        patron = rf"{etiqueta}.{{0,{max_chars}}}?({PATRON_IMPORTE})"
        m = re.search(patron, texto_norm, flags=re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1)

    return None


def buscar_importe_por_patrones(texto_lower, patrones):
    return _buscar_importe_en_texto(texto_lower, patrones)


def _extraer_totales_por_linea(texto):
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
        if "iva" in l and "total" not in l:
            continue

        if any(tag in l for tag in ["total factura", "importe total", "total eur", "total"]):
            importes = re.findall(PATRON_IMPORTE, linea)
            for imp in importes:
                valor = normalizar_importe(imp)
                if valor is not None:
                    candidatos.append((imp, valor, linea))

    return candidatos


def _extraer_ultimo_total_documento(texto):
    if not texto:
        return None

    patrones_total = [
        rf"\btotal factura\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\bimporte total\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal a pagar\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal a abonar\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\bimporte a pagar\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal eur\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
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
    if not texto:
        return None

    texto_lower = texto.lower()
    texto_norm = " ".join(texto_lower.split())

    if "base imponible" in texto_norm and ("iva" in texto_norm or "i.v.a" in texto_norm):
        importes = re.findall(PATRON_IMPORTE, texto_norm)

        importes_validos = []
        for imp in importes:
            valor = normalizar_importe(imp)
            if valor is not None:
                importes_validos.append((imp, valor))

        if len(importes_validos) >= 2:
            return max(importes_validos, key=lambda x: x[1])[0]

    return None


def _extraer_importe_total_explicito(texto):
    if not texto:
        return None

    patrones_total = [
        rf"\btotal factura\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\bimporte total\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal a pagar\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal a abonar\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\bimporte a pagar\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal eur\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
        rf"\btotal\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})\b",
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
        total_base_iva = _extraer_total_desde_base_iva_total(texto)
        if total_base_iva:
            return total_base_iva

        ultimo_total = _extraer_ultimo_total_documento(texto)
        if ultimo_total:
            return ultimo_total

        candidatos_linea = _extraer_totales_por_linea(texto)
        if candidatos_linea:
            candidatos_linea.sort(key=lambda x: x[1])
            return candidatos_linea[-1][0]

        return max(importes_numericos, key=lambda x: x[1])[0]

    if tipo_documento == "factura_compra":
        total_base_iva = _extraer_total_desde_base_iva_total(texto)
        if total_base_iva:
            return total_base_iva

        ultimo_total = _extraer_ultimo_total_documento(texto)
        if ultimo_total:
            return ultimo_total

        candidatos_linea = _extraer_totales_por_linea(texto)
        if candidatos_linea:
            candidatos_linea.sort(key=lambda x: x[1])
            return candidatos_linea[-1][0]

        return max(importes_numericos, key=lambda x: x[1])[0]

    return None


def inferir_banco_desde_texto(texto):
    texto = (texto or "").lower()

    if "n26" in texto:
        return "N26"

    if "paypal" in texto:
        return "PayPal"

    mapa = [
        ("caixabank", "CaixaBank"),
        ("caixa", "CaixaBank"),
        ("santander", "Santander"),
        ("bbva", "BBVA"),
        ("sabadell", "Sabadell"),
        ("revolut", "Revolut"),
        ("wise", "Wise"),
        ("bankinter", "Bankinter"),
        ("abanca", "Abanca"),
        ("ing", "ING"),
    ]

    for clave, nombre in mapa:
        if clave in texto:
            return nombre

    claves_n26 = [
        "saldo previo",
        "transacciones salientes",
        "transacciones entrantes",
        "tu nuevo saldo",
    ]
    if any(k in texto for k in claves_n26):
        return "N26"

    claves_paypal = [
        "saldo inicial disponible",
        "saldo final disponible",
        "pagos recibidos",
        "pagos enviados",
        "retiradas y cargos",
        "depósitos y créditos",
        "depositos y creditos",
        "liberaciones",
        "retenido",
        "tarifas",
    ]
    if any(k in texto for k in claves_paypal):
        return "PayPal"

    return None


def extraer_resumen_extracto(texto):
    texto = texto or ""

    campos = {
        "banco": inferir_banco_desde_texto(texto),
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

    # ======================================================
    # 1) N26 PRIMERO
    # ======================================================
    saldo_previo = _buscar_importe_despues_de_etiqueta(
        texto,
        [r"saldo previo"]
    )
    transacciones_salientes = _buscar_importe_despues_de_etiqueta(
        texto,
        [r"transacciones salientes"]
    )
    transacciones_entrantes = _buscar_importe_despues_de_etiqueta(
        texto,
        [r"transacciones entrantes"]
    )
    tu_nuevo_saldo = _buscar_importe_despues_de_etiqueta(
        texto,
        [r"tu nuevo saldo"]
    )

    if any([saldo_previo, transacciones_salientes, transacciones_entrantes, tu_nuevo_saldo]):
        campos["banco"] = "N26"
        campos["saldo_inicial_disponible"] = normalizar_importe(saldo_previo) if saldo_previo else 0.0
        campos["saldo_final_disponible"] = normalizar_importe(tu_nuevo_saldo) if tu_nuevo_saldo else 0.0
        campos["depositos_y_creditos"] = abs(normalizar_importe(transacciones_entrantes) or 0.0)
        campos["retiradas_y_cargos"] = abs(normalizar_importe(transacciones_salientes) or 0.0)
        campos["pagos_recibidos"] = 0.0
        campos["pagos_enviados"] = 0.0
        campos["tarifas"] = 0.0
        campos["liberaciones"] = 0.0
        campos["retenido"] = 0.0
        return campos

    # ======================================================
    # 2) PAYPAL DESPUÉS
    # ======================================================
    patrones_paypal = {
        "saldo_inicial_disponible": [
            rf"saldo inicial disponible\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "saldo_final_disponible": [
            rf"saldo final disponible\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "saldo_inicial_retenido": [
            rf"saldo inicial retenido\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "saldo_final_retenido": [
            rf"saldo final retenido\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "pagos_recibidos": [
            rf"pagos recibidos\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "pagos_enviados": [
            rf"pagos enviados\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "retiradas_y_cargos": [
            rf"retiradas y cargos\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "depositos_y_creditos": [
            rf"depósitos y créditos\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
            rf"depositos y creditos\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "tarifas": [
            rf"tarifas\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "liberaciones": [
            rf"liberaciones\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
        "retenido": [
            rf"\bretenido\s*[:\-]?\s*€?\s*({PATRON_IMPORTE})",
        ],
    }

    for campo, lista_patrones in patrones_paypal.items():
        encontrado = _buscar_importe_en_texto(texto, lista_patrones)
        if encontrado is not None:
            valor = normalizar_importe(encontrado)
            if valor is not None:
                campos[campo] = valor

    hay_paypal = any(
        campos[k] is not None
        for k in [
            "saldo_inicial_disponible",
            "saldo_final_disponible",
            "pagos_recibidos",
            "pagos_enviados",
            "retiradas_y_cargos",
            "depositos_y_creditos",
            "tarifas",
            "liberaciones",
            "retenido",
        ]
    )

    if hay_paypal:
        campos["banco"] = "PayPal"
        return campos

    return campos
