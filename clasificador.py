def clasificar_documento(nombre, texto):
    nombre = nombre.lower()
    texto = texto.lower()

    if ("factura" in nombre or "invoice" in texto) and ("venta" in nombre or "total" in texto):
        return "factura_venta"
    elif "factura" in nombre or "invoice" in texto:
        return "factura_compra"
    elif "banco" in nombre or "extracto" in nombre or "saldo" in texto:
        return "extracto_bancario"
    else:
        return "otros"
