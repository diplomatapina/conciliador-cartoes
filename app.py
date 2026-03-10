from flask import Flask, request, render_template_string
import pandas as pd
import io

app = Flask(__name__)

HTML = """
<h2>Sistema de Conciliação</h2>

<form method="post" action="/conciliar" enctype="multipart/form-data">

<p>Relatório TEF</p>
<input type="file" name="tef"><br><br>

<p>Relatório Maquineta</p>
<input type="file" name="maquineta"><br><br>

<p>Extrato Bancário</p>
<input type="file" name="extrato"><br><br>

<button type="submit">Conciliar</button>

</form>

{% if resultado %}
<h3>Resultado</h3>
{{resultado|safe}}
{% endif %}
"""


# ----------------------------
# LEITOR TEF
# ----------------------------

def carregar_tef(file):

    df = pd.read_csv(
        file,
        sep=";",
        encoding="latin1",
        skiprows=4
    )

    df.columns = df.columns.str.replace('"','').str.strip()

    df["Valor"] = (
        df["Valor"]
        .astype(str)
        .str.replace(",",".")
        .astype(float)
    )

    df = df[df["Estado Transação"].str.contains("Efetuada", na=False)]

    return df


# ----------------------------
# LEITOR MAQUINETA
# ----------------------------

def carregar_maquineta(file):

    if file.filename.endswith("xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    return df


# ----------------------------
# LEITOR EXTRATO
# ----------------------------

def carregar_extrato(file):

    if file.filename.endswith("xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    return df


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)


@app.route("/conciliar", methods=["POST"])
def conciliar():

    resultado = ""

    # -------------------
    # TEF
    # -------------------

    if "tef" in request.files:

        file = request.files["tef"]

        stream = io.StringIO(file.stream.read().decode("latin1"))

        tef = carregar_tef(stream)

        total_tef = tef["Valor"].sum()

        resultado += f"<p>Total TEF: R$ {total_tef:,.2f}</p>"


    # -------------------
    # MAQUINETA
    # -------------------

    if "maquineta" in request.files:

        file = request.files["maquineta"]

        maq = carregar_maquineta(file)

        if "Valor" in maq.columns:

            maq["Valor"] = (
                maq["Valor"]
                .astype(str)
                .str.replace(",",".")
                .astype(float)
            )

            total_maq = maq["Valor"].sum()

            resultado += f"<p>Total Maquineta: R$ {total_maq:,.2f}</p>"


    # -------------------
    # EXTRATO
    # -------------------

    if "extrato" in request.files:

        file = request.files["extrato"]

        ext = carregar_extrato(file)

        if "Valor" in ext.columns:

            ext["Valor"] = (
                ext["Valor"]
                .astype(str)
                .str.replace(",",".")
                .astype(float)
            )

            total_ext = ext["Valor"].sum()

            resultado += f"<p>Total Extrato: R$ {total_ext:,.2f}</p>"


    return render_template_string(HTML, resultado=resultado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
