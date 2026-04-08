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

        else:
            for monto_original, valor in importes_validos:
                ledger.append({
                    "archivo": doc["archivo"],
                    "tipo": doc["tipo"],
                    "fecha": doc["fecha"],
                    "importe": monto_original,
                    "naturaleza": naturaleza
                })

    return ledger
