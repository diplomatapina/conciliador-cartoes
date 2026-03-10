@app.route("/")
def home():
    return """
    <h1>Sistema de Conciliação</h1>

    <form action="/conciliar" method="post" enctype="multipart/form-data">

    <label>Selecione a loja:</label>
    <select name="loja">
        <option>Pina</option>
        <option>Navegantes</option>
        <option>Setubal</option>
        <option>Conselheiro</option>
        <option>Exclusive</option>
    </select>

    <br><br>

    <label>Upload relatórios TEF (Excel):</label><br>
    <input type="file" name="tef_files" multiple>

    <br><br>

    <label>Upload relatórios Maquineta (PDF):</label><br>
    <input type="file" name="maquineta_files" multiple>

    <br><br>

    <label>Upload extrato bancário (CSV):</label><br>
    <input type="file" name="extrato_file">

    <br><br>

    <button type="submit">Conciliar</button>

    </form>
    """
