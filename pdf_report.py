from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit


def _fmt_eur(numero):
    try:
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"


def _num(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except:
        try:
            return float(valor)
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
        "balance": total_entradas - total_salidas
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
        "pendiente_pago": pendiente_pago
    }


def _draw_paragraph(c, text, x, y, width, font_name="Helvetica", font_size=11, leading=15, color=HexColor("#1f2937")):
    c.setFont(font_name, font_size)
    c.setFillColor(color)

    lines = simpleSplit(text, font_name, font_size, width)
    current_y = y

    for line in lines:
        c.drawString(x, current_y, line)
        current_y -= leading

    return current_y


def _draw_metric_box(c, x, y, w, h, title, value, bg="#ffffff", title_color="#6b7280", value_color="#111827"):
    c.setFillColor(HexColor(bg))
    c.roundRect(x, y - h, w, h, 10, fill=1, stroke=0)

    c.setFillColor(HexColor(title_color))
    c.setFont("Helvetica", 9)
    c.drawString(x + 12, y - 18, title)

    c.setFillColor(HexColor(value_color))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(x + 12, y - 40, value)


def generar_pdf_ejecutivo(pdf_path, nombre_zip, clasificados, ledger, conciliacion):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    margin_x = 2 * cm
    y = height - 2 * cm

    # Fondo superior
    c.setFillColor(HexColor("#0f172a"))
    c.rect(0, height - 5.2 * cm, width, 5.2 * cm, fill=1, stroke=0)

    # Título
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin_x, height - 2.2 * cm, "Resumen ejecutivo financiero")

    c.setFont("Helvetica", 11)
    c.drawString(margin_x, height - 3.0 * cm, f"Archivo analizado: {nombre_zip}")

    c.setFillColor(HexColor("#e5e7eb"))
    c.setFont("Helvetica", 10)
    c.drawString(margin_x, height - 3.7 * cm, "Informe preliminar automático para dueños de PYME")

    flujo = _resumen_flujo(ledger)
    conc = _resumen_conciliacion(conciliacion)

    # Tarjetas de métricas
    y_cards = height - 6.4 * cm
    box_w = (width - (2 * margin_x) - 12) / 2
    box_h = 1.9 * cm

    _draw_metric_box(c, margin_x, y_cards, box_w, box_h, "Entradas", f"€ {_fmt_eur(flujo['entradas'])}")
    _draw_metric_box(c, margin_x + box_w + 12, y_cards, box_w, box_h, "Salidas", f"€ {_fmt_eur(flujo['salidas'])}")

    y_cards_2 = y_cards - box_h - 12
    _draw_metric_box(c, margin_x, y_cards_2, box_w, box_h, "Balance preliminar", f"€ {_fmt_eur(flujo['balance'])}", bg="#eff6ff")
    _draw_metric_box(c, margin_x + box_w + 12, y_cards_2, box_w, box_h, "Pendientes de conciliación", str(conc["pendientes"]), bg="#fff7ed")

    y = y_cards_2 - box_h - 24

    # Hallazgos
    c.setFillColor(HexColor("#111827"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "Hallazgos ejecutivos")
    y -= 18

    hallazgos = [
        f"Pendiente de cobro estimado: € {_fmt_eur(conc['pendiente_cobro'])}.",
        f"Pendiente de pago estimado: € {_fmt_eur(conc['pendiente_pago'])}.",
        f"Facturas conciliadas: {conc['conciliadas']}. Parcialmente conciliadas: {conc['parciales']}.",
        f"Balance preliminar del periodo analizado: € {_fmt_eur(flujo['balance'])}."
    ]

    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#1f2937"))
    for item in hallazgos:
        y = _draw_paragraph(c, f"- {item}", margin_x, y, width - 2 * margin_x, "Helvetica", 11, 15)
        y -= 4

    y -= 8

    # Clasificación documental
    c.setFillColor(HexColor("#111827"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "Clasificación documental")
    y -= 20

    clasif_lines = [
        f"Facturas de venta: {len(clasificados.get('factura_venta', []))}",
        f"Facturas de compra: {len(clasificados.get('factura_compra', []))}",
        f"Extractos bancarios: {len(clasificados.get('extracto_bancario', []))}",
        f"Otros documentos: {len(clasificados.get('otros', []))}"
    ]

    c.setFont("Helvetica", 11)
    for line in clasif_lines:
        c.drawString(margin_x, y, line)
        y -= 15

    y -= 10

    # Observación final
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
        HexColor("#7c2d12")
    )

    c.showPage()
    c.save()
