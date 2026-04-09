from flask import Flask, request, send_from_directory
import os
import zipfile

from extractor import extraer_texto_pdf
from clasificador import clasificar_documento
from parser_financiero import extraer_importes, extraer_fecha
from ledger import construir_ledger
from conciliador import detectar_inconsistencias
from reportes import generar_html_resultado
from pdf_report import generar_pdf_ejecutivo

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTRACT_FOLDER = "extracted"
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PYME Financial Analyzer</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                color: #1f2937;
            }
            .hero {
                background: linear-gradient(135deg, #0f172a, #1d4ed8);
                color: white;
                padding: 70px 20px;
                text-align: center;
            }
            .hero h1 {
                margin: 0 0 20px 0;
                font-size: 42px;
                line-height: 1.2;
            }
            .hero p {
                max-width: 800px;
                margin: 0 auto 30px auto;
                font-size: 20px;
                line-height: 1.6;
            }
            .cta-btn {
                display: inline-block;
                background: #f59e0b;
                color: #111827;
                padding: 16px 28px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: bold;
                font-size: 18px;
                border: none;
                cursor: pointer;
            }
            .section {
                max-width: 1100px;
                margin: 0 auto;
                padding: 60px 20px;
            }
            .section h2 {
                text-align: center;
                font-size: 32px;
                margin-bottom: 20px;
            }
            .section p.lead {
                text-align: center;
                font-size: 18px;
                max-width: 850px;
                margin: 0 auto 40px auto;
                line-height: 1.7;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            .card {
                background: white;
                padding: 25px;
                border-radius: 14px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            }
            .card h3 {
                margin-top: 0;
                font-size: 22px;
            }
            .card p {
                line-height: 1.6;
                font-size: 16px;
            }
            .outputs {
                background: #eaf1ff;
                border-radius: 16px;
                padding: 30px;
            }
            .footer-cta {
                text-align: center;
                padding: 60px 20px 80px 20px;
            }
            .footer-cta h2 {
                font-size: 34px;
                margin-bottom: 20px;
            }
            .footer-cta p {
                font-size: 18px;
                max-width: 800px;
                margin: 0 auto 30px auto;
                line-height: 1.6;
            }
            .upload-form {
                margin-top: 25px;
            }
            .file-input {
                margin-bottom: 15px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>

        <section class="hero">
            <h1>Convierte tus documentos en claridad financiera para tu PYME</h1>
            <p>
                Sube un único archivo ZIP con facturas, extractos y documentos administrativos,
                y recibe un análisis automático con dashboard visual de flujo de caja
                y resumen ejecutivo en PDF.
            </p>
            <a class="cta-btn" href="#subir">Subir ZIP ahora</a>
        </section>

        <section class="section">
            <h2>¿Qué hace este sistema?</h2>
            <p class="lead">
                Analiza automáticamente documentos financieros y administrativos de tu empresa,
                construye movimientos reales, concilia soportes y detecta pendientes,
                inconsistencias y señales críticas para la toma de decisiones.
            </p>

            <div class="cards">
                <div class="card">
                    <h3>Subida simple</h3>
                    <p>La PYME sube un solo archivo ZIP con facturas, extractos bancarios, extractos PayPal, recibos, nóminas y otros documentos.</p>
                </div>
                <div class="card">
                    <h3>Procesamiento automático</h3>
                    <p>El sistema lee PDFs, Excel y Word, extrae texto, clasifica documentos y construye un ledger completo movimiento por movimiento.</p>
                </div>
                <div class="card">
                    <h3>Detección inteligente</h3>
                    <p>Identifica cobros sin factura, pagos sin soporte, retenciones, pendientes y posibles inconsistencias contables o documentales.</p>
                </div>
            </div>
        </section>

        <section class="section">
            <div class="outputs">
                <h2>Outputs que recibe la PYME</h2>
                <div class="cards">
                    <div class="card">
                        <h3>Dashboard HTML</h3>
                        <p>Un informe visual, claro y profesional con flujo de caja, ingresos vs gastos, pendientes, inconsistencias y métricas clave.</p>
                    </div>
                    <div class="card">
                        <h3>Resumen ejecutivo PDF</h3>
                        <p>Un documento vistoso y directo, pensado para dueños de PYME, con hallazgos, problemas principales e insights accionables.</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="footer-cta" id="subir">
            <h2>Sube tu ZIP y obtén una radiografía financiera real</h2>
            <p>
                Una experiencia simple, limpia y profesional para transformar documentos dispersos
                en información útil para decidir mejor.
            </p>

            <form class="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                <input class="file-input" type="file" name="file" accept=".zip" required>
                <br>
                <button class="cta-btn" type="submit">Subir ZIP</button>
            </form>
        </section>

    </body>
    </html>
    """


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file:
        return "No se subió ningún archivo"

    if file.filename == "":
        return "No se seleccionó ningún archivo"

    if not file.filename.lower().endswith(".zip"):
        return "Solo se permiten archivos ZIP"

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    extract_subfolder = os.path.join(EXTRACT_FOLDER, os.path.splitext(file.filename)[0])
    os.makedirs(extract_subfolder, exist_ok=True)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_subfolder)

    total_files = 0
    clasificados = {
        "factura_venta": [],
        "factura_compra": [],
        "extracto_bancario": [],
        "otros": []
    }
    documentos = []
    importes_detectados = []

    for root, dirs, files in os.walk(extract_subfolder):
        for filename in files:
            total_files += 1
            ruta_archivo = os.path.join(root, filename)
            ruta_relativa = os.path.relpath(ruta_archivo, extract_subfolder)

            texto = ""
            if filename.lower().endswith(".pdf"):
                texto = extraer_texto_pdf(ruta_archivo)

            tipo = clasificar_documento(filename, texto)
            clasificados[tipo].append(filename)

            importes = extraer_importes(texto)
            fecha = extraer_fecha(f"{filename.lower()} {texto}")

            documentos.append({
                "archivo": ruta_relativa,
                "tipo": tipo,
                "fecha": fecha,
                "importes": importes,
                "texto": texto
            })

            if filename.lower().endswith(".pdf"):
                importes_detectados.append({
                    "archivo": ruta_relativa,
                    "importes": importes
                })

    ledger = construir_ledger(documentos)
    conciliacion = detectar_inconsistencias(ledger)

    html_resultado = generar_html_resultado(
        total=total_files,
        clasificados=clasificados,
        importes=importes_detectados,
        documentos=documentos,
        ledger=ledger,
        conciliacion=conciliacion
    )

    nombre_base = os.path.splitext(file.filename)[0]

    output_html_filename = f"{nombre_base}_analisis.html"
    output_html_path = os.path.join(OUTPUT_FOLDER, output_html_filename)

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_resultado)

    output_pdf_filename = f"{nombre_base}_reporte.pdf"
    output_pdf_path = os.path.join(OUTPUT_FOLDER, output_pdf_filename)

    generar_pdf_ejecutivo(
        pdf_path=output_pdf_path,
        nombre_zip=file.filename,
        clasificados=clasificados,
        ledger=ledger,
        conciliacion=conciliacion
    )

    enlaces_descarga = f"""
    <div style="margin: 24px 0 40px 0; display:flex; gap:12px; flex-wrap:wrap;">
        <a href="/outputs/{output_html_filename}" target="_blank"
           style="display:inline-block; background:#1d4ed8; color:white; padding:14px 22px;
                  border-radius:10px; text-decoration:none; font-weight:bold;">
            Descargar análisis HTML
        </a>

        <a href="/outputs/{output_pdf_filename}" target="_blank"
           style="display:inline-block; background:#16a34a; color:white; padding:14px 22px;
                  border-radius:10px; text-decoration:none; font-weight:bold;">
            Descargar PDF ejecutivo
        </a>
    </div>
    """

    return html_resultado + enlaces_descarga


@app.route("/outputs/<path:filename>")
def descargar_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
