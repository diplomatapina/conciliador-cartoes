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


def encontrar_cabecalho(df):

    for i in range(len(df)):

        linha = df.iloc[i].astype(str).str.lower()

        if linha.str.contains("produto").any():
            return i

    return None


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")

    tef_files = request.files.getlist("tef_files")

    resumo_tef = {}

    for file in tef_files:

        try:

            df = pd.read_excel(file, header=None)

            linha_cabecalho = encontrar_cabecalho(df)

            if linha_cabecalho is None:
                continue

            df = pd.read_excel(file, header=linha_cabecalho)

            col_produto = None
            col_operacao = None
            col_valor = None

            for col in df.columns:

                nome = str(col).lower()

                if "produto" in nome:
                    col_produto = col

                if "opera" in nome:
                    col_operacao = col

                if "confirm" in nome:
                    col_valor = col

            if not col_produto or not col_operacao or not col_valor:
                continue

            ultimo_produto = None

            for _, row in df.iterrows():

                produto = str(row[col_produto]).strip()
                operacao = str(row[col_operacao]).strip().lower()
                valor = converter_valor(row[col_valor])

                if produto and produto != "nan":
                    ultimo_produto = produto

                if "total" in operacao and ultimo_produto:

                    if ultimo_produto not in resumo_tef:
                        resumo_tef[ultimo_produto] = 0

                    resumo_tef[ultimo_produto] += valor

        except Exception as e:
            print("Erro lendo arquivo:", e)

    resultado = f"<h1>Conciliação - Loja {loja}</h1>"
    resultado += "<h2>Resumo TEF</h2>"

    if resumo_tef:

        for produto, valor in resumo_tef.items():

            resultado += f"{produto}: R$ {valor:,.2f}<br>"

    else:

        resultado += "Nenhum dado TEF encontrado<br>"

    return resultado
