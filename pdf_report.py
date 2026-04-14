import os
from io import BytesIO
from urllib.request import Request, urlopen
import ssl

from branding import BRANDING
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

from reportes import (
    fmt_importe_reporte,
    normalizar_importe_reporte,
    construir_resumen_documentos,
    construir_resumen_flujo,
    construir_resumen_conciliacion,
    construir_narrativa_ejecutiva,
    normalizar_estado_conciliacion,
    humanizar_estado_conciliacion,
    inferir_nombre_empresa,
)


def _fmt_eur(numero):
    return fmt_importe_reporte(numero)


def _num(valor):
    return normalizar_importe_reporte(valor)


def _resumen_flujo(documentos, ledger):
    return construir_resumen_flujo(ledger)


def _resumen_conciliacion(conciliacion):
    return construir_resumen_conciliacion(conciliacion)


def _resumen_documentos(clasificados):
    return construir_resumen_documentos(clasificados)


def _narrativa_pdf(total_documentos, docs, flujo, conc):
    return construir_narrativa_ejecutiva(total_documentos, docs, flujo, conc)


def _nombre_empresa_pdf(documentos, ledger):
    nombre_empresa = inferir_nombre_empresa(documentos, ledger)

    if not nombre_empresa or str(nombre_empresa).strip().lower() == "la empresa":
        return "la empresa analizada"

    nombre_empresa = " ".join(str(nombre_empresa).strip().split())
    if not nombre_empresa:
        return "la empresa analizada"

    if len(nombre_empresa) > 60:
        return "la empresa analizada"

    return nombre_empresa


def _titulo_pdf_empresa(nombre_empresa):
    nombre_empresa = " ".join(str(nombre_empresa or "").strip().split())
    if not nombre_empresa:
        return "Informe financiero de la empresa analizada"
    return f"Informe financiero de {nombre_empresa}"


def _subtitulo_pdf_empresa(nombre_empresa):
    nombre_empresa = " ".join(str(nombre_empresa or "").strip().split())
    if not nombre_empresa or nombre_empresa.lower() == "la empresa analizada":
        return "Resumen ejecutivo del período analizado"
    return f"Resumen ejecutivo del período analizado de {nombre_empresa}"


def _hallazgos_conciliacion_texto(conc):
    partes = [
        f"Pendiente de cobro estimado: € {_fmt_eur(conc.get('pendiente_cobro', 0))}.",
        f"Pendiente de pago estimado: € {_fmt_eur(conc.get('pendiente_pago', 0))}.",
        f"Conciliaciones exactas: {conc.get('conciliadas', 0)}.",
        f"Conciliaciones exactas múltiples: {conc.get('conciliadas_multi', 0)}.",
        f"Conciliaciones probables: {conc.get('parciales', 0)}.",
        f"Conciliaciones probables múltiples: {conc.get('probables_multi', 0)}.",
        f"Registros pendientes: {conc.get('pendientes', 0)}.",
        f"Movimientos sin soporte: {conc.get('sin_soporte', 0)}.",
        f"Duplicados potenciales: {conc.get('duplicados', 0)}.",
    ]
    return " ".join(partes)


def _observacion_ejecutiva(conc):
    nivel = conc.get("nivel_cierre", "medio")

    if nivel == "bajo":
        return (
            "La lectura financiera del período todavía no puede considerarse cerrada. "
            "Aunque el flujo ya es visible, persisten elementos pendientes, movimientos sin soporte "
            "o duplicados potenciales que reducen la confiabilidad del cierre."
        )

    if nivel == "medio":
        return (
            "La lectura financiera ya es útil para gestión, pero todavía requiere validaciones antes "
            "de considerarse un cierre limpio. Persisten coincidencias múltiples o señales de revisión "
            "que conviene confirmar."
        )

    return (
        "La lectura financiera del período es razonablemente consistente para revisión ejecutiva. "
        "Aun así, este documento no sustituye la validación contable, fiscal o documental definitiva."
    )


def _texto_calidad_cierre(conc):
    nivel = conc.get("nivel_cierre", "medio")
    if nivel == "alto":
        return "Cierre preliminar alto"
    if nivel == "medio":
        return "Cierre preliminar medio"
    return "Cierre preliminar bajo"


def _score_financiero_pdf(flujo, conc):
    score = 100
    score -= conc.get("pendientes", 0) * 12
    score -= conc.get("sin_soporte", 0) * 8
    score -= conc.get("duplicados", 0) * 6
    score -= conc.get("parciales", 0) * 5
    score -= conc.get("probables_multi", 0) * 7
    score -= conc.get("movimientos_bancarios_no_conciliables", 0) * 3
    score -= conc.get("movimientos_internos", 0) * 1

    if flujo.get("variacion", 0) < 0:
        score -= 8

    return max(min(score, 100), 0)


def _texto_score_financiero(score):
    if score >= 85:
        return "Muy sólido"
    if score >= 70:
        return "Sólido"
    if score >= 55:
        return "Aceptable"
    if score >= 40:
        return "Frágil"
    return "Crítico"


def _draw_paragraph(
    c,
    text,
    x,
    y,
    width,
    font_name="Helvetica",
    font_size=10,
    leading=13,
    color=HexColor("#334155"),
):
    c.setFont(font_name, font_size)
    c.setFillColor(color)

    lines = simpleSplit(str(text or ""), font_name, font_size, width)
    current_y = y

    for line in lines:
        c.drawString(x, current_y, line)
        current_y -= leading

    return current_y


def _draw_title_block(c, x, y, title, subtitle=None, width=15.5 * cm):
    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title)

    if subtitle:
        return _draw_paragraph(
            c,
            subtitle,
            x,
            y - 16,
            width,
            "Helvetica",
            9.5,
            12,
            HexColor("#64748b"),
        )
    return y - 16


def _draw_metric_card(
    c,
    x,
    y,
    w,
    h,
    title,
    value,
    subtitle="",
    bg="#ffffff",
    title_color="#64748b",
    value_color="#0f172a",
    subtitle_color="#94a3b8",
):
    c.setFillColor(HexColor(bg))
    c.roundRect(x, y - h, w, h, 14, fill=1, stroke=0)

    c.setFillColor(HexColor(title_color))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 12, y - 18, title)

    c.setFillColor(HexColor(value_color))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x + 12, y - 40, value)

    if subtitle:
        subtitle_lines = simpleSplit(str(subtitle), "Helvetica", 8.5, w - 24)
        c.setFillColor(HexColor(subtitle_color))
        c.setFont("Helvetica", 8.5)
        current_y = y - 56
        for line in subtitle_lines[:2]:
            c.drawString(x + 12, current_y, line)
            current_y -= 10


def _draw_info_box(c, x, y, w, h, title, body, bg="#ffffff", accent="#2563eb", chip_text="Resumen"):
    c.setFillColor(HexColor(bg))
    c.roundRect(x, y - h, w, h, 16, fill=1, stroke=0)

    chip_w = max(42, c.stringWidth(chip_text, "Helvetica-Bold", 8) + 16)
    c.setFillColor(HexColor(accent))
    c.roundRect(x + 10, y - 24, chip_w, 16, 8, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + 10 + chip_w / 2, y - 18, chip_text)

    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 18, y - 42, title)

    _draw_paragraph(
        c,
        body,
        x + 12,
        y - 60,
        w - 24,
        "Helvetica",
        9.5,
        12.5,
        HexColor("#475569"),
    )


def _draw_alert_card(c, x, y, w, h, tag, title, body, tag_bg, tag_fg):
    c.setFillColor(HexColor("#ffffff"))
    c.roundRect(x, y - h, w, h, 16, fill=1, stroke=0)

    tag_w = max(52, c.stringWidth(tag, "Helvetica-Bold", 7.5) + 18)
    c.setFillColor(HexColor(tag_bg))
    c.roundRect(x + 12, y - 22, tag_w, 14, 7, fill=1, stroke=0)

    c.setFillColor(HexColor(tag_fg))
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(x + 12 + tag_w / 2, y - 17, tag)

    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 10.5)
    title_lines = simpleSplit(str(title), "Helvetica-Bold", 10.5, w - 24)
    title_y = y - 38
    for line in title_lines[:2]:
        c.drawString(x + 12, title_y, line)
        title_y -= 12

    _draw_paragraph(
        c,
        body,
        x + 12,
        title_y - 4,
        w - 24,
        "Helvetica",
        8.7,
        11.2,
        HexColor("#475569"),
    )


def _safe_draw_remote_image(c, url, x, y, width=None, height=None):
    if not url:
        return False

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }

        req = Request(url, headers=headers)
        context = ssl.create_default_context()

        with urlopen(req, timeout=15, context=context) as response:
            img_bytes = response.read()

        img = ImageReader(BytesIO(img_bytes))
        c.drawImage(
            img,
            x,
            y,
            width=width,
            height=height,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )
        return True

    except Exception as e:
        print(f"Error cargando imagen remota {url}: {e}")
        return False


def _safe_draw_local_image(c, relative_path, x, y, width=None, height=None):
    if not relative_path:
        return False

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, relative_path)

        if not os.path.exists(image_path):
            print(f"Imagen local no encontrada: {image_path}")
            return False

        img = ImageReader(image_path)
        c.drawImage(
            img,
            x,
            y,
            width=width,
            height=height,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )
        return True

    except Exception as e:
        print(f"Error cargando imagen local {relative_path}: {e}")
        return False


def _draw_footer(c, width):
    c.setStrokeColor(HexColor("#e2e8f0"))
    c.setLineWidth(0.6)
    c.line(2 * cm, 1.4 * cm, width - 2 * cm, 1.4 * cm)

    c.setFillColor(HexColor("#64748b"))
    c.setFont("Helvetica", 8.5)
    c.drawString(
        2 * cm,
        0.95 * cm,
        "PYME Financial Analyzer · Resumen ejecutivo generado a partir de documentos procesados",
    )
    c.drawRightString(width - 2 * cm, 0.95 * cm, str(c.getPageNumber()))


def generar_pdf_ejecutivo(pdf_path, nombre_zip, clasificados, documentos, ledger, conciliacion):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin_x = 2 * cm
    usable_w = width - 2 * margin_x

    branding_data = BRANDING[BRANDING["modo"]]
    docs = _resumen_documentos(clasificados)
    flujo = _resumen_flujo(documentos, ledger)
    conc = _resumen_conciliacion(conciliacion)

    nombre_empresa = _nombre_empresa_pdf(documentos, ledger)
    titulo_pdf_empresa = _titulo_pdf_empresa(nombre_empresa)
    subtitulo_pdf_empresa = _subtitulo_pdf_empresa(nombre_empresa)

    titular, narrativa = _narrativa_pdf(
        total_documentos=sum(docs.values()),
        docs=docs,
        flujo=flujo,
        conc=conc,
    )

    total_docs_clasificados = (
        len(clasificados.get("factura_venta", []))
        + len(clasificados.get("factura_compra", []))
        + len(clasificados.get("extracto_bancario", []))
        + len(clasificados.get("otros", []))
    )

    score_financiero = _score_financiero_pdf(flujo, conc)
    texto_score = _texto_score_financiero(score_financiero)
    cierre_texto = _texto_calidad_cierre(conc)

    # =========================
    # PÁGINA 1
    # =========================
    c.setFillColor(HexColor("#eef4fb"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setFillColor(HexColor("#0f172a"))
    c.roundRect(margin_x, height - 7.8 * cm, usable_w, 6.0 * cm, 22, fill=1, stroke=0)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_x + 18, height - 2.4 * cm, "PYME FINANCIAL ANALYZER")

    c.setFont("Helvetica-Bold", 21)
    titulo_lineas = simpleSplit(titulo_pdf_empresa, "Helvetica-Bold", 21, usable_w - 36)
    titulo_y = height - 3.25 * cm
    for linea in titulo_lineas[:2]:
        c.drawString(margin_x + 18, titulo_y, linea)
        titulo_y -= 0.62 * cm

    c.setFillColor(HexColor("#cbd5e1"))
    c.setFont("Helvetica", 10.2)
    c.drawString(margin_x + 18, height - 4.55 * cm, f"Archivo analizado: {nombre_zip}")
    c.drawString(margin_x + 18, height - 5.15 * cm, subtitulo_pdf_empresa)

    chip_y = height - 6.25 * cm
    chip_x = margin_x + 18
    chip_gap = 8
    chips = [
        f"Documentos clasificados: {total_docs_clasificados}",
        f"Pendientes: {conc.get('pendientes', 0)}",
        f"Variación: € {_fmt_eur(flujo.get('variacion', 0))}",
        cierre_texto,
    ]
    current_x = chip_x
    for chip in chips:
        tw = c.stringWidth(chip, "Helvetica-Bold", 8.5) + 18
        if current_x + tw > width - margin_x - 18:
            break
        c.setFillColor(HexColor("#1e293b"))
        c.roundRect(current_x, chip_y, tw, 18, 9, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(current_x + 9, chip_y + 5.5, chip)
        current_x += tw + chip_gap

    y_cards = height - 8.95 * cm
    card_gap = 10
    card_w = (usable_w - card_gap) / 2
    card_h = 2.35 * cm

    _draw_metric_card(
        c, margin_x, y_cards, card_w, card_h,
        "Entradas", f"€ {_fmt_eur(flujo.get('entradas', 0))}",
        "Dinero que entró en el período", bg="#ffffff"
    )
    _draw_metric_card(
        c, margin_x + card_w + card_gap, y_cards, card_w, card_h,
        "Salidas", f"€ {_fmt_eur(flujo.get('salidas', 0))}",
        "Dinero que salió en el período", bg="#fef7ed"
    )

    y_cards_2 = y_cards - card_h - 10
    _draw_metric_card(
        c, margin_x, y_cards_2, card_w, card_h,
        "Saldo final", f"€ {_fmt_eur(flujo.get('saldo_final', 0))}",
        f"Saldo inicial: € {_fmt_eur(flujo.get('saldo_inicial', 0))}",
        bg="#eff6ff", value_color="#0f4cff"
    )
    _draw_metric_card(
        c, margin_x + card_w + card_gap, y_cards_2, card_w, card_h,
        "Score financiero", f"{score_financiero}/100",
        texto_score, bg="#f8fafc", value_color="#111827"
    )

    y = y_cards_2 - card_h - 18

    y = _draw_title_block(
        c,
        margin_x,
        y,
        "Lectura ejecutiva",
        "Resumen narrativo del flujo, la conciliación y las principales señales detectadas durante el procesamiento.",
        width=usable_w,
    )

    c.setFillColor(HexColor("#ffffff"))
    c.roundRect(margin_x, y - 3.45 * cm, usable_w, 3.45 * cm, 16, fill=1, stroke=0)

    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 12)
    titular_lineas = simpleSplit(str(titular), "Helvetica-Bold", 12, usable_w - 28)
    titulo_box_y = y - 16
    for linea in titular_lineas[:2]:
        c.drawString(margin_x + 14, titulo_box_y, linea)
        titulo_box_y -= 13

    _draw_paragraph(
        c,
        narrativa,
        margin_x + 14,
        titulo_box_y - 4,
        usable_w - 28,
        "Helvetica",
        9.3,
        12.2,
        HexColor("#475569"),
    )

    y -= 3.95 * cm

    box_gap = 10
    box_w = (usable_w - (2 * box_gap)) / 3
    alert_h = 3.35 * cm

    _draw_alert_card(
        c,
        margin_x,
        y,
        box_w,
        alert_h,
        "FORTALEZA",
        "Base documental estructurada",
        "Los documentos procesados ya permiten reconstruir una lectura útil del período y una base inicial para revisión financiera.",
        "#ecfdf3",
        "#16a34a",
    )

    _draw_alert_card(
        c,
        margin_x + box_w + box_gap,
        y,
        box_w,
        alert_h,
        "SEGUIMIENTO",
        "Calidad del cierre",
        (
            f"Nivel del cierre: {cierre_texto}. "
            f"Pendientes: {conc.get('pendientes', 0)}. "
            f"Conciliaciones probables múltiples: {conc.get('probables_multi', 0)}."
        ),
        "#fff9e8",
        "#ca8a04",
    )

    _draw_alert_card(
        c,
        margin_x + (box_w + box_gap) * 2,
        y,
        box_w,
        alert_h,
        "RIESGO",
        "Señales relevantes",
        (
            f"Sin soporte: {conc.get('sin_soporte', 0)}. "
            f"Duplicados potenciales: {conc.get('duplicados', 0)}. "
            f"No conciliables: {conc.get('no_conciliables', 0)}."
        ),
        "#fef2f2",
        "#dc2626",
    )

    _draw_footer(c, width)

    # =========================
    # PÁGINA 2
    # =========================
    c.showPage()
    c.setFillColor(HexColor("#eef4fb"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    y = height - 2.2 * cm

    y = _draw_title_block(
        c,
        margin_x,
        y,
        "Desglose ejecutivo",
        "Clasificación documental, conciliación y contexto complementario del informe.",
        width=usable_w,
    )

    info_h = 3.45 * cm
    _draw_info_box(
        c,
        margin_x,
        y - 0.2 * cm,
        usable_w,
        info_h,
        "Composición documental",
        (
            f"Facturas de venta: {len(clasificados.get('factura_venta', []))}. "
            f"Facturas de compra: {len(clasificados.get('factura_compra', []))}. "
            f"Extractos bancarios: {len(clasificados.get('extracto_bancario', []))}. "
            f"Otros documentos: {len(clasificados.get('otros', []))}."
        ),
        bg="#ffffff",
        accent="#2563eb",
        chip_text="Documentos",
    )

    y -= info_h + 18

    _draw_info_box(
        c,
        margin_x,
        y,
        usable_w,
        info_h,
        "Conciliación del período",
        _hallazgos_conciliacion_texto(conc),
        bg="#ffffff",
        accent="#0f172a",
        chip_text="Conciliación",
    )

    y -= info_h + 18

    c.setFillColor(HexColor("#fff7ed"))
    c.roundRect(margin_x, y - 3.55 * cm, usable_w, 3.55 * cm, 16, fill=1, stroke=0)

    c.setFillColor(HexColor("#9a3412"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x + 14, y - 18, "Observación ejecutiva")

    texto_observacion = _observacion_ejecutiva(conc)

    _draw_paragraph(
        c,
        texto_observacion,
        margin_x + 14,
        y - 36,
        usable_w - 28,
        "Helvetica",
        9.6,
        12.8,
        HexColor("#7c2d12"),
    )

    y -= 4.05 * cm

    if BRANDING.get("mostrar_bio", False):
        c.setFillColor(HexColor("#ffffff"))
        c.roundRect(margin_x, y - 4.7 * cm, usable_w, 4.7 * cm, 18, fill=1, stroke=0)

        imagen_x = margin_x + 14
        imagen_y = y - 3.5 * cm
        texto_x = margin_x + 14
        texto_w = usable_w - 28

        imagen_ok = False
        if branding_data.get("imagen_url"):
            imagen_ok = _safe_draw_remote_image(
                c,
                branding_data["imagen_url"],
                imagen_x,
                imagen_y,
                width=2.8 * cm,
                height=2.8 * cm,
            )

        if imagen_ok:
            texto_x = imagen_x + 3.4 * cm
            texto_w = width - texto_x - margin_x - 14

        c.setFillColor(HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(texto_x, y - 18, branding_data.get("titulo", "Acerca del autor"))

        nombre_autor = " ".join(str(branding_data.get("nombre", "")).split())
        nombre_lineas = simpleSplit(nombre_autor, "Helvetica-Bold", 14, texto_w)
        c.setFont("Helvetica-Bold", 14)
        nombre_y = y - 36
        for linea in nombre_lineas[:2]:
            c.drawString(texto_x, nombre_y, linea)
            nombre_y -= 14

        y_text = _draw_paragraph(
            c,
            branding_data.get("subtitulo", ""),
            texto_x,
            nombre_y - 4,
            texto_w,
            "Helvetica",
            9.4,
            12.2,
            HexColor("#475569"),
        )

        _draw_paragraph(
            c,
            branding_data.get("descripcion", ""),
            texto_x,
            y_text - 6,
            texto_w,
            "Helvetica",
            9.0,
            11.8,
            HexColor("#64748b"),
        )

        y -= 5.1 * cm

    if BRANDING.get("mostrar_libros", False) and branding_data.get("libros"):
        c.setFillColor(HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin_x, y, "Libros")
        y -= 16

        for libro in branding_data["libros"]:
            card_h = 4.2 * cm

            if y - card_h < 2.5 * cm:
                _draw_footer(c, width)
                c.showPage()
                c.setFillColor(HexColor("#eef4fb"))
                c.rect(0, 0, width, height, fill=1, stroke=0)
                y = height - 2.2 * cm

            c.setFillColor(HexColor("#ffffff"))
            c.roundRect(margin_x, y - card_h, usable_w, card_h, 16, fill=1, stroke=0)

            portada_x = margin_x + 14
            portada_y = y - 3.3 * cm
            portada_ok = False

            if libro.get("portada_local"):
                portada_ok = _safe_draw_local_image(
                    c,
                    libro["portada_local"],
                    portada_x,
                    portada_y,
                    width=2.4 * cm,
                    height=3.2 * cm,
                )

            text_x = portada_x + 3.0 * cm if portada_ok else portada_x
            text_w = usable_w - (text_x - margin_x) - 14

            y_text = _draw_paragraph(
                c,
                libro.get("titulo", ""),
                text_x,
                y - 22,
                text_w,
                "Helvetica-Bold",
                11,
                13,
                HexColor("#0f172a"),
            )

            c.setFillColor(HexColor("#1d4ed8"))
            c.setFont("Helvetica-Bold", 9.5)
            c.drawString(text_x, y_text - 10, "Ver en Amazon")

            c.setFillColor(HexColor("#64748b"))
            c.setFont("Helvetica", 8.5)
            short_url = libro.get("url", "")
            if len(short_url) > 60:
                short_url = short_url[:57] + "..."
            c.drawString(text_x, y_text - 23, short_url)

            y -= card_h + 12

    if BRANDING.get("mostrar_contacto", False) and branding_data.get("contacto_url"):
        if y < 4 * cm:
            _draw_footer(c, width)
            c.showPage()
            c.setFillColor(HexColor("#eef4fb"))
            c.rect(0, 0, width, height, fill=1, stroke=0)
            y = height - 2.2 * cm

        c.setFillColor(HexColor("#0f172a"))
        c.roundRect(margin_x, y - 1.8 * cm, usable_w, 1.8 * cm, 16, fill=1, stroke=0)

        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin_x + 14, y - 18, "Contacto")

        c.setFont("Helvetica", 9.5)
        c.drawString(margin_x + 14, y - 34, branding_data.get("contacto_texto", "Contacto"))

        c.setFillColor(HexColor("#cbd5e1"))
        c.setFont("Helvetica", 8.5)
        contact_url = branding_data.get("contacto_url", "")
        if len(contact_url) > 75:
            contact_url = contact_url[:72] + "..."
        c.drawRightString(width - margin_x - 14, y - 28, contact_url)

    _draw_footer(c, width)
    c.save()
