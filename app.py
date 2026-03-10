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

    <p>
    Upload relatórios Maquineta (PDF):<br>
    <input type="file" name="maquineta_files" multiple>
    </p>

    <p>
    Upload extrato bancário (CSV):<br>
    <input type="file" name="extrato_file">
    </p>

    <button type="submit">Conciliar</button>

    </form>
    """


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")
    tef_files = request.files.getlist("tef_files")

    resumo = {}

    for arquivo in tef_files:

        df = pd.read_excel(arquivo, header=None)

        produto_atual = None

        for i in range(7, len(df)):

            produto = str(df.iloc[i,3])
            operacao = str(df.iloc[i,5]).lower()
            valor = df.iloc[i,6]

            if produto != "nan":
                produto_atual = produto

            if "total" in operacao:

                try:
                    valor = float(valor)
                except:
                    valor = 0

                resumo[produto_atual] = resumo.get(produto_atual, 0) + valor

    resultado = f"<h2>Conciliação - Loja {loja}</h2>"

    for produto, valor in resumo.items():

        valor = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

        resultado += f"{produto}: R$ {valor}<br>"

    return resultado


if __name__ == "__main__":
    app.run(debug=True)
