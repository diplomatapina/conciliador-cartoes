from flask import Flask, render_template, request

app = Flask(__name__)

lojas = [
    "Pina",
    "Navegantes",
    "Setubal",
    "Conselheiro",
    "Exclusive"
]

@app.route("/")
def index():
    return render_template("index.html", lojas=lojas)

@app.route("/conciliar", methods=["POST"])
def conciliar():
    loja = request.form.get("loja")
    return f"Conciliação iniciada para a loja: {loja}"

if __name__ == "__main__":
    app.run(debug=True)
