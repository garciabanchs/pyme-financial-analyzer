import re

def extraer_importes(texto):
    montos = re.findall(r"\d{1,3}(?:\.\d{3})*,\d{2}", texto)
    unicos = []
    for m in montos:
        if m not in unicos:
            unicos.append(m)
    return unicos[:15]

def extraer_fecha(texto):
    fechas = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", texto)
    return fechas[0] if fechas else "No detectada"
