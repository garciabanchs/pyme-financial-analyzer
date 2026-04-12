from branding import BRANDING


UMBRAL_RELEVANTE_REPORTE = 100.0


def fmt_importe_reporte(numero):
    try:
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def normalizar_importe_reporte(valor):
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        return float(str(valor).replace(".", "").replace(",", "."))
    except Exception:
        return 0.0


def normalizar_estado_conciliacion(estado):
    estado = (estado or "").strip().lower().replace("-", "_").replace(" ", "_")

    mapa = {
        "conciliado_exacto": "conciliado_exacto",
        "conciliado exacto": "conciliado_exacto",
        "conciliado_exacto_multi": "conciliado_exacto_multi",
        "conciliado exacto multi": "conciliado_exacto_multi",
        "conciliado_probable": "conciliado_probable",
        "probablemente_conciliado": "conciliado_probable",
        "conciliado probable": "conciliado_probable",
        "conciliado_probable_multi": "conciliado_probable_multi",
        "conciliado probable multi": "conciliado_probable_multi",
        "probablemente_conciliado_multi": "conciliado_probable_multi",
        "pendiente": "pendiente",
        "pendiente_cobro": "pendiente_cobro",
        "pendiente cobro": "pendiente_cobro",
        "pendiente_pago": "pendiente_pago",
        "pendiente pago": "pendiente_pago",
        "sin_soporte": "sin_soporte",
        "sin soporte": "sin_soporte",
        "sin_soporte_menor": "sin_soporte_menor",
        "sin soporte menor": "sin_soporte_menor",
        "no_conciliable": "no_conciliable",
        "no conciliable": "no_conciliable",
        "duplicado_potencial": "duplicado_potencial",
        "duplicado potencial": "duplicado_potencial",
        "duplicado_o_conflictivo": "duplicado_potencial",
        "duplicado o conflictivo": "duplicado_potencial",
        "movimiento_interno": "movimiento_interno",
        "movimiento interno": "movimiento_interno",
        "movimiento_bancario_no_conciliable": "movimiento_bancario_no_conciliable",
        "movimiento bancario no conciliable": "movimiento_bancario_no_conciliable",
        "movimiento_bancario_no_conciliable_menor": "movimiento_bancario_no_conciliable_menor",
        "movimiento bancario no conciliable menor": "movimiento_bancario_no_conciliable_menor",
        "movimiento_agrupado": "movimiento_agrupado",
        "movimiento agrupado": "movimiento_agrupado",
        "agrupado": "agrupado",
    }

    return mapa.get(estado, estado)


def humanizar_estado_conciliacion(estado):
    estado_norm = normalizar_estado_conciliacion(estado)

    mapa = {
        "conciliado_exacto": "Conciliado exacto",
        "conciliado_exacto_multi": "Conciliado exacto (múltiples movimientos)",
        "conciliado_probable": "Conciliado probable",
        "conciliado_probable_multi": "Conciliado probable (múltiples movimientos)",
        "pendiente": "Pendiente",
        "pendiente_cobro": "Pendiente de cobro",
        "pendiente_pago": "Pendiente de pago",
        "sin_soporte": "Sin soporte",
        "sin_soporte_menor": "Sin soporte menor",
        "no_conciliable": "No conciliable",
        "duplicado_potencial": "Duplicado potencial",
        "movimiento_interno": "Movimiento interno",
        "movimiento_bancario_no_conciliable": "Movimiento bancario no conciliable",
        "movimiento_bancario_no_conciliable_menor": "Movimiento bancario no conciliable menor",
        "movimiento_agrupado": "Movimiento agrupado",
        "agrupado": "Agrupado",
    }

    return mapa.get(estado_norm, str(estado).replace("_", " ").title())


def badge_class_estado_conciliacion(estado):
    estado_norm = normalizar_estado_conciliacion(estado)

    if estado_norm in ["conciliado_exacto", "conciliado_exacto_multi"]:
        return "badge-green"

    if estado_norm in ["conciliado_probable", "conciliado_probable_multi", "duplicado_potencial"]:
        return "badge-yellow"

    if estado_norm in [
        "pendiente",
        "pendiente_cobro",
        "pendiente_pago",
        "sin_soporte",
        "sin_soporte_menor",
    ]:
        return "badge-red"

    if estado_norm in [
        "no_conciliable",
        "movimiento_interno",
        "movimiento_bancario_no_conciliable",
        "movimiento_bancario_no_conciliable_menor",
        "movimiento_agrupado",
        "agrupado",
    ]:
        return "badge-gray"

    return "badge-gray"


def humanizar_categoria(categoria):
    categoria = (categoria or "").strip().lower()

    mapa = {
        "factura_venta": "Factura de venta",
        "factura_compra": "Factura de compra",
        "extracto_bancario": "Extracto bancario",
        "extracto_resumen": "Resumen del extracto",
        "resumen_extracto": "Resumen del extracto",
        "otros": "Otros",
        "cobro_cliente": "Cobro de cliente",
        "pago_proveedor": "Pago a proveedor",
        "retiro_propio": "Retiro propio",
        "gasto_operativo": "Gasto operativo",
        "transferencia_interna": "Transferencia interna",
        "traspaso": "Transferencia interna",
        "comision": "Comisión",
        "impuesto": "Impuesto",
        "retencion": "Retención",
        "ajuste": "Ajuste",
        "otros_cobros": "Otros cobros",
        "otros_pagos": "Otros pagos",
        "movimiento_interno": "Movimiento interno",
        "no_conciliable": "No conciliable",
    }

    return mapa.get(categoria, str(categoria).replace("_", " ").title())


def humanizar_tipo_documento(tipo):
    tipo = (tipo or "").strip().lower()

    mapa = {
        "factura_venta": "Factura de venta",
        "factura_compra": "Factura de compra",
        "extracto_bancario": "Extracto bancario",
        "extracto_resumen": "Resumen del extracto",
        "otros": "Otros",
    }

    return mapa.get(tipo, str(tipo).replace("_", " ").title())


def humanizar_naturaleza(naturaleza):
    naturaleza = (naturaleza or "").strip().lower()

    mapa = {
        "entrada": "Entrada",
        "salida": "Salida",
        "revisar": "Revisar",
        "resumen": "Resumen",
        "desconocido": "Desconocido",
    }

    return mapa.get(naturaleza, str(naturaleza).replace("_", " ").title())


def pluralizar(numero, singular, plural=None):
    plural = plural or f"{singular}s"
    return singular if numero == 1 else plural


def construir_resumen_documentos(clasificados):
    clasificados = clasificados or {}
    return {
        "factura_venta": len(clasificados.get("factura_venta", [])),
        "factura_compra": len(clasificados.get("factura_compra", [])),
        "extracto_bancario": len(clasificados.get("extracto_bancario", [])),
        "otros": len(clasificados.get("otros", [])),
    }


def construir_resumen_flujo(ledger):
    ledger = ledger or []

    for item in ledger:
        if item.get("tipo") == "extracto_resumen":
            resumen = item.get("resumen_extracto", {}) or {}

            saldo_inicial = resumen.get("saldo_inicial_disponible") or 0.0
            saldo_final = resumen.get("saldo_final_disponible") or 0.0
            retenido = abs(resumen.get("retenido") or 0.0)

            entradas = max(resumen.get("pagos_recibidos") or 0.0, 0.0)
            entradas += max(resumen.get("depositos_y_creditos") or 0.0, 0.0)
            entradas += max(resumen.get("liberaciones") or 0.0, 0.0)

            salidas = abs(min(resumen.get("pagos_enviados") or 0.0, 0.0))
            salidas += abs(min(resumen.get("retiradas_y_cargos") or 0.0, 0.0))
            salidas += abs(min(resumen.get("tarifas") or 0.0, 0.0))
            salidas += abs(min(resumen.get("retenido") or 0.0, 0.0))

            variacion = saldo_final - saldo_inicial

            return {
                "saldo_inicial": saldo_inicial,
                "entradas": entradas,
                "salidas": salidas,
                "saldo_final": saldo_final,
                "variacion": variacion,
                "retenido": retenido,
                "balance": variacion,
                "movimientos": entradas + salidas,
                "revisar": 0.0,
            }

    saldo_inicial = 0.0
    entradas = 0.0
    salidas = 0.0

    for item in ledger:
        if item.get("tipo") != "extracto_bancario":
            continue

        valor_firmado = item.get("importe_firmado_num")
        if valor_firmado is None:
            continue

        if valor_firmado > 0:
            entradas += valor_firmado
        elif valor_firmado < 0:
            salidas += abs(valor_firmado)

    saldo_final = saldo_inicial + entradas - salidas
    variacion = saldo_final - saldo_inicial

    return {
        "saldo_inicial": saldo_inicial,
        "entradas": entradas,
        "salidas": salidas,
        "saldo_final": saldo_final,
        "variacion": variacion,
        "retenido": 0.0,
        "balance": variacion,
        "movimientos": entradas + salidas,
        "revisar": 0.0,
    }


def construir_resumen_conciliacion(conciliacion):
    conciliacion = conciliacion or []

    total_exactas = 0
    total_probables = 0
    total_probables_multi = 0
    total_exactas_multi = 0
    total_pendientes = 0
    total_sin_soporte = 0
    total_sin_soporte_menor = 0
    total_no_conciliables = 0
    total_conflictivos = 0
    total_duplicados = 0
    total_movimientos_internos = 0
    total_movimientos_bancarios_no_conciliables = 0
    total_movimientos_bancarios_no_conciliables_menor = 0
    total_movimientos_agrupados = 0

    importe_pendiente = 0.0
    pendiente_cobro = 0.0
    pendiente_pago = 0.0

    cierre_confiable = True
    requiere_validacion = False

    for item in conciliacion:
        estado = normalizar_estado_conciliacion(item.get("estado", ""))
        importe = normalizar_importe_reporte(item.get("importe", 0))
        tipo = item.get("tipo", "")

        if estado == "conciliado_exacto":
            total_exactas += 1

        elif estado == "conciliado_exacto_multi":
            total_exactas_multi += 1
            requiere_validacion = True

        elif estado == "conciliado_probable":
            total_probables += 1
            requiere_validacion = True
            cierre_confiable = False

        elif estado == "conciliado_probable_multi":
            total_probables_multi += 1
            requiere_validacion = True
            cierre_confiable = False

        elif estado in ["pendiente", "pendiente_cobro", "pendiente_pago"]:
            total_pendientes += 1
            importe_pendiente += importe
            cierre_confiable = False

            if estado == "pendiente_cobro" or tipo == "factura_venta":
                pendiente_cobro += importe
            elif estado == "pendiente_pago" or tipo == "factura_compra":
                pendiente_pago += importe

        elif estado == "sin_soporte":
            total_sin_soporte += 1
            cierre_confiable = False

        elif estado == "sin_soporte_menor":
            total_sin_soporte_menor += 1

        elif estado == "no_conciliable":
            total_no_conciliables += 1

        elif estado == "duplicado_potencial":
            total_conflictivos += 1
            total_duplicados += 1
            requiere_validacion = True
            cierre_confiable = False

        elif estado == "movimiento_interno":
            total_movimientos_internos += 1

        elif estado == "movimiento_bancario_no_conciliable":
            total_movimientos_bancarios_no_conciliables += 1
            total_no_conciliables += 1

        elif estado == "movimiento_bancario_no_conciliable_menor":
            total_movimientos_bancarios_no_conciliables_menor += 1
            total_movimientos_bancarios_no_conciliables += 1
            total_no_conciliables += 1

        elif estado in ["movimiento_agrupado", "agrupado"]:
            total_movimientos_agrupados += 1

    nivel_cierre = "alto"
    if not cierre_confiable:
        nivel_cierre = "bajo"
    elif requiere_validacion:
        nivel_cierre = "medio"

    return {
        "conciliadas": total_exactas,
        "conciliadas_multi": total_exactas_multi,
        "parciales": total_probables,
        "probables_multi": total_probables_multi,
        "pendientes": total_pendientes,
        "sin_soporte": total_sin_soporte,
        "sin_soporte_menor": total_sin_soporte_menor,
        "no_conciliables": total_no_conciliables,
        "conflictivos": total_conflictivos,
        "duplicados": total_duplicados,
        "movimientos_internos": total_movimientos_internos,
        "movimientos_bancarios_no_conciliables": total_movimientos_bancarios_no_conciliables,
        "movimientos_bancarios_no_conciliables_menor": total_movimientos_bancarios_no_conciliables_menor,
        "movimientos_agrupados": total_movimientos_agrupados,
        "importe_pendiente": importe_pendiente,
        "pendiente_cobro": pendiente_cobro,
        "pendiente_pago": pendiente_pago,
        "cierre_confiable": cierre_confiable,
        "requiere_validacion": requiere_validacion,
        "nivel_cierre": nivel_cierre,
    }


def analizar_movimientos_bancarios_ledger(ledger, umbral_relevante=UMBRAL_RELEVANTE_REPORTE):
    ledger = ledger or []

    entradas_relevantes = []
    salidas_relevantes = []

    otros_cobros_total = 0.0
    otros_pagos_total = 0.0
    otros_cobros_cantidad = 0
    otros_pagos_cantidad = 0

    for item in ledger:
        if item.get("tipo") != "extracto_bancario":
            continue

        categoria = item.get("categoria", "")
        valor = item.get("importe_firmado_num")
        if valor is None:
            valor = normalizar_importe_reporte(item.get("importe", 0))
            if item.get("naturaleza") == "salida":
                valor = -abs(valor)

        fila = {
            "archivo": item.get("archivo", "-"),
            "fecha": item.get("fecha", "-"),
            "importe_abs": abs(valor),
            "importe_fmt": fmt_importe_reporte(abs(valor)),
            "naturaleza": item.get("naturaleza", "-"),
            "naturaleza_humana": humanizar_naturaleza(item.get("naturaleza", "-")),
            "descripcion": item.get("descripcion", "-"),
            "categoria": categoria,
            "categoria_humana": humanizar_categoria(categoria),
            "moneda": item.get("moneda", "") or "",
            "clase_fila": "row-entrada" if valor >= 0 else "row-salida",
        }

        if categoria == "otros_cobros":
            otros_cobros_total += abs(valor)
            desc = item.get("descripcion", "")
            try:
                otros_cobros_cantidad += int(str(desc).split()[0])
            except Exception:
                otros_cobros_cantidad += 1
            entradas_relevantes.append(fila)
            continue

        if categoria == "otros_pagos":
            otros_pagos_total += abs(valor)
            desc = item.get("descripcion", "")
            try:
                otros_pagos_cantidad += int(str(desc).split()[0])
            except Exception:
                otros_pagos_cantidad += 1
            salidas_relevantes.append(fila)
            continue

        if abs(valor) >= umbral_relevante:
            if valor >= 0:
                entradas_relevantes.append(fila)
            else:
                salidas_relevantes.append(fila)
        else:
            if valor >= 0:
                otros_cobros_cantidad += 1
                otros_cobros_total += abs(valor)
            else:
                otros_pagos_cantidad += 1
                otros_pagos_total += abs(valor)

    entradas_relevantes.sort(key=lambda x: (x["fecha"], -x["importe_abs"]))
    salidas_relevantes.sort(key=lambda x: (x["fecha"], -x["importe_abs"]))

    return {
        "entradas_relevantes": entradas_relevantes,
        "salidas_relevantes": salidas_relevantes,
        "otros_cobros_cantidad": otros_cobros_cantidad,
        "otros_cobros_total": otros_cobros_total,
        "otros_pagos_cantidad": otros_pagos_cantidad,
        "otros_pagos_total": otros_pagos_total,
    }


def construir_narrativa_ejecutiva(total, docs, flujo, conc):
    saldo_inicial = flujo["saldo_inicial"]
    entradas = flujo["entradas"]
    salidas = flujo["salidas"]
    saldo_final = flujo["saldo_final"]
    variacion = flujo["variacion"]
    pendientes = conc["pendientes"]
    probables = conc["parciales"]
    probables_multi = conc.get("probables_multi", 0)
    exactas_multi = conc.get("conciliadas_multi", 0)
    sin_soporte = conc.get("sin_soporte", 0)
    sin_soporte_menor = conc.get("sin_soporte_menor", 0)
    duplicados = conc.get("duplicados", 0)
    movimientos_internos = conc.get("movimientos_internos", 0)
    nivel_cierre = conc.get("nivel_cierre", "medio")

    if variacion > 0:
        titular = "La caja del período cerró mejor que como empezó."
    elif variacion < 0:
        titular = "La caja del período cerró peor que como empezó."
    else:
        titular = "La caja del período cerró prácticamente igual que como empezó."

    resumen_docs = (
        f"Se analizaron {total} {pluralizar(total, 'archivo')}: "
        f"{docs['factura_venta']} {pluralizar(docs['factura_venta'], 'factura de venta')}, "
        f"{docs['factura_compra']} {pluralizar(docs['factura_compra'], 'factura de compra')}, "
        f"{docs['extracto_bancario']} {pluralizar(docs['extracto_bancario'], 'extracto bancario')} "
        f"y {docs['otros']} {pluralizar(docs['otros'], 'documento', 'documentos')} adicional(es)."
    )

    if nivel_cierre == "bajo":
        partes = []
        if pendientes > 0:
            partes.append(f"{pendientes} {pluralizar(pendientes, 'factura pendiente', 'facturas pendientes')}")
        if probables > 0:
            partes.append(f"{probables} {pluralizar(probables, 'conciliación probable', 'conciliaciones probables')}")
        if probables_multi > 0:
            partes.append(
                f"{probables_multi} {pluralizar(probables_multi, 'conciliación probable múltiple', 'conciliaciones probables múltiples')}"
            )
        if sin_soporte > 0:
            partes.append(
                f"{sin_soporte} {pluralizar(sin_soporte, 'movimiento relevante sin soporte', 'movimientos relevantes sin soporte')}"
            )
        if duplicados > 0:
            partes.append(f"{duplicados} {pluralizar(duplicados, 'duplicado potencial', 'duplicados potenciales')}")
        if movimientos_internos > 0:
            partes.append(
                f"{movimientos_internos} {pluralizar(movimientos_internos, 'movimiento interno', 'movimientos internos')}"
            )

        detalle = ", ".join(partes) if partes else "elementos que todavía requieren validación"
        complemento = f" El cierre todavía no puede considerarse definitivo: persisten {detalle}."
    elif nivel_cierre == "medio":
        partes = []
        if exactas_multi > 0:
            partes.append(
                f"{exactas_multi} {pluralizar(exactas_multi, 'conciliación exacta múltiple', 'conciliaciones exactas múltiples')}"
            )
        if probables_multi > 0:
            partes.append(
                f"{probables_multi} {pluralizar(probables_multi, 'conciliación probable múltiple', 'conciliaciones probables múltiples')}"
            )
        if duplicados > 0:
            partes.append(f"{duplicados} {pluralizar(duplicados, 'duplicado potencial', 'duplicados potenciales')}")
        if movimientos_internos > 0:
            partes.append(
                f"{movimientos_internos} {pluralizar(movimientos_internos, 'movimiento interno', 'movimientos internos')}"
            )

        detalle = ", ".join(partes) if partes else "validaciones adicionales"
        complemento = f" La lectura es útil, pero todavía requiere validación adicional: se observan {detalle}."
    elif sin_soporte > 0:
        complemento = (
            f" No se observan pendientes fuertes de conciliación, pero existen "
            f"{sin_soporte} {pluralizar(sin_soporte, 'movimiento relevante sin soporte documental', 'movimientos relevantes sin soporte documental')}."
        )
    elif sin_soporte_menor > 0:
        complemento = (
            f" No se observan pendientes relevantes, aunque existen "
            f"{sin_soporte_menor} {pluralizar(sin_soporte_menor, 'movimiento menor sin soporte directo', 'movimientos menores sin soporte directo')}."
        )
    else:
        complemento = " No se observan pendientes relevantes de conciliación en la estructura analizada."

    narrativa = (
        f"{resumen_docs} "
        f"El saldo inicial fue de € {fmt_importe_reporte(saldo_inicial)}, "
        f"entraron € {fmt_importe_reporte(entradas)}, "
        f"salieron € {fmt_importe_reporte(salidas)} "
        f"y el saldo final se ubicó en € {fmt_importe_reporte(saldo_final)}, "
        f"con una variación neta de € {fmt_importe_reporte(variacion)}."
        f"{complemento}"
    )

    return titular, narrativa


def generar_html_resultado(total, clasificados, importes, documentos, ledger=None, conciliacion=None):
    assert BRANDING["modo"] in BRANDING, f"Modo inválido en BRANDING: {BRANDING.get('modo')}"
    branding_data = BRANDING[BRANDING["modo"]]

    ledger = ledger or []
    conciliacion = conciliacion or []
    documentos = documentos or []
    importes = importes or []

    UMBRAL_RELEVANTE = UMBRAL_RELEVANTE_REPORTE

    def fmt(numero):
        return fmt_importe_reporte(numero)

    def normalizar_importe(valor):
        return normalizar_importe_reporte(valor)

    def humanizar_estado(estado):
        return humanizar_estado_conciliacion(estado)

    def badge_class_estado(estado):
        return badge_class_estado_conciliacion(estado)

    def contar_docs():
        return construir_resumen_documentos(clasificados)

    def resumen_flujo():
        return construir_resumen_flujo(ledger)

    def resumen_conciliacion():
        return construir_resumen_conciliacion(conciliacion)

    def analizar_movimientos_bancarios():
        return analizar_movimientos_bancarios_ledger(ledger, UMBRAL_RELEVANTE)

    def texto_lectura_ejecutiva(flujo, conc, docs):
        return construir_narrativa_ejecutiva(total, docs, flujo, conc)

    def clase_badge_categoria(categoria):
        categoria = (categoria or "").lower()
        if categoria in ["cobro_cliente", "otros_cobros"]:
            return "badge-green"
        if categoria in ["pago_proveedor", "gasto_operativo", "otros_pagos"]:
            return "badge-red"
        if categoria in ["retiro_propio", "transferencia_interna", "traspaso"]:
            return "badge-gray"
        if categoria in ["comision", "retencion", "impuesto", "ajuste"]:
            return "badge-yellow"
        return "badge-gray"

    def construir_botones_filtro():
        botones = [
            ("all", "Ver todo"),
            ("entradas", "Entradas"),
            ("salidas", "Salidas"),
            ("cobros", "Cobros"),
            ("pagos", "Pagos"),
            ("internos", "Movimientos internos"),
            ("pendientes", "Facturas pendientes"),
            ("conciliadas", "Facturas conciliadas"),
            ("sin-soporte", "Sin soporte"),
            ("no-conciliables", "No conciliables"),
        ]

        html = ""
        for valor, etiqueta in botones:
            clase = "filter-btn active" if valor == "all" else "filter-btn"
            html += f'<button class="{clase}" type="button" data-filter="{valor}">{etiqueta}</button>'
        return html

    def tabla_ledger_html():
        if not ledger:
            return """
            <div class="empty-state">
                <p>No hay movimientos en el ledger.</p>
            </div>
            """

        filas = ""
        for item in ledger:
            naturaleza = (item.get("naturaleza") or "").lower()
            clase_fila = "row-entrada" if naturaleza == "entrada" else "row-salida" if naturaleza == "salida" else ""
            categoria = humanizar_categoria(item.get("categoria", "-"))
            tipo = humanizar_tipo_documento(item.get("tipo", "-"))

            filas += f"""
            <tr class="{clase_fila}">
                <td>{item.get('archivo', '-')}</td>
                <td>{tipo}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
                <td class="mono">€ {fmt(normalizar_importe(item.get('importe', 0)))}</td>
                <td>{humanizar_naturaleza(item.get('naturaleza', '-'))}</td>
                <td><span class="badge {clase_badge_categoria(item.get('categoria'))}">{categoria}</span></td>
            </tr>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Movimiento financiero base</h3>
                    <p>Registro preliminar de movimientos identificados a partir de la documentación cargada.</p>
                </div>
                <div class="chip">{len(ledger)} movimientos</div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Tipo</th>
                            <th>Fecha</th>
                            <th>Importe</th>
                            <th>Naturaleza</th>
                            <th>Categoría</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def tarjetas_moviles_movimientos(items, titulo, clase, extra_tags=None):
        extra_tags = extra_tags or []
        if not items:
            return ""

        cards = ""
        for item in items:
            tags = ["all"]
            if clase == "row-entrada":
                tags.extend(["entradas", "cobros"])
            if clase == "row-salida":
                tags.append("salidas")
                if item["categoria"] in ["pago_proveedor", "gasto_operativo", "otros_pagos"]:
                    tags.append("pagos")
                if item["categoria"] in ["retiro_propio", "transferencia_interna", "traspaso"]:
                    tags.append("internos")

            for t in extra_tags:
                if t not in tags:
                    tags.append(t)

            cards += f"""
            <article class="mobile-movement-card {clase}" data-kind="{' '.join(tags)}">
                <div class="mobile-movement-head">
                    <span class="badge {clase_badge_categoria(item['categoria'])}">{item['categoria_humana']}</span>
                    <span class="mobile-amount">€ {item['importe_fmt']}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Fecha</span>
                    <span class="mono">{item['fecha']}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Naturaleza</span>
                    <span>{item['naturaleza_humana']}</span>
                </div>
                <div class="mobile-description">{item['descripcion']}</div>
            </article>
            """

        return f"""
        <div class="mobile-movements-block">
            <div class="mobile-block-title">{titulo}</div>
            <div class="mobile-movements-grid">
                {cards}
            </div>
        </div>
        """

    def tabla_movimientos_relevantes_html():
        analisis = analizar_movimientos_bancarios()
        entradas = analisis["entradas_relevantes"]
        salidas = analisis["salidas_relevantes"]

        if not entradas and not salidas:
            return """
            <div class="empty-state">
                <p>No hay movimientos bancarios relevantes para mostrar.</p>
            </div>
            """

        secciones = []

        if entradas:
            filas_entradas = ""
            for item in entradas:
                tags = ["entradas", "cobros", "all"]
                if item["categoria"] == "otros_cobros":
                    tags.append("cobros")
                filas_entradas += f"""
                <tr class="row-entrada mov-row"
                    data-kind="{' '.join(sorted(set(tags)))}"
                    data-category="{item['categoria']}">
                    <td class="mono">{item['fecha']}</td>
                    <td class="mono">€ {item['importe_fmt']}</td>
                    <td>{item['descripcion']}</td>
                    <td><span class="badge {clase_badge_categoria(item['categoria'])}">{item['categoria_humana']}</span></td>
                </tr>
                """
            secciones.append(f"""
            <div class="table-shell">
                <div class="table-head">
                    <div>
                        <h3>Entradas relevantes</h3>
                        <p>Movimientos de entrada iguales o mayores a € {fmt(UMBRAL_RELEVANTE)} y agrupados ejecutivos.</p>
                    </div>
                    <div class="chip">{len(entradas)} entradas</div>
                </div>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Importe</th>
                                <th>Descripción</th>
                                <th>Categoría</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_entradas}
                        </tbody>
                    </table>
                </div>
            </div>
            {tarjetas_moviles_movimientos(entradas, "Entradas relevantes", "row-entrada")}
            """)

        if salidas:
            filas_salidas = ""
            for item in salidas:
                tags = ["salidas", "all"]
                if item["categoria"] in ["pago_proveedor", "gasto_operativo", "otros_pagos"]:
                    tags.append("pagos")
                if item["categoria"] in ["retiro_propio", "transferencia_interna", "traspaso"]:
                    tags.append("internos")
                filas_salidas += f"""
                <tr class="row-salida mov-row"
                    data-kind="{' '.join(sorted(set(tags)))}"
                    data-category="{item['categoria']}">
                    <td class="mono">{item['fecha']}</td>
                    <td class="mono">€ {item['importe_fmt']}</td>
                    <td>{item['descripcion']}</td>
                    <td><span class="badge {clase_badge_categoria(item['categoria'])}">{item['categoria_humana']}</span></td>
                </tr>
                """
            secciones.append(f"""
            <div class="table-shell">
                <div class="table-head">
                    <div>
                        <h3>Salidas relevantes</h3>
                        <p>Movimientos de salida iguales o mayores a € {fmt(UMBRAL_RELEVANTE)} y agrupados ejecutivos.</p>
                    </div>
                    <div class="chip">{len(salidas)} salidas</div>
                </div>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Importe</th>
                                <th>Descripción</th>
                                <th>Categoría</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_salidas}
                        </tbody>
                    </table>
                </div>
            </div>
            {tarjetas_moviles_movimientos(salidas, "Salidas relevantes", "row-salida")}
            """)

        return "".join(secciones)

    def tabla_conciliacion_html():
        if not conciliacion:
            return """
            <div class="empty-state">
                <p>No hay conciliación disponible.</p>
            </div>
            """

        filas = ""
        cards = ""

        for item in conciliacion:
            importe = fmt(normalizar_importe(item.get("importe", 0)))
            diferencia = "-"
            if item.get("diferencia") is not None:
                diferencia = fmt(normalizar_importe(item.get("diferencia", 0)))

            estado_raw = item.get("estado", "-")
            estado_norm = normalizar_estado_conciliacion(estado_raw)
            estado = humanizar_estado(estado_raw)
            badge_class = badge_class_estado(estado_raw)

            tags = ["all"]
            if estado_norm in ["pendiente", "pendiente_cobro", "pendiente_pago"]:
                tags.append("pendientes")
            if estado_norm in ["conciliado_exacto", "conciliado_exacto_multi", "conciliado_probable", "conciliado_probable_multi"]:
                tags.append("conciliadas")
            if estado_norm in ["sin_soporte", "sin_soporte_menor"]:
                tags.append("sin-soporte")
            if estado_norm in ["no_conciliable", "movimiento_bancario_no_conciliable", "movimiento_bancario_no_conciliable_menor"]:
                tags.append("no-conciliables")
            if estado_norm == "movimiento_interno":
                tags.append("internos")

            filas += f"""
            <tr class="conc-row" data-kind="{' '.join(sorted(set(tags)))}">
                <td>{item.get('archivo', '-')}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
                <td class="mono">€ {importe}</td>
                <td><span class="badge {badge_class}">{estado}</span></td>
                <td class="mono">{diferencia if diferencia == '-' else '€ ' + diferencia}</td>
                <td><span class="badge {clase_badge_categoria(item.get('categoria'))}">{humanizar_categoria(item.get('categoria'))}</span></td>
            </tr>
            """

            cards += f"""
            <article class="mobile-conc-card" data-kind="{' '.join(sorted(set(tags)))}">
                <div class="mobile-conc-head">
                    <span class="badge {badge_class}">{estado}</span>
                    <span class="mobile-amount">€ {importe}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Archivo</span>
                    <span>{item.get('archivo', '-')}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Fecha</span>
                    <span class="mono">{item.get('fecha', '-')}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Diferencia</span>
                    <span class="mono">{diferencia if diferencia == '-' else '€ ' + diferencia}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Categoría</span>
                    <span>{humanizar_categoria(item.get('categoria'))}</span>
                </div>
            </article>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Conciliación</h3>
                    <p>Estado de coincidencia entre facturas y movimientos detectados en banco.</p>
                </div>
                <div class="chip">{len(conciliacion)} registros</div>
            </div>
            <div class="filter-toolbar">
                {construir_botones_filtro()}
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Fecha</th>
                            <th>Importe</th>
                            <th>Estado</th>
                            <th>Diferencia</th>
                            <th>Categoría</th>
                        </tr>
                    </thead>
                    <tbody id="conc-body">
                        {filas}
                    </tbody>
                </table>
            </div>
            <div class="mobile-conc-grid" id="conc-mobile-grid">
                {cards}
            </div>
        </div>
        """

    def documentos_html():
        if not documentos:
            return """
            <div class="empty-state">
                <p>No hay documentos detectados.</p>
            </div>
            """

        filas = ""
        cards = ""
        for item in documentos:
            tipo_humano = humanizar_tipo_documento(item.get("tipo", "-"))
            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td>{tipo_humano}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
            </tr>
            """

            cards += f"""
            <article class="mobile-doc-card">
                <div class="mobile-doc-title">{item.get('archivo', '-')}</div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Tipo</span>
                    <span>{tipo_humano}</span>
                </div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Fecha</span>
                    <span class="mono">{item.get('fecha', '-')}</span>
                </div>
            </article>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Documentos detectados</h3>
                    <p>Inventario base de documentos reconocidos por el sistema durante el procesamiento.</p>
                </div>
                <div class="chip">{len(documentos)} documentos</div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Tipo</th>
                            <th>Fecha</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            </div>
            <div class="mobile-doc-grid">
                {cards}
            </div>
        </div>
        """

    def _seleccionar_importes_presentables(importes_lista, max_visibles=12):
        if not importes_lista:
            return []

        unicos = []
        vistos = set()
        for imp in importes_lista:
            clave = str(imp).strip()
            if not clave or clave in vistos:
                continue
            vistos.add(clave)
            unicos.append(clave)

        positivos = []
        negativos = []
        neutros = []

        for imp in unicos:
            valor = normalizar_importe_reporte(imp)
            if valor > 0:
                positivos.append(imp)
            elif valor < 0:
                negativos.append(imp)
            else:
                neutros.append(imp)

        seleccion = []
        seleccion.extend(positivos[:6])
        seleccion.extend(negativos[:4])
        seleccion.extend(neutros[:2])

        if len(seleccion) < max_visibles:
            for imp in unicos:
                if imp not in seleccion:
                    seleccion.append(imp)
                if len(seleccion) >= max_visibles:
                    break

        return seleccion[:max_visibles]

    def _formatear_lista_importes(importes_lista):
        if not importes_lista:
            return "No se detectaron montos"

        seleccion = _seleccionar_importes_presentables(importes_lista, max_visibles=12)
        total = len(importes_lista)
        texto = "  ;  ".join(seleccion)

        if total > len(seleccion):
            texto += f"  ;  ... (+{total - len(seleccion)} más)"

        return texto

    def _resumen_importes(importes_lista):
        if not importes_lista:
            return "Sin montos detectados"

        total = len(importes_lista)
        seleccion = _seleccionar_importes_presentables(importes_lista, max_visibles=12)
        positivos = sum(1 for x in importes_lista if normalizar_importe_reporte(x) > 0)
        negativos = sum(1 for x in importes_lista if normalizar_importe_reporte(x) < 0)

        partes = [f"{total} {pluralizar(total, 'monto')} detectado(s)"]
        if positivos > 0:
            partes.append(f"{positivos} positivo(s)")
        if negativos > 0:
            partes.append(f"{negativos} negativo(s)")

        return " · ".join(partes), "  ;  ".join(seleccion)

    def importes_html():
        if not importes:
            return """
            <div class="empty-state">
                <p>No hay montos detectados.</p>
            </div>
            """

        filas = ""
        cards = ""
        for item in importes:
            importes_lista = item.get("importes", []) or []
            montos = _formatear_lista_importes(importes_lista)
            resumen_texto, resumen_lista = _resumen_importes(importes_lista)

            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td>{resumen_texto}</td>
                <td class="amounts-cell">{montos}</td>
            </tr>
            """

            cards += f"""
            <article class="mobile-amount-card">
                <div class="mobile-doc-title">{item.get('archivo', '-')}</div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Resumen</span>
                    <span>{resumen_texto}</span>
                </div>
                <div class="mobile-amount-list">{resumen_lista}</div>
            </article>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Montos identificados</h3>
                    <p>Montos encontrados automáticamente en cada documento. Se priorizan los más representativos para mejorar la lectura.</p>
                </div>
                <div class="chip">{len(importes)} documentos con montos</div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Resumen</th>
                            <th>Montos visibles</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            </div>
            <div class="mobile-amount-grid">
                {cards}
            </div>
        </div>
        """

    def bloque_movimientos_menores_html():
        analisis = analizar_movimientos_bancarios()

        return f"""
        <div class="metrics-grid compact-grid">
            <article class="kpi">
                <div class="label">Otros cobros menores</div>
                <div class="amount">{analisis['otros_cobros_cantidad']}</div>
                <div class="meta"><span class="trend up">€ {fmt(analisis['otros_cobros_total'])}</span><span>Menores a € {fmt(UMBRAL_RELEVANTE)}</span></div>
            </article>

            <article class="kpi">
                <div class="label">Otros pagos menores</div>
                <div class="amount">{analisis['otros_pagos_cantidad']}</div>
                <div class="meta"><span class="trend warn">€ {fmt(analisis['otros_pagos_total'])}</span><span>Menores a € {fmt(UMBRAL_RELEVANTE)}</span></div>
            </article>
        </div>
        """

    def bloque_branding_html():
        partes = []

        if BRANDING.get("mostrar_bio", False):
            imagen_html = ""
            imagen_src = branding_data.get("imagen_html") or branding_data.get("imagen_url")
            if imagen_src:
                imagen_html = f"""
                <img src="{imagen_src}" alt="{branding_data['nombre']}" class="author-photo">
                """

            partes.append(f"""
            <section class="section">
                <div class="section-head solo">
                    <div>
                        <h3 class="section-title">{branding_data.get('titulo', 'Acerca del autor')}</h3>
                        <p class="section-sub">Perfil y contexto del autor o marca detrás del informe.</p>
                    </div>
                </div>
                <div class="author-card">
                    <div class="author-card-inner">
                        {imagen_html}
                        <div class="author-copy">
                            <div class="author-name">{branding_data.get('nombre', '')}</div>
                            <div class="author-subtitle">{branding_data.get('subtitulo', '')}</div>
                            <div class="author-description">{branding_data.get('descripcion', '')}</div>
                        </div>
                    </div>
                </div>
            </section>
            """)

        if BRANDING.get("mostrar_libros", False) and branding_data.get("libros"):
            items = ""
            for libro in branding_data["libros"]:
                portada = ""
                portada_src = libro.get("portada_html") or libro.get("portada_url")
                if portada_src:
                    portada = f"""
                    <img src="{portada_src}" alt="{libro['titulo']}" class="book-cover">
                    """

                items += f"""
                <div class="book-item">
                    {portada}
                    <div class="book-copy">
                        <div class="book-title">{libro.get('titulo', '')}</div>
                        <a href="{libro.get('url', '#')}" target="_blank" class="book-link">Ver en Amazon</a>
                    </div>
                </div>
                """

            partes.append(f"""
            <section class="section books-section">
                <div class="section-head solo">
                    <div>
                        <h3 class="section-title">Libros</h3>
                        <p class="section-sub">Publicaciones relacionadas con finanzas, patrimonio y visión empresarial.</p>
                    </div>
                </div>
                <div class="books-card">
                    {items}
                </div>
            </section>
            """)

        if BRANDING.get("mostrar_contacto", False) and branding_data.get("contacto_url"):
            partes.append(f"""
            <section class="section">
                <div class="contact-card">
                    <div>
                        <div class="contact-title">Contacto</div>
                        <div class="contact-subtitle">Canal directo para profundizar en análisis, consultoría o acompañamiento.</div>
                    </div>
                    <div>
                        <a href="{branding_data.get('contacto_url', '#')}" target="_blank" class="cta-button">
                            {branding_data.get('contacto_texto', 'Contacto')}
                        </a>
                    </div>
                </div>
            </section>
            """)

        return "".join(partes)

    def texto_calidad_cierre(nivel):
        if nivel == "alto":
            return "Cierre preliminar alto"
        if nivel == "medio":
            return "Cierre preliminar medio"
        return "Cierre preliminar bajo"

    docs = contar_docs()
    flujo = resumen_flujo()
    conc = resumen_conciliacion()
    titular_ejecutivo, narrativa_ejecutiva = texto_lectura_ejecutiva(flujo, conc, docs)

    total_docs_clasificados = docs["factura_venta"] + docs["factura_compra"] + docs["extracto_bancario"] + docs["otros"]

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Informe Financiero PYME</title>
        <style>
            :root {{
                --bg:#f4f7fb;
                --panel:rgba(255,255,255,.82);
                --panel-strong:#ffffff;
                --text:#0f172a;
                --muted:#64748b;
                --line:rgba(148,163,184,.22);
                --blue-1:#0f4cff;
                --blue-2:#5ea7ff;
                --green:#16a34a;
                --green-soft:#ecfdf3;
                --green-line:#d8f5e4;
                --yellow:#ca8a04;
                --yellow-soft:#fff9e8;
                --red:#dc2626;
                --red-soft:#fef2f2;
                --red-line:#ffdede;
                --gray:#475569;
                --gray-soft:#f1f5f9;
                --shadow-sm:0 10px 25px rgba(15,23,42,.06);
                --shadow-md:0 20px 45px rgba(15,23,42,.08);
                --shadow-lg:0 30px 80px rgba(15,23,42,.12);
                --max:1340px;
            }}

            * {{
                box-sizing:border-box;
            }}

            html {{
                scroll-behavior:smooth;
            }}

            body {{
                margin:0;
                font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
                color:var(--text);
                background:
                    radial-gradient(circle at top left, rgba(94,167,255,.18), transparent 28%),
                    radial-gradient(circle at 85% 20%, rgba(15,76,255,.10), transparent 24%),
                    linear-gradient(180deg, #f8fbff 0%, #f4f7fb 45%, #edf2f8 100%);
                min-height:100vh;
                letter-spacing:-.02em;
            }}

            .wrap {{
                width:min(calc(100% - 28px), var(--max));
                margin:0 auto;
            }}

            .topbar-shell {{
                padding:16px 0 0;
            }}

            .topbar {{
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:18px;
                padding:18px 22px;
                background:rgba(255,255,255,.75);
                backdrop-filter:blur(18px);
                border:1px solid rgba(255,255,255,.65);
                border-radius:24px;
                box-shadow:var(--shadow-md);
                flex-wrap:wrap;
            }}

            .brand {{
                display:flex;
                flex-direction:column;
                gap:4px;
                min-width:0;
            }}

            .eyebrow {{
                display:inline-flex;
                align-items:center;
                gap:8px;
                color:var(--blue-1);
                font-size:12px;
                font-weight:700;
                text-transform:uppercase;
                letter-spacing:.12em;
            }}

            .eyebrow::before {{
                content:"";
                width:8px;
                height:8px;
                border-radius:999px;
                background:linear-gradient(135deg,var(--blue-1),var(--blue-2));
                box-shadow:0 0 0 6px rgba(94,167,255,.15);
            }}

            .brand h1 {{
                margin:0;
                font-size:1.15rem;
                font-weight:800;
            }}

            .company-meta {{
                display:flex;
                flex-wrap:wrap;
                gap:10px;
            }}

            .chip {{
                border:1px solid var(--line);
                background:rgba(255,255,255,.85);
                color:var(--muted);
                border-radius:999px;
                padding:10px 14px;
                font-size:.9rem;
                font-weight:600;
            }}

            .chip-strong {{
                background:#eef5ff;
                color:var(--blue-1);
                border-color:#d9e7ff;
            }}

            main {{
                padding:24px 0 44px;
            }}

            .hero {{
                display:grid;
                grid-template-columns:1.2fr .95fr;
                gap:22px;
                padding:28px;
                border-radius:36px;
                background:
                    radial-gradient(circle at 20% 10%, rgba(94,167,255,.20), transparent 36%),
                    linear-gradient(135deg, rgba(255,255,255,.88), rgba(255,255,255,.68));
                border:1px solid rgba(255,255,255,.7);
                box-shadow:var(--shadow-lg);
            }}

            .hero-copy {{
                display:flex;
                flex-direction:column;
                justify-content:space-between;
                gap:22px;
            }}

            .hero-kicker {{
                display:inline-flex;
                align-items:center;
                gap:8px;
                width:max-content;
                padding:8px 12px;
                border-radius:999px;
                background:#eef5ff;
                color:var(--blue-1);
                font-size:.8rem;
                font-weight:700;
            }}

            .hero h2 {{
                margin:0;
                font-size:clamp(2rem,4vw,3.1rem);
                line-height:1.02;
                font-weight:900;
                letter-spacing:-.05em;
            }}

            .hero p {{
                margin:0;
                max-width:72ch;
                color:var(--muted);
                font-size:1.02rem;
                line-height:1.72;
            }}

            .hero-side {{
                display:grid;
                grid-template-columns:repeat(2,1fr);
                gap:14px;
            }}

            .metric-card {{
                padding:20px;
                border-radius:26px;
                background:rgba(255,255,255,.9);
                border:1px solid rgba(255,255,255,.72);
                box-shadow:var(--shadow-sm);
                min-height:164px;
                display:flex;
                flex-direction:column;
                justify-content:space-between;
            }}

            .metric-label {{
                color:var(--muted);
                font-weight:700;
                font-size:.95rem;
            }}

            .metric-value {{
                margin-top:8px;
                font-size:clamp(1.7rem,2.3vw,2.4rem);
                font-weight:900;
                letter-spacing:-.05em;
                line-height:1;
            }}

            .metric-delta {{
                display:flex;
                justify-content:space-between;
                gap:12px;
                color:var(--muted);
                font-size:.88rem;
                font-weight:600;
            }}

            .metric-primary {{
                background:linear-gradient(180deg,#ffffff,#f7fbff);
            }}

            .metric-in {{
                background:linear-gradient(180deg,#f8fcff,#f0f7ff);
            }}

            .metric-out {{
                background:linear-gradient(180deg,#fffdf8,#fff7eb);
            }}

            .metric-end {{
                background:linear-gradient(135deg, rgba(15,76,255,.95), rgba(94,167,255,.88));
                color:white;
            }}

            .metric-end .metric-label,
            .metric-end .metric-delta {{
                color:rgba(255,255,255,.82);
            }}

            .section {{
                margin-top:24px;
                border-radius:34px;
                background:rgba(255,255,255,.74);
                backdrop-filter:blur(14px);
                border:1px solid rgba(255,255,255,.7);
                box-shadow:var(--shadow-md);
                overflow:visible;
            }}

            .section-head {{
                padding:22px 22px 8px;
                display:flex;
                align-items:flex-end;
                justify-content:space-between;
                gap:16px;
                flex-wrap:wrap;
            }}

            .section-head.solo {{
                padding-bottom:0;
            }}

            .section-title {{
                margin:0;
                font-size:1.35rem;
                font-weight:900;
                letter-spacing:-.04em;
            }}

            .section-sub {{
                margin:8px 0 0;
                color:var(--muted);
                line-height:1.6;
                max-width:72ch;
            }}

            .metrics-grid {{
                display:grid;
                grid-template-columns:repeat(5,1fr);
                gap:14px;
                padding:18px 22px 6px;
            }}

            .compact-grid {{
                grid-template-columns:repeat(2,1fr);
                padding-top:0;
            }}

            .kpi {{
                padding:20px;
                border-radius:24px;
                background:var(--panel-strong);
                border:1px solid var(--line);
                box-shadow:var(--shadow-sm);
                min-height:148px;
                display:flex;
                flex-direction:column;
                justify-content:space-between;
            }}

            .kpi .label {{
                color:var(--muted);
                font-size:.92rem;
                font-weight:800;
            }}

            .kpi .amount {{
                font-size:1.72rem;
                line-height:1;
                font-weight:900;
                letter-spacing:-.05em;
                margin:10px 0 8px;
            }}

            .kpi .meta {{
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:10px;
                color:var(--muted);
                font-size:.86rem;
                font-weight:700;
            }}

            .trend {{
                display:inline-flex;
                align-items:center;
                gap:8px;
                border-radius:999px;
                padding:8px 10px;
                font-size:.78rem;
                font-weight:800;
            }}

            .trend.up {{
                background:var(--green-soft);
                color:var(--green);
            }}

            .trend.warn {{
                background:var(--yellow-soft);
                color:var(--yellow);
            }}

            .trend.down {{
                background:var(--red-soft);
                color:var(--red);
            }}

            .trend.gray {{
                background:var(--gray-soft);
                color:var(--gray);
            }}

            .story-layout {{
                display:grid;
                grid-template-columns:1.1fr .9fr;
                gap:16px;
                padding:8px 22px 22px;
            }}

            .story-card,
            .insight-card,
            .table-shell,
            .alerts-grid .alert-card,
            .author-card,
            .books-card,
            .contact-card {{
                background:var(--panel-strong);
                border:1px solid var(--line);
                box-shadow:var(--shadow-sm);
                border-radius:28px;
            }}

            .story-card,
            .insight-card {{
                padding:24px;
            }}

            .story-card h3,
            .table-head h3,
            .alerts-title {{
                margin:0 0 12px;
                font-size:1.18rem;
                font-weight:900;
            }}

            .story-card p {{
                margin:0 0 14px;
                color:var(--muted);
                line-height:1.78;
                font-size:.98rem;
            }}

            .insight-card {{
                display:flex;
                flex-direction:column;
                gap:18px;
                justify-content:space-between;
                background:
                    radial-gradient(circle at top right, rgba(94,167,255,.18), transparent 34%),
                    linear-gradient(180deg,#ffffff,#f8fbff);
            }}

            .ring {{
                width:168px;
                height:168px;
                border-radius:50%;
                margin:0 auto;
                background:
                    radial-gradient(closest-side,#fff 74%,transparent 76% 100%),
                    conic-gradient(var(--blue-1) 0 70%, #dbeafe 70% 100%);
                display:grid;
                place-items:center;
            }}

            .ring span {{
                display:flex;
                flex-direction:column;
                align-items:center;
                gap:4px;
                font-weight:900;
                font-size:1.8rem;
                letter-spacing:-.05em;
            }}

            .ring small {{
                font-size:.8rem;
                color:var(--muted);
                font-weight:800;
            }}

            .bullet-list {{
                display:grid;
                gap:12px;
            }}

            .bullet {{
                display:flex;
                align-items:flex-start;
                gap:12px;
                color:var(--muted);
                line-height:1.5;
                font-weight:600;
            }}

            .bullet::before {{
                content:"";
                width:10px;
                height:10px;
                margin-top:7px;
                border-radius:999px;
                background:linear-gradient(135deg,var(--blue-1),var(--blue-2));
                flex:none;
            }}

            .filter-toolbar {{
                display:flex;
                gap:10px;
                flex-wrap:wrap;
                padding:0 22px 8px;
            }}

            .filter-btn {{
                appearance:none;
                border:none;
                background:#eef2ff;
                color:#334155;
                padding:12px 14px;
                border-radius:999px;
                cursor:pointer;
                font-weight:800;
                font-size:.86rem;
                transition:all .18s ease;
                border:1px solid #dbe5ff;
            }}

            .filter-btn:hover {{
                transform:translateY(-1px);
                opacity:.96;
            }}

            .filter-btn.active {{
                background:#111827;
                color:#ffffff;
                border-color:#111827;
            }}

            .table-shell {{
                overflow:hidden;
                margin:18px 22px 22px;
            }}

            .table-head {{
                padding:22px 22px 10px;
                display:flex;
                justify-content:space-between;
                gap:16px;
                align-items:flex-end;
                flex-wrap:wrap;
            }}

            .table-head p {{
                margin:0;
                color:var(--muted);
                max-width:68ch;
                line-height:1.6;
            }}

            .table-wrap {{
                overflow:auto;
            }}

            table {{
                width:100%;
                border-collapse:separate;
                border-spacing:0;
                min-width:860px;
            }}

            thead th {{
                position:sticky;
                top:0;
                z-index:2;
                background:rgba(248,250,252,.96);
                text-align:left;
                font-size:.85rem;
                font-weight:900;
                color:var(--muted);
                padding:16px 18px;
                border-bottom:1px solid var(--line);
            }}

            tbody td {{
                padding:16px 18px;
                border-bottom:1px solid rgba(148,163,184,.14);
                font-size:.95rem;
                color:#1e293b;
                vertical-align:middle;
                line-height:1.55;
            }}

            .row-entrada td {{
                background:linear-gradient(180deg, rgba(236,253,243,.55), rgba(255,255,255,.88));
                border-bottom-color:var(--green-line);
            }}

            .row-salida td {{
                background:linear-gradient(180deg, rgba(254,242,242,.55), rgba(255,255,255,.88));
                border-bottom-color:var(--red-line);
            }}

            .mono {{
                font-variant-numeric:tabular-nums;
                font-feature-settings:'tnum';
                white-space:nowrap;
                font-weight:800;
            }}

            .amounts-cell {{
                line-height:1.9;
                word-break:break-word;
                white-space:normal;
                color:#334155;
            }}

            .alerts-grid {{
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:14px;
                padding:0 22px 22px;
            }}

            .alert-card {{
                padding:22px;
                min-height:220px;
            }}

            .alert-tag {{
                display:inline-flex;
                padding:8px 12px;
                border-radius:999px;
                font-size:.78rem;
                font-weight:900;
                margin-bottom:14px;
            }}

            .alert-card.green {{
                background:linear-gradient(180deg,#ffffff,#f3fdf7);
            }}

            .alert-card.yellow {{
                background:linear-gradient(180deg,#ffffff,#fffaf0);
            }}

            .alert-card.red {{
                background:linear-gradient(180deg,#ffffff,#fff4f4);
            }}

            .alert-card.green .alert-tag {{
                background:var(--green-soft);
                color:var(--green);
            }}

            .alert-card.yellow .alert-tag {{
                background:var(--yellow-soft);
                color:var(--yellow);
            }}

            .alert-card.red .alert-tag {{
                background:var(--red-soft);
                color:var(--red);
            }}

            .alert-card h4 {{
                margin:0 0 10px;
                font-size:1.08rem;
                font-weight:900;
            }}

            .alert-card p {{
                margin:0;
                color:var(--muted);
                line-height:1.68;
                font-weight:600;
            }}

            .badge {{
                display:inline-flex;
                align-items:center;
                gap:8px;
                padding:8px 12px;
                border-radius:999px;
                font-size:.78rem;
                font-weight:900;
                white-space:nowrap;
                border:1px solid transparent;
                text-transform:none;
            }}

            .badge::before {{
                content:"";
                width:8px;
                height:8px;
                border-radius:999px;
                background:currentColor;
            }}

            .badge-green {{
                color:var(--green);
                background:var(--green-soft);
            }}

            .badge-yellow {{
                color:var(--yellow);
                background:var(--yellow-soft);
            }}

            .badge-red {{
                color:var(--red);
                background:var(--red-soft);
            }}

            .badge-gray {{
                color:var(--gray);
                background:var(--gray-soft);
            }}

            .mobile-doc-grid,
            .mobile-amount-grid,
            .mobile-movements-block,
            .mobile-conc-grid {{
                display:none;
            }}

            .mobile-doc-card,
            .mobile-amount-card,
            .mobile-movement-card,
            .mobile-conc-card {{
                background:#ffffff;
                border:1px solid var(--line);
                border-radius:22px;
                padding:16px;
                box-shadow:var(--shadow-sm);
            }}

            .mobile-doc-title,
            .mobile-block-title {{
                font-size:1rem;
                font-weight:900;
                color:var(--text);
                margin-bottom:12px;
            }}

            .mobile-meta-row {{
                display:flex;
                justify-content:space-between;
                gap:12px;
                padding:8px 0;
                border-bottom:1px dashed rgba(148,163,184,.25);
            }}

            .mobile-meta-row:last-child {{
                border-bottom:none;
            }}

            .mobile-label {{
                color:var(--muted);
                font-weight:700;
                flex-shrink:0;
            }}

            .mobile-amount {{
                font-weight:900;
                font-size:1rem;
            }}

            .mobile-description,
            .mobile-amount-list {{
                margin-top:12px;
                color:#334155;
                line-height:1.75;
                word-break:break-word;
            }}

            .mobile-movements-grid,
            .mobile-doc-grid,
            .mobile-amount-grid,
            .mobile-conc-grid {{
                gap:14px;
                padding:0 16px 16px;
            }}

            .mobile-movement-card.row-entrada {{
                background:linear-gradient(180deg, rgba(236,253,243,.70), #ffffff);
            }}

            .mobile-movement-card.row-salida {{
                background:linear-gradient(180deg, rgba(254,242,242,.70), #ffffff);
            }}

            .mobile-movement-head,
            .mobile-conc-head {{
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:12px;
                margin-bottom:12px;
            }}

            .author-card,
            .books-card,
            .contact-card {{
                margin:18px 22px 22px;
                padding:22px;
            }}

            .author-card-inner {{
                display:flex;
                gap:20px;
                align-items:flex-start;
                flex-wrap:wrap;
            }}

            .author-photo {{
                width:108px;
                height:108px;
                border-radius:999px;
                object-fit:cover;
                flex-shrink:0;
                box-shadow:0 10px 24px rgba(0,0,0,.12);
            }}

            .author-copy {{
                flex:1;
                min-width:280px;
            }}

            .author-name {{
                font-size:1.35rem;
                font-weight:900;
                margin-bottom:10px;
            }}

            .author-subtitle {{
                font-size:1rem;
                line-height:1.7;
                color:#374151;
                margin-bottom:12px;
            }}

            .author-description {{
                font-size:1rem;
                line-height:1.7;
                color:#4b5563;
            }}

            .book-item {{
                display:grid;
                grid-template-columns:96px minmax(0, 1fr);
                gap:16px;
                align-items:start;
                padding:16px 0;
                border-bottom:1px solid rgba(148,163,184,.14);
            }}

            .book-item:last-child {{
                border-bottom:none;
                padding-bottom:0;
            }}

            .book-cover {{
                width:96px;
                height:144px;
                object-fit:cover;
                border-radius:12px;
                display:block;
                box-shadow:0 8px 20px rgba(0,0,0,.14);
            }}

            .book-copy {{
                display:flex;
                flex-direction:column;
                gap:10px;
                min-width:0;
            }}

            .book-title {{
                font-weight:900;
                line-height:1.5;
                word-break:break-word;
            }}

            .book-link {{
                color:#1d4ed8;
                text-decoration:none;
                font-weight:800;
                width:max-content;
                max-width:100%;
            }}

            .contact-card {{
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:18px;
                flex-wrap:wrap;
            }}

            .contact-title {{
                font-size:1.2rem;
                font-weight:900;
                margin-bottom:8px;
            }}

            .contact-subtitle {{
                color:var(--muted);
                line-height:1.6;
                max-width:64ch;
            }}

            .cta-button {{
                display:inline-flex;
                align-items:center;
                justify-content:center;
                background:#111827;
                color:white;
                padding:14px 22px;
                border-radius:12px;
                text-decoration:none;
                font-weight:800;
                box-shadow:0 10px 24px rgba(17,24,39,.16);
            }}

            .empty-state {{
                margin:18px 22px 22px;
                padding:22px;
                border-radius:22px;
                background:#fff;
                border:1px solid var(--line);
                color:var(--muted);
                box-shadow:var(--shadow-sm);
            }}

            .footer-card {{
                display:flex;
                justify-content:space-between;
                gap:18px;
                align-items:center;
                padding:18px 22px;
                border-radius:24px;
                background:rgba(255,255,255,.72);
                border:1px solid rgba(255,255,255,.74);
                box-shadow:var(--shadow-sm);
                color:var(--muted);
                flex-wrap:wrap;
                margin:26px 0 20px;
            }}

            .footer-card strong {{
                color:var(--text);
            }}

            .footer-right {{
                display:flex;
                align-items:center;
                gap:10px;
                flex-wrap:wrap;
            }}

            .footer-pill {{
                padding:9px 12px;
                border-radius:999px;
                background:rgba(255,255,255,.85);
                border:1px solid var(--line);
                font-weight:800;
                font-size:.82rem;
                color:var(--muted);
            }}

            .footer-actions {{
                display:flex;
                flex-direction:column;
                gap:16px;
                align-items:center;
                margin:0 0 10px;
            }}

            .footer-note {{
                color:var(--muted);
                font-size:.92rem;
                text-align:center;
                line-height:1.6;
                max-width:760px;
            }}

            .actions-bar {{
                display:flex;
                justify-content:center;
                align-items:center;
                gap:14px;
                flex-wrap:wrap;
                width:100%;
            }}

            .btn-ghost {{
                display:inline-flex;
                align-items:center;
                justify-content:center;
                min-width:180px;
                padding:14px 22px;
                border-radius:12px;
                text-decoration:none;
                font-weight:800;
                font-size:.95rem;
                background:rgba(255,255,255,.9);
                color:var(--text);
                border:1px solid var(--line);
                box-shadow:var(--shadow-sm);
            }}

            .btn-ghost:hover,
            .cta-button:hover,
            .book-link:hover {{
                transform:translateY(-1px);
                opacity:.96;
            }}

            .is-hidden {{
                display:none !important;
            }}

            @media (max-width:1180px) {{
                .hero,
                .story-layout {{
                    grid-template-columns:1fr;
                }}

                .metrics-grid {{
                    grid-template-columns:repeat(3,1fr);
                }}

                .alerts-grid {{
                    grid-template-columns:1fr;
                }}
            }}

            @media (max-width:900px) {{
                .metrics-grid {{
                    grid-template-columns:1fr 1fr;
                }}

                .compact-grid {{
                    grid-template-columns:1fr 1fr;
                }}
            }}

            @media (max-width:820px) {{
                .hero-side {{
                    grid-template-columns:1fr;
                }}
            }}

            @media (max-width:760px) {{
                .table-wrap {{
                    display:none;
                }}

                .mobile-doc-grid,
                .mobile-amount-grid,
                .mobile-conc-grid {{
                    display:grid;
                }}

                .mobile-movements-block {{
                    display:block;
                }}

                .filter-toolbar {{
                    padding:0 16px 10px;
                    overflow:auto;
                    flex-wrap:nowrap;
                }}

                .filter-btn {{
                    white-space:nowrap;
                    flex:0 0 auto;
                }}
            }}

            @media (max-width:640px) {{
                .wrap {{
                    width:min(calc(100% - 16px), var(--max));
                }}

                .topbar {{
                    padding:16px;
                    border-radius:20px;
                }}

                .hero {{
                    padding:20px;
                    border-radius:28px;
                }}

                .section {{
                    border-radius:26px;
                }}

                .section-head {{
                    padding:18px 16px 6px;
                }}

                .table-shell,
                .author-card,
                .books-card,
                .contact-card,
                .empty-state {{
                    margin:16px;
                    padding:16px;
                }}

                .story-layout {{
                    padding:8px 16px 16px;
                }}

                .metrics-grid {{
                    grid-template-columns:1fr;
                    padding:16px 16px 4px;
                }}

                .compact-grid {{
                    grid-template-columns:1fr;
                }}

                .alerts-grid {{
                    padding:0 16px 16px;
                }}

                .book-item {{
                    grid-template-columns:1fr;
                    justify-items:center;
                    text-align:center;
                    gap:14px;
                }}

                .book-cover {{
                    width:128px;
                    height:192px;
                }}

                .book-copy {{
                    align-items:center;
                }}

                .book-link {{
                    width:100%;
                    text-align:center;
                }}

                .author-card-inner {{
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    text-align:center;
                    gap:18px;
                }}

                .author-copy {{
                    min-width:0;
                    width:100%;
                    max-width:100%;
                }}

                .author-name {{
                    font-size:1.9rem;
                    line-height:1.15;
                    margin-bottom:12px;
                }}

                .author-subtitle,
                .author-description {{
                    width:100%;
                    max-width:100%;
                    text-align:center;
                    word-break:normal;
                    overflow-wrap:break-word;
                    line-height:1.7;
                }}

                .contact-card {{
                    text-align:center;
                    justify-content:center;
                }}

                .cta-button,
                .btn-ghost {{
                    width:100%;
                    min-width:0;
                }}

                .footer-card {{
                    margin:22px 0 16px;
                    padding:16px;
                    justify-content:center;
                    text-align:center;
                }}

                .footer-right {{
                    justify-content:center;
                }}

                .books-section,
                .books-card {{
                    display:block !important;
                    visibility:visible !important;
                    opacity:1 !important;
                }}
            }}

            @media (max-width:560px) {{
                .metrics-grid {{
                    grid-template-columns:1fr;
                }}

                .company-meta {{
                    gap:8px;
                }}

                .chip {{
                    font-size:.82rem;
                    padding:9px 12px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="topbar-shell">
                <header class="topbar">
                    <div class="brand">
                        <div class="eyebrow">PYME Financial Analyzer</div>
                        <h1>Informe financiero ejecutivo</h1>
                    </div>
                    <div class="company-meta">
                        <div class="chip">Archivos analizados: {total}</div>
                        <div class="chip">Documentos clasificados: {total_docs_clasificados}</div>
                        <div class="chip chip-strong">{texto_calidad_cierre(conc["nivel_cierre"])}</div>
                    </div>
                </header>
            </div>

            <main>
                <section class="hero">
                    <div class="hero-copy">
                        <div>
                            <div class="hero-kicker">Lectura ejecutiva del período</div>
                            <h2>{titular_ejecutivo}</h2>
                        </div>
                        <p>{narrativa_ejecutiva}</p>
                    </div>

                    <div class="hero-side">
                        <article class="metric-card metric-primary">
                            <div>
                                <div class="metric-label">Saldo inicial</div>
                                <div class="metric-value">€ {fmt(flujo["saldo_inicial"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Inicio del período</span>
                                <span>Caja</span>
                            </div>
                        </article>

                        <article class="metric-card metric-in">
                            <div>
                                <div class="metric-label">Entradas</div>
                                <div class="metric-value">€ {fmt(flujo["entradas"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Dinero que entró</span>
                                <span>Período</span>
                            </div>
                        </article>

                        <article class="metric-card metric-out">
                            <div>
                                <div class="metric-label">Salidas</div>
                                <div class="metric-value">€ {fmt(flujo["salidas"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Dinero que salió</span>
                                <span>Período</span>
                            </div>
                        </article>

                        <article class="metric-card metric-end">
                            <div>
                                <div class="metric-label">Saldo final</div>
                                <div class="metric-value">€ {fmt(flujo["saldo_final"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Variación: € {fmt(flujo["variacion"])}</span>
                                <span>Cierre</span>
                            </div>
                        </article>
                    </div>
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Resumen ejecutivo</h3>
                            <p class="section-sub">Vista sintética del flujo, la calidad del cierre y los principales puntos de atención para la gestión del negocio.</p>
                        </div>
                    </div>

                    <div class="metrics-grid">
                        <article class="kpi">
                            <div class="label">Movimiento del período</div>
                            <div class="amount">€ {fmt(flujo["movimientos"])}</div>
                            <div class="meta"><span class="trend up">Actividad</span><span>Caja</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Retenido</div>
                            <div class="amount">€ {fmt(flujo["retenido"])}</div>
                            <div class="meta"><span class="trend warn">Liquidez</span><span>Bloqueada</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Facturas conciliadas</div>
                            <div class="amount">{conc["conciliadas"]}</div>
                            <div class="meta"><span class="trend up">Correcto</span><span>Exactas</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Facturas pendientes</div>
                            <div class="amount">{conc["pendientes"]}</div>
                            <div class="meta"><span class="trend down">Seguimiento</span><span>Documental</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Movimientos sin soporte</div>
                            <div class="amount">{conc.get("sin_soporte", 0)}</div>
                            <div class="meta"><span class="trend down">Banco</span><span>Revisar</span></div>
                        </article>
                    </div>

                    <div class="story-layout">
                        <article class="story-card">
                            <h3>Qué muestra este informe</h3>
                            <p>Este informe resume qué ocurrió con la caja durante el período, qué documentos fueron reconocidos, qué facturas quedaron conciliadas y qué movimientos todavía requieren revisión adicional.</p>
                            <p>En esta ejecución, el saldo inicial fue de € {fmt(flujo["saldo_inicial"])}, las entradas alcanzan € {fmt(flujo["entradas"])}, las salidas € {fmt(flujo["salidas"])} y el saldo final queda en € {fmt(flujo["saldo_final"])}, con una variación neta de € {fmt(flujo["variacion"])}.</p>
                            <p>Además, se observan {conc.get("sin_soporte", 0)} {pluralizar(conc.get("sin_soporte", 0), "movimiento relevante sin soporte", "movimientos relevantes sin soporte")}, {conc.get("movimientos_internos", 0)} {pluralizar(conc.get("movimientos_internos", 0), "movimiento interno", "movimientos internos")}, {conc.get("pendientes", 0)} {pluralizar(conc.get("pendientes", 0), "factura pendiente", "facturas pendientes")} y {conc.get("duplicados", 0)} {pluralizar(conc.get("duplicados", 0), "duplicado potencial", "duplicados potenciales")}.</p>
                        </article>

                        <aside class="insight-card">
                            <div>
                                <h3 style="margin:0 0 18px;font-size:1.18rem;font-weight:900;">Calidad preliminar del cierre</h3>
                                <div class="ring">
                                    <span>{0 if total == 0 else min(100, round((total_docs_clasificados / total) * 100))}%<small>documentos clasificados</small></span>
                                </div>
                            </div>
                            <div class="bullet-list">
                                <div class="bullet">Facturas de venta: {docs["factura_venta"]}</div>
                                <div class="bullet">Facturas de compra: {docs["factura_compra"]}</div>
                                <div class="bullet">Extractos bancarios: {docs["extracto_bancario"]}</div>
                                <div class="bullet">Otros documentos: {docs["otros"]}</div>
                                <div class="bullet">{texto_calidad_cierre(conc["nivel_cierre"])}</div>
                            </div>
                        </aside>
                    </div>

                    <section class="alerts-grid">
                        <article class="alert-card green">
                            <div class="alert-tag">Bien</div>
                            <h4>Información estructurada</h4>
                            <p>La documentación ya está organizada en un formato útil para lectura gerencial y revisión financiera.</p>
                        </article>

                        <article class="alert-card yellow">
                            <div class="alert-tag">Revisar</div>
                            <h4>Validaciones pendientes</h4>
                            <p>Se observan {conc["pendientes"]} {pluralizar(conc["pendientes"], "factura pendiente", "facturas pendientes")}, € {fmt(conc["importe_pendiente"])} por validar y {conc.get("movimientos_internos", 0)} {pluralizar(conc.get("movimientos_internos", 0), "movimiento interno", "movimientos internos")}.</p>
                        </article>

                        <article class="alert-card red">
                            <div class="alert-tag">Atención</div>
                            <h4>Movimientos sin soporte</h4>
                            <p>Se detectan {conc.get("sin_soporte", 0)} {pluralizar(conc.get("sin_soporte", 0), "movimiento relevante sin soporte documental", "movimientos relevantes sin soporte documental")} y {conc.get("sin_soporte_menor", 0)} {pluralizar(conc.get("sin_soporte_menor", 0), "movimiento menor sin soporte directo", "movimientos menores sin soporte directo")}.</p>
                        </article>
                    </section>
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Documentos y montos identificados</h3>
                            <p class="section-sub">Visibilidad estructurada sobre los documentos reconocidos por el sistema y los montos extraídos automáticamente durante el procesamiento.</p>
                        </div>
                    </div>
                    {documentos_html()}
                    {importes_html()}
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Movimientos bancarios relevantes</h3>
                            <p class="section-sub">Primero se muestran las entradas y salidas relevantes. Los movimientos menores al umbral se agrupan aparte para no ensuciar la lectura ejecutiva.</p>
                        </div>
                    </div>
                    <div class="filter-toolbar">
                        {construir_botones_filtro()}
                    </div>
                    {tabla_movimientos_relevantes_html()}
                    {bloque_movimientos_menores_html()}
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Ledger base</h3>
                            <p class="section-sub">Trazabilidad preliminar del flujo de caja construida a partir del ledger generado automáticamente.</p>
                        </div>
                    </div>
                    {tabla_ledger_html()}
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Conciliación</h3>
                            <p class="section-sub">Resumen de coincidencias, pendientes, movimientos sin soporte y diferencias detectadas entre documentos y movimientos bancarios.</p>
                        </div>
                    </div>

                    <div class="metrics-grid">
                        <article class="kpi">
                            <div class="label">Facturas conciliadas exactas</div>
                            <div class="amount">{conc["conciliadas"]}</div>
                            <div class="meta"><span class="trend up">Correcto</span><span>Estado</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Conciliadas exactas múltiples</div>
                            <div class="amount">{conc.get("conciliadas_multi", 0)}</div>
                            <div class="meta"><span class="trend up">Correcto</span><span>Múltiples movimientos</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Conciliadas probables</div>
                            <div class="amount">{conc["parciales"]}</div>
                            <div class="meta"><span class="trend warn">Revisión</span><span>Estado</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Conciliadas probables múltiples</div>
                            <div class="amount">{conc.get("probables_multi", 0)}</div>
                            <div class="meta"><span class="trend gray">Validar</span><span>Múltiples movimientos</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Facturas pendientes</div>
                            <div class="amount">{conc["pendientes"]}</div>
                            <div class="meta"><span class="trend down">Pendiente</span><span>Facturas</span></div>
                        </article>
                    </div>

                    <div class="metrics-grid">
                        <article class="kpi">
                            <div class="label">Sin soporte</div>
                            <div class="amount">{conc.get("sin_soporte", 0)}</div>
                            <div class="meta"><span class="trend down">Banco</span><span>Revisar</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Sin soporte menor</div>
                            <div class="amount">{conc.get("sin_soporte_menor", 0)}</div>
                            <div class="meta"><span class="trend warn">Banco</span><span>Menor</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">No conciliables</div>
                            <div class="amount">{conc.get("no_conciliables", 0)}</div>
                            <div class="meta"><span class="trend gray">Banco</span><span>Informativo</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Duplicados potenciales</div>
                            <div class="amount">{conc.get("duplicados", 0)}</div>
                            <div class="meta"><span class="trend warn">Revisar</span><span>Banco</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Movimientos internos</div>
                            <div class="amount">{conc.get("movimientos_internos", 0)}</div>
                            <div class="meta"><span class="trend gray">Informativo</span><span>Banco</span></div>
                        </article>
                    </div>

                    <div class="metrics-grid compact-grid">
                        <article class="kpi">
                            <div class="label">Pendiente de cobro</div>
                            <div class="amount">€ {fmt(conc["pendiente_cobro"])}</div>
                            <div class="meta"><span class="trend warn">Ventas</span><span>Seguimiento</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Pendiente de pago</div>
                            <div class="amount">€ {fmt(conc["pendiente_pago"])}</div>
                            <div class="meta"><span class="trend warn">Compras</span><span>Seguimiento</span></div>
                        </article>
                    </div>

                    {tabla_conciliacion_html()}
                </section>

                {bloque_branding_html()}

                <footer>
                    <div class="footer-card">
                        <div>
                            <strong>PYME Financial Analyzer</strong> · Informe visual para revisión ejecutiva, control documental y lectura preliminar de caja.
                        </div>
                        <div class="footer-right">
                            <span class="footer-pill">Archivos: {total}</span>
                            <span class="footer-pill">Clasificados: {total_docs_clasificados}</span>
                            <span class="footer-pill">{texto_calidad_cierre(conc["nivel_cierre"])}</span>
                        </div>
                    </div>

                    <div class="footer-actions">
                        <div class="footer-note">
                            Informe preliminar automático generado a partir de documentos cargados por el usuario.
                        </div>
                        <div class="actions-bar">
                            <a href="/" class="btn-ghost">← Volver</a>
                        </div>
                    </div>
                </footer>
            </main>
        </div>

        <script>
            (function() {{
                function applyFilter(value) {{
                    const allRows = document.querySelectorAll("[data-kind]");
                    const buttons = document.querySelectorAll(".filter-btn");

                    buttons.forEach(btn => {{
                        if (btn.getAttribute("data-filter") === value) {{
                            btn.classList.add("active");
                        }} else {{
                            btn.classList.remove("active");
                        }}
                    }});

                    allRows.forEach(el => {{
                        const kinds = (el.getAttribute("data-kind") || "").split(" ").filter(Boolean);
                        if (value === "all" || kinds.includes(value)) {{
                            el.classList.remove("is-hidden");
                        }} else {{
                            el.classList.add("is-hidden");
                        }}
                    }});
                }}

                document.querySelectorAll(".filter-btn").forEach(btn => {{
                    btn.addEventListener("click", function() {{
                        const value = this.getAttribute("data-filter") || "all";
                        applyFilter(value);
                    }});
                }});

                applyFilter("all");
            }})();
        </script>
    </body>
    </html>
    """

    return html
