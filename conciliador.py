def normalizar_importe(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except Exception:
        return None


def detectar_inconsistencias(ledger):
    conciliacion = []

    facturas = []
    movimientos_banco = []

    # =========================================
    # 0. SEPARAR FACTURAS Y MOVIMIENTOS BANCO
    # =========================================
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
                "tipo": tipo,
                "importe_firmado": item.get("importe_firmado_num", 0.0),
                "importe_abs": round(abs(item.get("importe_firmado_num", importe)), 2),
                "moneda": item.get("moneda"),
                "categoria": item.get("categoria"),
                "descripcion": item.get("descripcion"),
            })

        elif tipo == "extracto_bancario":
            movimientos_banco.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "tipo": tipo,
                "importe_firmado": item.get("importe_firmado_num", 0.0),
                "importe_abs": round(abs(item.get("importe_firmado_num", importe)), 2),
                "naturaleza": item.get("naturaleza"),
                "categoria": item.get("categoria"),
                "descripcion": item.get("descripcion"),
                "moneda": item.get("moneda"),
            })

    usados_banco = set()

    # =========================================
    # 1. CONCILIAR FACTURAS
    # =========================================
    for factura in facturas:
        importe_factura = factura.get("importe_firmado", 0.0)

        mejor_match = None
        mejor_estado = None
        mejor_diferencia = None
        mejor_indice = None

        # -------------------------------------
        # 1A. MATCH EXACTO
        # -------------------------------------
        for i, mov in enumerate(movimientos_banco):
            if i in usados_banco:
                continue

            importe_banco = mov.get("importe_firmado", 0.0)

            # coherencia económica: entrada con entrada / salida con salida
            if (importe_factura > 0 and importe_banco < 0) or (importe_factura < 0 and importe_banco > 0):
                continue

            # exacto al céntimo
            diferencia = abs(importe_factura - importe_banco)

            if diferencia <= 0.01:
                mejor_match = mov
                mejor_estado = "conciliado exacto"
                mejor_diferencia = round(diferencia, 2)
                mejor_indice = i
                break

        # -------------------------------------
        # 1B. MATCH PROBABLE
        # -------------------------------------
        if mejor_match is None:
            for i, mov in enumerate(movimientos_banco):
                if i in usados_banco:
                    continue

                importe_banco = mov.get("importe_firmado", 0.0)

                # coherencia económica
                if (importe_factura > 0 and importe_banco < 0) or (importe_factura < 0 and importe_banco > 0):
                    continue

                # tolerancia: 2% con techo de 50
                tolerancia = min(max(0.01, abs(importe_factura) * 0.02), 50.0)
                diferencia = abs(importe_factura - importe_banco)

                if diferencia <= tolerancia:
                    if mejor_match is None or diferencia < mejor_diferencia:
                        mejor_match = mov
                        mejor_estado = "conciliado probable"
                        mejor_diferencia = round(diferencia, 2)
                        mejor_indice = i

        # -------------------------------------
        # 1C. RESULTADO FACTURA
        # -------------------------------------
        if mejor_match is not None:
            usados_banco.add(mejor_indice)

            conciliacion.append({
                "id": factura["id"],
                "tipo": factura["tipo"],
                "archivo": factura["archivo"],
                "fecha": factura["fecha"],
                "importe": factura["importe_abs"],
                "estado": mejor_estado,
                "match": mejor_match.get("archivo"),
                "movimiento_asociado": mejor_match.get("archivo"),
                "diferencia": mejor_diferencia,
                "categoria": factura.get("categoria"),
                "moneda": factura.get("moneda"),
                "riesgo": "bajo" if mejor_estado == "conciliado exacto" else "medio",
            })

        else:
            estado_pendiente = "pendiente cobro" if factura["tipo"] == "factura_venta" else "pendiente pago"

            conciliacion.append({
                "id": factura["id"],
                "tipo": factura["tipo"],
                "archivo": factura["archivo"],
                "fecha": factura["fecha"],
                "importe": factura["importe_abs"],
                "estado": estado_pendiente,
                "match": None,
                "movimiento_asociado": None,
                "diferencia": None,
                "categoria": factura.get("categoria"),
                "moneda": factura.get("moneda"),
                "riesgo": "alto",
            })

    # =========================================
    # 2. MOVIMIENTOS BANCO SIN SOPORTE
    # =========================================
    for i, mov in enumerate(movimientos_banco):
        if i in usados_banco:
            continue

        importe = mov.get("importe_abs", 0.0)
        categoria = mov.get("categoria", "desconocido")

        # no todos los sin soporte pesan igual
        if importe >= 100:
            estado = "sin soporte"
            riesgo = "alto"
        else:
            estado = "sin soporte menor"
            riesgo = "bajo"

        conciliacion.append({
            "id": mov["id"],
            "tipo": "extracto_bancario",
            "archivo": mov["archivo"],
            "fecha": mov["fecha"],
            "importe": round(importe, 2),
            "estado": estado,
            "match": None,
            "movimiento_asociado": None,
            "diferencia": None,
            "categoria": categoria,
            "moneda": mov.get("moneda"),
            "riesgo": riesgo,
        })

    return conciliacion
