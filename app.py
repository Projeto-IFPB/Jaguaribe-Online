from flask import Flask, render_template, request,redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

#configuração para upload fotos produtos

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#cadastro produtos

PRODUTOS = "data/produtos.csv"

def ler_produtos():
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    return[]

def guardar_produtos(produto, nome_imagem, preco, vendedor, descricao):
    id = 1
    if os.path.exists(PRODUTOS) and os.path.getsize(PRODUTOS) > 0:
        with open(PRODUTOS, 'r', encoding='utf-8') as f:
            ultima_linha = f.readlines()[-1].strip()
            if ultima_linha:
                ultimo_id = ultima_linha.split('=', 1)[0]
                id = int(ultimo_id) + 1
    with open(PRODUTOS, 'a', encoding='utf-8') as f:
        f.write(f"{id} = {produto} = {nome_imagem} = {preco} = {vendedor} = {descricao}\n")

# Ler arquivo com produtos

def ler_produtos_card():
    produtos = []
    if not os.path.exists('data/produtos.csv'):
        return []

    with open('data/produtos.csv', 'r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        if not linhas:
            return []
        
        # .strip() remove o \n e [x.strip() for x in ...] remove espaços ao redor do '='
        cabecalho = [x.strip() for x in linhas[0].strip().split('=')]
        
        for linha in linhas[1:]:
            if not linha.strip(): # Pula linhas vazias para evitar o IndexError
                continue
                
            valores = [x.strip() for x in linha.strip().split('=')]
            
            # Verifica se a linha tem o mesmo número de colunas que o cabeçalho
            if len(valores) == len(cabecalho):
                item = dict(zip(cabecalho, valores))
                produtos.append(item)
                
    return produtos

#rotas 
@app.route("/")
def pagina_inicial():
    return render_template("index.html")

@app.route("/produtos")
def pagina_produtos():

    # Pega o objeto de busca(pela URL)
    termo_busca = request.args.get('busca', '').lower()

    # Carrega todos os produtos
    lista_de_produtos = ler_produtos_card()

    if termo_busca:
        lista_de_produtos = [
            p for p in lista_de_produtos
            if termo_busca in p['nome'].lower()
        ]
        
    return render_template("produtos.html", produtos=lista_de_produtos)


@app.route("/produto")
def produto_descricao():
    return render_template("produto_descricao.html")


@app.route("/cadastro produtos", methods=["GET","POST"])
def cadastro_produtos():
    if request.method == "POST":
        produto = request.form.get("produto")
        preco = request.form.get("preco")
        vendedor = request.form.get("vendedor")
        descricao = request.form.get("descricao")

        file = request.files.get('imagem')
        nome_imagem = "None"

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nome_imagem = filename

        if produto and preco and vendedor:
            guardar_produtos(produto,nome_imagem,preco,vendedor,descricao)

        return redirect(url_for('cadastro_produtos'))
    
    produtos = ler_produtos()
    return render_template("cadastro_produtos.html")

@app.route("/login")
def pagina_login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)