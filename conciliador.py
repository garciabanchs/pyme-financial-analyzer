def detectar_inconsistencias(ledger):
    inconsistencias = []

    for item in ledger:
        if item["tipo"] == "factura_venta":
            # ejemplo simple: montos muy pequeños sospechosos
            if float(item["importe"].replace(".", "").replace(",", ".")) < 10:
                inconsistencias.append(item)

    return inconsistencias
