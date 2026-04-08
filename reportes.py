def generar_html_resultado(total, clasificados, importes, documentos, ledger=None):
    def lista(lista):
        return "".join(f"<li>{x}</li>" for x in lista) if lista else "<li>No hay</li>"

    def lista_importes(lista):
        if not lista:
            return "<li>No hay importes detectados</li>"

        html = ""
        for item in lista:
            montos = ", ".join(item["importes"]) if item["importes"] else "No se detectaron importes"
            html += f"<li><strong>{item['archivo']}</strong>: {montos}</li>"
        return html

    def lista_documentos(lista):
        if not lista:
            return "<li>No hay documentos detectados</li>"

        html = ""
        for item in lista:
            html += f"<li><strong>{item['archivo']}</strong> | {item['tipo']} | {item['fecha']}</li>"
        return html

    def tabla_ledger(ledger):
        if not ledger:
            return "<p>No hay movimientos en el ledger.</p>"

        filas = ""
        for item in ledger:
            filas += f"""
            <tr>
                <td>{item['archivo']}</td>
                <td>{item['tipo']}</td>
                <td>{item['fecha']}</td>
                <td>{item['importe']}</td>
                <td>{item['naturaleza']}</td>
            </tr>
            """

        return f"""
        <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; background:white;">
                <thead>
                    <tr>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Archivo</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Tipo</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Fecha</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Importe</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Naturaleza</th>
                    </tr>
                </thead>
                <tbody>
                    {filas}
                </tbody>
            </table>
        </div>
        """

    html = f"""
    <h2>Procesamiento completado</h2>
    <p><strong>Total archivos:</strong> {total}</p>

    <h3>📄 Facturas venta</h3>
    <ul>{lista(clasificados["factura_venta"])}</ul>

    <h3>🧾 Facturas compra</h3>
    <ul>{lista(clasificados["factura_compra"])}</ul>

    <h3>🏦 Extractos</h3>
    <ul>{lista(clasificados["extracto_bancario"])}</ul>

    <h3>📁 Otros</h3>
    <ul>{lista(clasificados["otros"])}</ul>

    <h3>💶 Importes</h3>
    <ul>{lista_importes(importes)}</ul>

    <h3>🗂 Documentos</h3>
    <ul>{lista_documentos(documentos)}</ul>

    <h3>📒 Ledger base</h3>
    {tabla_ledger(ledger)}

    <br><a href="/">Volver</a>
    """

    return html
