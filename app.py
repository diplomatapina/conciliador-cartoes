from flask import Flask, request
import pandas as pd

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>Sistema de Conciliação</h1>

    <form action="/conciliar" method="post" enctype="multipart/form-data">

    Loja:
    <select name="loja">
        <option>Pina</option>
        <option>Navegantes</option>
        <option>Setubal</option>
        <option>Conselheiro</option>
        <option>Exclusive</option>
    </select>

    <br><br>

    Relatórios TEF:
    <input type="file" name="tef_files" multiple>

    <br><br>

    <button type="submit">Conciliar</button>

    </form>
    """


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

    arquivos = request.files.getlist("tef_files")

    resumo = {}

    for file in arquivos:

        df = pd.read_excel(file, header=None)

        ultimo_produto = None

        for _, row in df.iterrows():

            linha = [str(x).strip() for x in row]

            for item in linha:

                item = item.lower()

                if item in [
                    "pix",
                    "ticket alimentacao",
                    "ticket alimentação",
                    "ticket restaurante",
                    "alelo alimentação",
                    "alelo alimentacao",
                    "alelo refeicao",
                    "alelo refeição",
                    "amex credito",
                    "amex crédito"
                ]:

                    ultimo_produto = item

            if "total" in " ".join(linha).lower() and ultimo_produto:

                valor = 0

                for item in linha:

                    v = converter_valor(item)

                    if v > 0:
                        valor = v
                        break

                if ultimo_produto not in resumo:
                    resumo[ultimo_produto] = 0

                resumo[ultimo_produto] += valor

    resultado = f"<h2>Conciliação - Loja {loja}</h2>"

    for produto, valor in resumo.items():

        valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        resultado += f"{produto}: R$ {valor_formatado}<br>"

    return resultado
