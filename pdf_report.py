from io import BytesIO
from urllib.request import Request, urlopen
import ssl

from branding import BRANDING
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas


def _fmt_eur(numero):
    try:
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"


def _num(valor):
    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        texto = str(valor).strip()
        return float(texto.replace(".", "").replace(",", "."))
    except:
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
    }


def _draw_paragraph(
    c,
    text,
    x,
    y,
    width,
    font_name="Helvetica",
    font_size=11,
    leading=15,
    color=HexColor("#1f2937"),
):
    c.setFont(font_name, font_size)
    c.setFillColor(color)

    lines = simpleSplit(str(text), font_name, font_size, width)
    current_y = y

    for line in lines:
        c.drawString(x, current_y, line)
        current_y -= leading

    return current_y


def _draw_metric_box(
    c,
    x,
    y,
    w,
    h,
    title,
    value,
    bg="#ffffff",
    title_color="#6b7280",
    value_color="#111827",
):
    c.setFillColor(HexColor(bg))
    c.roundRect(x, y - h, w, h, 10, fill=1, stroke=0)

    c.setFillColor(HexColor(title_color))
    c.setFont("Helvetica", 9)
    c.drawString(x + 12, y - 18, title)

    c.setFillColor(HexColor(value_color))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x + 12, y - 40, value)


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


def generar_pdf_ejecutivo(pdf_path, nombre_zip, clasificados, ledger, conciliacion):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin_x = 2 * cm

    branding_data = BRANDING[BRANDING["modo"]]
    flujo = _resumen_flujo(ledger)
    conc = _resumen_conciliacion(conciliacion)

    # =========================
    # PÁGINA 1
    # =========================
    c.setFillColor(HexColor("#0f172a"))
    c.rect(0, height - 5.2 * cm, width, 5.2 * cm, fill=1, stroke=0)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin_x, height - 2.2 * cm, "Resumen ejecutivo financiero")

    c.setFont("Helvetica", 11)
    c.drawString(margin_x, height - 3.0 * cm, f"Archivo analizado: {nombre_zip}")

    c.setFillColor(HexColor("#e5e7eb"))
    c.setFont("Helvetica", 10)
    c.drawString(margin_x, height - 3.7 * cm, "Informe preliminar automático para dueños de PYME")

    y_cards = height - 6.4 * cm
    box_w = (width - (2 * margin_x) - 12) / 2
    box_h = 1.9 * cm

    _draw_metric_box(c, margin_x, y_cards, box_w, box_h, "Entradas", f"€ {_fmt_eur(flujo['entradas'])}")
    _draw_metric_box(c, margin_x + box_w + 12, y_cards, box_w, box_h, "Salidas", f"€ {_fmt_eur(flujo['salidas'])}")

    y_cards_2 = y_cards - box_h - 12
    _draw_metric_box(
        c,
        margin_x,
        y_cards_2,
        box_w,
        box_h,
        "Balance preliminar",
        f"€ {_fmt_eur(flujo['balance'])}",
        bg="#eff6ff",
    )
    _draw_metric_box(
        c,
        margin_x + box_w + 12,
        y_cards_2,
        box_w,
        box_h,
        "Pendientes de conciliación",
        str(conc["pendientes"]),
        bg="#fff7ed",
    )

    y = y_cards_2 - box_h - 24

    c.setFillColor(HexColor("#111827"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "Hallazgos ejecutivos")
    y -= 18

    hallazgos = [
        f"Pendiente de cobro estimado: € {_fmt_eur(conc['pendiente_cobro'])}.",
        f"Pendiente de pago estimado: € {_fmt_eur(conc['pendiente_pago'])}.",
        f"Facturas conciliadas: {conc['conciliadas']}. Parcialmente conciliadas: {conc['parciales']}.",
        f"Balance preliminar del periodo analizado: € {_fmt_eur(flujo['balance'])}.",
    ]

    for item in hallazgos:
        y = _draw_paragraph(
            c,
            f"- {item}",
            margin_x,
            y,
            width - 2 * margin_x,
            "Helvetica",
            11,
            15,
            HexColor("#1f2937"),
        )
        y -= 4

    y -= 8

    c.setFillColor(HexColor("#111827"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "Clasificación documental")
    y -= 20

    clasif_lines = [
        f"Facturas de venta: {len(clasificados.get('factura_venta', []))}",
        f"Facturas de compra: {len(clasificados.get('factura_compra', []))}",
        f"Extractos bancarios: {len(clasificados.get('extracto_bancario', []))}",
        f"Otros documentos: {len(clasificados.get('otros', []))}",
    ]

    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#1f2937"))
    for line in clasif_lines:
        c.drawString(margin_x, y, line)
        y -= 15

    y -= 10

    c.setFillColor(HexColor("#fff7ed"))
    c.roundRect(margin_x, y - 2.8 * cm, width - 2 * margin_x, 2.8 * cm, 10, fill=1, stroke=0)

    c.setFillColor(HexColor("#9a3412"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin_x + 12, y - 18, "Observación ejecutiva")

    texto_final = (
        "Este informe es preliminar. El sistema ya identifica estructura financiera, "
        "clasifica documentos, resume flujo de caja y detecta conciliaciones pendientes. "
        "El siguiente nivel consiste en refinar la lectura de extractos, mejorar la conciliación "
        "y consolidar el resumen final para toma de decisiones."
    )

    _draw_paragraph(
        c,
        texto_final,
        margin_x + 12,
        y - 38,
        width - 2 * margin_x - 24,
        "Helvetica",
        10,
        13,
        HexColor("#7c2d12"),
    )

    # =========================
    # PÁGINA 2
    # =========================
    c.showPage()
    y = height - 2 * cm

    if BRANDING.get("mostrar_bio", False):
        box_h = 5.2 * cm
        c.setFillColor(HexColor("#f3f4f6"))
        c.roundRect(margin_x, y - box_h, width - 2 * margin_x, box_h, 12, fill=1, stroke=0)

        imagen_x = margin_x + 14
        imagen_y = y - 3.8 * cm
        texto_x = margin_x + 14
        texto_ancho = width - 2 * margin_x - 28

        imagen_ok = False
        if branding_data.get("imagen_url"):
            imagen_ok = _safe_draw_remote_image(
                c,
                branding_data["imagen_url"],
                imagen_x,
                imagen_y,
                width=2.4 * cm,
                height=2.4 * cm,
            )

        if imagen_ok:
            texto_x = imagen_x + 3.0 * cm
            texto_ancho = width - texto_x - margin_x

        c.setFillColor(HexColor("#111827"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(texto_x, y - 18, branding_data.get("titulo", ""))

        c.setFont("Helvetica-Bold", 14)
        c.drawString(texto_x, y - 36, branding_data.get("nombre", ""))

        y_text = _draw_paragraph(
            c,
            branding_data.get("subtitulo", ""),
            texto_x,
            y - 56,
            texto_ancho,
            "Helvetica",
            10,
            13,
            HexColor("#374151"),
        )

        _draw_paragraph(
            c,
            branding_data.get("descripcion", ""),
            texto_x,
            y_text - 6,
            texto_ancho,
            "Helvetica",
            10,
            13,
            HexColor("#374151"),
        )

        y -= box_h + 16

    if BRANDING.get("mostrar_libros", False) and branding_data.get("libros"):
        c.setFillColor(HexColor("#111827"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin_x, y, "Libros")
        y -= 20

        for libro in branding_data["libros"]:
            card_h = 4.5 * cm

            if y - card_h < 2 * cm:
                c.showPage()
                y = height - 2 * cm

            c.setFillColor(HexColor("#ffffff"))
            c.roundRect(margin_x, y - card_h, width - 2 * margin_x, card_h, 12, fill=1, stroke=1)

            portada_x = margin_x + 14
            portada_y = y - 3.6 * cm
            portada_ok = False

            if libro.get("portada_url"):
                portada_ok = _safe_draw_remote_image(
                    c,
                    libro["portada_url"],
                    portada_x,
                    portada_y,
                    width=2.5 * cm,
                    height=3.5 * cm,
                )

            text_x = portada_x + 3.2 * cm if portada_ok else portada_x
            text_w = width - text_x - margin_x - 16

            y_text = _draw_paragraph(
                c,
                libro.get("titulo", ""),
                text_x,
                y - 24,
                text_w,
                "Helvetica-Bold",
                12,
                14,
                HexColor("#111827"),
            )

            _draw_paragraph(
                c,
                f"Ver en Amazon: {libro.get('url', '')}",
                text_x,
                y_text - 10,
                text_w,
                "Helvetica",
                10,
                13,
                HexColor("#1d4ed8"),
            )

            y -= card_h + 14

    if BRANDING.get("mostrar_contacto", False) and branding_data.get("contacto_url"):
        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm

        c.setFillColor(HexColor("#111827"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, y, "Contacto")
        y -= 16

        _draw_paragraph(
            c,
            f"{branding_data.get('contacto_texto', 'Contacto')}: {branding_data.get('contacto_url', '')}",
            margin_x,
            y,
            width - 2 * margin_x,
            "Helvetica",
            10,
            13,
            HexColor("#1f2937"),
        )

    c.save()
