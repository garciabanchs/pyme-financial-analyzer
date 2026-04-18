import os
import re
import unicodedata
from parser_financiero import (
    normalizar_importe,
    extraer_importe_principal,
    obtener_periodo,
)

PATRON_FECHA = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
PATRON_IMPORTE = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")
PATRON_MONEDA = re.compile(
    r"\b(?:eur|usd|ves|cop|mxn|ars|clp|pen|gbp|brl|cad|chf|jpy|cny)\b|€|\$|us\$",
    flags=re.IGNORECASE,
)

UMBRAL_MOVIMIENTO_RELEVANTE = 100.0

# =========================================================
# DETECCIÓN ESCALABLE DE ENTIDADES FINANCIERAS / BANCOS
# =========================================================
ENTIDADES_FINANCIERAS_CONOCIDAS = {
    "paypal": ["paypal", "pypl"],
    "wise": ["wise", "transferwise"],
    "stripe": ["stripe"],
    "caixabank": ["caixabank", "caixa bank", "la caixa"],
    "santander": ["santander", "banco santander"],
    "bbva": ["bbva", "banco bilbao vizcaya argentaria"],
    "sabadell": ["sabadell", "banc sabadell"],
    "bankinter": ["bankinter"],
    "abanca": ["abanca"],
    "kutxabank": ["kutxabank"],
    "unicaja": ["unicaja"],
    "openbank": ["openbank"],
    "imagin": ["imagin", "imaginbank"],
    "revolut": ["revolut"],
    "n26": ["n26"],
    "bunq": ["bunq"],
    "pibank": ["pibank"],
    "ing": ["ing", "ing direct"],
    "bnext": ["bnext"],
    "airwallex": ["airwallex"],
    "adyen": ["adyen"],
    "sumup": ["sumup"],
    "square": ["square", "block inc"],
    "zelle": ["zelle"],
    "skrill": ["skrill"],
    "neteller": ["neteller"],
    "mercadopago": ["mercado pago", "mercadopago"],
    "payoneer": ["payoneer"],
    "payu": ["payu", "pay u"],
    "klarna": ["klarna"],
    "amazon pay": ["amazon pay"],
    "apple pay": ["apple pay"],
    "google pay": ["google pay", "gpay"],
    "alipay": ["alipay"],
    "wechat pay": ["wechat pay"],
}

PALABRAS_CLAVE_ENTIDAD_FINANCIERA = [
    "bank",
    "banco",
    "banking",
    "financial",
    "finance",
    "payments",
    "payment",
    "wallet",
    "card",
    "cards",
    "cuenta",
    "account",
    "extracto",
    "statement",
    "pasarela",
    "gateway",
    "merchant services",
    "e-money",
    "money transfer",
    "wire",
    "sepa",
    "iban",
    "swift",
    "bic",
]

PATRONES_ENTIDAD_EXPLICITA = [
    re.compile(
        r"\b(?:bank|banco|entidad|financial institution|instituci[oó]n financiera|provider|proveedor financiero)\s*[:\-]\s*([A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ0-9&.,()'\/ \-]{2,80})",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:statement from|extracto de|extracto del|account provider|cuenta en|cuenta de)\s+([A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ0-9&.,()'\/ \-]{2,80})",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:paypal|wise|stripe|revolut|n26|bunq|caixabank|santander|bbva|bankinter|openbank|ing|abanca|sabadell|adyen|airwallex|sumup|payoneer|mercadopago)\b",
        re.IGNORECASE,
    ),
]

PATRON_IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
PATRON_SWIFT_BIC = re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b")
PATRON_CUENTA_EXPLICITA = re.compile(
    r"\b(?:cuenta|account|iban|n[úu]mero de cuenta|account number|wallet id|merchant id|customer id|id\.?\s*de cuenta)\s*[:\-]?\s*([A-Z0-9@\.\-\* ]{4,40})",
    re.IGNORECASE,
)
PATRON_ULTIMOS_4 = re.compile(
    r"\b(?:ending|ends? with|terminad[oa] en|ultimos?\s*4|últimos?\s*4|last\s*4)\s*[:\-]?\s*([0-9]{4})\b",
    re.IGNORECASE,
)

# =========================================================
# PATRONES DE CONTRAPARTE / CLIENTE_PROVEEDOR
# =========================================================
PATRONES_CLIENTE_PROVEEDOR = [
    re.compile(r"\b(?:cliente|customer|bill to|billed to|sold to|client)\s*[:\-]\s*([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\b(?:proveedor|supplier|vendor)\s*[:\-]\s*([^\n|]{2,120})", re.IGNORECASE),

    # Factura de venta: patrones típicos del cliente
    re.compile(r"\bcliente\s*[:\-]\s*([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\bdatos del cliente\s*[:\-]?\s*([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\bseñor(?:es)?\s*[:\-]?\s*([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\bdestinatario\s*[:\-]?\s*([^\n|]{2,120})", re.IGNORECASE),

    # Factura de compra: patrones típicos del proveedor
    re.compile(r"\bproveedor\s*[:\-]\s*([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\bemisor\s*[:\-]?\s*([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\braz[oó]n social\s*[:\-]?\s*([^\n|]{2,120})", re.IGNORECASE),

    # Extractos / movimientos
    re.compile(r"\b(?:payment received from|received from|paid by|cobro de|abono de|ingreso de)\s+([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\b(?:payment sent to|payment to|paid to|pago a|transfer to|transferencia a|sent to)\s+([^\n|]{2,120})", re.IGNORECASE),
    re.compile(r"\b(?:merchant|comercio|beneficiary|beneficiario|ordenante|remitente)\s*[:\-]\s*([^\n|]{2,120})", re.IGNORECASE),
]
STOPWORDS_CONTRAPARTE = {
    "payment",
    "payments",
    "bank",
    "banco",
    "cuenta",
    "account",
    "statement",
    "extracto",
    "summary",
    "resumen",
    "total",
    "saldo",
    "balance",
    "eur",
    "usd",
    "invoice",
    "factura",
    "document",
    "movimiento",
    "transaction",
    "transfer",
    "transferencia",
    "sepa",
    "wire",
    "debit",
    "credit",
    "cargo",
    "abono",
    "merchant services",
    "overview",
    "payment received",
    "payment sent",
    "bank transfer",
    "transferencia bancaria",
}

STOPWORDS_ENTIDAD_FINANCIERA = {
    "bank",
    "banco",
    "account",
    "cuenta",
    "statement",
    "extracto",
    "payment",
    "payments",
    "wallet",
    "financial",
    "finance",
    "provider",
    "merchant services",
    "gateway",
    "pasarela",
    "banking",
    "e-money",
    "money transfer",
    "wire",
    "sepa",
}

STOPWORDS_CUENTA = {
    "account",
    "account number",
    "numero de cuenta",
    "número de cuenta",
    "wallet",
    "wallet id",
    "merchant id",
    "customer id",
    "iban",
    "swift",
    "bic",
    "id de cuenta",
    "payment",
    "bank",
    "banco",
    "provider",
}

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)


def limpiar_descripcion(linea):
    return " ".join((linea or "").strip().split())


def detectar_moneda(texto):
    if not texto:
        return None

    m = PATRON_MONEDA.search(texto)
    if not m:
        return None

    valor = m.group(0).upper()
    if valor == "€":
        return "EUR"
    if valor in ["$", "US$"]:
        return "USD"
    return valor


def _normalizar_texto_base(texto):
    texto = (texto or "").strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower()


def _limpiar_nombre_entidad(valor):
    if not valor:
        return None

    valor = valor.strip(" -:|,.;")
    valor = re.sub(r"\s+", " ", valor).strip()

    if not valor:
        return None

    valor_lower = _normalizar_texto_base(valor)

    basura = [
        "page ",
        "pagina ",
        "fecha ",
        "descripcion ",
        "saldo ",
        "importe ",
        "resumen ",
        "summary ",
        "overview ",
    ]
    if any(valor_lower.startswith(b) for b in basura):
        return None

    if len(valor) < 3:
        return None

    return valor[:120]


def _contiene_alguno(texto, patrones):
    t = (texto or "").lower()
    return any(p in t for p in patrones)


def _tokenizar_nombre_archivo(archivo):
    base = os.path.basename(archivo or "")
    nombre, _ = os.path.splitext(base)
    return [tok for tok in re.split(r"[^a-zA-Z0-9@]+", nombre.lower()) if tok]


def _buscar_entidad_conocida(textos):
    mejor = None
    mejor_score = 0

    for canonico, alias_list in ENTIDADES_FINANCIERAS_CONOCIDAS.items():
        score = 0
        for texto, peso in textos:
            texto_norm = _normalizar_texto_base(texto)
            for alias in alias_list:
                alias_norm = _normalizar_texto_base(alias)
                if alias_norm in texto_norm:
                    score += peso + max(0, len(alias_norm) // 5)

        if score > mejor_score:
            mejor = canonico
            mejor_score = score

    return mejor


def _capitalizar_entidad(entidad):
    if not entidad:
        return None

    entidad_lower = entidad.lower()
    for canonico, alias_list in ENTIDADES_FINANCIERAS_CONOCIDAS.items():
        if entidad_lower == canonico:
            principal = alias_list[0]
            if principal.lower() == "bbva":
                return "BBVA"
            if principal.lower() in {"paypal", "wise", "stripe", "n26", "adyen"}:
                return principal.capitalize()
            return principal.title()

    if entidad.isupper():
        return entidad
    return entidad.title()


def _extraer_entidad_por_patron(texto):
    texto = texto or ""
    for patron in PATRONES_ENTIDAD_EXPLICITA:
        m = patron.search(texto)
        if m:
            valor = m.group(1) if m.lastindex else m.group(0)
            valor = _limpiar_nombre_entidad(valor)
            if valor:
                return valor
    return None


def _extraer_entidad_generica(texto):
    texto = texto or ""
    lineas = [limpiar_descripcion(x) for x in texto.splitlines() if limpiar_descripcion(x)]
    candidatos = []

    for linea in lineas[:40]:
        ll = _normalizar_texto_base(linea)
        if any(palabra in ll for palabra in PALABRAS_CLAVE_ENTIDAD_FINANCIERA):
            limpia = re.sub(
                r"\b(statement|extracto|account|cuenta|bank|banco|financial institution|institucion financiera|provider|wallet|iban|swift|bic|payment|payments|merchant services|gateway|pasarela)\b",
                " ",
                linea,
                flags=re.IGNORECASE,
            )
            limpia = _limpiar_nombre_entidad(limpia)
            if limpia and len(limpia.split()) <= 4:
                candidatos.append(limpia)

    if not candidatos:
        return None

    candidatos.sort(key=lambda x: len(x), reverse=True)
    return candidatos[0]


def _es_nombre_banco_aceptable(valor):
    if not valor:
        return False

    valor = limpiar_descripcion(valor)
    if not valor:
        return False

    valor_norm = _normalizar_texto_base(valor)
    valor_norm = valor_norm.strip(" -:|,.;")

    if not valor_norm:
        return False

    if valor_norm in STOPWORDS_ENTIDAD_FINANCIERA:
        return False

    if len(valor_norm) < 3 or len(valor_norm) > 60:
        return False

    if PATRON_IMPORTE.search(valor):
        return False

    if PATRON_IBAN.search(valor.upper()):
        return False

    if PATRON_SWIFT_BIC.search(valor.upper()):
        return False

    palabras = [p for p in re.split(r"[^a-z0-9]+", valor_norm) if p]
    if not palabras:
        return False

    if len(palabras) == 1 and palabras[0] in STOPWORDS_ENTIDAD_FINANCIERA:
        return False

    if len(palabras) == 1 and len(palabras[0]) <= 2:
        return False

    funcionales = sum(1 for p in palabras if p in STOPWORDS_ENTIDAD_FINANCIERA)
    if funcionales >= max(1, len(palabras) - 1):
        return False

    if any(p in {"summary", "overview", "statement", "extracto", "resumen"} for p in palabras):
        return False

    if re.fullmatch(r"[a-z0-9\-_]+", valor_norm) and len(palabras) == 1 and any(ch.isdigit() for ch in valor_norm):
        return False

    return True


def _es_cuenta_financiera_aceptable(valor):
    if not valor:
        return False

    valor = limpiar_descripcion(valor).strip(" -:|,.;")
    if not valor:
        return False

    valor_norm = _normalizar_texto_base(valor)

    if valor_norm in STOPWORDS_CUENTA:
        return False

    if len(valor) < 4 or len(valor) > 40:
        return False

    if PATRON_IMPORTE.search(valor):
        return False

    if "\n" in valor or "|" in valor:
        return False

    palabras = [p for p in re.split(r"[^a-z0-9@]+", valor_norm) if p]
    if len(palabras) > 5:
        return False

    if len(palabras) >= 3 and not EMAIL_RE.fullmatch(valor) and not re.fullmatch(r"[A-Z0-9 \-*\.@]+", valor, re.IGNORECASE):
        return False

    funcionales = sum(1 for p in palabras if p in STOPWORDS_CUENTA or p in STOPWORDS_ENTIDAD_FINANCIERA)
    if funcionales >= max(1, len(palabras) - 1):
        return False

    if PATRON_IBAN.search(valor.upper()):
        return True

    if EMAIL_RE.fullmatch(valor):
        return True

    if re.fullmatch(r"\*{0,4}\d{4,20}", valor.replace(" ", "")):
        return True

    alnum = re.sub(r"[^A-Z0-9@]", "", valor.upper())
    if len(alnum) < 4 or len(alnum) > 34:
        return False

    return True


def _es_cliente_proveedor_aceptable(valor):
    if not valor:
        return False

    valor = limpiar_descripcion(valor).strip(" -:|,.;")
    if not valor:
        return False

    valor_norm = _normalizar_texto_base(valor)

    if valor_norm in STOPWORDS_CONTRAPARTE:
        return False

    if len(valor) < 3 or len(valor) > 120:
        return False

    if PATRON_IMPORTE.search(valor):
        return False

    if PATRON_IBAN.search(valor.upper()):
        return False

    if PATRON_SWIFT_BIC.search(valor.upper()):
        return False

    if any(x in valor_norm for x in ["statement", "extracto", "summary", "overview", "saldo", "movimiento", "transaction", "transferencia bancaria", "merchant services"]):
        return False

    palabras = [p for p in re.split(r"[^a-z0-9@]+", valor_norm) if p]
    if not palabras:
        return False

    funcionales = sum(1 for p in palabras if p in STOPWORDS_CONTRAPARTE or p in STOPWORDS_ENTIDAD_FINANCIERA)
    if funcionales >= max(1, len(palabras) - 1):
        return False

    if len(palabras) == 1:
        p = palabras[0]
        if p in STOPWORDS_CONTRAPARTE or p in STOPWORDS_ENTIDAD_FINANCIERA:
            return False
        if len(p) < 4:
            return False
        if p.isdigit():
            return False

    if len(palabras) > 12:
        return False

    if re.fullmatch(r"[a-z0-9\-_]+", valor_norm) and any(ch.isdigit() for ch in valor_norm) and len(palabras) == 1:
        return False

    return True


def _normalizar_banco_detectado(valor):
    if not _es_nombre_banco_aceptable(valor):
        return None
    return _capitalizar_entidad(valor)


def _normalizar_cuenta_detectada(valor):
    if not _es_cuenta_financiera_aceptable(valor):
        return None
    return limpiar_descripcion(valor).strip(" -:|,.;")[:80]


def _normalizar_cliente_proveedor_detectado(valor):
    if not _es_cliente_proveedor_aceptable(valor):
        return None
    return limpiar_descripcion(valor).strip(" -:|,.;")[:120]
    

def _parece_nombre_empresa_factura(linea):
    if not linea:
        return False

    linea = limpiar_descripcion(linea).strip(" -:|,.;")
    if not linea:
        return False

    linea_norm = _normalizar_texto_base(linea)

    # demasiado corta o demasiado larga
    if len(linea) < 5 or len(linea) > 120:
        return False

    # basura típica
    basura = [
        "factura",
        "invoice",
        "fecha",
        "date",
        "vencimiento",
        "subtotal",
        "total",
        "base imponible",
        "iva",
        "cuota",
        "importe",
        "forma de pago",
        "nro",
        "numero",
        "albaran",
        "pedido",
        "referencia",
        "extracto",
        "statement",
        "resumen",
        "pagina",
        "page",
        "cliente",
        "proveedor",
        "emisor",
        "razon social",
        "datos del cliente",
    ]
    if any(b in linea_norm for b in basura):
        return False

    # no debe parecer importe o fecha o identificador puro
    if PATRON_IMPORTE.search(linea):
        return False
    if PATRON_FECHA.search(linea):
        return False
    if PATRON_IBAN.search(linea.upper()):
        return False
    if PATRON_SWIFT_BIC.search(linea.upper()):
        return False

    # debe tener letras
    letras = sum(1 for c in linea if c.isalpha())
    if letras < 4:
        return False

    # suele ser un nombre corporativo corto/medio
    palabras = [p for p in re.split(r"\s+", linea) if p]
    if len(palabras) > 8:
        return False

    return True


def inferir_banco_desde_fuentes(archivo=None, texto=None, bloque_texto=None, resumen_extracto=None):
    """
    Devuelve:
    {
        "banco": ...,
        "entidad_financiera": ...,
        "cuenta": ...,
        "metodo_deteccion_banco": ...
    }
    """
    archivo = archivo or ""
    texto = texto or ""
    bloque_texto = bloque_texto or ""
    resumen_extracto = resumen_extracto or {}

    textos_ponderados = [
        (archivo, 6),
        (bloque_texto, 4),
        (texto[:4000], 3),
        (str(resumen_extracto), 2),
    ]

    entidad_conocida = _buscar_entidad_conocida(textos_ponderados)
    entidad_patron = _extraer_entidad_por_patron("\n".join([archivo, bloque_texto, texto[:5000], str(resumen_extracto)]))
    entidad_generica = _extraer_entidad_generica("\n".join([bloque_texto, texto[:3000]]))

    cuenta = inferir_cuenta_financiera(
        texto="\n".join([bloque_texto, texto[:5000], str(resumen_extracto)]),
        archivo=archivo,
        banco=entidad_conocida or entidad_patron or entidad_generica,
    )

    entidad_conocida_norm = _normalizar_banco_detectado(entidad_conocida)
    if entidad_conocida_norm:
        return {
            "banco": entidad_conocida_norm,
            "entidad_financiera": entidad_conocida_norm,
            "cuenta": cuenta,
            "metodo_deteccion_banco": "alias_conocido",
        }

    entidad_patron_norm = _normalizar_banco_detectado(entidad_patron)
    if entidad_patron_norm:
        return {
            "banco": entidad_patron_norm,
            "entidad_financiera": entidad_patron_norm,
            "cuenta": cuenta,
            "metodo_deteccion_banco": "patron_explicito",
        }

    entidad_generica_norm = _normalizar_banco_detectado(entidad_generica)
    if entidad_generica_norm:
        return {
            "banco": entidad_generica_norm,
            "entidad_financiera": entidad_generica_norm,
            "cuenta": cuenta,
            "metodo_deteccion_banco": "heuristica_generica",
        }

    return {
        "banco": "No detectado",
        "entidad_financiera": "No detectada",
        "cuenta": cuenta,
        "metodo_deteccion_banco": "fallback",
    }


def inferir_cuenta_financiera(texto=None, archivo=None, banco=None):
    texto = texto or ""
    archivo = archivo or ""

    m_iban = PATRON_IBAN.search((texto + "\n" + archivo).upper())
    if m_iban:
        iban = m_iban.group(0)
        return f"IBAN ****{iban[-4:]}"

    m_last4 = PATRON_ULTIMOS_4.search(texto)
    if m_last4:
        return f"****{m_last4.group(1)}"

    email = EMAIL_RE.search(texto)
    if email and banco and _normalizar_texto_base(banco) in {"paypal", "wise"}:
        return email.group(0)

    m_cuenta = PATRON_CUENTA_EXPLICITA.search(texto)
    if m_cuenta:
        valor = re.sub(r"\s+", " ", m_cuenta.group(1)).strip()
        valor = valor.strip(" -:|,.;")
        valor = _normalizar_cuenta_detectada(valor)
        if valor:
            return valor

    tokens = _tokenizar_nombre_archivo(archivo)
    for i, tok in enumerate(tokens):
        if tok in {"iban", "account", "cuenta", "wallet"} and i + 1 < len(tokens):
            sig = tokens[i + 1]
            sig = _normalizar_cuenta_detectada(sig)
            if sig:
                return sig

    return "No detectada"


def _es_texto_retiro_propio(texto):
    patrones = [
        "retirada iniciada por el usuario",
        "withdrawal initiated by user",
        "retirada",
        "withdrawal",
        "cash withdrawal",
        "transfer to bank",
        "transferencia a banco",
        "retirar fondos",
        "retiro",
        "withdraw funds",
        "transferencia realizada por el usuario",
    ]
    return _contiene_alguno(texto, patrones)


def _es_texto_transferencia_interna(texto):
    patrones = [
        "transfer",
        "bank transfer",
        "transferencia",
        "traspaso",
        "bizum",
        "sepa",
        "wire",
        "entre cuentas",
        "internal transfer",
        "transferencia interna",
        "transfer between",
        "movimiento entre cuentas",
    ]
    return _contiene_alguno(texto, patrones)


def _es_texto_gasto_operativo(texto):
    patrones = [
        "transacción de la tarjeta de débito",
        "transaccion de la tarjeta de debito",
        "card",
        "tarjeta",
        "debit card",
        "purchase",
        "compra",
        "merchant",
        "store",
        "vendor",
        "general de paypal",
        "pos",
        "punto de venta",
        "suscripción",
        "suscripcion",
        "subscription",
        "office",
        "software",
        "hosting",
        "restaurant",
        "hotel",
        "travel",
        "uber",
        "taxi",
    ]
    return _contiene_alguno(texto, patrones)


def _es_texto_pago_proveedor(texto):
    patrones = [
        "supplier",
        "proveedor",
        "vendor payment",
        "payment sent",
        "pago enviado",
        "invoice payment",
        "payment to",
        "bill payment",
        "factura proveedor",
        "pago proveedor",
        "al proveedor",
    ]
    return _contiene_alguno(texto, patrones)


def _es_texto_cobro_cliente(texto):
    patrones = [
        "payment received",
        "pago recibido",
        "received from",
        "cobro",
        "abono",
        "ingreso",
        "credit",
        "crédito",
        "credito",
        "deposit",
        "depósito",
        "deposito",
        "pago en punto de venta",
        "customer payment",
        "client payment",
    ]
    return _contiene_alguno(texto, patrones)


def clasificar_movimiento_bancario(texto, valor):
    t = (texto or "").lower()

    if any(x in t for x in ["fee", "tarifa", "comisión", "comision", "commission"]):
        return "comision"

    if any(x in t for x in ["retenido", "retención", "retencion", "retention", "hold", "withholding"]):
        return "retencion"

    if any(x in t for x in ["impuesto", "tax", "iva", "vat"]):
        return "impuesto"

    if any(x in t for x in ["reembolso", "refund", "devolución", "devolucion"]):
        return "reembolso"

    if any(x in t for x in ["ajuste", "adjustment", "corrección", "correccion"]):
        return "ajuste"

    if valor < 0 and _es_texto_retiro_propio(t):
        return "retiro_propio"

    if _es_texto_transferencia_interna(t):
        if "internal transfer" in t or "transferencia interna" in t or "traspaso" in t:
            return "transferencia_interna"

        if not _es_texto_gasto_operativo(t) and not _es_texto_cobro_cliente(t) and not _es_texto_pago_proveedor(t):
            return "transferencia_interna"

    if valor < 0 and _es_texto_gasto_operativo(t):
        return "gasto_operativo"

    if valor < 0 and _es_texto_pago_proveedor(t):
        return "pago_proveedor"

    if valor > 0 and _es_texto_cobro_cliente(t):
        return "cobro_cliente"

    if valor > 0:
        return "cobro_cliente"

    if valor < 0:
        return "pago_proveedor"

    return "desconocido"


def es_linea_ruido(linea_lower):
    if not linea_lower:
        return True

    fragmentos_ignorar = [
        "resumen",
        "summary",
        "overview",
        "activity summary",
        "saldo inicial disponible",
        "saldo final disponible",
        "saldo inicial retenido",
        "saldo final retenido",
        "saldo inicial",
        "saldo final",
        "pagos recibidos",
        "pagos enviados",
        "retiradas y cargos",
        "depósitos y créditos",
        "depositos y creditos",
        "tarifas",
        "liberaciones",
        "retenido",
        "historial de transacciones - eur",
        "fecha descripción",
        "fecha descripcion",
        "descripción eur",
        "descripcion eur",
        "bruto comisión neto",
        "bruto comision neto",
        "subtotal",
        "totales",
        "balance",
        "id. de cuenta",
        "id. de paypal",
        "nombre \\ correo electrónico",
        "nombre \\ correo electronico",
        "página",
        "pagina",
    ]

    return any(fragmento in linea_lower for fragmento in fragmentos_ignorar)


def es_linea_componente(linea_lower):
    patrones = [
        "fee",
        "tarifa",
        "comisión",
        "comision",
        "commission",
        "retenido",
        "retención",
        "retencion",
        "retention",
        "hold",
        "liberación",
        "liberacion",
        "importe neto",
        "importe bruto",
        "neto",
        "bruto",
        "cancelación de retención",
        "cancelacion de retencion",
    ]
    return any(p in linea_lower for p in patrones)


def tiene_huella_transaccional(linea_lower):
    patrones = [
        "pago",
        "payment",
        "purchase",
        "compra",
        "card",
        "tarjeta",
        "transfer",
        "transferencia",
        "depósito",
        "deposito",
        "withdrawal",
        "retirada",
        "cargo",
        "debit",
        "débito",
        "debito",
        "credit",
        "crédito",
        "credito",
        "abono",
        "ingreso",
        "received",
        "received from",
        "sent",
        "refund",
        "reembolso",
        "bizum",
        "sepa",
        "wire",
        "atm",
        "cash",
        "merchant",
        "store",
        "vendor",
    ]
    return any(p in linea_lower for p in patrones)


def partir_en_bloques_transaccionales(texto):
    bloques = []
    bloque_actual = []

    for raw in (texto or "").splitlines():
        linea = limpiar_descripcion(raw)
        if not linea:
            continue

        linea_lower = linea.lower()
        tiene_fecha = bool(PATRON_FECHA.search(linea))
        tiene_importe = bool(PATRON_IMPORTE.search(linea))
        huella = tiene_huella_transaccional(linea_lower)

        abre_bloque = False
        if tiene_fecha:
            abre_bloque = True
        elif tiene_importe and huella and not bloque_actual:
            abre_bloque = True

        if abre_bloque:
            if bloque_actual:
                bloques.append(bloque_actual)
            bloque_actual = [linea]
        else:
            if bloque_actual:
                bloque_actual.append(linea)
            else:
                if tiene_importe or huella:
                    bloque_actual = [linea]

    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques


def extraer_fecha_de_bloque(bloque, fecha_doc):
    for linea in bloque:
        m = PATRON_FECHA.search(linea)
        if m:
            return m.group()
    return fecha_doc if fecha_doc and fecha_doc != "No detectada" else "No detectada"


def extraer_moneda_de_bloque(bloque):
    for linea in bloque:
        moneda = detectar_moneda(linea)
        if moneda:
            return moneda
    return None


def seleccionar_importe_principal_bloque(bloque):
    texto_bloque = " ".join(bloque)
    texto_lower = texto_bloque.lower()
    importes = PATRON_IMPORTE.findall(texto_bloque)

    if not importes:
        return None

    if es_linea_componente(texto_lower) and len(importes) >= 2:
        return None

    if len(importes) >= 4:
        return None

    candidatos = []
    for imp in importes:
        valor = normalizar_importe(imp)
        if valor is not None:
            candidatos.append((imp, valor))

    if not candidatos:
        return None

    if len(candidatos) == 1:
        return candidatos[0][1]

    candidatos.sort(key=lambda x: abs(x[1]), reverse=True)
    return candidatos[0][1]


def extraer_descripcion_bloque(bloque):
    if not bloque:
        return ""
    return " | ".join(bloque)[:250]


def inferir_naturaleza_bloque(texto_lower, valor):
    if valor > 0:
        return "entrada"
    if valor < 0:
        return "salida"

    entradas = [
        "payment received",
        "pago recibido",
        "abono",
        "ingreso",
        "credit",
        "crédito",
        "credito",
        "refund",
        "reembolso",
        "deposit",
        "depósito",
        "deposito",
    ]
    salidas = [
        "pago enviado",
        "payment sent",
        "compra",
        "purchase",
        "withdrawal",
        "retirada",
        "debit",
        "débito",
        "debito",
        "cargo",
    ]

    if any(p in texto_lower for p in entradas):
        return "entrada"
    if any(p in texto_lower for p in salidas):
        return "salida"

    return "desconocido"


def bloque_es_agregado_o_resumen(bloque):
    texto = " ".join(bloque).lower()

    if es_linea_ruido(texto):
        return True

    if not tiene_huella_transaccional(texto):
        return True

    total_importes = len(PATRON_IMPORTE.findall(texto))
    if len(bloque) >= 4 and total_importes >= 4:
        return True

    return False


def es_movimiento_relevante(valor, categoria):
    """
    Filtro fuerte de relevancia financiera.
    Lo que no pase este filtro no se pierde: se agrupa.
    """
    if valor is None:
        return False

    v = abs(valor)

    if v < UMBRAL_MOVIMIENTO_RELEVANTE:
        return False

    if v < 100 and categoria in [
        "comision",
        "retencion",
        "ajuste",
        "impuesto",
    ]:
        return False

    return True


def _normalizar_categoria_agrupada(categoria, valor):
    categoria = (categoria or "").lower()

    if valor > 0:
        if categoria in ["cobro_cliente"]:
            return "otros_cobros"
        return "otros_cobros"

    if valor < 0:
        if categoria in [
            "pago_proveedor",
            "retiro_propio",
            "gasto_operativo",
            "transferencia_interna",
            "comision",
            "retencion",
            "impuesto",
            "ajuste",
        ]:
            return "otros_pagos"
        return "otros_pagos"

    return "otros_pagos"


def _limpiar_cliente_proveedor(valor):
    valor = (valor or "").strip()
    valor = valor.strip(" -:|,.;")
    valor = re.sub(r"\s+", " ", valor)

    if not valor:
        return None

    valor = re.sub(
        r"\b(?:invoice|factura|payment|pago|transferencia|transfer|sepa|wire|iban|swift|bic|date|fecha|importe|amount|statement|extracto|summary|overview|saldo|movimiento|transaction|merchant services|nro\.?\s*de\s*factura|fecha\s*de\s*factura|forma\s*de\s*pago|anticipo\s*cuenta)\b",
        " ",
        valor,
        flags=re.IGNORECASE,
    )

    valor = re.sub(r"\s+", " ", valor).strip(" -:|,.;")

    if not valor:
        return None

    # corta si después del nombre aparece una línea OCR rara o demasiado larga
    valor = valor.split("  ")[0].strip()

    return _normalizar_cliente_proveedor_detectado(valor)


def _nombre_archivo_puede_ser_contraparte(archivo):
    nombre = os.path.splitext(os.path.basename(archivo or ""))[0]
    nombre_norm = _normalizar_texto_base(nombre)

    if not nombre_norm:
        return False

    if len(nombre_norm) > 80:
        return False

    if any(p in nombre_norm for p in [
        "extracto",
        "statement",
        "bank",
        "banco",
        "invoice",
        "factura",
        "ocr",
        "scan",
        "pago",
        "payment",
        "movimiento",
        "ledger",
        "report",
        "resumen",
        "summary",
    ]):
        return False

    if re.fullmatch(r"[a-z0-9\-_]+", nombre_norm) and any(ch.isdigit() for ch in nombre_norm):
        return False

    tokens = [t for t in re.split(r"[^a-z0-9]+", nombre_norm) if t]
    if len(tokens) > 6:
        return False

    funcionales = sum(1 for t in tokens if t in STOPWORDS_CONTRAPARTE or t in STOPWORDS_ENTIDAD_FINANCIERA)
    if funcionales > 0:
        return False

    return True


def inferir_cliente_proveedor(texto=None, archivo=None, tipo_doc=None, categoria=None, valor=None):
    texto = texto or ""
    archivo = archivo or ""
    tipo_doc = tipo_doc or ""
    categoria = categoria or ""
    # =====================================================
    # PRIORIDAD ALTA: facturas
    # Regla:
    # - factura_venta  -> buscamos cliente
    # - factura_compra -> buscamos proveedor / emisor
    # =====================================================
    lineas = [limpiar_descripcion(x) for x in texto.splitlines() if limpiar_descripcion(x)]

    if tipo_doc == "factura_venta":
        patrones_venta = [
            r"\bcliente\s*[:\-]\s*(.+)",
            r"\bdatos del cliente\s*[:\-]?\s*(.+)",
            r"\bdestinatario\s*[:\-]?\s*(.+)",
            r"\bseñor(?:es)?\s*[:\-]?\s*(.+)",
        ]

        for linea in lineas[:80]:
            for patron in patrones_venta:
                m = re.search(patron, linea, flags=re.IGNORECASE)
                if m:
                    candidato = _limpiar_cliente_proveedor(m.group(1))
                    if candidato:
                        return candidato

    if tipo_doc == "factura_compra":
        patrones_compra = [
            r"\bproveedor\s*[:\-]\s*(.+)",
            r"\bemisor\s*[:\-]?\s*(.+)",
            r"\braz[oó]n social\s*[:\-]?\s*(.+)",
            r"\bsupplier\s*[:\-]\s*(.+)",
            r"\bvendor\s*[:\-]\s*(.+)",
        ]

        for linea in lineas[:80]:
            for patron in patrones_compra:
                m = re.search(patron, linea, flags=re.IGNORECASE)
                if m:
                    candidato = _limpiar_cliente_proveedor(m.group(1))
                    if candidato:
                        return candidato
    
    

    for patron in PATRONES_CLIENTE_PROVEEDOR:
        m = patron.search(texto)
        if m:
            candidato = _limpiar_cliente_proveedor(m.group(1))
            if candidato:
                return candidato

    texto_lineal = " | ".join([limpiar_descripcion(x) for x in texto.splitlines() if limpiar_descripcion(x)])
    pistas_controladas = [
        r"(?:payment received from|received from|paid by|cobro de|abono de|ingreso de)\s+([A-ZÁÉÍÓÚÑ0-9][^|]{2,100})",
        r"(?:payment sent to|payment to|paid to|pago a|transfer to|transferencia a|sent to)\s+([A-ZÁÉÍÓÚÑ0-9][^|]{2,100})",
        r"(?:merchant|comercio|beneficiary|beneficiario|ordenante|remitente)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ0-9][^|]{2,100})",
    ]
    for expr in pistas_controladas:
        m = re.search(expr, texto_lineal, flags=re.IGNORECASE)
        if m:
            candidato = _limpiar_cliente_proveedor(m.group(1))
            if candidato:
                return candidato

    # =====================================================
    # FALLBACK PARA FACTURAS:
    # si no hubo etiqueta explícita, buscar nombre de empresa
    # en las primeras líneas del documento
    # =====================================================
    if tipo_doc in ["factura_venta", "factura_compra"]:
        for linea in lineas[:40]:
            if _parece_nombre_empresa_factura(linea):
                candidato = _limpiar_cliente_proveedor(linea)
                if candidato:
                    return candidato

    email = EMAIL_RE.search(texto)
    if email:
        candidato_email = _normalizar_cliente_proveedor_detectado(email.group(0))
        if candidato_email:
            return candidato_email

    if _nombre_archivo_puede_ser_contraparte(archivo):
        nombre_archivo = os.path.splitext(os.path.basename(archivo or ""))[0]
        nombre_archivo = re.sub(r"[_\-]+", " ", nombre_archivo)
        nombre_archivo = re.sub(r"\s+", " ", nombre_archivo).strip()
        candidato_archivo = _limpiar_cliente_proveedor(nombre_archivo)
        if candidato_archivo:
            return candidato_archivo

    if categoria == "cobro_cliente" or (valor is not None and valor > 0):
        return "No detectado"
    if categoria in ["pago_proveedor", "gasto_operativo"] or (valor is not None and valor < 0):
        return "No detectado"
    if tipo_doc in ["factura_venta", "factura_compra"]:
        return "No detectado"

    return None

def extraer_movimientos_extracto(
    texto,
    archivo,
    fecha_doc,
    banco_doc=None,
    cuenta_doc=None,
    entidad_financiera_doc=None,
    resumen_extracto=None,
):
    movimientos = []
    if not texto:
        return movimientos

    resumen_extracto = resumen_extracto or {}

    deteccion_doc = inferir_banco_desde_fuentes(
        archivo=archivo,
        texto=texto,
        bloque_texto="",
        resumen_extracto=resumen_extracto,
    )
    banco_doc = _normalizar_banco_detectado(banco_doc) or _normalizar_banco_detectado(deteccion_doc.get("banco"))
    entidad_financiera_doc = _normalizar_banco_detectado(entidad_financiera_doc) or _normalizar_banco_detectado(deteccion_doc.get("entidad_financiera"))
    cuenta_doc = _normalizar_cuenta_detectada(cuenta_doc) or _normalizar_cuenta_detectada(deteccion_doc.get("cuenta"))

    if not banco_doc:
        banco_doc = "No detectado"
    if not entidad_financiera_doc:
        entidad_financiera_doc = "No detectada"
    if not cuenta_doc:
        cuenta_doc = "No detectada"

    bloques = partir_en_bloques_transaccionales(texto)
    vistos = set()
    contador = 1

    otros_cobros_total = 0.0
    otros_pagos_total = 0.0
    otros_cobros_cantidad = 0
    otros_pagos_cantidad = 0

    for bloque in bloques:
        texto_bloque = " ".join(bloque)
        texto_lower = texto_bloque.lower()

        if bloque_es_agregado_o_resumen(bloque):
            continue

        if es_linea_componente(texto_lower):
            continue

        valor = seleccionar_importe_principal_bloque(bloque)
        if valor is None:
            continue

        if abs(valor) < 0.01:
            continue

        if abs(valor) > 100000:
            continue

        categoria = clasificar_movimiento_bancario(texto_lower, valor)
        fecha = extraer_fecha_de_bloque(bloque, fecha_doc)
        descripcion = extraer_descripcion_bloque(bloque)
        moneda = extraer_moneda_de_bloque(bloque) or detectar_moneda(texto)

        naturaleza = inferir_naturaleza_bloque(texto_lower, valor)
        if naturaleza == "desconocido":
            naturaleza = "entrada" if valor > 0 else "salida"

        deteccion_mov = inferir_banco_desde_fuentes(
            archivo=archivo,
            texto=texto[:4000],
            bloque_texto=texto_bloque,
            resumen_extracto=resumen_extracto,
        )

        banco_mov_bloque = _normalizar_banco_detectado(deteccion_mov.get("banco"))
        entidad_financiera_mov_bloque = _normalizar_banco_detectado(deteccion_mov.get("entidad_financiera"))
        cuenta_mov_bloque = _normalizar_cuenta_detectada(deteccion_mov.get("cuenta"))

        banco_mov = banco_mov_bloque or banco_doc or "No detectado"
        entidad_financiera_mov = entidad_financiera_mov_bloque or entidad_financiera_doc or banco_mov or "No detectada"
        cuenta_mov = cuenta_mov_bloque or cuenta_doc or "No detectada"

        if not _es_nombre_banco_aceptable(banco_mov):
            banco_mov = banco_doc if _es_nombre_banco_aceptable(banco_doc) else "No detectado"

        if not _es_nombre_banco_aceptable(entidad_financiera_mov):
            entidad_financiera_mov = entidad_financiera_doc if _es_nombre_banco_aceptable(entidad_financiera_doc) else (
                banco_mov if _es_nombre_banco_aceptable(banco_mov) else "No detectada"
            )

        if not _es_cuenta_financiera_aceptable(cuenta_mov):
            cuenta_mov = cuenta_doc if _es_cuenta_financiera_aceptable(cuenta_doc) else "No detectada"

        cliente_proveedor = inferir_cliente_proveedor(
            texto=texto_bloque,
            archivo=archivo,
            tipo_doc="extracto_bancario",
            categoria=categoria,
            valor=valor,
        )
        cliente_proveedor = _normalizar_cliente_proveedor_detectado(cliente_proveedor) or (
            "No detectado" if cliente_proveedor == "No detectado" else None
        )

        if not es_movimiento_relevante(valor, categoria):
            categoria_agrupada = _normalizar_categoria_agrupada(categoria, valor)

            if valor > 0:
                otros_cobros_total += abs(valor)
                otros_cobros_cantidad += 1
            else:
                otros_pagos_total += abs(valor)
                otros_pagos_cantidad += 1

            _ = categoria_agrupada
            continue

        clave = (
            archivo,
            banco_mov,
            cuenta_mov,
            fecha or "sin_fecha",
            round(valor, 2),
            descripcion[:180],
            categoria,
        )
        if clave in vistos:
            continue

        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": fecha or "No detectada",
            "periodo": obtener_periodo(fecha or "No detectada"),
            "importe": f"{abs(valor):.2f}".replace(".", ","),
            "importe_num": abs(valor),
            "importe_firmado_num": valor,
            "naturaleza": naturaleza,
            "categoria": categoria,
            "descripcion": descripcion,
            "moneda": moneda,
            "banco": banco_mov,
            "entidad_financiera": entidad_financiera_mov,
            "cuenta": cuenta_mov,
            "cliente_proveedor": cliente_proveedor,
            "metodo_deteccion_banco": deteccion_mov.get("metodo_deteccion_banco", "fallback"),
            "soporte": False,
            "estado_conciliacion": "pendiente",
        })

        vistos.add(clave)
        contador += 1

    if otros_cobros_cantidad > 0:
        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": fecha_doc or "No detectada",
            "periodo": obtener_periodo(fecha_doc or "No detectada"),
            "importe": f"{otros_cobros_total:.2f}".replace(".", ","),
            "importe_num": otros_cobros_total,
            "importe_firmado_num": otros_cobros_total,
            "naturaleza": "entrada",
            "categoria": "otros_cobros",
            "descripcion": f"{otros_cobros_cantidad} movimientos menores agrupados",
            "moneda": detectar_moneda(texto),
            "banco": banco_doc or "No detectado",
            "entidad_financiera": entidad_financiera_doc or banco_doc or "No detectada",
            "cuenta": cuenta_doc or "No detectada",
            "cliente_proveedor": None,
            "metodo_deteccion_banco": deteccion_doc.get("metodo_deteccion_banco", "fallback"),
            "soporte": False,
            "estado_conciliacion": "agrupado",
        })
        contador += 1

    if otros_pagos_cantidad > 0:
        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": fecha_doc or "No detectada",
            "periodo": obtener_periodo(fecha_doc or "No detectada"),
            "importe": f"{otros_pagos_total:.2f}".replace(".", ","),
            "importe_num": otros_pagos_total,
            "importe_firmado_num": -otros_pagos_total,
            "naturaleza": "salida",
            "categoria": "otros_pagos",
            "descripcion": f"{otros_pagos_cantidad} movimientos menores agrupados",
            "moneda": detectar_moneda(texto),
            "banco": banco_doc or "No detectado",
            "entidad_financiera": entidad_financiera_doc or banco_doc or "No detectada",
            "cuenta": cuenta_doc or "No detectada",
            "cliente_proveedor": None,
            "metodo_deteccion_banco": deteccion_doc.get("metodo_deteccion_banco", "fallback"),
            "soporte": False,
            "estado_conciliacion": "agrupado",
        })

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
        moneda_doc = detectar_moneda(texto)

        deteccion_financiera_doc = inferir_banco_desde_fuentes(
            archivo=archivo,
            texto=texto,
            bloque_texto="",
            resumen_extracto=resumen_extracto,
        )
        metodo_deteccion_banco = deteccion_financiera_doc.get("metodo_deteccion_banco", "fallback")

        banco_doc_confiable = None
        entidad_financiera_doc_confiable = None
        cuenta_doc_confiable = None

        if tipo_doc == "extracto_bancario":
            banco_doc_confiable = _normalizar_banco_detectado(deteccion_financiera_doc.get("banco")) or "No detectado"
            entidad_financiera_doc_confiable = _normalizar_banco_detectado(deteccion_financiera_doc.get("entidad_financiera")) or "No detectada"
            cuenta_doc_confiable = _normalizar_cuenta_detectada(deteccion_financiera_doc.get("cuenta")) or "No detectada"
        else:
            if metodo_deteccion_banco in ["alias_conocido", "patron_explicito"]:
                banco_doc_confiable = _normalizar_banco_detectado(deteccion_financiera_doc.get("banco"))
                entidad_financiera_doc_confiable = _normalizar_banco_detectado(deteccion_financiera_doc.get("entidad_financiera"))
                cuenta_doc_confiable = _normalizar_cuenta_detectada(deteccion_financiera_doc.get("cuenta"))

        if tipo_doc in ["factura_venta", "factura_compra"]:
            importe_principal = extraer_importe_principal(texto, tipo_doc, importes)

            if importe_principal:
                naturaleza = "entrada" if tipo_doc == "factura_venta" else "salida"
                importe_num = normalizar_importe(importe_principal) or 0.0
                cliente_proveedor = doc.get("cliente_proveedor") or inferir_cliente_proveedor(
                    texto=texto,
                    archivo=archivo,
                    tipo_doc=tipo_doc,
                    valor=importe_num if naturaleza == "entrada" else -importe_num,
                )
                cliente_proveedor = _normalizar_cliente_proveedor_detectado(cliente_proveedor) or (
                    "No detectado" if cliente_proveedor == "No detectado" else None
                )

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
                    "moneda": moneda_doc,
                    "banco": banco_doc_confiable,
                    "entidad_financiera": entidad_financiera_doc_confiable,
                    "cuenta": cuenta_doc_confiable,
                    "cliente_proveedor": cliente_proveedor,
                    "metodo_deteccion_banco": metodo_deteccion_banco,
                    "soporte": True,
                    "estado_conciliacion": "pendiente",
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
                    "moneda": moneda_doc,
                    "banco": banco_doc_confiable,
                    "entidad_financiera": entidad_financiera_doc_confiable,
                    "cuenta": cuenta_doc_confiable,
                    "cliente_proveedor": None,
                    "metodo_deteccion_banco": metodo_deteccion_banco,
                    "soporte": True,
                    "resumen_extracto": resumen_extracto,
                    "estado_conciliacion": "no_aplica",
                })

            movimientos = extraer_movimientos_extracto(
                texto=texto,
                archivo=archivo,
                fecha_doc=fecha,
                banco_doc=banco_doc_confiable,
                cuenta_doc=cuenta_doc_confiable,
                entidad_financiera_doc=entidad_financiera_doc_confiable,
                resumen_extracto=resumen_extracto,
            )

            for n, movimiento in enumerate(movimientos, start=1):
                movimiento["id"] = f"bank_{idx}_{n}"
                ledger.append(movimiento)

        else:
            importe_principal = extraer_importe_principal(texto, tipo_doc, importes)

            if importe_principal:
                importe_num = normalizar_importe(importe_principal) or 0.0
                cliente_proveedor = doc.get("cliente_proveedor") or inferir_cliente_proveedor(
                    texto=texto,
                    archivo=archivo,
                    tipo_doc=tipo_doc,
                    valor=importe_num,
                )
                cliente_proveedor = _normalizar_cliente_proveedor_detectado(cliente_proveedor) or (
                    "No detectado" if cliente_proveedor == "No detectado" else None
                )

                ledger.append({
                    "id": f"doc_{idx}",
                    "archivo": archivo,
                    "tipo": tipo_doc,
                    "fecha": fecha,
                    "periodo": periodo,
                    "importe": importe_principal,
                    "importe_num": importe_num,
                    "importe_firmado_num": 0.0,
                    "naturaleza": "revisar",
                    "categoria": "otros",
                    "descripcion": archivo,
                    "moneda": moneda_doc,
                    "banco": banco_doc_confiable,
                    "entidad_financiera": entidad_financiera_doc_confiable,
                    "cuenta": cuenta_doc_confiable,
                    "cliente_proveedor": cliente_proveedor,
                    "metodo_deteccion_banco": metodo_deteccion_banco,
                    "soporte": True,
                    "estado_conciliacion": "pendiente",
                })

    return ledger
