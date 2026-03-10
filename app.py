from flask import Flask, request
import pandas as pd
import unicodedata

app = Flask(__name__)


def normalizar_texto(txt):
    txt = str(txt).strip().lower()
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return txt


def encontrar_header(df):
    for i in range(len(df)):
        linha = [normalizar_texto(x) for x in df.iloc[i]]
        if "produto" in linha and ("operacao" in linha or "operação" in linha):
            return i
    return None


def identificar_colunas(df):
    col_produto = None
    col_operacao = None
    col_valor = None

    for c in df.columns:
        n = normalizar_texto(c)

        if "produto" in n:
            col_produto = c
        if "operacao" in n:
            col_operacao = c
        if "confirm" in n or "valor" in n:
            col_valor = c

    return col_produto, col_operacao, col_valor


@app.route("/")
def home():
    return """
    <h1>Sistema de Conciliação</h1>

    <form action="/conciliar" method="post" enctype="multipart/form-data">

    <p>
    <label>Selecione a loja:</label><br>
    <select name="loja">
        <option>Pina</option>
        <option>Navegantes</option>
        <option>Setubal</option>
        <option>Conselheiro</option>
        <option>Exclusive</option>
    </select>
    </p>

    <p>
    <label>Upload relatórios TEF (Excel):</label><br>
    <input type="file" name="tef_files" multiple>
    </p>

    <p>
    <label>Upload relatórios Maquineta (PDF):</label><br>
    <input type="file" name="maquineta_files" multiple>
    </p>

    <p>
    <label>Upload extrato bancário (CSV):</label><br>
    <input type="file" name="extrato_file">
    </p>

    <button type="submit">Conciliar</button>

    </form>
    """


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")
    arquivos = request.files.getlist("tef_files")

    resumo = {}

    for arquivo in arquivos:

        df_raw = pd.read_excel(arquivo, header=None)

        header_row = encontrar_header(df_raw)
        if header_row is None:
            continue

        df = pd.read_excel(arquivo, header=header_row)

        col_produto, col_operacao, col_valor = identificar_colunas(df)

        if not col_produto or not col_operacao or not col_valor:
            continue

        produto_atual = None

        for _, row in df.iterrows():

            produto = str(row[col_produto]).strip()
            operacao = normalizar_texto(row[col_operacao])

            if produto and produto.lower() != "nan":
                produto_atual = produto

            if "total" in operacao and produto_atual:

                try:
                    valor = float(row[col_valor])
                except:
                    valor = 0

                resumo[produto_atual] = resumo.get(produto_atual, 0) + valor

    resultado = f"<h2>Conciliação - Loja {loja}</h2>"

    if resumo:
        for produto, valor in resumo.items():
            valor_fmt = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            resultado += f"{produto}: R$ {valor_fmt}<br>"
    else:
        resultado += "Nenhum dado encontrado"

    return resultado
