def normalizar_importe(valor):
    try:
        return float(str(valor).replace(".", "").replace(",", "."))
    except:
        return None


def construir_ledger(documentos):
    ledger = []

    for doc in documentos:
        if doc["tipo"] == "factura_venta":
            naturaleza = "entrada"
        elif doc["tipo"] == "factura_compra":
            naturaleza = "salida"
        elif doc["tipo"] == "extracto_bancario":
            naturaleza = "movimiento"
        else:
            naturaleza = "revisar"

        importes_validos = []
        for monto in doc["importes"]:
            valor = normalizar_importe(monto)
            if valor is not None:
                importes_validos.append((monto, valor))

        if doc["tipo"] in ["factura_venta", "factura_compra"]:
            if importes_validos:
                monto_principal = max(importes_validos, key=lambda x: x[1])[0]

                ledger.append({
                    "archivo": doc["archivo"],
                    "tipo": doc["tipo"],
                    "fecha": doc["fecha"],
                    "importe": monto_principal,
                    "naturaleza": naturaleza
                })

        elif doc["tipo"] == "extracto_bancario":
            vistos = set()

            for monto_original, valor in sorted(importes_validos, key=lambda x: x[1], reverse=True):
                if valor == 0:
                    continue

                if valor < 100:
                    continue

                clave = round(valor, 2)
                if clave in vistos:
                    continue
                vistos.add(clave)

                if valor > 1000:
                    naturaleza_mov = "entrada"
                else:
                    naturaleza_mov = "salida"

                ledger.append({
                    "archivo": doc["archivo"],
                    "tipo": doc["tipo"],
                    "fecha": doc["fecha"],
                    "importe": monto_original,
                    "naturaleza": naturaleza_mov
                })

        else:
            if importes_validos:
                monto_principal = max(importes_validos, key=lambda x: x[1])[0]

                ledger.append({
                    "archivo": doc["archivo"],
                    "tipo": doc["tipo"],
                    "fecha": doc["fecha"],
                    "importe": monto_principal,
                    "naturaleza": naturaleza
                })

    return ledger
