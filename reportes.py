from branding import BRANDING


def generar_html_resultado(total, clasificados, importes, documentos, ledger=None, conciliacion=None):

    branding_data = BRANDING[BRANDING["modo"]]

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
                valor = float(str(item["importe"]).replace(".", "").replace(",", "."))
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

    def bloque_branding_html():
        partes = []

        if BRANDING.get("mostrar_bio", False):
            imagen_html = ""
            if branding_data.get("imagen_url"):
                imagen_html = f"""
                <img src="{branding_data['imagen_url']}" alt="{branding_data['nombre']}"
                     style="width:96px; height:96px; border-radius:999px; object-fit:cover; flex-shrink:0;">
                """

            partes.append(f"""
            <div style="background:#f3f4f6; border-radius:18px; padding:24px; margin:32px 0;">
                <div style="display:flex; gap:20px; align-items:flex-start; flex-wrap:wrap;">
                    {imagen_html}
                    <div style="flex:1; min-width:280px;">
                        <div style="font-size:15px; font-weight:bold; margin-bottom:8px;">{branding_data['titulo']}</div>
                        <div style="font-size:18px; font-weight:bold; margin-bottom:10px;">{branding_data['nombre']}</div>
                        <div style="font-size:15px; line-height:1.6; color:#374151; margin-bottom:12px;">
                            {branding_data['subtitulo']}
                        </div>
                        <div style="font-size:15px; line-height:1.6; color:#374151;">
                            {branding_data['descripcion']}
                        </div>
                    </div>
                </div>
            </div>
            """)

                if BRANDING.get("mostrar_libros", False) and branding_data.get("libros"):
            items = ""
            for libro in branding_data["libros"]:
                portada_html = ""
                if libro.get("portada_url"):
                    portada_html = f"""
                    <img src="{libro['portada_url']}" alt="{libro['titulo']}"
                         style="width:90px; height:135px; object-fit:cover; border-radius:10px; flex-shrink:0; box-shadow:0 6px 16px rgba(0,0,0,0.12);">
                    """

                items += f"""
                <div style="display:flex; gap:16px; align-items:flex-start; margin-bottom:18px;">
                    {portada_html}
                    <div>
                        <div style="font-weight:bold; margin-bottom:6px;">{libro['titulo']}</div>
                        <a href="{libro['url']}" target="_blank"
                           style="color:#1d4ed8; text-decoration:none; font-weight:bold;">
                            Ver en Amazon
                        </a>
                    </div>
                </div>
                """

            partes.append(f"""
            <div style="background:white; border-radius:14px; padding:22px; box-shadow:0 8px 24px rgba(0,0,0,0.08); margin:24px 0;">
                <h3 style="margin-top:0;">📚 Libros</h3>
                {items}
            </div>
            """)

        if BRANDING.get("mostrar_contacto", False) and branding_data.get("contacto_url"):
            partes.append(f"""
            <div style="margin:24px 0 10px 0;">
                <a href="{branding_data['contacto_url']}" target="_blank"
                   style="display:inline-block; background:#111827; color:white; padding:14px 22px;
                          border-radius:10px; text-decoration:none; font-weight:bold;">
                    {branding_data['contacto_texto']}
                </a>
            </div>
            """)

        return "".join(partes)

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

    {bloque_branding_html()}

    <br><a href="/">Volver</a>
    """

    return html
