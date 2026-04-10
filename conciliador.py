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

        tipo = item.get("tipo")

        if tipo in ["factura_venta", "factura_compra"]:
            facturas.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "periodo": item.get("periodo"),
                "tipo": tipo,
                "importe": round(abs(importe), 2),
            })

        elif tipo == "extracto_bancario":
            movimientos_banco.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "periodo": item.get("periodo"),
                "naturaleza": item.get("naturaleza"),
                "categoria": item.get("categoria"),
                "importe": round(abs(importe), 2),
                "descripcion": item.get("descripcion"),
            })

    conciliacion = []
    movimientos_usados = set()

    # 1. Conciliación de facturas contra banco
    for factura in facturas:
        candidatos = []

        for movimiento in movimientos_banco:
            if movimiento["id"] in movimientos_usados:
                continue

            if factura["tipo"] == "factura_venta" and movimiento["naturaleza"] != "entrada":
                continue

            if factura["tipo"] == "factura_compra" and movimiento["naturaleza"] != "salida":
                continue

            if movimiento.get("categoria") in ["comision", "retencion", "traspaso", "ajuste"]:
                continue

            diferencia = abs(factura["importe"] - movimiento["importe"])
            misma_fecha_aprox = factura["fecha"] == movimiento["fecha"] or factura["periodo"] == movimiento["periodo"]

            score = 0
            if diferencia <= 0.01:
                score += 100
            elif diferencia <= 5:
                score += 70
            elif diferencia <= 30:
                score += 40

            if misma_fecha_aprox:
                score += 10

            if score > 0:
                candidatos.append((score, diferencia, movimiento))

        candidatos.sort(key=lambda x: (-x[0], x[1]))

        if len(candidatos) > 1 and candidatos[0][1] == candidatos[1][1]:
            conciliacion.append({
                "id": factura["id"],
                "archivo": factura["archivo"],
                "fecha": factura["fecha"],
                "tipo": factura["tipo"],
                "importe": round(factura["importe"], 2),
                "estado": "duplicado_o_conflictivo",
                "diferencia": round(candidatos[0][1], 2),
                "movimiento_asociado": None,
            })
            continue

        if not candidatos:
            conciliacion.append({
                "id": factura["id"],
                "archivo": factura["archivo"],
                "fecha": factura["fecha"],
                "tipo": factura["tipo"],
                "importe": round(factura["importe"], 2),
                "estado": "pendiente",
                "diferencia": None,
                "movimiento_asociado": None,
            })
            continue

        mejor_score, mejor_dif, mejor_mov = candidatos[0]
        movimientos_usados.add(mejor_mov["id"])

        estado = "conciliado_exacto" if mejor_dif <= 0.01 else "probablemente_conciliado"

        conciliacion.append({
            "id": factura["id"],
            "archivo": factura["archivo"],
            "fecha": factura["fecha"],
            "tipo": factura["tipo"],
            "importe": round(factura["importe"], 2),
            "estado": estado,
            "diferencia": round(mejor_dif, 2),
            "movimiento_asociado": mejor_mov["archivo"],
        })

    # 2. Movimientos bancarios sobrantes
    for movimiento in movimientos_banco:
        if movimiento["id"] in movimientos_usados:
            continue

        categoria = movimiento.get("categoria")

        if categoria in ["comision", "retencion", "traspaso", "ajuste"]:
            estado_extra = "no_conciliable"
        else:
            estado_extra = "sin_soporte"

        conciliacion.append({
            "id": movimiento["id"],
            "archivo": movimiento["archivo"],
            "fecha": movimiento["fecha"],
            "tipo": "movimiento_bancario",
            "importe": round(movimiento["importe"], 2),
            "estado": estado_extra,
            "diferencia": None,
            "movimiento_asociado": None,
        })

    return conciliacion
