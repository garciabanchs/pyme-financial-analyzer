def clasificar_documento(nombre, texto):
    nombre = (nombre or "").lower()
    texto = (texto or "").lower()

    # Extractos
    if (
        "paypal" in texto
        or "extracto bancario" in texto
        or "resumen de saldo" in texto
        or "historial de transacciones" in texto
        or "resumen de actividad" in texto
        or "extracto" in nombre
    ):
        return "extracto_bancario"

    # Facturas
    if "factura" in nombre or "factura" in texto or "invoice" in texto:
        indicadores_venta = [
            "cliente:",
            "nro. de factura",
            "fecha de factura",
            "forma de pago",
            "anticipo cuenta",
            "hmy yudigar"
        ]

        indicadores_compra = [
            "albarán",
            "f. envío",
            "subtotal",
            "desglose impositivo",
            "verdnatura",
            "rec. eq.",
        ]

        score_venta = sum(1 for ind in indicadores_venta if ind in texto)
        score_compra = sum(1 for ind in indicadores_compra if ind in texto)

        if score_venta > score_compra:
            return "factura_venta"
        if score_compra > score_venta:
            return "factura_compra"

        # fallback prudente
        return "otros"

    return "otros"
