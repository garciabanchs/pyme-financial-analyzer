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

        for monto in doc["importes"]:
            ledger.append({
                "archivo": doc["archivo"],
                "tipo": doc["tipo"],
                "fecha": doc["fecha"],
                "importe": monto,
                "naturaleza": naturaleza
            })

    return ledger
