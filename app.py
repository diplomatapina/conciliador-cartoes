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

            df = pd.read_excel(file, header=None)

            ultimo_produto = None

            for _, row in df.iterrows():

                linha = [str(x).strip() for x in row]

                # detectar produto
                for item in linha:

                    if item.lower() in [
                        "pix",
                        "ticket alimentacao",
                        "ticket flex",
                        "ticket restaurante",
                        "alelo alimentação",
                        "alelo refeicao",
                        "amex credito",
                    ]:

                        ultimo_produto = item

                # detectar linha total
                if "total" in " ".join(linha).lower() and ultimo_produto:

                    valor = 0

                    for item in linha:

                        try:
                            valor = converter_valor(item)

                            if valor > 0:
                                break
                        except:
                            pass

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
