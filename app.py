from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>PYME Financial Analyzer</h1>
    <p>El sistema está funcionando correctamente.</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
