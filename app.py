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

        # já é número
        if isinstance(valor, (int, float)):
            return float(valor)

        valor = str(valor)

        # formato brasileiro
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

        try:

            df = pd.read_excel(file, header=None)

            ultimo_produto = None

            for _, row in df.iterrows():

                linha = [str(x).strip() for x in row]

                # detectar produtos
                for item in linha:

                    item_lower = item.lower()

                    if item_lower in [
                        "pix",
                        "ticket alimentacao",
                        "ticket alimentação",
                        "ticket flex",
                        "ticket restaurante",
                        "alelo alimentação",
                        "alelo alimentacao",
                        "alelo refeicao",
                        "alelo refeição",
                        "amex credito",
                        "amex crédito"
                    ]:

                        ultimo_produto = item

                # detectar linha TOTAL
                if "total" in " ".join(linha).lower() and ultimo_produto:

                    valor = 0

                    for item in linha:

                        v = converter_valor(item)

                        if v > 0:
                            valor = v
                            break

                    if ultimo_produto not in resumo_tef:
                        resumo_tef[ultimo_produto] = 0

                    resumo_tef[ultimo_produto] += valor

        except Exception as e:
            print("Erro lendo arquivo:", e)

    resultado = f"<h1>Conciliação - Loja {loja}</h1>"
    resultado += "<h2>Resumo TEF</h2>"

    if resumo_tef:

        for produto, valor in resumo_tef.items():

            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado += f"{produto}: R$ {valor_formatado}<br>"

    else:

        resultado += "Nenhum dado TEF encontrado<br>"

    return resultado


if __name__ == "__main__":
    app.run()
