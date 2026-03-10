from flask import Flask, render_template, request
import pandas as pd
import os

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

        if isinstance(valor, (int, float)):
            return float(valor)

        valor = str(valor)

        if "," in valor and "." in valor:
            valor = valor.replace(".", "").replace(",", ".")

        elif "," in valor:
            valor = valor.replace(",", ".")

        return float(valor)

    except:
        return 0


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")
    tef_files = request.files.getlist("tef_files")

    resumo_tef = {}

    for file in tef_files:

        df = pd.read_excel(file, header=None)

        linha_produto = None
        linha_header = None

        for i in range(len(df)):

            linha = df.iloc[i].astype(str).str.lower()

            if "produto" in " ".join(linha):
                linha_header = i

        if linha_header is None:
            continue

        df = pd.read_excel(file, header=linha_header)

        for _, row in df.iterrows():

            produto = str(row.get("Produto", "")).strip()
            operacao = str(row.get("Operação", "")).lower()

            if "total" in operacao and produto != "nan":

                valor = converter_valor(row.get("Confirmadas", 0))

                if produto not in resumo_tef:
                    resumo_tef[produto] = 0

                resumo_tef[produto] += valor

    resultado = f"<h1>Conciliação - Loja {loja}</h1>"
    resultado += "<h2>Resumo TEF</h2>"

    if resumo_tef:

        for produto, valor in resumo_tef.items():

            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado += f"{produto}: R$ {valor_formatado}<br>"

    else:

        resultado += "Nenhum dado TEF encontrado<br>"

    return resultado
