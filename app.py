from flask import Flask, request, render_template_string
import pandas as pd
import io

app = Flask(__name__)

HTML = """
<h2>Conciliação TEF</h2>

<form method="post" action="/conciliar" enctype="multipart/form-data">
    <p>Relatório TEF:</p>
    <input type="file" name="tef">
    <br><br>
    <button type="submit">Conciliar</button>
</form>

{% if tabela %}
<h3>Resumo</h3>
{{ tabela|safe }}

<h3>Total</h3>
<p><b>{{ total }}</b></p>
{% endif %}
"""


def carregar_tef(file):

    df = pd.read_csv(
        file,
        sep=";",
        encoding="latin1",
        skiprows=4
    )

    # limpar nomes das colunas
    df.columns = df.columns.str.replace('"', '').str.strip()

    # garantir que coluna valor existe
    if "Valor" in df.columns:

        df["Valor"] = (
            df["Valor"]
            .astype(str)
            .str.replace(",", ".")
            .astype(float)
        )

    # converter data se existir
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)

    # manter apenas aprovadas
    if "Estado Transação" in df.columns:
        df = df[df["Estado Transação"].str.contains("Efetuada", na=False)]

    return df


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)


@app.route("/conciliar", methods=["POST"])
def conciliar():

    if "tef" not in request.files:
        return "Arquivo TEF não enviado"

    file = request.files["tef"]

    if file.filename == "":
        return "Arquivo inválido"

    stream = io.StringIO(file.stream.read().decode("latin1"))

    df = carregar_tef(stream)

    if "Tipo Produto" in df.columns:

        resumo = (
            df.groupby("Tipo Produto")["Valor"]
            .sum()
            .reset_index()
        )

    else:
        resumo = df

    tabela = resumo.to_html(index=False)

    total = f"R$ {df['Valor'].sum():,.2f}"

    return render_template_string(
        HTML,
        tabela=tabela,
        total=total
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
