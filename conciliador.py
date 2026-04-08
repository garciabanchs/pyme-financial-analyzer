def normalizar_importe(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except:
        return None

def detectar_inconsistencias(ledger):
    facturas_por_archivo = {}
    movimientos_banco = []

    for item in ledger:
        importe = normalizar_importe(item["importe"])
        if importe is None:
            continue

        if item["tipo"] in ["factura_venta", "factura_compra"]:
            archivo = item["archivo"]

            if archivo not in facturas_por_archivo:
                facturas_por_archivo[archivo] = {
                    "archivo": archivo,
                    "fecha": item["fecha"],
                    "tipo": item["tipo"],
                    "importes": []
                }

            facturas_por_archivo[archivo]["importes"].append(importe)

        elif item["tipo"] == "extracto_bancario":
            movimientos_banco.append({
                "archivo": item["archivo"],
                "fecha": item["fecha"],
                "importe": importe
            })

    conciliacion = []

    for factura in facturas_por_archivo.values():
        importe_principal = max(factura["importes"]) if factura["importes"] else 0.0
        estado = "pendiente"

        for movimiento in movimientos_banco:
            if abs(importe_principal - movimiento["importe"]) < 0.01:
                estado = "conciliado"
                break

        conciliacion.append({
            "archivo": factura["archivo"],
            "fecha": factura["fecha"],
            "tipo": factura["tipo"],
            "importe": round(importe_principal, 2),
            "estado": estado
        })

    return conciliacion
