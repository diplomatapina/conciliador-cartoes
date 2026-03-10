from flask import Flask, request
import pandas as pd

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Sistema de Conciliação</h1>

    <form action="/conciliar" method="post" enctype="multipart/form-data">

    <p>
    Loja:<br>
    <select name="loja">
        <option>Pina</option>
    </select>
    </p>

    <p>
    Upload relatórios TEF (Excel):<br>
    <input type="file" name="tef_files" multiple>
    </p>

    <button type="submit">Conciliar</button>

    </form>
    """

@app.route("/conciliar", methods=["POST"])
def conciliar():

    arquivos = request.files.getlist("tef_files")

    resultado = "<h2>Diagnóstico do Excel</h2>"

    for arquivo in arquivos:

        df = pd.read_excel(arquivo, header=None)

        resultado += "<h3>Primeiras 15 linhas da planilha</h3>"
        resultado += df.head(15).to_html()

    return resultado


if __name__ == "__main__":
    app.run(debug=True)
