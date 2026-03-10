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
    Relatórios TEF:<br>
    <input type="file" name="tef_files" multiple>
    </p>

    <button type="submit">Conciliar</button>

    </form>
    """


def encontrar_header(df):

    for i in range(len(df)):

        linha = df.iloc[i].astype(str).str.lower().tolist()

        if "produto" in linha and "operação" in linha:

            return i

    return None


@app.route("/conciliar", methods=["POST"])
def conciliar():

    arquivos = request.files.getlist("tef_files")

    resumo = {}

    for arquivo in arquivos:

        df_bruto = pd.read_excel(arquivo, header=None)

        header = encontrar_header(df_bruto)

        if header is None:
            continue

        df = pd.read_excel(arquivo, header=header)

        produto_atual = None

        for _, row in df.iterrows():

            produto = str(row.get("Produto", "")).strip()
            operacao = str(row.get("Operação", "")).lower()

            if produto and produto != "nan":
                produto_atual = produto

            if "total" in operacao:

                valor = row.get("Confirmadas", 0)

                try:
                    valor = float(valor)
                except:
                    valor = 0

                resumo[produto_atual] = resumo.get(produto_atual, 0) + valor

    resultado = "<h2>Conciliação - Loja Pina</h2>"

    if resumo:

        for produto, valor in resumo.items():

            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado += f"{produto}: R$ {valor_formatado}<br>"

    else:

        resultado += "Nenhum dado encontrado"

    return resultado
