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


def normalizar_colunas(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")
    arquivos = request.files.getlist("tef_files")

    resumo = {}

    for arquivo in arquivos:

        # encontrar linha do cabeçalho
        df_temp = pd.read_excel(arquivo, header=None)

        header_row = None
        for i in range(len(df_temp)):
            linha = df_temp.iloc[i].astype(str).str.lower().tolist()
            if "produto" in linha and "operação" in linha:
                header_row = i
                break

        if header_row is None:
            continue

        # ler novamente com header correto
        df = pd.read_excel(arquivo, header=header_row)
        df = normalizar_colunas(df)

        produto_atual = None

        for _, row in df.iterrows():

            produto = str(row.get("produto", "")).strip()
            operacao = str(row.get("operação", "")).lower()

            if produto and produto != "nan":
                produto_atual = produto

            if "total" in operacao and produto_atual:

                valor = row.get("confirmadas", 0)

                try:
                    valor = float(valor)
                except:
                    valor = 0

                if produto_atual not in resumo:
                    resumo[produto_atual] = 0

                resumo[produto_atual] += valor

    resultado = f"<h2>Conciliação - Loja {loja}</h2>"

    if resumo:

        for produto, valor in resumo.items():

            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado += f"{produto}: R$ {valor_formatado}<br>"

    else:

        resultado += "Nenhum dado encontrado"

    return resultado
