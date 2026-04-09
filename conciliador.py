def normalizar_importe(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except:
        return None


def detectar_inconsistencias(ledger):
    facturas = []
    movimientos_banco = []

    for item in ledger:
        importe = normalizar_importe(item["importe"])
        if importe is None:
            continue

        if item["tipo"] in ["factura_venta", "factura_compra"]:
            facturas.append({
                "archivo": item["archivo"],
                "fecha": item["fecha"],
                "tipo": item["tipo"],
                "importe": importe
            })

        elif item["tipo"] == "extracto_bancario":
            movimientos_banco.append({
                "archivo": item["archivo"],
                "fecha": item["fecha"],
                "tipo": item["tipo"],
                "importe": importe
            })

    conciliacion = []

    for factura in facturas:
        estado = "pendiente"
        mejor_diferencia = None

        for movimiento in movimientos_banco:
            diferencia = abs(factura["importe"] - movimiento["importe"])

            if diferencia <= 0.01:
                estado = "conciliado"
                mejor_diferencia = diferencia
                break

            if diferencia <= 5.00:
                if estado != "conciliado":
                    estado = "parcialmente_conciliado"
                    mejor_diferencia = diferencia

        conciliacion.append({
            "archivo": factura["archivo"],
            "fecha": factura["fecha"],
            "tipo": factura["tipo"],
            "importe": round(factura["importe"], 2),
            "estado": estado,
            "diferencia": round(mejor_diferencia, 2) if mejor_diferencia is not None else None
        })

    return conciliacion
