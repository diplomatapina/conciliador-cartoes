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
    maquineta_files = request.files.getlist("maquineta_files")
    extrato_file = request.files.get("extrato_file")

    resumo_tef = {}

    for file in tef_files:

        try:

            df = pd.read_excel(file, skiprows=6)

            ultimo_produto = None

            for index, row in df.iterrows():

                produto = str(row.get("Produto", "")).strip()
                operacao = str(row.get("Operação", "")).strip()
                valor = row.get("Confirmadas", 0)

                if produto:
                    ultimo_produto = produto

                if operacao == "Total" and ultimo_produto:

                    if ultimo_produto not in resumo_tef:
                        resumo_tef[ultimo_produto] = 0

                    try:
                        resumo_tef[ultimo_produto] += float(valor)
                    except:
                        pass

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
