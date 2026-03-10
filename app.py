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
        <option>Navegantes</option>
        <option>Setubal</option>
        <option>Conselheiro</option>
        <option>Exclusive</option>
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


def encontrar_header(df):

    for i in range(len(df)):

        linha = df.iloc[i].astype(str).str.lower().tolist()

        if "produto" in linha and "operação" in linha:
            return i

    return None


@app.route("/conciliar", methods=["POST"])
def conciliar():

    loja = request.form.get("loja")

    tef_files = request.files.getlist("tef_files")
    maquineta_files = request.files.getlist("maquineta_files")
    extrato_file = request.files.get("extrato_file")

    resumo_tef = {}

    # ----------- PROCESSAR TEF -----------

    for arquivo in tef_files:

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

                resumo_tef[produto_atual] = resumo_tef.get(produto_atual, 0) + valor

    # ----------- RESULTADO -----------

    resultado = f"<h2>Conciliação - Loja {loja}</h2>"

    resultado += "<h3>Resumo TEF</h3>"

    if resumo_tef:

        for produto, valor in resumo_tef.items():

            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado += f"{produto}: R$ {valor_formatado}<br>"

    else:

        resultado += "Nenhum dado TEF encontrado<br>"

    # ----------- STATUS ARQUIVOS -----------

    resultado += "<h3>Arquivos recebidos</h3>"

    resultado += f"Arquivos TEF enviados: {len(tef_files)}<br>"
    resultado += f"Arquivos Maquineta enviados: {len(maquineta_files)}<br>"

    if extrato_file and extrato_file.filename:
        resultado += "Extrato enviado: Sim<br>"
    else:
        resultado += "Extrato enviado: Não<br>"

    return resultado


if __name__ == "__main__":
    app.run(debug=True)
