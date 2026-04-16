from itertools import combinations


def normalizar_importe(valor):
    if valor is None:
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    try:
        v = str(valor).strip()

        # eliminar símbolos de moneda
        v = v.replace("€", "").replace("$", "").replace("US$", "")
        v = v.replace(" ", "")

        # detectar formato
        if "," in v and "." in v:
            # ambos presentes → detectar cuál es decimal (el último)
            if v.rfind(",") > v.rfind("."):
                # formato europeo: 1.234,56
                v = v.replace(".", "").replace(",", ".")
            else:
                # formato anglosajón: 1,234.56
                v = v.replace(",", "")
        elif "," in v:
            # solo coma → puede ser decimal europeo
            if len(v.split(",")[-1]) == 2:
                v = v.replace(".", "").replace(",", ".")
            else:
                v = v.replace(",", "")
        elif "." in v:
            # solo punto → puede ser decimal anglosajón
            if len(v.split(".")[-1]) == 2:
                pass  # correcto → no tocar
            else:
                v = v.replace(".", "")

        return float(v)

    except Exception:
        return None


def _coherencia_signo(importe_factura, importe_banco):
    if importe_factura > 0 and importe_banco > 0:
        return True
    if importe_factura < 0 and importe_banco < 0:
        return True
    return False


def _tolerancia_factura(importe_factura):
    return min(max(0.01, abs(importe_factura) * 0.02), 50.0)


def _es_categoria_no_conciliable(categoria):
    categoria = (categoria or "").lower()
    return categoria in [
        "comision",
        "retencion",
        "impuesto",
        "ajuste",
        "traspaso",
        "transferencia_interna",
        "retiro_propio",
    ]


def _es_categoria_operativa_no_facturable(categoria):
    categoria = (categoria or "").lower()
    return categoria in [
        "traspaso",
        "transferencia_interna",
        "retiro_propio",
        "comision",
        "retencion",
        "impuesto",
        "ajuste",
        "otros_cobros",
        "otros_pagos",
    ]


def _es_categoria_comercial_facturable(categoria):
    categoria = (categoria or "").lower()
    return categoria in [
        "cobro_cliente",
        "pago_proveedor",
        "gasto_operativo",
    ]


def _movimiento_puede_conciliar_con_factura(factura, mov):
    categoria = (mov.get("categoria") or "").lower()
    tipo_factura = (factura.get("tipo") or "").lower()

    if _es_categoria_no_conciliable(categoria):
        return False

    if categoria in ["otros_cobros", "otros_pagos"]:
        return False

    if tipo_factura == "factura_venta":
        return categoria in ["cobro_cliente"]

    if tipo_factura == "factura_compra":
        return categoria in ["pago_proveedor", "gasto_operativo"]

    return False


def _normalizar_texto_duplicado(texto):
    texto = (texto or "").lower().strip()
    if not texto:
        return ""

    reemplazos = [
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("|", " "),
        (":", " "),
        (";", " "),
        (",", " "),
        (".", " "),
        ("(", " "),
        (")", " "),
        ("[", " "),
        ("]", " "),
        ("{", " "),
        ("}", " "),
        ("-", " "),
        ("_", " "),
        ("/", " "),
        ("\\", " "),
    ]

    for origen, destino in reemplazos:
        texto = texto.replace(origen, destino)

    return " ".join(texto.split())


def _extraer_token_id_desde_descripcion(descripcion):
    descripcion_norm = _normalizar_texto_duplicado(descripcion)
    if not descripcion_norm:
        return None

    tokens = descripcion_norm.split()
    for i, token in enumerate(tokens[:-1]):
        if token in ["id", "id."]:
            candidato = tokens[i + 1]
            if len(candidato) >= 6:
                return candidato

    for token in tokens:
        if len(token) >= 10 and any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
            return token

    return None


def _firma_textual_movimiento(mov):
    descripcion = _normalizar_texto_duplicado(mov.get("descripcion"))
    if not descripcion:
        return ""

    token_id = _extraer_token_id_desde_descripcion(descripcion)
    if token_id:
        return f"id::{token_id}"

    return descripcion[:180]


def _es_duplicado_potencial_fuerte(mov_a, mov_b):
    fecha_a = mov_a.get("fecha")
    fecha_b = mov_b.get("fecha")

    importe_a = round(abs(mov_a.get("importe_firmado", 0.0)), 2)
    importe_b = round(abs(mov_b.get("importe_firmado", 0.0)), 2)

    categoria_a = (mov_a.get("categoria") or "").lower()
    categoria_b = (mov_b.get("categoria") or "").lower()

    direccion_a = "entrada" if mov_a.get("importe_firmado", 0.0) > 0 else "salida"
    direccion_b = "entrada" if mov_b.get("importe_firmado", 0.0) > 0 else "salida"

    if fecha_a != fecha_b:
        return False

    if importe_a != importe_b:
        return False

    if categoria_a != categoria_b:
        return False

    if direccion_a != direccion_b:
        return False

    firma_a = _firma_textual_movimiento(mov_a)
    firma_b = _firma_textual_movimiento(mov_b)

    if not firma_a or not firma_b:
        return False

    if firma_a == firma_b:
        return True

    return False


def _clasificar_movimiento_suelto(mov):
    importe = abs(mov.get("importe_abs", 0.0))
    categoria = (mov.get("categoria") or "desconocido").lower()

    if categoria in ["traspaso", "transferencia_interna"]:
        return "movimiento interno", "bajo"

    if categoria == "retiro_propio":
        return "movimiento interno", "bajo"

    if categoria in ["comision", "retencion", "impuesto", "ajuste"]:
        if importe >= 100:
            return "movimiento bancario no conciliable", "medio"
        return "movimiento bancario no conciliable menor", "bajo"

    if categoria in ["otros_cobros", "otros_pagos"]:
        return "movimiento agrupado", "bajo"

    if categoria == "gasto_operativo":
        if importe >= 100:
            return "sin soporte", "alto"
        return "sin soporte menor", "bajo"

    if categoria == "pago_proveedor":
        if importe >= 100:
            return "sin soporte", "alto"
        return "sin soporte menor", "bajo"

    if categoria == "cobro_cliente":
        if importe >= 100:
            return "sin soporte", "alto"
        return "sin soporte menor", "bajo"

    if importe >= 100:
        return "sin soporte", "alto"

    return "sin soporte menor", "bajo"


def _es_valor_util(valor):
    if valor is None:
        return False

    if isinstance(valor, str):
        v = valor.strip()
        if not v:
            return False
        if v in ["No detectado", "No detectada", "No aplica", "No aplica.", "N/A", "n/a"]:
            return False
        return True

    return True


def _normalizar_valor_combinable(valor):
    if not _es_valor_util(valor):
        return None
    if isinstance(valor, str):
        return " ".join(valor.strip().split())
    return str(valor)


def _combinar_valores(valores, fallback=None, separador=" | "):
    vistos = []
    normalizados = set()

    for valor in valores or []:
        v = _normalizar_valor_combinable(valor)
        if not v:
            continue

        clave = v.lower()
        if clave in normalizados:
            continue

        normalizados.add(clave)
        vistos.append(v)

        if len(vistos) >= 3:
            break

    if not vistos:
        return fallback

    return separador.join(vistos)


def _combinar_bancos(valores, fallback="No detectado"):
    return _combinar_valores(valores, fallback=fallback)


def _combinar_contrapartes(valores, fallback=None):
    return _combinar_valores(valores, fallback=fallback)


def _combinar_cuentas(valores, fallback=None):
    return _combinar_valores(valores, fallback=fallback)


def _combinar_entidades_financieras(valores, fallback="No detectada"):
    return _combinar_valores(valores, fallback=fallback)


def _valor_prioritario(*valores, fallback=None):
    for valor in valores:
        v = _normalizar_valor_combinable(valor)
        if v:
            return v
    return fallback


def _normalizar_banco_salida(valor):
    v = _normalizar_valor_combinable(valor)
    return v if v else "No detectado"


def _normalizar_entidad_financiera_salida(valor):
    v = _normalizar_valor_combinable(valor)
    return v if v else "No detectada"


def _normalizar_cliente_proveedor_salida(valor):
    v = _normalizar_valor_combinable(valor)
    return v if v else None


def _normalizar_cuenta_salida(valor):
    v = _normalizar_valor_combinable(valor)
    return v if v else None


def _resolver_banco_resultado(factura, movimientos):
    bancos_mov = [m.get("banco") for m in movimientos]
    banco_mov = _combinar_bancos(bancos_mov, fallback=None)
    if banco_mov:
        return _normalizar_banco_salida(banco_mov)
    return _normalizar_banco_salida(_valor_prioritario(factura.get("banco"), fallback=None))


def _resolver_entidad_financiera_resultado(factura, movimientos):
    entidades_mov = [m.get("entidad_financiera") for m in movimientos]
    entidad_mov = _combinar_entidades_financieras(entidades_mov, fallback=None)
    if entidad_mov:
        return _normalizar_entidad_financiera_salida(entidad_mov)
    return _normalizar_entidad_financiera_salida(
        _valor_prioritario(factura.get("entidad_financiera"), factura.get("banco"), fallback=None)
    )


def _resolver_cuenta_resultado(factura, movimientos):
    cuentas_mov = [m.get("cuenta") for m in movimientos]
    cuenta_mov = _combinar_cuentas(cuentas_mov, fallback=None)
    if cuenta_mov:
        return _normalizar_cuenta_salida(cuenta_mov)
    return _normalizar_cuenta_salida(_valor_prioritario(factura.get("cuenta"), fallback=None))


def _resolver_cliente_proveedor_resultado(factura, movimientos):
    cliente_factura = _normalizar_valor_combinable(factura.get("cliente_proveedor"))
    if cliente_factura:
        return _normalizar_cliente_proveedor_salida(cliente_factura)

    contrapartes_mov = [m.get("cliente_proveedor") for m in movimientos]
    return _normalizar_cliente_proveedor_salida(_combinar_contrapartes(contrapartes_mov, fallback=None))


def _preparar_facturas_y_banco(ledger):
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
            importe_firmado = item.get("importe_firmado_num", 0.0)
            facturas.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "tipo": tipo,
                "importe_firmado": importe_firmado,
                "importe_abs": round(abs(importe_firmado if importe_firmado is not None else importe), 2),
                "moneda": item.get("moneda"),
                "categoria": item.get("categoria"),
                "descripcion": item.get("descripcion"),
                "banco": item.get("banco"),
                "entidad_financiera": item.get("entidad_financiera"),
                "cuenta": item.get("cuenta"),
                "cliente_proveedor": item.get("cliente_proveedor"),
            })

        elif tipo == "extracto_bancario":
            importe_firmado = item.get("importe_firmado_num", 0.0)
            movimientos_banco.append({
                "id": item.get("id"),
                "archivo": item.get("archivo"),
                "fecha": item.get("fecha"),
                "tipo": tipo,
                "importe_firmado": importe_firmado,
                "importe_abs": round(abs(importe_firmado if importe_firmado is not None else importe), 2),
                "naturaleza": item.get("naturaleza"),
                "categoria": item.get("categoria"),
                "descripcion": item.get("descripcion"),
                "moneda": item.get("moneda"),
                "banco": item.get("banco"),
                "entidad_financiera": item.get("entidad_financiera"),
                "cuenta": item.get("cuenta"),
                "cliente_proveedor": item.get("cliente_proveedor"),
            })

    return facturas, movimientos_banco


def _buscar_match_exacto(factura, movimientos_banco, usados_banco):
    importe_factura = factura.get("importe_firmado", 0.0)

    for i, mov in enumerate(movimientos_banco):
        if i in usados_banco:
            continue

        if not _movimiento_puede_conciliar_con_factura(factura, mov):
            continue

        importe_banco = mov.get("importe_firmado", 0.0)

        if not _coherencia_signo(importe_factura, importe_banco):
            continue

        diferencia = abs(importe_factura - importe_banco)
        if diferencia <= 0.01:
            return {
                "indices": [i],
                "estado": "conciliado exacto",
                "diferencia": round(diferencia, 2),
                "match_archivos": [mov.get("archivo")],
                "match_ids": [mov.get("id")],
            }

    return None


def _buscar_match_probable_simple(factura, movimientos_banco, usados_banco):
    importe_factura = factura.get("importe_firmado", 0.0)
    tolerancia = _tolerancia_factura(importe_factura)

    mejor = None

    for i, mov in enumerate(movimientos_banco):
        if i in usados_banco:
            continue

        if not _movimiento_puede_conciliar_con_factura(factura, mov):
            continue

        importe_banco = mov.get("importe_firmado", 0.0)

        if not _coherencia_signo(importe_factura, importe_banco):
            continue

        diferencia = abs(importe_factura - importe_banco)

        if diferencia <= tolerancia:
            if mejor is None or diferencia < mejor["diferencia"]:
                mejor = {
                    "indices": [i],
                    "estado": "conciliado probable",
                    "diferencia": round(diferencia, 2),
                    "match_archivos": [mov.get("archivo")],
                    "match_ids": [mov.get("id")],
                }

    return mejor


def _buscar_match_multi(factura, movimientos_banco, usados_banco, max_componentes=3):
    """
    Busca conciliación de una factura contra suma de 2 o 3 movimientos bancarios.
    Esto sirve para pagos parciales o cobros fragmentados.
    """
    importe_factura = factura.get("importe_firmado", 0.0)
    tolerancia = _tolerancia_factura(importe_factura)

    candidatos = []
    for i, mov in enumerate(movimientos_banco):
        if i in usados_banco:
            continue

        if not _movimiento_puede_conciliar_con_factura(factura, mov):
            continue

        importe_banco = mov.get("importe_firmado", 0.0)

        if not _coherencia_signo(importe_factura, importe_banco):
            continue

        candidatos.append((i, mov))

    if len(candidatos) < 2:
        return None

    mejor = None

    limite = min(max_componentes, len(candidatos))
    for r in range(2, limite + 1):
        for combo in combinations(candidatos, r):
            indices = [x[0] for x in combo]
            movimientos = [x[1] for x in combo]
            suma = sum(m["importe_firmado"] for m in movimientos)
            diferencia = abs(importe_factura - suma)

            if diferencia <= tolerancia:
                estado = "conciliado exacto multi" if diferencia <= 0.01 else "conciliado probable multi"
                if mejor is None or diferencia < mejor["diferencia"]:
                    mejor = {
                        "indices": indices,
                        "estado": estado,
                        "diferencia": round(diferencia, 2),
                        "match_archivos": [m.get("archivo") for m in movimientos],
                        "match_ids": [m.get("id") for m in movimientos],
                    }

    return mejor


def _detectar_duplicados(movimientos_banco, usados_banco):
    """
    Detecta duplicados potenciales con criterio más estricto:
    mismo día, mismo importe absoluto, misma categoría, misma dirección
    y además firma textual equivalente.
    Esto evita marcar como duplicado dos movimientos distintos que solo
    coinciden en fecha e importe.
    """
    candidatos = []
    for i, mov in enumerate(movimientos_banco):
        if i in usados_banco:
            continue
        candidatos.append((i, mov))

    duplicados = []
    ya_marcados = set()

    for idx_a in range(len(candidatos)):
        i_a, mov_a = candidatos[idx_a]

        if i_a in ya_marcados:
            continue

        grupo_actual = [(i_a, mov_a)]

        for idx_b in range(idx_a + 1, len(candidatos)):
            i_b, mov_b = candidatos[idx_b]

            if i_b in ya_marcados:
                continue

            if _es_duplicado_potencial_fuerte(mov_a, mov_b):
                grupo_actual.append((i_b, mov_b))

        if len(grupo_actual) >= 2:
            for i, mov in grupo_actual:
                duplicados.append((i, mov))
                ya_marcados.add(i)

    return duplicados


def detectar_inconsistencias(ledger):
    conciliacion = []

    facturas, movimientos_banco = _preparar_facturas_y_banco(ledger)
    usados_banco = set()

    # =========================================
    # 1. CONCILIAR FACTURAS
    # =========================================
    for factura in facturas:
        match = None

        # 1A. exacto 1 a 1
        match = _buscar_match_exacto(factura, movimientos_banco, usados_banco)

        # 1B. probable 1 a 1
        if match is None:
            match = _buscar_match_probable_simple(factura, movimientos_banco, usados_banco)

        # 1C. exacto/probable multi-match
        if match is None:
            match = _buscar_match_multi(factura, movimientos_banco, usados_banco, max_componentes=3)

        # 1D. resultado factura
        if match is not None:
            movimientos_match = [movimientos_banco[idx] for idx in match["indices"]]

            for idx in match["indices"]:
                usados_banco.add(idx)

            estado = match["estado"]
            riesgo = "bajo" if "exacto" in estado else "medio"

            conciliacion.append({
                "id": factura["id"],
                "tipo": factura["tipo"],
                "archivo": factura["archivo"],
                "fecha": factura["fecha"],
                "importe": factura["importe_abs"],
                "estado": estado,
                "match": " | ".join(match["match_archivos"]),
                "movimiento_asociado": " | ".join(match["match_ids"]),
                "diferencia": match["diferencia"],
                "categoria": factura.get("categoria"),
                "moneda": factura.get("moneda"),
                "banco": _normalizar_banco_salida(_resolver_banco_resultado(factura, movimientos_match)),
                "entidad_financiera": _normalizar_entidad_financiera_salida(
                    _resolver_entidad_financiera_resultado(factura, movimientos_match)
                ),
                "cuenta": _normalizar_cuenta_salida(_resolver_cuenta_resultado(factura, movimientos_match)),
                "cliente_proveedor": _normalizar_cliente_proveedor_salida(
                    _resolver_cliente_proveedor_resultado(factura, movimientos_match)
                ),
                "riesgo": riesgo,
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
                "banco": _normalizar_banco_salida(_valor_prioritario(factura.get("banco"), fallback=None)),
                "entidad_financiera": _normalizar_entidad_financiera_salida(
                    _valor_prioritario(factura.get("entidad_financiera"), factura.get("banco"), fallback=None)
                ),
                "cuenta": _normalizar_cuenta_salida(_valor_prioritario(factura.get("cuenta"), fallback=None)),
                "cliente_proveedor": _normalizar_cliente_proveedor_salida(
                    _valor_prioritario(factura.get("cliente_proveedor"), fallback=None)
                ),
                "riesgo": "alto",
            })

    # =========================================
    # 2. DETECTAR DUPLICADOS BANCARIOS
    # =========================================
    duplicados = _detectar_duplicados(movimientos_banco, usados_banco)
    indices_duplicados = set(i for i, _ in duplicados)

    for i, mov in duplicados:
        conciliacion.append({
            "id": mov["id"],
            "tipo": "extracto_bancario",
            "archivo": mov["archivo"],
            "fecha": mov["fecha"],
            "importe": round(mov.get("importe_abs", 0.0), 2),
            "estado": "duplicado potencial",
            "match": None,
            "movimiento_asociado": None,
            "diferencia": None,
            "categoria": mov.get("categoria"),
            "moneda": mov.get("moneda"),
            "banco": _normalizar_banco_salida(_valor_prioritario(mov.get("banco"), fallback=None)),
            "entidad_financiera": _normalizar_entidad_financiera_salida(
                _valor_prioritario(mov.get("entidad_financiera"), mov.get("banco"), fallback=None)
            ),
            "cuenta": _normalizar_cuenta_salida(_valor_prioritario(mov.get("cuenta"), fallback=None)),
            "cliente_proveedor": _normalizar_cliente_proveedor_salida(
                _valor_prioritario(mov.get("cliente_proveedor"), fallback=None)
            ),
            "riesgo": "medio",
        })

    # =========================================
    # 3. MOVIMIENTOS BANCO SUELTOS
    # =========================================
    for i, mov in enumerate(movimientos_banco):
        if i in usados_banco:
            continue

        if i in indices_duplicados:
            continue

        estado, riesgo = _clasificar_movimiento_suelto(mov)

        conciliacion.append({
            "id": mov["id"],
            "tipo": "extracto_bancario",
            "archivo": mov["archivo"],
            "fecha": mov["fecha"],
            "importe": round(mov.get("importe_abs", 0.0), 2),
            "estado": estado,
            "match": None,
            "movimiento_asociado": None,
            "diferencia": None,
            "categoria": mov.get("categoria"),
            "moneda": mov.get("moneda"),
            "banco": _normalizar_banco_salida(_valor_prioritario(mov.get("banco"), fallback=None)),
            "entidad_financiera": _normalizar_entidad_financiera_salida(
                _valor_prioritario(mov.get("entidad_financiera"), mov.get("banco"), fallback=None)
            ),
            "cuenta": _normalizar_cuenta_salida(_valor_prioritario(mov.get("cuenta"), fallback=None)),
            "cliente_proveedor": _normalizar_cliente_proveedor_salida(
                _valor_prioritario(mov.get("cliente_proveedor"), fallback=None)
            ),
            "riesgo": riesgo,
        })

    return conciliacion
