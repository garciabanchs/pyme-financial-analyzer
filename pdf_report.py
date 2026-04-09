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


def _fmt_eur(numero):
    try:
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def _num(valor):
    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        texto = str(valor).strip()
        return float(texto.replace(".", "").replace(",", "."))
    except Exception:
        return 0.0


def _resumen_flujo(ledger):
    total_entradas = 0.0
    total_salidas = 0.0
    total_movimientos = 0.0
    total_revisar = 0.0

    for item in ledger or []:
        valor = _num(item.get("importe", 0))

        if item.get("naturaleza") == "entrada":
            total_entradas += valor
        elif item.get("naturaleza") == "salida":
            total_salidas += valor
        elif item.get("naturaleza") == "movimiento":
            total_movimientos += valor
        else:
            total_revisar += valor

    return {
        "entradas": total_entradas,
        "salidas": total_salidas,
        "movimientos": total_movimientos,
        "revisar": total_revisar,
        "balance": total_entradas - total_salidas,
    }


def _resumen_conciliacion(conciliacion):
    conciliadas = 0
    parciales = 0
    pendientes = 0
    pendiente_cobro = 0.0
    pendiente_pago = 0.0
    importe_pendiente = 0.0

    for item in conciliacion or []:
        estado = item.get("estado", "")
        tipo = item.get("tipo", "")
        importe = _num(item.get("importe", 0))

        if estado == "conciliado":
            conciliadas += 1
        elif estado == "parcialmente_conciliado":
            parciales += 1
        else:
            pendientes += 1
            importe_pendiente += importe
            if tipo == "factura_venta":
                pendiente_cobro += importe
            elif tipo == "factura_compra":
                pendiente_pago += importe

    return {
        "conciliadas": conciliadas,
        "parciales": parciales,
        "pendientes": pendientes,
        "pendiente_cobro": pendiente_cobro,
        "pendiente_pago": pendiente_pago,
        "importe_pendiente": importe_pendiente,
    }


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

    lines = simpleSplit(str(text), font_name, font_size, width)
    current_y = y

    for line in lines:
        c.drawString(x, current_y, line)
        current_y -= leading

    return current_y


def _draw_title_block(c, x, y, title, subtitle=None):
    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, title)

    if subtitle:
        return _draw_paragraph(
            c,
            subtitle,
            x,
            y - 16,
            15.5 * cm,
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
        c.setFillColor(HexColor(subtitle_color))
        c.setFont("Helvetica", 8.5)
        c.drawString(x + 12, y - 56, subtitle)


def _draw_info_box(c, x, y, w, h, title, body, bg="#ffffff", accent="#2563eb"):
    c.setFillColor(HexColor(bg))
    c.roundRect(x, y - h, w, h, 16, fill=1, stroke=0)

    c.setFillColor(HexColor(accent))
    c.roundRect(x + 10, y - 24, 36, 16, 8, fill=1, stroke=0)

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + 28, y - 18, "INFO")

    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 56, y - 18, title)

    _draw_paragraph(
        c,
        body,
        x + 12,
        y - 38,
        w - 24,
        "Helvetica",
        9.5,
        12.5,
        HexColor("#475569"),
    )


def _draw_alert_card(c, x, y, w, h, tag, title, body, tag_bg, tag_fg):
    c.setFillColor(HexColor("#ffffff"))
    c.roundRect(x, y - h, w, h, 16, fill=1, stroke=0)

    c.setFillColor(HexColor(tag_bg))
    c.roundRect(x + 12, y - 22, 52, 14, 7, fill=1, stroke=0)

    c.setFillColor(HexColor(tag_fg))
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(x + 38, y - 17, tag)

    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x + 12, y - 38, title)

    _draw_paragraph(
        c,
        body,
        x + 12,
        y - 54,
        w - 24,
        "Helvetica",
        8.8,
        11.5,
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
    c.drawString(2 * cm, 0.95 * cm, "PYME Financial Analyzer · Informe preliminar automático")
    c.drawRightString(width - 2 * cm, 0.95 * cm, str(c.getPageNumber()))


def generar_pdf_ejecutivo(pdf_path, nombre_zip, clasificados, ledger, conciliacion):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin_x = 2 * cm
    usable_w = width - 2 * margin_x

    branding_data = BRANDING[BRANDING["modo"]]
    flujo = _resumen_flujo(ledger)
    conc = _resumen_conciliacion(conciliacion)

    total_docs_clasificados = (
        len(clasificados.get("factura_venta", []))
        + len(clasificados.get("factura_compra", []))
        + len(clasificados.get("extracto_bancario", []))
        + len(clasificados.get("otros", []))
    )

    # =========================
    # PÁGINA 1
    # =========================
    c.setFillColor(HexColor("#eef4fb"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setFillColor(HexColor("#0f172a"))
    c.roundRect(margin_x, height - 7.4 * cm, usable_w, 5.6 * cm, 22, fill=1, stroke=0)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin_x + 18, height - 2.4 * cm, "PYME FINANCIAL ANALYZER")

    c.setFont("Helvetica-Bold", 23)
    c.drawString(margin_x + 18, height - 3.35 * cm, "Informe financiero ejecutivo")

    c.setFillColor(HexColor("#cbd5e1"))
    c.setFont("Helvetica", 10.5)
    c.drawString(margin_x + 18, height - 4.1 * cm, f"Archivo analizado: {nombre_zip}")
    c.drawString(margin_x + 18, height - 4.7 * cm, "Lectura preliminar para toma de decisiones en PYME")

    chip_y = height - 5.85 * cm
    chip_x = margin_x + 18
    chip_gap = 8
    chips = [
        f"Documentos clasificados: {total_docs_clasificados}",
        f"Pendientes: {conc['pendientes']}",
        f"Balance: € {_fmt_eur(flujo['balance'])}",
    ]
    current_x = chip_x
    for chip in chips:
        tw = c.stringWidth(chip, "Helvetica-Bold", 8.5) + 18
        c.setFillColor(HexColor("#1e293b"))
        c.roundRect(current_x, chip_y, tw, 18, 9, fill=1, stroke=0)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(current_x + 9, chip_y + 5.5, chip)
        current_x += tw + chip_gap

    y_cards = height - 8.5 * cm
    card_gap = 10
    card_w = (usable_w - card_gap) / 2
    card_h = 2.2 * cm

    _draw_metric_card(
        c, margin_x, y_cards, card_w, card_h,
        "Entradas", f"€ {_fmt_eur(flujo['entradas'])}",
        "Actividad detectada", bg="#ffffff"
    )
    _draw_metric_card(
        c, margin_x + card_w + card_gap, y_cards, card_w, card_h,
        "Salidas", f"€ {_fmt_eur(flujo['salidas'])}",
        "Impacto en caja", bg="#fef7ed"
    )

    y_cards_2 = y_cards - card_h - 10
    _draw_metric_card(
        c, margin_x, y_cards_2, card_w, card_h,
        "Balance preliminar", f"€ {_fmt_eur(flujo['balance'])}",
        "Resultado neto", bg="#eff6ff", value_color="#0f4cff"
    )
    _draw_metric_card(
        c, margin_x + card_w + card_gap, y_cards_2, card_w, card_h,
        "Pendientes", str(conc["pendientes"]),
        "Conciliación", bg="#fff7ed", value_color="#9a3412"
    )

    y = y_cards_2 - card_h - 18

    y = _draw_title_block(
        c,
        margin_x,
        y,
        "Lectura ejecutiva",
        "Resumen narrativo del flujo, la conciliación y las principales señales detectadas durante el procesamiento.",
    )

    titular = (
        "El negocio muestra generación positiva de caja preliminar durante el período analizado."
        if flujo["entradas"] > 0 and flujo["balance"] > 0
        else "El negocio registra actividad, pero el balance preliminar sugiere presión sobre la caja."
        if flujo["entradas"] > 0
        else "La información disponible es insuficiente para confirmar una generación sólida de caja."
    )

    narrativa = (
        f"Durante el período analizado entraron € {_fmt_eur(flujo['entradas'])} y salieron "
        f"€ {_fmt_eur(flujo['salidas'])}, dejando un balance preliminar de € {_fmt_eur(flujo['balance'])}. "
        f"Se observan {conc['pendientes']} registros pendientes de conciliación, con "
        f"€ {_fmt_eur(conc['importe_pendiente'])} todavía sujetos a validación documental. "
        f"El objetivo de este informe es mostrar qué pasó con la caja, qué movimientos ya tienen soporte "
        f"y qué elementos siguen pendientes de revisión."
    )

    c.setFillColor(HexColor("#ffffff"))
    c.roundRect(margin_x, y - 2.7 * cm, usable_w, 2.7 * cm, 16, fill=1, stroke=0)

    c.setFillColor(HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x + 14, y - 16, titular)

    _draw_paragraph(
        c,
        narrativa,
        margin_x + 14,
        y - 34,
        usable_w - 28,
        "Helvetica",
        9.5,
        12.5,
        HexColor("#475569"),
    )

    y -= 3.15 * cm

    box_gap = 10
    box_w = (usable_w - (2 * box_gap)) / 3
    alert_h = 3.0 * cm

    _draw_alert_card(
        c,
        margin_x,
        y,
        box_w,
        alert_h,
        "BIEN",
        "Documentación estructurada",
        "El sistema ya clasifica documentos y arma una base útil para revisión gerencial.",
        "#ecfdf3",
        "#16a34a",
    )

    _draw_alert_card(
        c,
        margin_x + box_w + box_gap,
        y,
        box_w,
        alert_h,
        "REVISAR",
        "Pendientes de conciliación",
        f"Hay {conc['pendientes']} registros por revisar y un importe asociado de € {_fmt_eur(conc['importe_pendiente'])}.",
        "#fff9e8",
        "#ca8a04",
    )

    _draw_alert_card(
        c,
        margin_x + (box_w + box_gap) * 2,
        y,
        box_w,
        alert_h,
        "ATENCIÓN",
        "Resultado preliminar",
        "Este informe orienta decisiones, pero no sustituye una revisión contable definitiva.",
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
    )

    info_h = 3.3 * cm
    _draw_info_box(
        c,
        margin_x,
        y - 0.2 * cm,
        usable_w,
        info_h,
        "Clasificación documental",
        (
            f"Facturas de venta: {len(clasificados.get('factura_venta', []))}. "
            f"Facturas de compra: {len(clasificados.get('factura_compra', []))}. "
            f"Extractos bancarios: {len(clasificados.get('extracto_bancario', []))}. "
            f"Otros documentos: {len(clasificados.get('otros', []))}."
        ),
        bg="#ffffff",
        accent="#2563eb",
    )

    y -= info_h + 18

    _draw_info_box(
        c,
        margin_x,
        y,
        usable_w,
        info_h,
        "Hallazgos clave de conciliación",
        (
            f"Pendiente de cobro estimado: € {_fmt_eur(conc['pendiente_cobro'])}. "
            f"Pendiente de pago estimado: € {_fmt_eur(conc['pendiente_pago'])}. "
            f"Facturas conciliadas exactas: {conc['conciliadas']}. "
            f"Facturas parcialmente conciliadas: {conc['parciales']}. "
            f"Registros pendientes: {conc['pendientes']}."
        ),
        bg="#ffffff",
        accent="#0f172a",
    )

    y -= info_h + 18

    c.setFillColor(HexColor("#fff7ed"))
    c.roundRect(margin_x, y - 3.2 * cm, usable_w, 3.2 * cm, 16, fill=1, stroke=0)

    c.setFillColor(HexColor("#9a3412"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x + 14, y - 18, "Observación ejecutiva")

    texto_observacion = (
        "Este informe es preliminar. El sistema ya identifica estructura financiera, clasifica documentos, "
        "resume flujo de caja y detecta conciliaciones pendientes. El siguiente nivel consiste en refinar "
        "la lectura de extractos, mejorar la conciliación y consolidar el resumen final para toma de decisiones."
    )

    _draw_paragraph(
        c,
        texto_observacion,
        margin_x + 14,
        y - 36,
        usable_w - 28,
        "Helvetica",
        9.8,
        13,
        HexColor("#7c2d12"),
    )

    y -= 3.7 * cm

    if BRANDING.get("mostrar_bio", False):
        c.setFillColor(HexColor("#ffffff"))
        c.roundRect(margin_x, y - 4.5 * cm, usable_w, 4.5 * cm, 18, fill=1, stroke=0)

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

        c.setFont("Helvetica-Bold", 14)
        c.drawString(texto_x, y - 36, branding_data.get("nombre", ""))

        y_text = _draw_paragraph(
            c,
            branding_data.get("subtitulo", ""),
            texto_x,
            y - 54,
            texto_w,
            "Helvetica",
            9.5,
            12.5,
            HexColor("#475569"),
        )

        _draw_paragraph(
            c,
            branding_data.get("descripcion", ""),
            texto_x,
            y_text - 6,
            texto_w,
            "Helvetica",
            9.2,
            12,
            HexColor("#64748b"),
        )

        y -= 4.9 * cm

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
