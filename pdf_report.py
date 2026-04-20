import os
import re
from weasyprint import HTML


CSS_PDF_EJECUTIVO = """
<style>
    @page {
        size: A4;
        margin: 14mm 12mm 16mm 12mm;
    }

    html, body {
        background: #ffffff !important;
        color: #0f172a !important;
        font-family: Arial, Helvetica, sans-serif !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    body {
        margin: 0 !important;
        padding: 0 !important;
    }

    .wrap {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
    }

    .topbar-shell {
        padding: 0 !important;
        margin: 0 0 8px 0 !important;
    }

    .topbar {
        box-shadow: none !important;
        border: 1px solid #dbe2ea !important;
        background: #ffffff !important;
        border-radius: 14px !important;
        padding: 12px 14px !important;
    }

    .company-meta {
        gap: 6px !important;
    }

    .chip,
    .chip-strong,
    .hero-kicker,
    .filter-toolbar,
    .accordion-icon,
    .actions-bar,
    .btn-ghost,
    .footer-actions,
    .footer-right,
    .footer-pill {
        display: none !important;
    }

    main {
        padding: 0 !important;
    }

    .hero,
    .section,
    .story-card,
    .insight-card,
    .diagnostic-card,
    .recommend-card,
    .score-card,
    .insight-hero-card,
    .metric-card,
    .kpi,
    .alert-card,
    .author-card,
    .books-card,
    .contact-card,
    .accordion-shell {
        background: #ffffff !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
        border: 1px solid #dbe2ea !important;
    }

    .hero {
        display: block !important;
        padding: 16px !important;
        border-radius: 18px !important;
        margin-bottom: 12px !important;
        page-break-inside: avoid;
    }

    .hero-copy {
        gap: 8px !important;
    }

    .hero h2 {
        font-size: 24px !important;
        line-height: 1.15 !important;
        margin-bottom: 8px !important;
    }

    .hero p {
        font-size: 13px !important;
        line-height: 1.55 !important;
        max-width: 100% !important;
    }

    .hero-side,
    .hero-side-bancos,
    .metrics-grid,
    .diagnostic-grid,
    .story-layout,
    .alerts-grid {
        display: block !important;
    }

    .metric-card,
    .kpi,
    .alert-card,
    .score-card,
    .insight-hero-card,
    .diagnostic-card,
    .recommend-card {
        min-height: auto !important;
        margin: 0 0 10px 0 !important;
        padding: 14px !important;
        border-radius: 14px !important;
        page-break-inside: avoid;
    }

    .metric-total,
    .metric-bank {
        background: #ffffff !important;
        color: #0f172a !important;
    }

    .metric-total .metric-label,
    .metric-total .metric-mini-label,
    .metric-total .metric-mini-value,
    .metric-total .metric-delta,
    .metric-total .metric-bank-tag {
        color: #0f172a !important;
    }

    .metric-total .metric-bank-tag,
    .metric-bank-tag {
        background: #eef5ff !important;
        border: 1px solid #d9e7ff !important;
    }

    .metric-split,
    .metric-bank-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        margin: 10px 0 !important;
    }

    .metric-block {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }

    .section {
        margin-top: 12px !important;
        border-radius: 18px !important;
        page-break-inside: avoid;
    }

    .section-head {
        padding: 14px 14px 6px 14px !important;
    }

    .section-title {
        font-size: 18px !important;
    }

    .section-sub {
        font-size: 11px !important;
        line-height: 1.45 !important;
        color: #475569 !important;
    }

    .accordion-shell {
        margin: 10px 14px 14px 14px !important;
        overflow: visible !important;
    }

    .accordion-toggle {
        display: none !important;
    }

    .accordion-panel {
        display: block !important;
        border-top: none !important;
        background: #ffffff !important;
    }

    .table-shell.compact-shell {
        margin: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .table-wrap {
        display: block !important;
        overflow: visible !important;
    }

    .mobile-doc-grid,
    .mobile-amount-grid,
    .mobile-movements-grid,
    .mobile-conc-grid {
        display: none !important;
    }

    table {
        width: 100% !important;
        min-width: 0 !important;
        border-collapse: collapse !important;
        font-size: 10px !important;
        table-layout: fixed !important;
    }

    thead th {
        position: static !important;
        background: #f8fafc !important;
        color: #334155 !important;
        border: 1px solid #dbe2ea !important;
        padding: 7px 8px !important;
        font-size: 9px !important;
        line-height: 1.25 !important;
    }

    tbody td {
        border: 1px solid #e5e7eb !important;
        padding: 7px 8px !important;
        font-size: 9px !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
        background: #ffffff !important;
    }

    .mono {
        white-space: nowrap !important;
    }

    .row-entrada td {
        background: #f0fdf4 !important;
    }

    .row-salida td {
        background: #fef2f2 !important;
    }

    .badge {
        font-size: 8px !important;
        padding: 4px 8px !important;
        border-radius: 999px !important;
    }

    .badge::before {
        width: 6px !important;
        height: 6px !important;
    }

    .amount-chip-wrap {
        gap: 4px !important;
    }

    .amount-chip {
        font-size: 8px !important;
        padding: 4px 6px !important;
        border-radius: 999px !important;
    }

    .ring,
    .score-ring {
        width: 120px !important;
        height: 120px !important;
        margin: 4px auto 0 auto !important;
    }

    .ring span,
    .score-ring span {
        font-size: 18px !important;
    }

    .ring small,
    .score-ring small {
        font-size: 9px !important;
    }

    .diagnostic-list,
    .recommend-list,
    .bullet-list {
        gap: 8px !important;
        padding-left: 0 !important;
        margin: 0 !important;
    }

    .diagnostic-list li,
    .recommend-list li,
    .bullet {
        font-size: 11px !important;
        line-height: 1.45 !important;
    }

    .book-item {
        grid-template-columns: 70px 1fr !important;
        gap: 10px !important;
        padding: 10px 0 !important;
    }

    .book-cover {
        width: 70px !important;
        height: 104px !important;
    }

    .contact-card {
        display: block !important;
        text-align: left !important;
    }

    .cta-button,
    .book-link {
        display: inline-block !important;
        box-shadow: none !important;
    }

    .footer-card {
        display: block !important;
        margin-top: 12px !important;
        padding: 12px 14px !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        background: #ffffff !important;
        border: 1px solid #dbe2ea !important;
        color: #475569 !important;
    }

    #detalle-documental-section,
    #detalle-contable-section,
    #movimientos-section {
        display: none !important;
    }

    #conciliacion-section .table-wrap {
        display: block !important;
    }
</style>
"""


def _limpiar_html_para_pdf(html_string):
    html = html_string or ""

    # Quitar scripts para evitar comportamiento web innecesario en PDF
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)

    # Forzar apertura de paneles colapsables
    html = re.sub(
        r'<div class="accordion-panel" style="display:\s*none;">',
        '<div class="accordion-panel" style="display:block;">',
        html,
        flags=re.IGNORECASE,
    )

    # Insertar CSS especial de impresión justo antes de </head>
    if "</head>" in html:
        html = html.replace("</head>", CSS_PDF_EJECUTIVO + "\n</head>")
    else:
        html = CSS_PDF_EJECUTIVO + html

    return html


def generar_pdf_ejecutivo(pdf_path, html_string):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_limpio = _limpiar_html_para_pdf(html_string)

    HTML(
        string=html_limpio,
        base_url=base_dir
    ).write_pdf(pdf_path)
