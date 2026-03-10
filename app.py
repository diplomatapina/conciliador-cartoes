from flask import Flask, request
import pandas as pd
import io

app = Flask(__name__)

@app.route("/")
def home():

    return """
    <h2>Sistema de Conciliação</h2>

    <form action="/conciliar" method="post" enctype="multipart/form-data">

    <p>Relatório TEF</p>
    <input type="file" name="tef"><br><br>

    <p>Relatório Maquineta</p>
    <input type="file" name="maquineta"><br><br>

    <p>Extrato Bancário</p>
    <input type="file" name="extrato"><br><br>

    <button type="submit">Conciliar</button>

    </form>
    """


@app.route("/conciliar", methods=["POST"])
def conciliar():

    resultado = "<h2>Resultado</h2>"

    # ----------------
    # TEF
    # ----------------

    if "tef" in request.files:

        file = request.files["tef"]

        if file.filename != "":

            stream = io.StringIO(file.stream.read().decode("latin1"))

            df = pd.read_csv(
                stream,
                sep=";",
                encoding="latin1",
                skiprows=4
            )

            df.columns = df.columns.str.replace('"','').str.strip()

            if "Valor" in df.columns:

                df["Valor"] = (
                    df["Valor"]
                    .astype(str)
                    .str.replace(",",".")
                    .astype(float)
                )

                total = df["Valor"].sum()

                resultado += f"<p>Total TEF: R$ {total:,.2f}</p>"

    return resultado


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
