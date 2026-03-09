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
    maquineta_files = request.files.getlist("maquineta_files")
    extrato_file = request.files.get("extrato_file")

    resumo_tef = {}

    for file in tef_files:

        try:

            df = pd.read_excel(file)

            # localizar colunas automaticamente
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

            if not col_produto or not col_valor:
                continue

            ultimo_produto = None

            for index, row in df.iterrows():

                produto = str(row[col_produto]).strip()

                operacao = ""
                if col_operacao:
                    operacao = str(row[col_operacao]).strip().lower()

                valor = converter_valor(row[col_valor])

                if produto and produto != "nan":
                    ultimo_produto = produto

                # aceita qualquer texto que contenha "total"
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

    resultado += "<br><h2>Arquivos recebidos</h2>"
    resultado += f"Arquivos TEF enviados: {len(tef_files)}<br>"
    resultado += f"Arquivos Maquineta enviados: {len(maquineta_files)}<br>"
    resultado += f"Extrato enviado: {'Sim' if extrato_file else 'Não'}<br>"

    return resultado


if __name__ == "__main__":
    app.run(debug=True)
