from flask import Flask, render_template,request,redirect, url_for
import os
app = Flask(__name__)


#rotas 
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

#cadastro produtos

PRODUTOS = "produtos.txt"

def ler_produtos():
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    return[]

def guardar_produtos(produto, imagem, preco, vendedor, descricao):
    id = 1
    if os.path.exists(PRODUTOS) and os.path.getsize(PRODUTOS) > 0:
        with open(PRODUTOS, 'r', encoding='utf-8') as f:
            ultima_linha = f.readlines()[-1].strip()
            if ultima_linha:
                ultimo_id = ultima_linha.split('=', 1)[0]
                id = int(ultimo_id) + 1
    with open(PRODUTOS, 'a', encoding='utf-8') as f:
        f.write(f"{id} = {produto} = {imagem} = {preco} = {vendedor} = {descricao}\n")

if __name__ == "__main__":
    app.run(debug=True)