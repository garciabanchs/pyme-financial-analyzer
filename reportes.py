def generar_html_resultado(total, clasificados, importes, documentos, ledger=None, conciliacion=None):

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

    def resumen_flujo(ledger):
        if not ledger:
            return "<p>No hay datos para resumen.</p>"

        total_entradas = 0.0
        total_salidas = 0.0
        total_movimientos = 0.0
        total_revisar = 0.0

        for item in ledger:
            try:
                valor = float(item["importe"].replace(".", "").replace(",", "."))
            except:
                continue

            if item["naturaleza"] == "entrada":
                total_entradas += valor
            elif item["naturaleza"] == "salida":
                total_salidas += valor
            elif item["naturaleza"] == "movimiento":
                total_movimientos += valor
            else:
                total_revisar += valor

        balance = total_entradas - total_salidas

        def fmt(numero):
            return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return f"""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Entradas</div>
                <div style="font-size:28px; font-weight:bold;">€ {fmt(total_entradas)}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Salidas</div>
                <div style="font-size:28px; font-weight:bold;">€ {fmt(total_salidas)}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Movimientos bancarios</div>
                <div style="font-size:28px; font-weight:bold;">€ {fmt(total_movimientos)}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Por revisar</div>
                <div style="font-size:28px; font-weight:bold;">€ {fmt(total_revisar)}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Balance preliminar</div>
                <div style="font-size:28px; font-weight:bold;">€ {fmt(balance)}</div>
            </div>
        </div>
        """

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

    def resumen_conciliacion(conciliacion):
        if not conciliacion:
            return "<p>No hay conciliación disponible.</p>"

        total_conciliadas = 0
        total_parciales = 0
        total_pendientes = 0
        importe_pendiente = 0.0

        for item in conciliacion:
            if item["estado"] == "conciliado":
                total_conciliadas += 1
            elif item["estado"] == "parcialmente_conciliado":
                total_parciales += 1
            else:
                total_pendientes += 1
                try:
                    importe_pendiente += float(item["importe"])
                except:
                    pass

        def fmt(numero):
            return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return f"""
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Facturas conciliadas</div>
                <div style="font-size:28px; font-weight:bold;">{total_conciliadas}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Parcialmente conciliadas</div>
                <div style="font-size:28px; font-weight:bold;">{total_parciales}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Facturas pendientes</div>
                <div style="font-size:28px; font-weight:bold;">{total_pendientes}</div>
            </div>
            <div style="background:white; padding:20px; border-radius:14px; box-shadow:0 8px 24px rgba(0,0,0,0.08);">
                <div style="font-size:14px; color:#6b7280;">Importe pendiente</div>
                <div style="font-size:28px; font-weight:bold;">€ {fmt(importe_pendiente)}</div>
            </div>
        </div>
        """

    def hallazgos_ejecutivos(conciliacion):
        if not conciliacion:
            return "<p>No hay hallazgos ejecutivos disponibles.</p>"

        pendiente_cobro = 0.0
        pendiente_pago = 0.0
        total_pendientes = 0

        for item in conciliacion:
            if item["estado"] != "pendiente":
                continue

            total_pendientes += 1

            try:
                importe = float(item["importe"])
            except:
                importe = 0.0

            if item.get("tipo") == "factura_venta":
                pendiente_cobro += importe
            elif item.get("tipo") == "factura_compra":
                pendiente_pago += importe

        def fmt(numero):
            return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return f"""
        <div style="background:#fff7ed; border:1px solid #fdba74; padding:20px; border-radius:14px; margin-bottom:24px;">
            <h3 style="margin-top:0;">📌 Hallazgos ejecutivos</h3>
            <ul style="margin:0; padding-left:20px; line-height:1.8;">
                <li><strong>Documentos pendientes de conciliación:</strong> {total_pendientes}</li>
                <li><strong>Pendiente de cobro estimado:</strong> € {fmt(pendiente_cobro)}</li>
                <li><strong>Pendiente de pago estimado:</strong> € {fmt(pendiente_pago)}</li>
            </ul>
        </div>
        """

    def tabla_conciliacion(conciliacion):
        if not conciliacion:
            return "<p>No hay conciliación disponible.</p>"

        filas = ""
        for item in conciliacion:
            importe = f"{item['importe']:.2f}".replace(".", ",")
            diferencia = "-"
            if item.get("diferencia") is not None:
                diferencia = f"{item['diferencia']:.2f}".replace(".", ",")

            filas += f"""
            <tr>
                <td>{item['archivo']}</td>
                <td>{item['fecha']}</td>
                <td>{importe}</td>
                <td>{item['estado']}</td>
                <td>{diferencia}</td>
            </tr>
            """

        return f"""
        <div style="overflow-x:auto;">
            <table style="width:100%; border-collapse:collapse; background:white;">
                <thead>
                    <tr>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Archivo</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Fecha</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Importe</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Estado</th>
                        <th style="border:1px solid #ddd; padding:10px; text-align:left;">Diferencia</th>
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

    <h3>📊 Resumen preliminar de flujo de caja</h3>
    {resumen_flujo(ledger)}

    <h3>📒 Ledger base</h3>
    {tabla_ledger(ledger)}

    {hallazgos_ejecutivos(conciliacion)}

    <h3>🔗 Resumen de conciliación</h3>
    {resumen_conciliacion(conciliacion)}

    <h3>🔗 Conciliación básica</h3>
    {tabla_conciliacion(conciliacion)}

    <br><a href="/">Volver</a>
    """

    return html
