from flask import Flask, request
import os
import zipfile
from pypdf import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTRACT_FOLDER = "extracted"
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

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

    for root, dirs, files in os.walk(extract_subfolder):
        for filename in files:
            total_files += 1
            nombre = filename.lower()
            texto_pdf = ""

            if filename.lower().endswith(".pdf"):
                try:
                    ruta_pdf = os.path.join(root, filename)
                    reader = PdfReader(ruta_pdf)

                    for page in reader.pages:
                        contenido = page.extract_text()
                        if contenido:
                            texto_pdf += contenido.lower()
                except Exception:
                    pass

            if ("factura" in nombre or "invoice" in texto_pdf) and ("venta" in nombre or "total" in texto_pdf):
                clasificados["factura_venta"].append(filename)
            elif "factura" in nombre or "invoice" in texto_pdf:
                clasificados["factura_compra"].append(filename)
            elif "banco" in nombre or "extracto" in nombre or "saldo" in texto_pdf:
                clasificados["extracto_bancario"].append(filename)
            else:
                clasificados["otros"].append(filename)

    def generar_lista(lista):
        return "".join(f"<li>{item}</li>" for item in lista) if lista else "<li>No hay</li>"

    return f"""
    <h2>Procesamiento completado</h2>

    <p><strong>Archivo:</strong> {file.filename}</p>
    <p><strong>Total de archivos:</strong> {total_files}</p>

    <h3>📄 Facturas de venta</h3>
    <ul>{generar_lista(clasificados["factura_venta"])}</ul>

    <h3>🧾 Facturas de compra</h3>
    <ul>{generar_lista(clasificados["factura_compra"])}</ul>

    <h3>🏦 Extractos bancarios</h3>
    <ul>{generar_lista(clasificados["extracto_bancario"])}</ul>

    <h3>📁 Otros documentos</h3>
    <ul>{generar_lista(clasificados["otros"])}</ul>

    <br>
    <a href="/">⬅ Volver a la landing</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
