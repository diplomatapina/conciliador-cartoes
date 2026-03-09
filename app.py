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


def converter_valor(valor):
    try:
        if isinstance(valor, str):
            valor = valor.replace(".", "").replace(",", ".")
        return float(valor)
    except:
        return 0


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")

    tef_files = request.files.getlist("tef_files")

    resumo_tef = {}

    for file in tef_files:

        try:

            # ignorar as primeiras linhas do relatório
            df = pd.read_excel(file, skiprows=5)

            ultimo_produto = None

            for index, row in df.iterrows():

                produto = str(row[3]).strip()
                operacao = str(row[5]).strip().lower()
                valor = converter_valor(row[6])

                if produto and produto != "nan":
                    ultimo_produto = produto

                if "total" in operacao and ultimo_produto:

                    if ultimo_produto not in resumo_tef:
                        resumo_tef[ultimo_produto] = 0

                    resumo_tef[ultimo_produto] += valor

        except Exception as e:
            print("Erro lendo TEF:", e)

    resultado = f"<h1>Conciliação - Loja {loja}</h1>"

    resultado += "<h2>Resumo TEF</h2>"

    if resumo_tef:

        for produto, valor in resumo_tef.items():
            resultado += f"{produto}: R$ {valor:,.2f}<br>"

    else:
        resultado += "Nenhum dado TEF encontrado<br>"

    return resultado


if __name__ == "__main__":
    app.run(debug=True)
