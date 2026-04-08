def construir_ledger(documentos):
    ledger = []

    for doc in documentos:
        for monto in doc["importes"]:
            ledger.append({
                "archivo": doc["archivo"],
                "tipo": doc["tipo"],
                "fecha": doc["fecha"],
                "importe": monto
            })

    return ledger
