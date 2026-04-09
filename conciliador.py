def normalizar_importe(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except Exception:
        return None


def detectar_inconsistencias(ledger):
    facturas = []
    movimientos_banco = []

    for item in ledger:
        importe = item.get("importe_num")
        if importe is None:
            importe = normalizar_importe(item.get("importe"))

        if importe is None:
            continue

        if item.get("tipo") in ["factura_venta", "factura_compra"]:
            facturas.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "tipo": item.get("tipo"),
                "importe": round(importe, 2),
            })

        elif item.get("tipo") == "extracto_bancario":
            movimientos_banco.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "naturaleza": item.get("naturaleza"),
                "categoria": item.get("categoria"),
                "importe": round(importe, 2),
            })

    conciliacion = []
    movimientos_usados = set()

    for factura in facturas:
        estado = "pendiente"
        mejor_diferencia = None
        mejor_movimiento = None

        for movimiento in movimientos_banco:
            if movimiento["id"] in movimientos_usados:
                continue

            # coherencia de sentido económico
            if factura["tipo"] == "factura_venta" and movimiento["naturaleza"] != "entrada":
                continue

            if factura["tipo"] == "factura_compra" and movimiento["naturaleza"] != "salida":
                continue

            # evitamos comisiones / retenciones / traspasos como match de factura
            if movimiento.get("categoria") in ["comision", "retencion", "traspaso"]:
                continue

            diferencia = abs(factura["importe"] - movimiento["importe"])

            if diferencia <= 0.01:
                estado = "conciliado"
                mejor_diferencia = diferencia
                mejor_movimiento = movimiento
                break

            if diferencia <= 5.00:
                if mejor_movimiento is None or diferencia < mejor_diferencia:
                    estado = "parcialmente_conciliado"
                    mejor_diferencia = diferencia
                    mejor_movimiento = movimiento

        if mejor_movimiento:
            movimientos_usados.add(mejor_movimiento["id"])

        conciliacion.append({
            "archivo": factura["archivo"],
            "fecha": factura["fecha"],
            "tipo": factura["tipo"],
            "importe": round(factura["importe"], 2),
            "estado": estado,
            "diferencia": round(mejor_diferencia, 2) if mejor_diferencia is not None else None,
            "movimiento_asociado": mejor_movimiento["archivo"] if mejor_movimiento else None
        })

    # movimientos de banco sin soporte / no conciliables
    for movimiento in movimientos_banco:
        if movimiento["id"] in movimientos_usados:
            continue

        estado_extra = "sin_soporte"
        if movimiento.get("categoria") in ["comision", "retencion", "traspaso"]:
            estado_extra = "no_conciliable"

        conciliacion.append({
            "archivo": movimiento["archivo"],
            "fecha": movimiento["fecha"],
            "tipo": "movimiento_bancario",
            "importe": round(movimiento["importe"], 2),
            "estado": estado_extra,
            "diferencia": None,
            "movimiento_asociado": None
        })

    return conciliacion
