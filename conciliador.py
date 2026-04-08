def normalizar_importe(valor):
    try:
        return float(valor.replace(".", "").replace(",", "."))
    except:
        return None

def detectar_inconsistencias(ledger):
    facturas_venta = []
    movimientos_banco = []

    for item in ledger:
        importe = normalizar_importe(item["importe"])
        if importe is None:
            continue

        if item["tipo"] == "factura_venta":
            facturas_venta.append({
                "archivo": item["archivo"],
                "fecha": item["fecha"],
                "importe": importe
            })

        if item["tipo"] == "extracto_bancario":
            movimientos_banco.append({
                "archivo": item["archivo"],
                "fecha": item["fecha"],
                "importe": importe
            })

    conciliacion = []

    for factura in facturas_venta:
        estado = "pendiente"

        for movimiento in movimientos_banco:
            if abs(factura["importe"] - movimiento["importe"]) < 0.01:
                estado = "conciliado"
                break

        conciliacion.append({
            "archivo": factura["archivo"],
            "fecha": factura["fecha"],
            "importe": factura["importe"],
            "estado": estado
        })

    return conciliacion
