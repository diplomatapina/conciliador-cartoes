from flask import Flask, request
import pandas as pd

app = Flask(__name__)


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


def converter_valor(v):
    try:
        if isinstance(v, (int, float)):
            return float(v)

        v = str(v)

        if "," in v and "." in v:
            v = v.replace(".", "").replace(",", ".")
        elif "," in v:
            v = v.replace(",", ".")

        return float(v)

    except:
        return 0


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")
    arquivos_tef = request.files.getlist("tef_files")

    resumo = {}

    for arquivo in arquivos_tef:

        df = pd.read_excel(arquivo, header=None)

        linha_header = None

        for i in range(len(df)):

            linha = df.iloc[i].astype(str).str.lower()

            if "produto" in linha.values:
                linha_header = i
                break

        if linha_header is None:
            continue

        df = pd.read_excel(arquivo, header=linha_header)

        for _, row in df.iterrows():

            produto = str(row.get("Produto", "")).strip()
            operacao = str(row.get("Operação", "")).lower()

            if produto == "" or produto == "nan":
                continue

            if "total" in operacao:

                valor = converter_valor(row.get("Confirmadas", 0))

                if produto not in resumo:
                    resumo[produto] = 0

                resumo[produto] += valor

    resultado = f"<h2>Conciliação - Loja {loja}</h2>"

    if resumo:

        for produto, valor in resumo.items():

            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado += f"{produto}: R$ {valor_formatado}<br>"

    else:

        resultado += "Nenhum dado encontrado"

    return resultado
