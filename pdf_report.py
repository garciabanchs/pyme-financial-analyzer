from weasyprint import HTML


def generar_pdf_ejecutivo(pdf_path, html_string):
    HTML(string=html_string).write_pdf(pdf_path)

