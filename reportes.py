from branding import BRANDING
import re


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
        "otros_cobros": "Otros ingresos",
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

            entradas = 0.0
            entradas += abs(resumen.get("pagos_recibidos") or 0.0)
            entradas += abs(resumen.get("depositos_y_creditos") or 0.0)
            entradas += abs(resumen.get("liberaciones") or 0.0)

            salidas = 0.0
            salidas += abs(resumen.get("pagos_enviados") or 0.0)
            salidas += abs(resumen.get("retiradas_y_cargos") or 0.0)
            salidas += abs(resumen.get("tarifas") or 0.0)
            salidas += abs(resumen.get("retenido") or 0.0)

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

    entradas_resumen = None
    salidas_resumen = None

    for item in ledger:
        if item.get("tipo") == "extracto_resumen":
            resumen = item.get("resumen_extracto", {}) or {}

            entradas_resumen = 0.0
            entradas_resumen += abs(resumen.get("pagos_recibidos") or 0.0)
            entradas_resumen += abs(resumen.get("depositos_y_creditos") or 0.0)
            entradas_resumen += abs(resumen.get("liberaciones") or 0.0)

            salidas_resumen = 0.0
            salidas_resumen += abs(resumen.get("pagos_enviados") or 0.0)
            salidas_resumen += abs(resumen.get("retiradas_y_cargos") or 0.0)
            salidas_resumen += abs(resumen.get("tarifas") or 0.0)
            salidas_resumen += abs(resumen.get("retenido") or 0.0)
            break

    entradas_identificadas = 0.0
    salidas_identificadas = 0.0
    otros_cobros_cantidad_real = 0
    otros_pagos_cantidad_real = 0

    for item in ledger:
        if item.get("tipo") != "extracto_bancario":
            continue

        categoria = (item.get("categoria") or "").strip().lower()
        valor = item.get("importe_firmado_num")

        if valor is None:
            valor = normalizar_importe_reporte(item.get("importe", 0))
            if item.get("naturaleza") == "salida":
                valor = -abs(valor)

        if valor is None:
            continue

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

        es_agrupado = categoria in ["otros_cobros", "otros_pagos"]

        if es_agrupado:
            desc = item.get("descripcion", "")
            try:
                cantidad = int(str(desc).split()[0])
            except Exception:
                cantidad = 1

            if valor >= 0:
                otros_cobros_cantidad_real += cantidad
            else:
                otros_pagos_cantidad_real += cantidad

            continue

        if abs(valor) >= umbral_relevante:
            if valor >= 0:
                entradas_relevantes.append(fila)
                entradas_identificadas += abs(valor)
            else:
                salidas_relevantes.append(fila)
                salidas_identificadas += abs(valor)
        else:
            if valor >= 0:
                otros_cobros_cantidad_real += 1
            else:
                otros_pagos_cantidad_real += 1

    if entradas_resumen is not None:
        otros_cobros_total = max(0.0, round(entradas_resumen - entradas_identificadas, 2))
    else:
        otros_cobros_total = 0.0
        for item in ledger:
            if item.get("tipo") != "extracto_bancario":
                continue
            valor = item.get("importe_firmado_num")
            if valor is None:
                valor = normalizar_importe_reporte(item.get("importe", 0))
                if item.get("naturaleza") == "salida":
                    valor = -abs(valor)
            if valor is None:
                continue
            if valor > 0 and abs(valor) < umbral_relevante:
                otros_cobros_total += abs(valor)

    if salidas_resumen is not None:
        otros_pagos_total = max(0.0, round(salidas_resumen - salidas_identificadas, 2))
    else:
        otros_pagos_total = 0.0
        for item in ledger:
            if item.get("tipo") != "extracto_bancario":
                continue
            valor = item.get("importe_firmado_num")
            if valor is None:
                valor = normalizar_importe_reporte(item.get("importe", 0))
                if item.get("naturaleza") == "salida":
                    valor = -abs(valor)
            if valor is None:
                continue
            if valor < 0 and abs(valor) < umbral_relevante:
                otros_pagos_total += abs(valor)

    if otros_cobros_total > 0:
        entradas_relevantes.insert(0, {
            "archivo": "-",
            "fecha": entradas_relevantes[0]["fecha"] if entradas_relevantes else "-",
            "importe_abs": otros_cobros_total,
            "importe_fmt": fmt_importe_reporte(otros_cobros_total),
            "naturaleza": "entrada",
            "naturaleza_humana": "Entrada",
            "descripcion": f"{otros_cobros_cantidad_real} movimientos menores agrupados",
            "categoria": "otros_cobros",
            "categoria_humana": "Otros ingresos",
            "moneda": "",
            "clase_fila": "row-entrada",
        })

    if otros_pagos_total > 0:
        salidas_relevantes.insert(0, {
            "archivo": "-",
            "fecha": salidas_relevantes[0]["fecha"] if salidas_relevantes else "-",
            "importe_abs": otros_pagos_total,
            "importe_fmt": fmt_importe_reporte(otros_pagos_total),
            "naturaleza": "salida",
            "naturaleza_humana": "Salida",
            "descripcion": f"{otros_pagos_cantidad_real} movimientos menores agrupados",
            "categoria": "otros_pagos",
            "categoria_humana": "Otros pagos",
            "moneda": "",
            "clase_fila": "row-salida",
        })

    entradas_relevantes.sort(key=lambda x: (x["fecha"], -x["importe_abs"]))
    salidas_relevantes.sort(key=lambda x: (x["fecha"], -x["importe_abs"]))

    return {
        "entradas_relevantes": entradas_relevantes,
        "salidas_relevantes": salidas_relevantes,
        "otros_cobros_cantidad": otros_cobros_cantidad_real,
        "otros_cobros_total": otros_cobros_total,
        "otros_pagos_cantidad": otros_pagos_cantidad_real,
        "otros_pagos_total": otros_pagos_total,
    }
def inferir_nombre_empresa(documentos, ledger):
    documentos = documentos or []

    def limpiar(texto):
        texto = (texto or "").strip()
        texto = re.sub(r"\([^)]*\)", "", texto)
        texto = re.sub(r"\s+", " ", texto).strip(" .,:;_-")
        return texto

    def es_nombre_valido(texto):
        if not texto:
            return False

        t = texto.lower().strip()

        bloqueados = [
            "extracto", "statement", "factura", "invoice", "resumen", "saldo",
            "fecha", "periodo", "período", "movimiento", "movimientos",
            "documento", "documentos", "cliente", "proveedor", "concepto",
            "descripcion", "descripción", "iban", "swift", "bic", "cuenta",
            "payment", "transfer", "transferencia"
        ]
        if any(b in t for b in bloqueados):
            return False

        if len(texto) < 3 or len(texto) > 80:
            return False

        if re.search(r"\d{4,}", texto):
            return False

        if not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", texto):
            return False

        return True

    # 1) PRIORIDAD ABSOLUTA: extracto bancario
    for item in documentos:
        if item.get("tipo") != "extracto_bancario":
            continue

        texto = (item.get("texto") or "").strip()
        if not texto:
            continue

        patrones = [
            r"(?im)^\s*raz[oó]n social\s*[:\-]\s*(.+?)\s*$",
            r"(?im)^\s*nombre\s+del\s+titular\s*[:\-]\s*(.+?)\s*$",
            r"(?im)^\s*titular\s*[:\-]\s*(.+?)\s*$",
            r"(?im)^\s*account holder\s*[:\-]\s*(.+?)\s*$",
            r"(?im)^\s*business name\s*[:\-]\s*(.+?)\s*$",
            r"(?im)^\s*empresa\s*[:\-]\s*(.+?)\s*$",
        ]

        for patron in patrones:
            m = re.search(patron, texto)
            if m:
                candidato = limpiar(m.group(1))
                if es_nombre_valido(candidato):
                    return candidato[:1].upper() + candidato[1:]

        # fallback: primeras líneas útiles del extracto
        for linea in texto.splitlines()[:25]:
            linea = limpiar(linea)
            if es_nombre_valido(linea):
                return linea[:1].upper() + linea[1:]

    # 2) Si no está claro en el extracto, no inventar
    return "la empresa"
    
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

    bloque_flujo = (
        f"El saldo inicial fue de € {fmt_importe_reporte(saldo_inicial)}, "
        f"entraron € {fmt_importe_reporte(entradas)}, "
        f"salieron € {fmt_importe_reporte(salidas)} "
        f"y el saldo final se ubicó en € {fmt_importe_reporte(saldo_final)}, "
        f"con una variación neta de € {fmt_importe_reporte(variacion)}."
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
        bloque_cierre = f" El cierre todavía no puede considerarse definitivo: persisten {detalle}."
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
        bloque_cierre = f" La lectura es útil, pero todavía requiere validación adicional: se observan {detalle}."
    elif sin_soporte > 0:
        bloque_cierre = (
            f" No se observan pendientes fuertes de conciliación, pero existen "
            f"{sin_soporte} {pluralizar(sin_soporte, 'movimiento relevante sin soporte documental', 'movimientos relevantes sin soporte documental')}."
        )
    elif sin_soporte_menor > 0:
        bloque_cierre = (
            f" No se observan pendientes relevantes, aunque existen "
            f"{sin_soporte_menor} {pluralizar(sin_soporte_menor, 'movimiento menor sin soporte directo', 'movimientos menores sin soporte directo')}."
        )
    else:
        bloque_cierre = " No se observan pendientes relevantes de conciliación en la estructura analizada."

    resumen_docs = (
        f"Durante el análisis se procesaron {total} {pluralizar(total, 'archivo')}: "
        f"{docs['factura_venta']} {pluralizar(docs['factura_venta'], 'factura de venta')}, "
        f"{docs['factura_compra']} {pluralizar(docs['factura_compra'], 'factura de compra')}, "
        f"{docs['extracto_bancario']} {pluralizar(docs['extracto_bancario'], 'extracto bancario')} "
        f"y {docs['otros']} {pluralizar(docs['otros'], 'documento', 'documentos')} adicional(es)."
    )

    narrativa = f"{bloque_flujo}{bloque_cierre} {resumen_docs}"

    return titular, narrativa


def calcular_score_financiero(flujo, conc):
    score = 100

    score -= conc.get("pendientes", 0) * 12
    score -= conc.get("sin_soporte", 0) * 8
    score -= conc.get("duplicados", 0) * 6
    score -= conc.get("parciales", 0) * 5
    score -= conc.get("probables_multi", 0) * 7
    score -= conc.get("movimientos_bancarios_no_conciliables", 0) * 3
    score -= conc.get("movimientos_internos", 0) * 1

    if flujo.get("variacion", 0) < 0:
        score -= 8

    return max(min(score, 100), 0)


def texto_score_financiero(score):
    if score >= 85:
        return "Muy sólido"
    if score >= 70:
        return "Sólido"
    if score >= 55:
        return "Aceptable"
    if score >= 40:
        return "Frágil"
    return "Crítico"


def generar_diagnostico_financiero(flujo, conc):
    diagnosticos = []

    if flujo.get("variacion", 0) > 0:
        diagnosticos.append(
            f"La caja mejoró en el período, con una variación positiva de € {fmt_importe_reporte(flujo.get('variacion', 0))}."
        )
    elif flujo.get("variacion", 0) < 0:
        diagnosticos.append(
            f"La caja se deterioró en el período, con una variación negativa de € {fmt_importe_reporte(abs(flujo.get('variacion', 0)))}."
        )
    else:
        diagnosticos.append("La caja cerró prácticamente al mismo nivel con el que empezó el período.")

    if conc.get("pendientes", 0) > 0:
        diagnosticos.append(
            f"Persisten {conc.get('pendientes', 0)} {pluralizar(conc.get('pendientes', 0), 'factura pendiente', 'facturas pendientes')}, "
            f"con € {fmt_importe_reporte(conc.get('importe_pendiente', 0))} todavía por validar o cerrar."
        )

    if conc.get("sin_soporte", 0) > 0:
        diagnosticos.append(
            f"Se identificaron {conc.get('sin_soporte', 0)} {pluralizar(conc.get('sin_soporte', 0), 'movimiento relevante sin soporte', 'movimientos relevantes sin soporte')}, "
            "lo que reduce la confiabilidad del cierre."
        )

    if conc.get("movimientos_internos", 0) > 0:
        diagnosticos.append(
            f"Hay {conc.get('movimientos_internos', 0)} {pluralizar(conc.get('movimientos_internos', 0), 'movimiento interno', 'movimientos internos')} "
            "que no deben confundirse con gasto comercial."
        )

    if not diagnosticos:
        diagnosticos.append("No se detectan alertas materiales en la lectura preliminar del período.")

    return diagnosticos[:5]


def generar_recomendaciones_financieras(flujo, conc):
    recomendaciones = []

    if conc.get("pendiente_cobro", 0) > 0:
        recomendaciones.append(
            f"Priorizar el cobro de facturas pendientes por € {fmt_importe_reporte(conc.get('pendiente_cobro', 0))}."
        )

    if conc.get("pendiente_pago", 0) > 0:
        recomendaciones.append(
            f"Verificar el calendario de pago de compras pendientes por € {fmt_importe_reporte(conc.get('pendiente_pago', 0))}."
        )

    if conc.get("sin_soporte", 0) > 0:
        recomendaciones.append(
            "Solicitar o localizar soporte documental de los movimientos relevantes detectados en banco."
        )

    if conc.get("movimientos_internos", 0) > 0:
        recomendaciones.append(
            "Separar formalmente los retiros propios y movimientos internos del gasto operativo del negocio."
        )

    if flujo.get("variacion", 0) < 0:
        recomendaciones.append(
            "Revisar el ritmo de salidas frente a entradas para evitar presión adicional sobre la liquidez."
        )

    if conc.get("duplicados", 0) > 0:
        recomendaciones.append(
            "Revisar inmediatamente los posibles duplicados antes de cerrar el período."
        )

    if not recomendaciones:
        recomendaciones.append("Mantener el control documental y repetir este cierre con periodicidad mensual.")

    return recomendaciones[:5]


def generar_insight_ejecutivo(flujo, conc):
    pendientes = conc.get("pendientes", 0)
    sin_soporte = conc.get("sin_soporte", 0)
    movimientos_internos = conc.get("movimientos_internos", 0)
    variacion = flujo.get("variacion", 0)

    if sin_soporte > 0 and pendientes > 0:
        return (
            "La principal debilidad del período no parece ser la liquidez, sino la falta de respaldo suficiente para dar el cierre por confiable."
        )

    if movimientos_internos > 0 and sin_soporte == 0 and pendientes == 0:
        return (
            "La operación luce relativamente ordenada, pero conviene separar mejor los movimientos internos para no confundirlos con gasto real del negocio."
        )

    if variacion < 0 and sin_soporte > 0:
        return (
            "La combinación de caída de caja y movimientos sin respaldo sugiere una señal de riesgo que conviene corregir antes del próximo cierre."
        )

    if variacion > 0 and pendientes == 0 and sin_soporte == 0:
        return (
            "La caja cerró en mejora y el período muestra una estructura bastante limpia para una lectura ejecutiva preliminar."
        )

    return (
        "El período ya permite una lectura útil para decidir, pero todavía no alcanza el nivel de orden documental ideal para cerrar con plena confianza."
    )


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

    def construir_botones_movimientos(section_target):
        botones = [
            ("all", "Ver todo"),
            ("entradas", "Entradas"),
            ("salidas", "Salidas"),
            ("cobros", "Cobros"),
            ("pagos", "Pagos"),
            ("internos", "Movimientos internos"),
        ]

        html = ""
        for valor, etiqueta in botones:
            clase = "filter-btn active" if valor == "all" else "filter-btn"
            html += (
                f'<button class="{clase}" type="button" '
                f'data-filter="{valor}" data-target="{section_target}">{etiqueta}</button>'
            )
        return html

    def construir_botones_conciliacion(section_target):
        botones = [
            ("all", "Ver todo"),
            ("pendientes", "Facturas pendientes"),
            ("conciliadas", "Facturas conciliadas"),
            ("sin-soporte", "Sin soporte"),
            ("no-conciliables", "No conciliables"),
            ("duplicados", "Duplicados potenciales"),
            ("internos", "Movimientos internos"),
        ]

        html = ""
        for valor, etiqueta in botones:
            clase = "filter-btn active" if valor == "all" else "filter-btn"
            html += (
                f'<button class="{clase}" type="button" '
                f'data-filter="{valor}" data-target="{section_target}">{etiqueta}</button>'
            )
        return html

    def construir_bloque_colapsable(titulo, cuerpo_html, subtitulo="", abierto=False, extra_class=""):
        clase_activa = "active" if abierto else ""
        estado_inicial = "block" if abierto else "none"
        icono = "−" if abierto else "+"

        subtitulo_html = ""
        if subtitulo:
            subtitulo_html = f'<div class="accordion-subtitle">{subtitulo}</div>'

        return f"""
        <div class="accordion-shell {extra_class}">
            <button type="button" class="accordion-toggle {clase_activa}">
                <span class="accordion-copy">
                    <span class="accordion-title">{titulo}</span>
                    {subtitulo_html}
                </span>
                <span class="accordion-icon">{icono}</span>
            </button>
            <div class="accordion-panel" style="display:{estado_inicial};">
                {cuerpo_html}
            </div>
        </div>
        """

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
        <div class="table-shell compact-shell">
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

    def tarjetas_moviles_movimientos(items, clase, section_target):
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

            cards += f"""
            <article class="mobile-movement-card {clase}" data-kind="{' '.join(sorted(set(tags)))}" data-target-section="{section_target}">
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

        return cards

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

        filas = ""
        cards = ""

        for item in entradas:
            tags = ["entradas", "cobros", "all"]
            filas += f"""
            <tr class="row-entrada mov-row"
                data-kind="{' '.join(sorted(set(tags)))}"
                data-category="{item['categoria']}"
                data-target-section="movimientos-section">
                <td class="mono">{item['fecha']}</td>
                <td>{item['descripcion']}</td>
                <td><span class="badge {clase_badge_categoria(item['categoria'])}">{item['categoria_humana']}</span></td>
                <td class="mono">€ {item['importe_fmt']}</td>
            </tr>
            """
        cards += tarjetas_moviles_movimientos(entradas, "row-entrada", "movimientos-section")

        for item in salidas:
            tags = ["salidas", "all"]
            if item["categoria"] in ["pago_proveedor", "gasto_operativo", "otros_pagos"]:
                tags.append("pagos")
            if item["categoria"] in ["retiro_propio", "transferencia_interna", "traspaso"]:
                tags.append("internos")
            filas += f"""
            <tr class="row-salida mov-row"
                data-kind="{' '.join(sorted(set(tags)))}"
                data-category="{item['categoria']}"
                data-target-section="movimientos-section">
                <td class="mono">{item['fecha']}</td>
                <td>{item['descripcion']}</td>
                <td><span class="badge {clase_badge_categoria(item['categoria'])}">{item['categoria_humana']}</span></td>
                <td class="mono">€ {item['importe_fmt']}</td>
            </tr>
            """
        cards += tarjetas_moviles_movimientos(salidas, "row-salida", "movimientos-section")

        return f"""
        <div class="table-shell compact-shell">
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Descripción</th>
                            <th>Categoría</th>
                            <th>Importe</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            </div>
            <div class="mobile-movements-grid">
                {cards}
            </div>
        </div>
        """

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
            if estado_norm in ["duplicado_potencial"]:
                tags.append("duplicados")
            if estado_norm == "movimiento_interno":
                tags.append("internos")

            filas += f"""
            <tr class="conc-row" data-kind="{' '.join(sorted(set(tags)))}" data-target-section="conciliacion-section">
                <td>{item.get('archivo', '-')}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
                <td class="mono">€ {importe}</td>
                <td><span class="badge {badge_class}">{estado}</span></td>
                <td class="mono">{diferencia if diferencia == '-' else '€ ' + diferencia}</td>
                <td><span class="badge {clase_badge_categoria(item.get('categoria'))}">{humanizar_categoria(item.get('categoria'))}</span></td>
            </tr>
            """

            cards += f"""
            <article class="mobile-conc-card" data-kind="{' '.join(sorted(set(tags)))}" data-target-section="conciliacion-section">
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
        <div class="table-shell compact-shell">
            <div class="filter-toolbar">
                {construir_botones_conciliacion("conciliacion-section")}
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
            <div class="mobile-conc-grid">
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
        <div class="table-shell compact-shell">
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

    def _seleccionar_importes_presentables(importes_lista, max_visibles=200):
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

        return unicos[:max_visibles]

    def _render_importe_chip(imp):
        valor = normalizar_importe_reporte(imp)
        clase = "amount-chip-neutral"
        if valor > 0:
            clase = "amount-chip-positive"
        elif valor < 0:
            clase = "amount-chip-negative"

        simbolo = "€ "
        return f'<span class="amount-chip {clase}">{simbolo}{imp}</span>'

    def _resumen_importes(importes_lista):
        if not importes_lista:
            return "Sin montos detectados", ""

        total_montos = len(importes_lista)
        positivos = sum(1 for x in importes_lista if normalizar_importe_reporte(x) > 0)
        negativos = sum(1 for x in importes_lista if normalizar_importe_reporte(x) < 0)

        partes = [f"{total_montos} {pluralizar(total_montos, 'monto')}"]
        if positivos > 0:
            partes.append(f"{positivos} positivo(s)")
        if negativos > 0:
            partes.append(f"{negativos} negativo(s)")

        chips = "".join(_render_importe_chip(imp) for imp in _seleccionar_importes_presentables(importes_lista))
        return " · ".join(partes), chips

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
            resumen_texto, chips_html = _resumen_importes(importes_lista)

            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td>{resumen_texto}</td>
                <td class="amounts-cell">
                    <div class="amount-chip-wrap">
                        {chips_html or '<span class="amount-chip amount-chip-neutral">Sin montos</span>'}
                    </div>
                </td>
            </tr>
            """

            cards += f"""
            <article class="mobile-amount-card">
                <div class="mobile-doc-title">{item.get('archivo', '-')}</div>
                <div class="mobile-meta-row">
                    <span class="mobile-label">Resumen</span>
                    <span>{resumen_texto}</span>
                </div>
                <div class="mobile-amount-list amount-chip-wrap">
                    {chips_html or '<span class="amount-chip amount-chip-neutral">Sin montos</span>'}
                </div>
            </article>
            """

        return f"""
        <div class="table-shell compact-shell">
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Resumen</th>
                            <th>Montos detectados</th>
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
        <div class="metrics-grid compact-grid compact-grid-soft">
            <article class="kpi">
                <div class="label">Otros cobros menores</div>
                <div class="amount">{analisis['otros_cobros_cantidad']}+</div>
                <div class="meta">
                    <span class="trend up">€ {fmt(analisis['otros_cobros_total'])}</span>
                    <span>Menores a € {fmt(UMBRAL_RELEVANTE)}</span>
                </div>
            </article>

            <article class="kpi">
                <div class="label">Otros pagos menores</div>
                <div class="amount">{analisis['otros_pagos_cantidad']}</div>
                <div class="meta">
                    <span class="trend warn">€ {fmt(analisis['otros_pagos_total'])}</span>
                    <span>Menores a € {fmt(UMBRAL_RELEVANTE)}</span>
                </div>
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
    nombre_empresa = inferir_nombre_empresa(documentos, ledger)
    nombre_empresa_titulo = nombre_empresa if nombre_empresa and nombre_empresa != "la empresa" else "la empresa analizada"
    titular_ejecutivo, narrativa_ejecutiva = texto_lectura_ejecutiva(flujo, conc, docs)
    score_financiero = calcular_score_financiero(flujo, conc)
    etiqueta_score = texto_score_financiero(score_financiero)
    diagnosticos = generar_diagnostico_financiero(flujo, conc)
    recomendaciones = generar_recomendaciones_financieras(flujo, conc)
    insight_ejecutivo = generar_insight_ejecutivo(flujo, conc)

    total_docs_clasificados = docs["factura_venta"] + docs["factura_compra"] + docs["extracto_bancario"] + docs["otros"]

    diagnosticos_html = "".join(f"<li>{item}</li>" for item in diagnosticos)
    recomendaciones_html = "".join(f"<li>{item}</li>" for item in recomendaciones)

    bloque_diagnostico = construir_bloque_colapsable(
        titulo="Ver diagnóstico detallado",
        subtitulo="Lectura ampliada del período y acciones sugeridas.",
        abierto=False,
        cuerpo_html=f"""
        <div class="diagnostic-grid no-top-padding">
            <article class="diagnostic-card">
                <h3>Diagnóstico automático</h3>
                <ul class="diagnostic-list">
                    {diagnosticos_html}
                </ul>
            </article>

            <article class="recommend-card">
                <h3>Recomendaciones sugeridas</h3>
                <ul class="recommend-list">
                    {recomendaciones_html}
                </ul>
            </article>
        </div>
        """,
    )

    bloque_como_leer = construir_bloque_colapsable(
        titulo="Cómo leer este informe",
        subtitulo="Contexto adicional sobre el alcance del análisis.",
        abierto=False,
        cuerpo_html=f"""
        <div class="story-layout no-top-padding">
            <article class="story-card">
                <h3>Qué muestra este informe</h3>
                <p>Este informe resume qué ocurrió con la caja durante el período, qué documentos fueron reconocidos, qué facturas quedaron conciliadas y qué movimientos todavía requieren revisión adicional.</p>
                <p>Para el período del informe, el saldo inicial fue de € {fmt(flujo["saldo_inicial"])}, las entradas alcanzan € {fmt(flujo["entradas"])}, las salidas € {fmt(flujo["salidas"])} y el saldo final queda en € {fmt(flujo["saldo_final"])}, con una variación neta de € {fmt(flujo["variacion"])}.</p>
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
        """,
    )

    bloque_documentos = construir_bloque_colapsable(
        titulo="Ver documentos analizados",
        subtitulo="Inventario documental del proceso.",
        abierto=False,
        cuerpo_html=documentos_html(),
    )

    bloque_importes = construir_bloque_colapsable(
        titulo="Ver montos detectados",
        subtitulo="Todos los montos encontrados, con color según signo.",
        abierto=False,
        cuerpo_html=importes_html(),
    )

    bloque_ledger = construir_bloque_colapsable(
        titulo="Ver detalle contable",
        subtitulo="Ledger base para revisión técnica.",
        abierto=False,
        cuerpo_html=tabla_ledger_html(),
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Informe financiero de {nombre_empresa_titulo}</title>
        <link rel="icon" type="image/png" href="https://angelgarciabanchs.com/wp-content/uploads/2025/06/imagen-circular.png">
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
                grid-template-columns:1.12fr .88fr;
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
                scroll-margin-top:18px;
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

            .compact-grid-soft {{
                padding-top:6px;
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
            .contact-card,
            .diagnostic-card,
            .recommend-card,
            .score-card,
            .insight-hero-card,
            .accordion-shell {{
                background:var(--panel-strong);
                border:1px solid var(--line);
                box-shadow:var(--shadow-sm);
                border-radius:28px;
            }}

            .story-card,
            .insight-card,
            .diagnostic-card,
            .recommend-card,
            .score-card,
            .insight-hero-card {{
                padding:24px;
            }}

            .story-card h3,
            .table-head h3,
            .alerts-title,
            .diagnostic-card h3,
            .recommend-card h3,
            .score-card h3,
            .insight-hero-card h3 {{
                margin:0 0 12px;
                font-size:1.18rem;
                font-weight:900;
            }}

            .story-card p,
            .diagnostic-card p,
            .recommend-card p,
            .score-card p,
            .insight-hero-card p {{
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

            .score-ring {{
                width:170px;
                height:170px;
                border-radius:50%;
                margin:0 auto;
                background:
                    radial-gradient(closest-side,#fff 73%,transparent 75% 100%),
                    conic-gradient(var(--blue-1) 0 {score_financiero}%, #dbeafe {score_financiero}% 100%);
                display:grid;
                place-items:center;
            }}

            .score-ring span {{
                display:flex;
                flex-direction:column;
                align-items:center;
                gap:4px;
                font-weight:900;
                font-size:2rem;
                letter-spacing:-.05em;
            }}

            .score-ring small {{
                font-size:.8rem;
                color:var(--muted);
                font-weight:800;
            }}

            .bullet-list,
            .diagnostic-list,
            .recommend-list {{
                display:grid;
                gap:12px;
            }}

            .bullet,
            .diagnostic-list li,
            .recommend-list li {{
                display:flex;
                align-items:flex-start;
                gap:12px;
                color:var(--muted);
                line-height:1.6;
                font-weight:600;
            }}

            .bullet::before,
            .diagnostic-list li::before,
            .recommend-list li::before {{
                content:"";
                width:10px;
                height:10px;
                margin-top:7px;
                border-radius:999px;
                background:linear-gradient(135deg,var(--blue-1),var(--blue-2));
                flex:none;
            }}

            .diagnostic-grid {{
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:16px;
                padding:8px 22px 22px;
            }}

            .diagnostic-grid.no-top-padding,
            .story-layout.no-top-padding {{
                padding-top:0;
            }}

            .insight-hero-card {{
                background:
                    radial-gradient(circle at top right, rgba(94,167,255,.18), transparent 35%),
                    linear-gradient(180deg,#ffffff,#f8fbff);
            }}

            .insight-highlight {{
                font-size:1.04rem;
                line-height:1.85;
                color:#334155;
                font-weight:700;
            }}

            .score-chip {{
                display:inline-flex;
                align-items:center;
                gap:8px;
                padding:8px 12px;
                border-radius:999px;
                background:#eef5ff;
                color:#0f4cff;
                font-size:.84rem;
                font-weight:900;
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

            .accordion-shell {{
                margin:18px 22px 22px;
                overflow:hidden;
            }}

            .accordion-toggle {{
                width:100%;
                display:flex;
                align-items:center;
                justify-content:space-between;
                gap:16px;
                padding:18px 22px;
                background:#ffffff;
                border:none;
                cursor:pointer;
                text-align:left;
            }}

            .accordion-copy {{
                display:flex;
                flex-direction:column;
                gap:6px;
                min-width:0;
            }}

            .accordion-title {{
                font-size:1rem;
                font-weight:900;
                color:var(--text);
            }}

            .accordion-subtitle {{
                color:var(--muted);
                font-size:.92rem;
                line-height:1.55;
            }}

            .accordion-icon {{
                width:34px;
                height:34px;
                border-radius:999px;
                display:inline-flex;
                align-items:center;
                justify-content:center;
                background:#eef5ff;
                color:#0f4cff;
                font-size:1.15rem;
                font-weight:900;
                flex-shrink:0;
            }}

            .accordion-toggle.active .accordion-icon {{
                background:#111827;
                color:#ffffff;
            }}

            .accordion-panel {{
                display:none;
                border-top:1px solid var(--line);
                background:rgba(255,255,255,.92);
            }}

            .table-shell.compact-shell {{
                margin:0;
                border:none;
                box-shadow:none;
                border-radius:0;
                background:transparent;
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

            .amount-chip-wrap {{
                display:flex;
                flex-wrap:wrap;
                gap:8px;
            }}

            .amount-chip {{
                display:inline-flex;
                align-items:center;
                justify-content:center;
                padding:8px 10px;
                border-radius:999px;
                font-size:.82rem;
                font-weight:800;
                border:1px solid transparent;
                white-space:nowrap;
            }}

            .amount-chip-positive {{
                background:var(--green-soft);
                color:var(--green);
                border-color:#cdeed8;
            }}

            .amount-chip-negative {{
                background:var(--red-soft);
                color:var(--red);
                border-color:#ffd4d4;
            }}

            .amount-chip-neutral {{
                background:var(--gray-soft);
                color:var(--gray);
                border-color:#e2e8f0;
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
            .mobile-movements-grid,
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

            .mobile-doc-title {{
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

            .mobile-doc-grid,
            .mobile-amount-grid,
            .mobile-movements-grid,
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
                gap:28px;
                align-items:flex-start;
                flex-wrap:wrap;
            }}

            .author-photo {{
                width:108px;
                height:108px;
                border-radius:999px;
                object-fit:cover;
                flex-shrink:0;
                margin-right:6px;
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
                .story-layout,
                .diagnostic-grid {{
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
                .mobile-movements-grid,
                .mobile-conc-grid {{
                    display:grid;
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

                .accordion-shell,
                .table-shell,
                .author-card,
                .books-card,
                .contact-card,
                .empty-state,
                .diagnostic-card,
                .recommend-card,
                .score-card,
                .insight-hero-card {{
                    margin:16px;
                    padding:16px;
                }}

                .accordion-toggle {{
                    padding:16px;
                }}

                .story-layout,
                .diagnostic-grid {{
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

@media print {{
    .filter-toolbar,
    .accordion-icon,
    .actions-bar,
    .btn-ghost,
    .topbar-shell .chip,
    .hero-kicker {{
        display: none !important;
    }}

    .accordion-panel {{
        display: block !important;
    }}

    .accordion-shell {{
        border: none !important;
        box-shadow: none !important;
        margin: 12px 0 !important;
        page-break-inside: avoid;
    }}

    .accordion-toggle {{
        display: none !important;
    }}

    .section,
    .story-card,
    .insight-card,
    .diagnostic-card,
    .recommend-card,
    .score-card,
    .insight-hero-card,
    .kpi,
    .metric-card,
    .alert-card,
    .author-card,
    .books-card,
    .contact-card {{
        box-shadow: none !important;
        backdrop-filter: none !important;
        background: #ffffff !important;
        page-break-inside: avoid;
    }}

    .hero,
    .hero-side,
    .metrics-grid,
    .diagnostic-grid,
    .story-layout,
    .alerts-grid {{
        display: block !important;
    }}

    .metric-card,
    .kpi,
    .alert-card,
    .score-card,
    .insight-hero-card,
    .diagnostic-card,
    .recommend-card {{
        margin-bottom: 12px !important;
    }}

    .topbar,
    .section,
    .hero {{
        border: 1px solid #dbe2ea !important;
    }}

    .brand h1,
    .hero h2,
    .section-title,
    .author-name,
    .book-title {{
        word-break: break-word;
        overflow-wrap: anywhere;
    }}

    .table-wrap {{
        display: block !important;
        overflow: visible !important;
    }}

    .mobile-doc-grid,
    .mobile-amount-grid,
    .mobile-movements-grid,
    .mobile-conc-grid {{
        display: none !important;
    }}

    table {{
        min-width: 0 !important;
        width: 100% !important;
        font-size: 11px !important;
    }}

    thead th,
    tbody td {{
        padding: 8px 10px !important;
    }}

    .footer-card {{
        margin-top: 18px !important;
        box-shadow: none !important;
        background: #ffffff !important;
    }}

    /* === RECORTE EJECUTIVO DEL PDF === */

    #detalle-documental-section,
    #detalle-contable-section {{
        display: none !important;
    }}

    #movimientos-section .filter-toolbar,
    #movimientos-section .table-shell,
    #movimientos-section .mobile-movements-grid,
    #movimientos-section .metrics-grid,
    #movimientos-section .compact-grid,
    #movimientos-section .compact-grid-soft {{
        display: none !important;
    }}

    #movimientos-section {{
        display: none !important;
    }}

    #conciliacion-section .filter-toolbar,
    #conciliacion-section .table-shell,
    #conciliacion-section .mobile-conc-grid {{
        display: none !important;
    }}

.contact-card {{
    display:block !important;
    text-align:left !important;
}}

.cta-button {{
    display:inline-flex !important;
    width:auto !important;
    min-width:0 !important;
    margin-top:14px !important;
    box-shadow:none !important;
}}

.book-link {{
    display:inline-block !important;
    width:auto !important;
}}

.footer-actions,
.footer-right,
.footer-pill {{
    display:none !important;
}}

.footer-card {{
    display:block !important;
    text-align:left !important;
    padding:14px 16px !important;
    margin-top:14px !important;
}}

.footer-card strong {{
    display:inline !important;
}}

#movimientos-section {{
    page-break-before:auto;
}}

.books-section,
.author-card,
.books-card,
.contact-card {{
    page-break-inside: avoid;
}}

.amount-chip-wrap {{
    gap:6px !important;
}}

.amount-chip {{
    padding:6px 8px !important;
    font-size:10px !important;
}}

    @page {{
        size: A4;
        margin: 12mm;
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
                        <h1>Informe financiero de {nombre_empresa_titulo}</h1>
                    </div>
                    <div class="company-meta">
                        <div class="chip">Archivos analizados: {total}</div>
                        <div class="chip">Documentos clasificados: {total_docs_clasificados}</div>
                        <div class="chip chip-strong">{texto_calidad_cierre(conc["nivel_cierre"])}</div>
                        <div class="chip">Score: {score_financiero}/100</div>
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
                                <span>{nombre_empresa_titulo}</span>
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

                <section class="section" id="diagnostico-section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Diagnóstico ejecutivo</h3>
                            <p class="section-sub">Resumen rápido de qué tan ordenado luce el período, qué impide cerrarlo con confianza y dónde conviene actuar primero.</p>
                        </div>
                    </div>

                    <div class="diagnostic-grid">
                        <article class="score-card">
                            <div class="score-chip">Score financiero</div>
                            <h3>Fortaleza preliminar del período</h3>
                            <div class="score-ring">
                                <span>{score_financiero}<small>{etiqueta_score}</small></span>
                            </div>
                            <p>Este indicador resume, de forma preliminar, qué tan cerca está el período de poder considerarse bien cerrado desde el punto de vista financiero y documental.</p>
                        </article>

                        <article class="insight-hero-card">
                            <div class="score-chip">Insight principal</div>
                            <h3>La lectura más importante del período</h3>
                            <p class="insight-highlight">{insight_ejecutivo}</p>
                        </article>
                    </div>

                    {bloque_diagnostico}
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
                            <div class="label">Volumen total movido (entradas + salidas)</div>
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

                    <section class="alerts-grid">
                        <article class="alert-card green">
                            <div class="alert-tag">Bien</div>
                            <h4>Base contable ya organizada</h4>
                            <p>La documentación cargada ya se transformó en una estructura útil para lectura gerencial y revisión financiera.</p>
                        </article>

                        <article class="alert-card yellow">
                            <div class="alert-tag">Revisar</div>
                            <h4>El cierre todavía requiere seguimiento</h4>
                            <p>Persisten {conc["pendientes"]} {pluralizar(conc["pendientes"], "factura pendiente", "facturas pendientes")} y € {fmt(conc["importe_pendiente"])} todavía por cerrar o validar antes de considerar el período razonablemente completo.</p>
                        </article>

                        <article class="alert-card red">
                            <div class="alert-tag">Atención</div>
                            <h4>Movimientos sin soporte detectados</h4>
                            <p>Se detectan {conc.get("sin_soporte", 0)} {pluralizar(conc.get("sin_soporte", 0), "movimiento relevante sin soporte documental", "movimientos relevantes sin soporte documental")} y {conc.get("sin_soporte_menor", 0)} {pluralizar(conc.get("sin_soporte_menor", 0), "movimiento menor sin soporte directo", "movimientos menores sin soporte directo")}.</p>
                        </article>
                    </section>

                    {bloque_como_leer}
                </section>

                <section class="section" id="detalle-documental-section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Detalle documental</h3>
                            <p class="section-sub">Sección opcional para revisar documentos y montos detectados con mayor detalle.</p>
                        </div>
                    </div>
                    {bloque_documentos}
                    {bloque_importes}
                </section>

                <section class="section" id="movimientos-section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Movimientos bancarios</h3>
                            <p class="section-sub">Usa los botones para ver solo entradas, salidas, cobros, pagos o movimientos internos. El filtro hace scroll automático a esta sección.</p>
                        </div>
                    </div>
                    <div class="filter-toolbar">
                        {construir_botones_movimientos("movimientos-section")}
                    </div>
                    {tabla_movimientos_relevantes_html()}
                    {bloque_movimientos_menores_html()}
                </section>

                <section class="section" id="detalle-contable-section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Detalle contable</h3>
                            <p class="section-sub">Sección opcional para revisión técnica del ledger generado por el sistema.</p>
                        </div>
                    </div>
                    {bloque_ledger}
                </section>

                <section class="section" id="conciliacion-section">
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
                            <strong>PYME Financial Analyzer</strong> · Informe visual para revisión ejecutiva, control documental y lectura preliminar de caja de {nombre_empresa_titulo}.
                        </div>
                        <div class="footer-right">
                            <span class="footer-pill">Archivos: {total}</span>
                            <span class="footer-pill">Clasificados: {total_docs_clasificados}</span>
                            <span class="footer-pill">{texto_calidad_cierre(conc["nivel_cierre"])}</span>
                            <span class="footer-pill">Score: {score_financiero}/100</span>
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
                function scrollToTarget(targetId) {{
                    const target = document.getElementById(targetId);
                    if (target) {{
                        target.scrollIntoView({{ behavior: "smooth", block: "start" }});
                    }}
                }}

                function applyFilter(value, targetId) {{
                    const allRows = document.querySelectorAll("[data-kind]");
                    const buttons = document.querySelectorAll('.filter-btn[data-target="' + targetId + '"]');

                    buttons.forEach(btn => {{
                        if (btn.getAttribute("data-filter") === value) {{
                            btn.classList.add("active");
                        }} else {{
                            btn.classList.remove("active");
                        }}
                    }});

                    allRows.forEach(el => {{
                        const elementTarget = el.getAttribute("data-target-section");
                        if (elementTarget && elementTarget !== targetId) {{
                            return;
                        }}

                        const kinds = (el.getAttribute("data-kind") || "").split(" ").filter(Boolean);
                        if (value === "all" || kinds.includes(value)) {{
                            el.classList.remove("is-hidden");
                        }} else {{
                            el.classList.add("is-hidden");
                        }}
                    }});

                    scrollToTarget(targetId);
                }}

                function bindAccordions() {{
                    document.querySelectorAll(".accordion-toggle").forEach(btn => {{
                        btn.addEventListener("click", function() {{
                            const panel = this.nextElementSibling;
                            const icon = this.querySelector(".accordion-icon");
                            const isOpen = this.classList.contains("active");

                            if (isOpen) {{
                                this.classList.remove("active");
                                panel.style.display = "none";
                                if (icon) icon.textContent = "+";
                            }} else {{
                                this.classList.add("active");
                                panel.style.display = "block";
                                if (icon) icon.textContent = "−";
                            }}
                        }});
                    }});
                }}

                document.querySelectorAll(".filter-btn").forEach(btn => {{
                    btn.addEventListener("click", function() {{
                        const value = this.getAttribute("data-filter") || "all";
                        const targetId = this.getAttribute("data-target") || "movimientos-section";
                        applyFilter(value, targetId);
                    }});
                }});

                bindAccordions();
                applyFilter("all", "movimientos-section");
                applyFilter("all", "conciliacion-section");
            }})();

if ('scrollRestoration' in history) {{
    history.scrollRestoration = 'manual';
}}

window.addEventListener("load", function () {{
    setTimeout(() => window.scrollTo(0, 0), 0);
}});
        </script>
    </body>
    </html>
    """

    return html

