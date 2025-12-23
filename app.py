from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route("/")
def pagina_inicial():
    return render_template("index.html")

@app.route("/produtos")
def pagina_produtos():
    return render_template("produtos.html")

@app.route("/login")
def pagina_login():
    return render_template("login.html")

@app.route("/produto")
def produto_descricao():
    return render_template("produto_descricao.html")

if __name__ == "__main__":
    app.run(debug=True)