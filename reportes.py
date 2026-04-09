from branding import BRANDING


def generar_html_resultado(total, clasificados, importes, documentos, ledger=None, conciliacion=None):
    assert BRANDING["modo"] in BRANDING, f"Modo inválido en BRANDING: {BRANDING.get('modo')}"
    branding_data = BRANDING[BRANDING["modo"]]

    ledger = ledger or []
    conciliacion = conciliacion or []
    documentos = documentos or []
    importes = importes or []

    def fmt(numero):
        try:
            return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return "0,00"

    def normalizar_importe(valor):
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            return float(str(valor).replace(".", "").replace(",", "."))
        except Exception:
            return 0.0

    def contar_docs():
        return {
            "factura_venta": len(clasificados.get("factura_venta", [])),
            "factura_compra": len(clasificados.get("factura_compra", [])),
            "extracto_bancario": len(clasificados.get("extracto_bancario", [])),
            "otros": len(clasificados.get("otros", [])),
        }

    def resumen_flujo():
        total_entradas = 0.0
        total_salidas = 0.0
        total_movimientos = 0.0
        total_revisar = 0.0

        for item in ledger:
            valor = normalizar_importe(item.get("importe", 0))
            naturaleza = item.get("naturaleza", "")

            if naturaleza == "entrada":
                total_entradas += valor
            elif naturaleza == "salida":
                total_salidas += valor
            elif naturaleza == "movimiento":
                total_movimientos += valor
            else:
                total_revisar += valor

        balance = total_entradas - total_salidas

        return {
            "entradas": total_entradas,
            "salidas": total_salidas,
            "movimientos": total_movimientos,
            "revisar": total_revisar,
            "balance": balance,
        }

    def resumen_conciliacion():
        total_conciliadas = 0
        total_parciales = 0
        total_pendientes = 0
        importe_pendiente = 0.0
        pendiente_cobro = 0.0
        pendiente_pago = 0.0

        for item in conciliacion:
            estado = item.get("estado", "")
            importe = normalizar_importe(item.get("importe", 0))
            tipo = item.get("tipo", "")

            if estado == "conciliado":
                total_conciliadas += 1
            elif estado == "parcialmente_conciliado":
                total_parciales += 1
            else:
                total_pendientes += 1
                importe_pendiente += importe

                if tipo == "factura_venta":
                    pendiente_cobro += importe
                elif tipo == "factura_compra":
                    pendiente_pago += importe

        return {
            "conciliadas": total_conciliadas,
            "parciales": total_parciales,
            "pendientes": total_pendientes,
            "importe_pendiente": importe_pendiente,
            "pendiente_cobro": pendiente_cobro,
            "pendiente_pago": pendiente_pago,
        }

    def texto_lectura_ejecutiva(flujo, conc, docs):
        entradas = flujo["entradas"]
        salidas = flujo["salidas"]
        balance = flujo["balance"]
        pendientes = conc["pendientes"]

        if entradas > 0 and balance > 0:
            titular = "El negocio muestra generación positiva de caja preliminar durante el período analizado."
        elif entradas > 0 and balance <= 0:
            titular = "El negocio registra actividad, pero el balance preliminar sugiere presión sobre la caja."
        else:
            titular = "La información disponible es insuficiente para confirmar una generación sólida de caja."

        if pendientes > 0:
            complemento = (
                f" Existen {pendientes} documentos pendientes de conciliación que conviene revisar "
                "antes de tomar decisiones definitivas."
            )
        else:
            complemento = " No se observan pendientes relevantes de conciliación en la estructura analizada."

        narrativa = (
            f"Se analizaron {total} archivos en total: "
            f"{docs['factura_venta']} facturas de venta, "
            f"{docs['factura_compra']} facturas de compra, "
            f"{docs['extracto_bancario']} extractos bancarios y "
            f"{docs['otros']} documentos clasificados como otros. "
            f"Las entradas preliminares ascienden a € {fmt(entradas)}, "
            f"las salidas a € {fmt(salidas)} "
            f"y el balance preliminar se ubica en € {fmt(balance)}."
            f"{complemento}"
        )

        return titular, narrativa

    def tabla_ledger_html():
        if not ledger:
            return """
            <div class="empty-state">
                <p>No hay movimientos en el ledger.</p>
            </div>
            """

        filas = ""
        for item in ledger:
            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td>{item.get('tipo', '-')}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
                <td class="mono">{item.get('importe', '-')}</td>
                <td>{item.get('naturaleza', '-')}</td>
            </tr>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Ledger base</h3>
                    <p>Registro preliminar de movimientos identificados a partir de la documentación cargada.</p>
                </div>
                <div class="chip">{len(ledger)} movimientos</div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Tipo</th>
                            <th>Fecha</th>
                            <th>Importe</th>
                            <th>Naturaleza</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
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
        for item in conciliacion:
            importe = fmt(normalizar_importe(item.get("importe", 0)))
            diferencia = "-"
            if item.get("diferencia") is not None:
                diferencia = fmt(normalizar_importe(item.get("diferencia", 0)))

            estado = item.get("estado", "-")
            badge_class = "badge-yellow"
            if estado == "conciliado":
                badge_class = "badge-green"
            elif estado == "parcialmente_conciliado":
                badge_class = "badge-yellow"
            else:
                badge_class = "badge-red"

            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
                <td class="mono">€ {importe}</td>
                <td><span class="badge {badge_class}">{estado}</span></td>
                <td class="mono">{diferencia if diferencia == '-' else '€ ' + diferencia}</td>
            </tr>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Conciliación básica</h3>
                    <p>Estado preliminar de coincidencia entre documentos y movimientos detectados.</p>
                </div>
                <div class="chip">{len(conciliacion)} registros</div>
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
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
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
        for item in documentos:
            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td>{item.get('tipo', '-')}</td>
                <td class="mono">{item.get('fecha', '-')}</td>
            </tr>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Documentos detectados</h3>
                    <p>Inventario base de documentos reconocidos por el sistema durante el procesamiento.</p>
                </div>
                <div class="chip">{len(documentos)} documentos</div>
            </div>
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
        </div>
        """

    def importes_html():
        if not importes:
            return """
            <div class="empty-state">
                <p>No hay importes detectados.</p>
            </div>
            """

        filas = ""
        for item in importes:
            montos = ", ".join(item.get("importes", [])) if item.get("importes") else "No se detectaron importes"
            filas += f"""
            <tr>
                <td>{item.get('archivo', '-')}</td>
                <td>{montos}</td>
            </tr>
            """

        return f"""
        <div class="table-shell">
            <div class="table-head">
                <div>
                    <h3>Importes detectados</h3>
                    <p>Montos identificados automáticamente en la documentación procesada.</p>
                </div>
                <div class="chip">{len(importes)} registros</div>
            </div>
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Archivo</th>
                            <th>Importes detectados</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas}
                    </tbody>
                </table>
            </div>
        </div>
        """

    def bloque_branding_html():
        partes = []

        if BRANDING.get("mostrar_bio", False):
            imagen_html = ""
            if branding_data.get("imagen_url"):
                imagen_html = f"""
                <img src="{branding_data['imagen_url']}" alt="{branding_data['nombre']}"
                     class="author-photo">
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
                if libro.get("portada_html"):
                    portada = f"""
                    <img src="{libro['portada_html']}" alt="{libro['titulo']}" class="book-cover">
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
            <section class="section">
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

    docs = contar_docs()
    flujo = resumen_flujo()
    conc = resumen_conciliacion()
    titular_ejecutivo, narrativa_ejecutiva = texto_lectura_ejecutiva(flujo, conc, docs)

    total_docs_clasificados = docs["factura_venta"] + docs["factura_compra"] + docs["extracto_bancario"] + docs["otros"]

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Informe Financiero PYME</title>
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
                --yellow:#ca8a04;
                --yellow-soft:#fff9e8;
                --red:#dc2626;
                --red-soft:#fef2f2;
                --shadow-sm:0 10px 25px rgba(15,23,42,.06);
                --shadow-md:0 20px 45px rgba(15,23,42,.08);
                --shadow-lg:0 30px 80px rgba(15,23,42,.12);
                --max:1320px;
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

            main {{
                padding:24px 0 44px;
            }}

            .hero {{
                display:grid;
                grid-template-columns:1.2fr .95fr;
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
                max-width:64ch;
                color:var(--muted);
                font-size:1.02rem;
                line-height:1.7;
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
                overflow:hidden;
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
            .contact-card {{
                background:var(--panel-strong);
                border:1px solid var(--line);
                box-shadow:var(--shadow-sm);
                border-radius:28px;
            }}

            .story-card,
            .insight-card {{
                padding:24px;
            }}

            .story-card h3,
            .table-head h3,
            .alerts-title {{
                margin:0 0 12px;
                font-size:1.18rem;
                font-weight:900;
            }}

            .story-card p {{
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

            .bullet-list {{
                display:grid;
                gap:12px;
            }}

            .bullet {{
                display:flex;
                align-items:flex-start;
                gap:12px;
                color:var(--muted);
                line-height:1.5;
                font-weight:600;
            }}

            .bullet::before {{
                content:"";
                width:10px;
                height:10px;
                margin-top:7px;
                border-radius:999px;
                background:linear-gradient(135deg,var(--blue-1),var(--blue-2));
                flex:none;
            }}

            .table-shell {{
                overflow:hidden;
                margin:18px 22px 22px;
            }}

            .table-head {{
                padding:22px 22px 10px;
                display:flex;
                justify-content:space-between;
                gap:16px;
                align-items:flex-end;
                flex-wrap:wrap;
            }}

            .table-head p {{
                margin:0;
                color:var(--muted);
                max-width:68ch;
                line-height:1.6;
            }}

            .table-wrap {{
                overflow:auto;
            }}

            table {{
                width:100%;
                border-collapse:separate;
                border-spacing:0;
                min-width:760px;
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
            }}

            .mono {{
                font-variant-numeric:tabular-nums;
                font-feature-settings:'tnum';
                white-space:nowrap;
                font-weight:800;
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

            .author-card,
            .books-card,
            .contact-card {{
                margin:18px 22px 22px;
                padding:22px;
            }}

            .author-card-inner {{
                display:flex;
                gap:20px;
                align-items:flex-start;
                flex-wrap:wrap;
            }}

            .author-photo {{
                width:108px;
                height:108px;
                border-radius:999px;
                object-fit:cover;
                flex-shrink:0;
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

            @media (max-width:1180px) {{
                .hero,
                .story-layout {{
                    grid-template-columns:1fr;
                }}

                .metrics-grid {{
                    grid-template-columns:repeat(3,1fr);
                }}

                .alerts-grid {{
                    grid-template-columns:1fr;
                }}
            }}

            @media (max-width:820px) {{
                .hero-side {{
                    grid-template-columns:1fr;
                }}

                .metrics-grid {{
                    grid-template-columns:1fr 1fr;
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

                .table-shell,
                .author-card,
                .books-card,
                .contact-card,
                .empty-state {{
                    margin:16px;
                    padding:16px;
                }}

                .story-layout {{
                    padding:8px 16px 16px;
                }}

                .metrics-grid {{
                    grid-template-columns:1fr;
                    padding:16px 16px 4px;
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
                    justify-content:center;
                    text-align:center;
                }}

                .author-copy {{
                    min-width:0;
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
            }}

            @media (max-width:560px) {{
                .metrics-grid {{
                    grid-template-columns:1fr;
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
                        <h1>Informe financiero ejecutivo</h1>
                    </div>
                    <div class="company-meta">
                        <div class="chip">Archivos analizados: {total}</div>
                        <div class="chip">Documentos clasificados: {total_docs_clasificados}</div>
                        <div class="chip">Modo branding: {BRANDING["modo"]}</div>
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
                                <div class="metric-label">Entradas</div>
                                <div class="metric-value">€ {fmt(flujo["entradas"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Actividad detectada</span>
                                <span>Ledger</span>
                            </div>
                        </article>

                        <article class="metric-card metric-in">
                            <div>
                                <div class="metric-label">Salidas</div>
                                <div class="metric-value">€ {fmt(flujo["salidas"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Impacto en caja</span>
                                <span>Ledger</span>
                            </div>
                        </article>

                        <article class="metric-card metric-out">
                            <div>
                                <div class="metric-label">Pendiente de cobro</div>
                                <div class="metric-value">€ {fmt(conc["pendiente_cobro"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Conciliación</span>
                                <span>Por revisar</span>
                            </div>
                        </article>

                        <article class="metric-card metric-end">
                            <div>
                                <div class="metric-label">Balance preliminar</div>
                                <div class="metric-value">€ {fmt(flujo["balance"])}</div>
                            </div>
                            <div class="metric-delta">
                                <span>Resultado neto</span>
                                <span>Preliminar</span>
                            </div>
                        </article>
                    </div>
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Resumen ejecutivo</h3>
                            <p class="section-sub">Vista sintética del flujo, calidad de conciliación y puntos de atención más relevantes para la gestión del negocio.</p>
                        </div>
                    </div>

                    <div class="metrics-grid">
                        <article class="kpi">
                            <div class="label">Movimientos bancarios</div>
                            <div class="amount">€ {fmt(flujo["movimientos"])}</div>
                            <div class="meta"><span class="trend up">Detectados</span><span>Ledger</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Por revisar</div>
                            <div class="amount">€ {fmt(flujo["revisar"])}</div>
                            <div class="meta"><span class="trend warn">Pendiente</span><span>Clasificación</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Conciliadas</div>
                            <div class="amount">{conc["conciliadas"]}</div>
                            <div class="meta"><span class="trend up">Estado</span><span>Facturas</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Parciales</div>
                            <div class="amount">{conc["parciales"]}</div>
                            <div class="meta"><span class="trend warn">Revisar</span><span>Coincidencias</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Pendientes</div>
                            <div class="amount">{conc["pendientes"]}</div>
                            <div class="meta"><span class="trend down">Atención</span><span>Conciliación</span></div>
                        </article>
                    </div>

                    <div class="story-layout">
                        <article class="story-card">
                            <h3>Qué muestra este procesamiento</h3>
                            <p>El sistema ya transforma documentación comercial dispersa en una lectura financiera preliminar útil para gestión. A partir de facturas, extractos y otros soportes, identifica entradas, salidas, movimientos, pendientes y una primera estructura de conciliación.</p>
                            <p>En esta ejecución, las entradas preliminares alcanzan € {fmt(flujo["entradas"])} y las salidas € {fmt(flujo["salidas"])}, con un balance preliminar de € {fmt(flujo["balance"])}. El importe pendiente total en conciliación asciende a € {fmt(conc["importe_pendiente"])}.</p>
                            <p>La utilidad principal de este informe es acelerar la revisión ejecutiva: detectar huecos de documentación, observar presión sobre caja y priorizar qué documentos deben revisarse primero antes de cerrar conclusiones financieras definitivas.</p>
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
                            </div>
                        </aside>
                    </div>

                    <section class="alerts-grid">
                        <article class="alert-card green">
                            <div class="alert-tag">Bien</div>
                            <h4>Documentación ya estructurada</h4>
                            <p>El sistema clasifica documentos y organiza una base financiera inicial que reduce trabajo manual y acelera la revisión gerencial.</p>
                        </article>

                        <article class="alert-card yellow">
                            <div class="alert-tag">Revisar</div>
                            <h4>Pendientes de conciliación</h4>
                            <p>Hay {conc["pendientes"]} registros pendientes y un importe asociado de € {fmt(conc["importe_pendiente"])}, por lo que aún conviene validar antes de cerrar conclusiones.</p>
                        </article>

                        <article class="alert-card red">
                            <div class="alert-tag">Atención</div>
                            <h4>Resultado todavía preliminar</h4>
                            <p>Este informe no sustituye una revisión contable final. Su valor está en orientar la toma de decisiones y señalar prioridades de verificación.</p>
                        </article>
                    </section>
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Documentos e importes detectados</h3>
                            <p class="section-sub">Visibilidad estructurada sobre los documentos reconocidos por el sistema y los importes extraídos durante el procesamiento.</p>
                        </div>
                    </div>
                    {documentos_html()}
                    {importes_html()}
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Movimiento financiero base</h3>
                            <p class="section-sub">Trazabilidad preliminar del flujo de caja construida a partir del ledger generado automáticamente.</p>
                        </div>
                    </div>
                    {tabla_ledger_html()}
                </section>

                <section class="section">
                    <div class="section-head">
                        <div>
                            <h3 class="section-title">Conciliación</h3>
                            <p class="section-sub">Resumen de coincidencias, pendientes y diferencias detectadas entre documentos y movimientos.</p>
                        </div>
                    </div>

                    <div class="metrics-grid">
                        <article class="kpi">
                            <div class="label">Facturas conciliadas</div>
                            <div class="amount">{conc["conciliadas"]}</div>
                            <div class="meta"><span class="trend up">Correcto</span><span>Estado</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Parcialmente conciliadas</div>
                            <div class="amount">{conc["parciales"]}</div>
                            <div class="meta"><span class="trend warn">Revisión</span><span>Estado</span></div>
                        </article>

                        <article class="kpi">
                            <div class="label">Facturas pendientes</div>
                            <div class="amount">{conc["pendientes"]}</div>
                            <div class="meta"><span class="trend down">Pendiente</span><span>Control</span></div>
                        </article>

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
                            <strong>PYME Financial Analyzer</strong> · Informe financiero visual para revisión ejecutiva, control documental y lectura preliminar de caja.
                        </div>
                        <div class="footer-right">
                            <span class="footer-pill">Archivos: {total}</span>
                            <span class="footer-pill">Clasificados: {total_docs_clasificados}</span>
                            <span class="footer-pill">Modo: {BRANDING["modo"]}</span>
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
    </body>
    </html>
    """

    return html
