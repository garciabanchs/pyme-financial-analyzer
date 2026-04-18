from pypdf import PdfReader
import os

def extraer_texto_pdf(ruta_pdf):
    texto = ""
    try:
        reader = PdfReader(ruta_pdf)
        for page in reader.pages:
            contenido = page.extract_text()
            if contenido:
                texto += contenido + "\n"
    except Exception:
        pass
    return texto
