from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

lojas = [
    "Pina",
    "Navegantes",
    "Setubal",
    "Conselheiro",
    "Exclusive"
]


@app.route("/")
def index():
    return render_template("index.html", lojas=lojas)


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")
    tef_files = request.files.getlist("tef_files")

    resultado = f"<h1>Diagnóstico TEF - Loja {loja}</h1>"

    for file in tef_files:

        resultado += "<h2>Arquivo recebido</h2>"

        try:

            df = pd.read_excel(file)

            resultado += "<b>Colunas detectadas:</b><br>"
            resultado += str(list(df.columns)) + "<br><br>"

            resultado += "<b>Primeiras linhas:</b><br>"

            resultado += df.head(10).to_html()

        except Exception as e:

            resultado += f"Erro lendo arquivo: {e}"

    return resultado


if __name__ == "__main__":
    app.run(debug=True)
