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
        indicadores_venta = [
            "cliente:",
            "nro. de factura",
            "fecha de factura",
            "yudigar"
        ]

        indicadores_compra = [
            "factura cliente",
            "albarán",
            "f. envío",
            "subtotal albarán"
        ]

        if any(ind in texto for ind in indicadores_compra):
            return "factura_compra"

        if any(ind in texto for ind in indicadores_venta):
            return "factura_venta"

        return "factura_compra"

    return "otros"
