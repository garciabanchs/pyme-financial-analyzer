import os
import re
from datetime import datetime
from parser_financiero import (
    normalizar_importe,
    extraer_importe_principal,
    obtener_periodo,
)

PATRON_FECHA = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b")
PATRON_IMPORTE = re.compile(r"-?\d{1,3}(?:\.\d{3})*,\d{2}")
PATRON_MONEDA = re.compile(
    r"\b(?:eur|usd|ves|cop|mxn|ars|clp|pen|gbp|brl|cad|chf|jpy|cny)\b|€|\$|us\$",
    flags=re.IGNORECASE,
)

UMBRAL_MOVIMIENTO_RELEVANTE = 100.0

# =========================================================
# DEBUG CONTROLADO
# Déjalo en False normalmente.
# Ponlo en True solo para diagnosticar.
# =========================================================
DEBUG_EXTRACTOS = False
DEBUG_SOLO_BANCOS = {"N26"}
DEBUG_FILE = "debug_extractos_n26.txt"

# =========================================================
# EXTRACCIÓN ROBUSTA DE ENTIDADES
# =========================================================
PALABRAS_FORMA_JURIDICA = [
    "sl", "s.l", "slu", "s.l.u", "sa", "s.a", "sau", "s.a.u",
    "sc", "s.c", "scp", "s.coop", "coop", "cooperativa",
    "cb", "c.b", "llc", "ltd", "inc", "corp", "gmbh", "sas",
    "spa", "bv", "nv", "oy", "ab", "as"
]

PALABRAS_EMPRESA = [
    "group", "holding", "solutions", "services", "systems",
    "industrial", "industriales", "comercial", "comerciales",
    "equipamiento", "logistica", "logística", "consulting",
    "consultoria", "consultoría", "management", "ventures",
    "partners", "studio", "market", "foods", "tech", "digital",
    "floristeria", "floristería", "decoracion", "decoración",
    "restaurante", "cafe", "café", "bar", "tienda", "shop",
    "medical", "clinic", "clinica", "clínica", "laboratorio",
    "farmacia", "transportes", "construcciones", "ingenieria",
    "ingeniería", "arquitectura", "abogados", "asesores",
    "consultores", "finanzas", "energia", "energía"
]

PALABRAS_RUIDO_DURAS = [
    "factura", "invoice", "fecha", "date", "vencimiento", "due date",
    "total", "subtotal", "base imponible", "cuota", "iva", "irpf",
    "descuento", "retencion", "retención", "cantidad", "precio",
    "concepto", "descripcion", "descripción", "articulo", "artículo",
    "importe", "saldo", "cuenta", "bank", "banco", "payment",
    "transfer", "transferencia", "domicilio", "direccion", "dirección",
    "calle", "avenida", "avda", "postal", "ciudad", "country",
    "pais", "país", "euros", "eur", "forma de pago", "metodo de pago",
    "método de pago", "payment method", "fecha de emision",
    "fecha de emisión", "invoice number", "numero de factura",
    "número de factura", "albaran", "albarán", "ref.", "ref",
    "cant.", "cant", "pvp", "datos de facturacion", "datos de facturación",
    "registro mercantil", "mercantil", "folio", "tomo", "libro", "hoja",
    "ref. cant. concepto", "pvp/u", "f. envio", "f. envío"
]

ETIQUETAS_CLIENTE = [
    r"\bcliente\b",
    r"\bcustomer\b",
    r"\bbill to\b",
    r"\bsold to\b",
    r"\bship to\b",
    r"\bdestinatario\b",
    r"\breceptor\b",
    r"\bdatos de facturacion\b",
    r"\bdatos de facturación\b",
]

ETIQUETAS_PROVEEDOR = [
    r"\bproveedor\b",
    r"\bsupplier\b",
    r"\bemisor\b",
    r"\bissuer\b",
    r"\bvendor\b",
]


def limpiar_descripcion(linea):
    return " ".join((linea or "").strip().split())


def normalizar_fecha_texto(fecha_texto):
    fecha_texto = (fecha_texto or "").strip()
    if not fecha_texto or fecha_texto.lower() == "no detectada":
        return "No detectada"

    formatos_entrada = [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%d.%m.%Y",
        "%d.%m.%y",
    ]

    for fmt in formatos_entrada:
        try:
            dt = datetime.strptime(fecha_texto, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            continue

    return fecha_texto


def fecha_ordenable(fecha_texto):
    fecha_texto = normalizar_fecha_texto(fecha_texto)
    if not fecha_texto or fecha_texto == "No detectada":
        return None

    try:
        return datetime.strptime(fecha_texto, "%d/%m/%Y")
    except ValueError:
        return None


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


# =========================================================
# HELPERS DE ENTIDADES
# =========================================================
def _limpiar_linea_entidad(linea):
    linea = (linea or "").strip()
    linea = re.sub(r"\s+", " ", linea)
    linea = linea.strip(" -:;,.|_/\\")
    return linea


def _normalizar_entidad(linea):
    linea = _limpiar_linea_entidad(linea).lower()
    linea = re.sub(r"[^a-záéíóúüñ0-9&.\- /]", " ", linea)
    linea = re.sub(r"\s+", " ", linea).strip()
    return linea


def _limpiar_nombre_entidad(linea):
    linea = _limpiar_linea_entidad(linea)
    linea = re.sub(
        r"\b(?:cliente|proveedor|bill to|sold to|ship to|customer|supplier|emisor|receptor|issuer|vendor)\b\s*[:\-]*",
        "",
        linea,
        flags=re.IGNORECASE,
    )
    linea = re.sub(r"\s+", " ", linea).strip(" -:;,.|_/\\")
    return linea


def _es_archivo_o_codigo(linea):
    x = (linea or "").strip()
    if not x:
        return True

    if re.search(r"\.pdf\b|\.(xml|csv|xlsx|xls|doc|docx)\b", x, flags=re.IGNORECASE):
        return True

    if re.fullmatch(r"[A-Za-z0-9_\-]+\.[A-Za-z0-9]+", x):
        return True

    if re.fullmatch(r"[A-Za-z]?\d{6,}[A-Za-z0-9\-]*", x):
        return True

    return False


def _limpiar_resultado_entidad(linea):
    x = _limpiar_nombre_entidad(linea)

    cortes = [
        r"\bCIF\b", r"\bNIF\b", r"\bNIE\b", r"\bVAT\b",
        r"\bIVA\b", r"\bIBAN\b", r"\bSWIFT\b", r"\bBIC\b",
        r"\bTEL\b", r"\bTLF\b", r"\bPHONE\b", r"\bFAX\b",
        r"\bEMAIL\b", r"\bE-?MAIL\b", r"@",
        r"\bC/\b", r"\bCALLE\b", r"\bAVDA\b", r"\bAVENIDA\b",
        r"\bPOL[ÍI]GONO\b", r"\bPOLIGONO\b", r"\bLOCAL\b",
        r"\bFACTURA\b", r"\bALBAR[ÁA]N\b",
        r"\bDATOS DE FACTURACI[ÓO]N\b",
        r"\bREGISTRO MERCANTIL\b", r"\bFOLIO\b", r"\bTOMO\b",
        r"\bLIBRO\b", r"\bHOJA\b", r"\bSECCI[ÓO]N\b",
        r"\bREF\.\b", r"\bCONCEPTO\b", r"\bPVP\b"
    ]

    for patron in cortes:
        m = re.search(patron, x, flags=re.IGNORECASE)
        if m:
            x = x[:m.start()].strip(" -:;,.|_/\\")
            break

    x = re.sub(r"\s+", " ", x).strip(" -:;,.|_/\\")
    return x


def _tiene_forma_juridica_pegada(linea):
    x = (linea or "").upper()
    formas = ["S.L.U.", "S.L.", "SLU", "SL", "S.A.U.", "S.A.", "SAU", "SA", "LLC", "LTD", "INC", "GMBH", "SAS"]
    for forma in formas:
        pos = x.find(forma)
        if pos != -1:
            return pos + len(forma)
    return -1


def _recortar_ocr_pegado_entidad(linea):
    x = _limpiar_resultado_entidad(linea)
    if not x:
        return x

    # Caso 1: cortar justo después de una forma jurídica aunque venga texto pegado
    fin_forma = _tiene_forma_juridica_pegada(x)
    if fin_forma != -1:
        candidato = x[:fin_forma].strip(" -:;,.|_/\\")
        if len(candidato.split()) >= 1:
            return candidato.upper()

    # Caso 2: cortar después de palabra empresarial fuerte aunque OCR haya pegado persona detrás
    palabras_corte = [
        "EQUIPAMIENTO", "INDUSTRIAL", "COMERCIAL", "SERVICES", "SOLUTIONS",
        "SYSTEMS", "GROUP", "HOLDING", "LOGISTICA", "LOGÍSTICA",
        "CONSULTING", "CONSULTORIA", "CONSULTORÍA", "MANAGEMENT",
        "DIGITAL", "TECH", "STUDIO", "MARKET", "FOODS", "CLINIC",
        "CLINICA", "CLÍNICA", "LABORATORIO", "FARMACIA", "TRANSPORTES",
        "CONSTRUCCIONES", "INGENIERIA", "INGENIERÍA", "ABOGADOS",
        "ASESORES", "CONSULTORES"
    ]

    x_upper = x.upper()
    for palabra in palabras_corte:
        pos = x_upper.find(palabra)
        if pos != -1:
            corte = pos + len(palabra)
            candidato = x_upper[:corte].strip(" -:;,.|_/\\")
            if len(candidato.split()) >= 2:
                return candidato

    return x


def _es_linea_basura_entidad(linea):
    raw = _limpiar_resultado_entidad(linea)
    t = _normalizar_entidad(raw)

    if not t:
        return True

    if len(raw) < 3 or len(raw) > 120:
        return True

    if raw.endswith(":"):
        return True

    if _es_archivo_o_codigo(raw):
        return True

    patrones_ruido = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b",
        r"\b(?:www\.|http://|https://)\S+\b",
        r"\b[a-z]{2}\d{2}[a-z0-9]{8,}\b",
        r"\b(?:cif|nif|nie|vat|iva|iban|swift|bic|ccc)\b",
        r"\b(?:tel|tlf|telefono|phone|m[óo]vil|mobile|fax)\b",
        r"\b\d{5}\b",
        r"\b\d{7,}\b",
        r"\b\d{1,3}(?:\.\d{3})*,\d{2}\b",
        r"\b\d+\.\d{2}\b",
    ]
    for patron in patrones_ruido:
        if re.search(patron, t, flags=re.IGNORECASE):
            return True

    if any(p in t for p in PALABRAS_RUIDO_DURAS):
        return True

    if raw.startswith("(") and raw.endswith(")"):
        return True

    if sum(ch.isdigit() for ch in raw) >= 6:
        return True

    if not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", raw):
        return True

    return False


def _tokens_significativos(linea):
    x = _limpiar_resultado_entidad(linea)
    x = re.sub(r"[|,;:()]+", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return [p for p in x.split() if p]


def _tiene_forma_juridica(linea):
    t = _normalizar_entidad(linea)
    return any(re.search(rf"\b{re.escape(p)}\b", t) for p in PALABRAS_FORMA_JURIDICA)


def _tiene_palabra_empresa(linea):
    t = _normalizar_entidad(linea)
    return any(re.search(rf"\b{re.escape(p)}\b", t) for p in PALABRAS_EMPRESA)


def _ratio_mayusculas(linea):
    letras = [c for c in (linea or "") if c.isalpha()]
    if not letras:
        return 0.0
    return sum(1 for c in letras if c.isupper()) / len(letras)


def _parece_persona(linea):
    x = _limpiar_resultado_entidad(linea)
    palabras = _tokens_significativos(x)

    if len(palabras) < 2 or len(palabras) > 4:
        return False

    if _tiene_forma_juridica(x) or _tiene_palabra_empresa(x):
        return False

    if any("&" in p for p in palabras):
        return False

    capitalizadas = 0
    for p in palabras:
        if p[:1].isupper() and (len(p) == 1 or p[1:].islower() or p[1:].isalpha()):
            capitalizadas += 1

    return capitalizadas >= max(2, len(palabras) - 1)


def _parece_autonomo(linea):
    x = _limpiar_resultado_entidad(linea)
    if _tiene_forma_juridica(x):
        return False
    return _parece_persona(x)


def _parece_empresa(linea):
    x = _recortar_ocr_pegado_entidad(linea)
    if _es_linea_basura_entidad(x):
        return False

    palabras = _tokens_significativos(x)
    if not palabras:
        return False

    if _tiene_forma_juridica(x):
        return True

    if _tiene_palabra_empresa(x):
        return True

    ratio = _ratio_mayusculas(x)
    if ratio > 0.72 and 1 <= len(palabras) <= 8:
        return True

    if 2 <= len(palabras) <= 6 and not _parece_persona(x):
        return True

    return False


def _extraer_por_etiquetas(texto, etiquetas, max_lineas=4):
    lineas = [_limpiar_linea_entidad(x) for x in (texto or "").splitlines()]
    lineas = [x for x in lineas if x]

    candidatos = []

    for i, linea in enumerate(lineas):
        linea_norm = _normalizar_entidad(linea)

        for etiqueta in etiquetas:
            if re.search(etiqueta, linea_norm, flags=re.IGNORECASE):
                partes = re.split(etiqueta, linea, flags=re.IGNORECASE)
                if len(partes) > 1:
                    resto = _limpiar_resultado_entidad(partes[-1])
                    if resto:
                        candidatos.append(("etiqueta_misma_linea", resto, i))

                for j in range(i + 1, min(i + 1 + max_lineas, len(lineas))):
                    cand = _limpiar_resultado_entidad(lineas[j])
                    if cand:
                        candidatos.append(("etiqueta_linea_siguiente", cand, j))

    return candidatos


def _extraer_candidatos_generales(texto, primeros_n=30):
    lineas = [_limpiar_linea_entidad(x) for x in (texto or "").splitlines()]
    lineas = [x for x in lineas if x][:primeros_n]

    candidatos = []
    for i, linea in enumerate(lineas):
        limpio = _limpiar_resultado_entidad(linea)
        if limpio:
            candidatos.append(("general", limpio, i))

    return candidatos


def _deduplicar_candidatos(candidatos):
    dedup = []
    vistos = set()

    for cand in candidatos:
        _, texto, _ = cand
        clave = _normalizar_entidad(_recortar_ocr_pegado_entidad(texto))
        if not clave or clave in vistos:
            continue
        vistos.add(clave)
        dedup.append(cand)

    return dedup


def _score_probabilistico_entidad(candidato, rol_esperado):
    origen, texto, posicion = candidato
    x = _recortar_ocr_pegado_entidad(texto)

    if not x or _es_archivo_o_codigo(x) or _es_linea_basura_entidad(x):
        return -999.0, {"tipo": "descartado"}

    palabras = _tokens_significativos(x)
    score = 0.0
    meta = {
        "tipo": "indefinido",
        "empresa": False,
        "autonomo": False,
        "persona": False,
    }

    if origen == "etiqueta_misma_linea":
        score += 70
    elif origen == "etiqueta_linea_siguiente":
        score += 55
    elif origen == "general":
        score += 15

    if rol_esperado == "proveedor":
        score += max(0, 20 - posicion * 1.5)
    else:
        score += max(0, 18 - abs(posicion - 6) * 1.2)

    if 2 <= len(palabras) <= 6:
        score += 18
    elif len(palabras) == 1:
        score += 5
    elif len(palabras) <= 8:
        score += 8
    else:
        score -= 20

    if 5 <= len(x) <= 60:
        score += 10
    elif len(x) > 90:
        score -= 20

    if _parece_empresa(x):
        score += 40
        meta["empresa"] = True
        meta["tipo"] = "empresa"

    if _parece_autonomo(x):
        score += 22
        meta["autonomo"] = True
        if meta["tipo"] == "indefinido":
            meta["tipo"] = "autonomo"

    if _parece_persona(x):
        meta["persona"] = True
        if meta["tipo"] == "indefinido":
            meta["tipo"] = "persona"

    if _tiene_forma_juridica(x):
        score += 30

    if _tiene_palabra_empresa(x):
        score += 12

    ratio_mayus = _ratio_mayusculas(x)
    if ratio_mayus > 0.75:
        score += 10
    elif ratio_mayus < 0.15 and not _parece_autonomo(x):
        score -= 8

    if any(ch.isdigit() for ch in x):
        score -= 8

    if re.search(r"@|http|www\.", x, flags=re.IGNORECASE):
        score -= 40

    if re.search(r"\b(calle|avda|avenida|local|piso|puerta|poligono|polígono)\b", _normalizar_entidad(x)):
        score -= 25

    return score, meta


def extraer_cliente_proveedor_desde_factura(texto, tipo_doc):
    texto = texto or ""
    tipo_doc = (tipo_doc or "").strip().lower()

    if tipo_doc not in ["factura_venta", "factura_compra"]:
        return None

    rol_esperado = "cliente" if tipo_doc == "factura_venta" else "proveedor"

    candidatos = []
    if rol_esperado == "cliente":
        candidatos.extend(_extraer_por_etiquetas(texto, ETIQUETAS_CLIENTE, max_lineas=5))
    else:
        candidatos.extend(_extraer_por_etiquetas(texto, ETIQUETAS_PROVEEDOR, max_lineas=4))

    candidatos.extend(_extraer_candidatos_generales(texto, primeros_n=30))
    candidatos = _deduplicar_candidatos(candidatos)

    if not candidatos:
        return None

    ranking = []
    for cand in candidatos:
        score, meta = _score_probabilistico_entidad(cand, rol_esperado=rol_esperado)
        if score > -200:
            ranking.append((score, cand, meta))

    if not ranking:
        return None

    ranking.sort(key=lambda x: x[0], reverse=True)

    # Para cliente: si el mejor parece persona y el segundo parece empresa, preferir empresa si está cerca
    if rol_esperado == "cliente" and len(ranking) >= 2:
        score1, cand1, meta1 = ranking[0]
        score2, cand2, meta2 = ranking[1]

        if meta1.get("persona") and meta2.get("empresa") and (score2 >= score1 - 12):
            ranking[0], ranking[1] = ranking[1], ranking[0]

    _, mejor_candidato, _ = ranking[0]
    _, mejor_texto, _ = mejor_candidato
    resultado = _recortar_ocr_pegado_entidad(mejor_texto)

    if not resultado:
        return None

    resultado = _recortar_ocr_pegado_entidad(resultado)

    if _es_linea_basura_entidad(resultado) or _es_archivo_o_codigo(resultado):
        return None

    return resultado


# =========================================================
# CLASIFICACIÓN BANCARIA
# =========================================================
def _contiene_alguno(texto, patrones):
    t = (texto or "").lower()
    return any(p in t for p in patrones)


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
        "instant transfer",
        "transferencias salientes",
        "transferencias entrantes",
        "incoming transfer",
        "outgoing transfer",
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
        "mastercard",
        "comida",
        "bares y restaurantes",
        "multimedia y tecnología",
        "multimedia y tecnologia",
        "cajeros automáticos",
        "cajeros automaticos",
        "ocio",
        "transporte",
        "compras",
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
        "bizum enviado",
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
        "bizum recibido",
        "ingresos",
        "received funds",
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
        if (
            "internal transfer" in t
            or "transferencia interna" in t
            or "traspaso" in t
            or "instant transfer" in t
            or "transferencias salientes" in t
            or "transferencias entrantes" in t
        ):
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


# =========================================================
# HELPERS EXTRACTOS
# =========================================================
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
        "transaction",
        "booking",
        "bank transfer",
        "direct debit",
        "cash withdrawal",
        "card payment",
        "pos",
        "visa",
        "mastercard",
        "transfer out",
        "transfer in",
        "incoming transfer",
        "outgoing transfer",
        "instant transfer",
        "ingresos",
        "compras",
        "comida",
        "transporte",
        "ocio",
        "bares y restaurantes",
        "multimedia y tecnología",
        "multimedia y tecnologia",
        "cajeros automáticos",
        "cajeros automaticos",
        "transferencias salientes",
        "transferencias entrantes",
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
            return normalizar_fecha_texto(m.group())

    fecha_doc_normalizada = normalizar_fecha_texto(fecha_doc)
    return fecha_doc_normalizada if fecha_doc_normalizada else "No detectada"


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
        "bizum recibido",
        "ingresos",
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
        "bizum enviado",
        "transferencias salientes",
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

    total_importes = len(PATRON_IMPORTE.findall(texto))
    tiene_fecha = any(bool(PATRON_FECHA.search(linea)) for linea in bloque)
    tiene_huella = tiene_huella_transaccional(texto)

    if total_importes == 0:
        return True

    if len(bloque) >= 4 and total_importes >= 4 and not tiene_fecha:
        return True

    if not tiene_huella and not tiene_fecha:
        return True

    return False


def es_movimiento_relevante(valor, categoria):
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
        return "otros_cobros"

    if valor < 0:
        return "otros_pagos"

    return "otros_pagos"


def _es_linea_resumen_bancario(linea):
    linea_lower = (linea or "").strip().lower()

    patrones_resumen = [
        "saldo inicial",
        "saldo final",
        "saldo previo",
        "tu nuevo saldo",
        "nuevo saldo",
        "balance",
        "summary",
        "resumen",
        "overview",
        "activity summary",
        "subtotal",
        "totales",
        "total",
        "pagos recibidos",
        "pagos enviados",
        "retiradas y cargos",
        "depósitos y créditos",
        "depositos y creditos",
        "tarifas",
        "liberaciones",
        "retenido",
        "transacciones entrantes",
        "transacciones salientes",
        "incoming transactions",
        "outgoing transactions",
        "credits total",
        "debits total",
        "account summary",
        "statement summary",
    ]

    if any(p in linea_lower for p in patrones_resumen):
        return True

    importes = PATRON_IMPORTE.findall(linea or "")
    if len(importes) == 1:
        tokens = [t for t in linea_lower.split() if t]
        if len(tokens) <= 6 and any(
            p in linea_lower for p in [
                "saldo", "entrantes", "salientes", "summary", "resumen", "balance"
            ]
        ):
            return True

    return False


def _linea_candidata_movimiento(linea):
    if not linea:
        return False

    linea_lower = linea.lower()

    if es_linea_ruido(linea_lower):
        return False

    if _es_linea_resumen_bancario(linea):
        return False

    importes = PATRON_IMPORTE.findall(linea)
    if not importes:
        return False

    if len(importes) >= 4:
        return False

    if PATRON_FECHA.search(linea):
        return True

    if tiene_huella_transaccional(linea_lower):
        return True

    return False


def _debug_append(texto):
    print(texto)


def _debug_lineas_extracto(texto, archivo="", banco=""):
    if not DEBUG_EXTRACTOS:
        return

    if DEBUG_SOLO_BANCOS and banco not in DEBUG_SOLO_BANCOS:
        return

    _debug_append("\n" + "=" * 90)
    _debug_append(f"DEBUG EXTRACTO | banco={banco} | archivo={archivo}")
    _debug_append("=" * 90)

    for i, raw in enumerate((texto or "").splitlines(), start=1):
        linea = limpiar_descripcion(raw)
        if not linea:
            continue

        tiene_fecha = bool(PATRON_FECHA.search(linea))
        importes = PATRON_IMPORTE.findall(linea)
        huella = tiene_huella_transaccional(linea.lower())
        resumen = _es_linea_resumen_bancario(linea)
        candidata = _linea_candidata_movimiento(linea)

        if importes or tiene_fecha or huella:
            _debug_append(
                f"[{i:03}] fecha={tiene_fecha} huella={huella} resumen={resumen} "
                f"candidata={candidata} importes={importes} :: {linea}"
            )


def _extraer_movimientos_extracto_por_linea(texto, archivo, fecha_doc, banco=None):
    movimientos = []
    vistos = set()
    contador = 1

    otros_cobros_total = 0.0
    otros_pagos_total = 0.0
    otros_cobros_cantidad = 0
    otros_pagos_cantidad = 0

    lineas = [limpiar_descripcion(raw) for raw in (texto or "").splitlines()]
    lineas = [l for l in lineas if l]

    for i, linea in enumerate(lineas):
        if _es_linea_resumen_bancario(linea):
            continue

        if not _linea_candidata_movimiento(linea):
            continue

        importes = PATRON_IMPORTE.findall(linea)
        if not importes:
            continue

        candidatos = []
        for imp in importes:
            valor = normalizar_importe(imp)
            if valor is not None:
                candidatos.append(valor)

        if not candidatos:
            continue

        valor = max(candidatos, key=lambda x: abs(x))

        if abs(valor) < 0.01 or abs(valor) > 100000:
            continue

        fecha = extraer_fecha_de_bloque([linea], fecha_doc)
        moneda = detectar_moneda(linea)

        descripcion_partes = []

        j = i - 1
        pasos = 0
        while j >= 0 and pasos < 3:
            previa = lineas[j]
            previa_lower = previa.lower()

            if _es_linea_resumen_bancario(previa):
                break

            if PATRON_IMPORTE.search(previa) and PATRON_FECHA.search(previa):
                break

            if not es_linea_ruido(previa_lower):
                descripcion_partes.insert(0, previa)

            if tiene_huella_transaccional(previa_lower):
                break

            j -= 1
            pasos += 1

        descripcion_partes.append(linea)

        descripcion = " | ".join([p for p in descripcion_partes if p])[:250]
        texto_clasificacion = " ".join(descripcion_partes).lower()

        categoria = clasificar_movimiento_bancario(texto_clasificacion, valor)

        naturaleza = inferir_naturaleza_bloque(texto_clasificacion, valor)
        if naturaleza == "desconocido":
            naturaleza = "entrada" if valor > 0 else "salida"

        if not es_movimiento_relevante(valor, categoria):
            if valor > 0:
                otros_cobros_total += abs(valor)
                otros_cobros_cantidad += 1
            else:
                otros_pagos_total += abs(valor)
                otros_pagos_cantidad += 1
            continue

        clave = (
            archivo,
            fecha or "sin_fecha",
            round(valor, 2),
            descripcion[:180],
            categoria,
        )
        if clave in vistos:
            continue

        movimientos.append({
            "id": f"bank_fallback_{contador}",
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
            "moneda": moneda or detectar_moneda(descripcion),
            "banco": banco,
            "soporte": False,
            "estado_conciliacion": "pendiente",
        })

        vistos.add(clave)
        contador += 1

    if otros_cobros_cantidad > 0:
        movimientos.append({
            "id": f"bank_fallback_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": normalizar_fecha_texto(fecha_doc),
            "periodo": obtener_periodo(normalizar_fecha_texto(fecha_doc)),
            "importe": f"{otros_cobros_total:.2f}".replace(".", ","),
            "importe_num": otros_cobros_total,
            "importe_firmado_num": otros_cobros_total,
            "naturaleza": "entrada",
            "categoria": "otros_cobros",
            "descripcion": f"{otros_cobros_cantidad} movimientos menores agrupados",
            "moneda": detectar_moneda(texto),
            "banco": banco,
            "soporte": False,
            "estado_conciliacion": "agrupado",
        })
        contador += 1

    if otros_pagos_cantidad > 0:
        movimientos.append({
            "id": f"bank_fallback_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": normalizar_fecha_texto(fecha_doc),
            "periodo": obtener_periodo(normalizar_fecha_texto(fecha_doc)),
            "importe": f"{otros_pagos_total:.2f}".replace(".", ","),
            "importe_num": otros_pagos_total,
            "importe_firmado_num": -otros_pagos_total,
            "naturaleza": "salida",
            "categoria": "otros_pagos",
            "descripcion": f"{otros_pagos_cantidad} movimientos menores agrupados",
            "moneda": detectar_moneda(texto),
            "banco": banco,
            "soporte": False,
            "estado_conciliacion": "agrupado",
        })

    return movimientos


def extraer_movimientos_extracto(texto, archivo, fecha_doc, banco=None):
    movimientos = []
    if not texto:
        return movimientos

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
        moneda = extraer_moneda_de_bloque(bloque)

        naturaleza = inferir_naturaleza_bloque(texto_lower, valor)
        if naturaleza == "desconocido":
            naturaleza = "entrada" if valor > 0 else "salida"

        if not es_movimiento_relevante(valor, categoria):
            if valor > 0:
                otros_cobros_total += abs(valor)
                otros_cobros_cantidad += 1
            else:
                otros_pagos_total += abs(valor)
                otros_pagos_cantidad += 1
            continue

        clave = (
            archivo,
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
            "banco": banco,
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
            "fecha": normalizar_fecha_texto(fecha_doc),
            "periodo": obtener_periodo(normalizar_fecha_texto(fecha_doc)),
            "importe": f"{otros_cobros_total:.2f}".replace(".", ","),
            "importe_num": otros_cobros_total,
            "importe_firmado_num": otros_cobros_total,
            "naturaleza": "entrada",
            "categoria": "otros_cobros",
            "descripcion": f"{otros_cobros_cantidad} movimientos menores agrupados",
            "moneda": detectar_moneda(texto),
            "banco": banco,
            "soporte": False,
            "estado_conciliacion": "agrupado",
        })
        contador += 1

    if otros_pagos_cantidad > 0:
        movimientos.append({
            "id": f"bank_{contador}",
            "archivo": archivo,
            "tipo": "extracto_bancario",
            "fecha": normalizar_fecha_texto(fecha_doc),
            "periodo": obtener_periodo(normalizar_fecha_texto(fecha_doc)),
            "importe": f"{otros_pagos_total:.2f}".replace(".", ","),
            "importe_num": otros_pagos_total,
            "importe_firmado_num": -otros_pagos_total,
            "naturaleza": "salida",
            "categoria": "otros_pagos",
            "descripcion": f"{otros_pagos_cantidad} movimientos menores agrupados",
            "moneda": detectar_moneda(texto),
            "banco": banco,
            "soporte": False,
            "estado_conciliacion": "agrupado",
        })

    movimientos_individuales = [
        m for m in movimientos
        if m.get("categoria") not in ["otros_cobros", "otros_pagos"]
    ]

    if not movimientos_individuales:
        fallback = _extraer_movimientos_extracto_por_linea(
            texto=texto,
            archivo=archivo,
            fecha_doc=fecha_doc,
            banco=banco,
        )

        fallback_individuales = [
            m for m in fallback
            if m.get("categoria") not in ["otros_cobros", "otros_pagos"]
        ]

        if fallback_individuales:
            return fallback

    return movimientos


# =========================================================
# LEDGER
# =========================================================
def construir_ledger(documentos):
    ledger = []

    print("========== DEBUG CONSTRUIR_LEDGER INICIO ==========")
    print(f"Total documentos recibidos: {len(documentos or [])}")

    if DEBUG_EXTRACTOS:
        try:
            print(f"DEBUG_EXTRACTOS=True | DEBUG_SOLO_BANCOS={DEBUG_SOLO_BANCOS}")
        except Exception:
            pass

    for idx, doc in enumerate(documentos, start=1):
        texto = doc.get("texto", "")
        tipo_doc = doc.get("tipo", "otros")
        fecha = normalizar_fecha_texto(doc.get("fecha", "No detectada"))
        periodo = obtener_periodo(fecha)
        archivo = doc.get("archivo", f"doc_{idx}")
        importes = doc.get("importes", [])
        resumen_extracto = doc.get("resumen_extracto", {}) or {}
        moneda_doc = detectar_moneda(texto)

        print(
            f"[DOC {idx}] archivo={archivo} tipo={tipo_doc} fecha={fecha} "
            f"texto_len={len(texto or '')} importes_detectados={len(importes or [])}"
        )

        if tipo_doc in ["factura_venta", "factura_compra"]:
            importe_principal = extraer_importe_principal(texto, tipo_doc, importes)

            if importe_principal:
                naturaleza = "entrada" if tipo_doc == "factura_venta" else "salida"
                importe_num = normalizar_importe(importe_principal) or 0.0
                cliente_proveedor = extraer_cliente_proveedor_desde_factura(texto, tipo_doc)

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
                    "cliente_proveedor": cliente_proveedor or "No aplica",
                    "soporte": True,
                    "estado_conciliacion": "pendiente",
                })

                print("DEBUG FACTURA:", archivo, tipo_doc, "=>", cliente_proveedor)

        elif tipo_doc == "extracto_bancario":
            banco_doc = (resumen_extracto.get("banco") or "").strip()

            if not banco_doc:
                archivo_lower = (archivo or "").lower()
                texto_lower = (texto or "").lower()

                if "n26" in archivo_lower or "n26" in texto_lower:
                    banco_doc = "N26"
                elif "paypal" in archivo_lower or "paypal" in texto_lower:
                    banco_doc = "PayPal"

            if banco_doc and not resumen_extracto.get("banco"):
                resumen_extracto["banco"] = banco_doc

            print(
                f"[EXTRACTO {idx}] archivo={archivo} banco={banco_doc} "
                f"fecha={fecha} resumen_keys={list(resumen_extracto.keys()) if resumen_extracto else []}"
            )

            _debug_lineas_extracto(texto=texto, archivo=archivo, banco=banco_doc)

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
                    "banco": banco_doc,
                    "soporte": True,
                    "resumen_extracto": resumen_extracto,
                    "estado_conciliacion": "no_aplica",
                })

            movimientos = extraer_movimientos_extracto(
                texto=texto,
                archivo=archivo,
                fecha_doc=fecha,
                banco=banco_doc,
            )

            print(
                f"[EXTRACTO {idx}] archivo={archivo} banco={banco_doc} "
                f"movimientos_generados={len(movimientos)}"
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
                    "moneda": moneda_doc,
                    "soporte": True,
                    "estado_conciliacion": "pendiente",
                })

    print("========== DEBUG CONSTRUIR_LEDGER FIN ==========")
    print(f"Total items ledger generados: {len(ledger)}")

    return ledger
