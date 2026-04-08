def generar_html_resultado(total, clasificados, importes, documentos):
    
    def lista(lista):
        return "".join(f"<li>{x}</li>" for x in lista) if lista else "<li>No hay</li>"

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
    <ul>
    {"".join(f"<li>{d['archivo']}: {', '.join(d['importes'])}</li>" for d in importes)}
    </ul>

    <h3>🗂 Documentos</h3>
    <ul>
    {"".join(f"<li>{d['archivo']} | {d['tipo']} | {d['fecha']}</li>" for d in documentos)}
    </ul>

    <br><a href="/">Volver</a>
    """

    return html
