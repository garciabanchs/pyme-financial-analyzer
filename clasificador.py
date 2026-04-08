def clasificar_documento(nombre, texto):
    nombre = nombre.lower()
    texto = texto.lower()

    if (
        "extracto" in nombre
        or "saldo" in texto
        or "paypal" in texto
        or "resumen de actividad" in texto
        or "resumen de saldo" in texto
    ):
        return "extracto_bancario"

    if "factura" in nombre or "factura" in texto or "invoice" in texto:
        if (
            "cliente:" in texto
            or "cliente " in texto
            or "nro. de factura" in texto
            or "fecha de factura" in texto
            or "venta" in nombre
            or "yudigar" in texto
        ):
            return "factura_venta"
        else:
            return "factura_compra"

    return "otros"
