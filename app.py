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

        header_row = None

        # localizar linha que contém "Produto"
        for i in range(len(df)):
            linha = df.iloc[i].astype(str).str.lower()

            if "produto" in " ".join(linha):
                header_row = i
                break

        if header_row is None:
            continue

        # recriar dataframe com header correto
        df = pd.read_excel(file, header=header_row)

        for _, row in df.iterrows():

            produto = str(row.get("Produto", "")).strip()
            operacao = str(row.get("Operação", "")).lower()

            if "total" in operacao and produto != "nan":

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

        resultado += "Nenhum dado TEF encontrado<br>"

    return resultado
