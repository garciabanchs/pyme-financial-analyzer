import os
from weasyprint import HTML

def generar_pdf_ejecutivo(pdf_path, html_string):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    HTML(string=html_string, base_url=base_dir).write_pdf(pdf_path)
