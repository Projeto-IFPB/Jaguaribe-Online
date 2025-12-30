import csv
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for,flash
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash,generate_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'chave_MasterCard_Nao_tem_preco')

#configuração para upload fotos produtos

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#arquivos CSV

USUARIOS = "data/usuarios.csv"
PRODUTOS = "data/produtos.csv"

# login Manager

login_manager = LoginManager(app)
login_manager.login_view = 'pagina_login'

class Usuario(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with open(USUARIOS, mode='r') as arq:
        leitor = csv.DictReader(arq, delimiter=";")
        for linha in leitor:
            if linha['id'] == user_id:
                return Usuario(linha['id'], linha['username'])
    return None



#cadastro produtos
def ler_produtos():
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, "r", encoding="utf-8") as arq:
            return [linha.strip() for linha in arq if linha.strip()]
    return[]

def guardar_produtos(produto, nome_imagem, preco, vendedor, descricao):
    id = 1
    if os.path.exists(PRODUTOS) and os.path.getsize(PRODUTOS) > 0:
        with open(PRODUTOS, 'r', encoding='utf-8') as arq:
            ultima_linha = arq.readlines()[-1].strip()
            if ultima_linha:
                ultimo_id = ultima_linha.split(';', 1)[0]
                id = int(ultimo_id) + 1
    with open(PRODUTOS, 'a', encoding='utf-8') as arq:
        escrever = csv.writer(arq, delimiter=';')
        escrever.writerow([id, produto, nome_imagem, preco, vendedor, username_vendedor, descricao])


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
        cabecalho = [x.strip() for x in linhas[0].strip().split(';')]
        
        for linha in linhas[1:]:
            if not linha.strip(): # Pula linhas vazias para evitar o IndexError
                continue
                
            valores = [x.strip() for x in linha.strip().split(';')]
            
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
    termo_busca = request.args.get('busca', '').lower().strip()
    ordem = request.args.get('ordem', 'az')

    # Carrega todos os produtos
    lista_de_produtos = ler_produtos_card()

    # Filtra pela busca
    if termo_busca:
        lista_de_produtos = [
            p for p in lista_de_produtos
            if termo_busca in p['nome'].lower()
        ]

    # Depois, ordena a lista resultante
    try:
        if ordem == 'az':
            lista_de_produtos.sort(key=lambda x: x['nome'].lower())
        elif ordem == 'maior-preco':
            # Ordena do maior para o menor (reverse=True)
            lista_de_produtos.sort(key=lambda x: float(x['preco'].replace(',', '.')), reverse=True)
        elif ordem == 'menor-preco':
            # Ordena do menor para o maior
            lista_de_produtos.sort(key=lambda x: float(x['preco'].replace(',', '.')))
    except (ValueError, KeyError):
        # Se um preço for inválido (ex: texto em vez de número), ignora a ordenação
        pass
        
    return render_template("produtos.html", produtos=lista_de_produtos)
        
@app.route("/produto")
def produto_descricao():
    return render_template("produto_descricao.html")


@app.route("/cadastro produtos", methods=["GET","POST"])
@login_required
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

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        data = request.form.get('data')
        username = request.form.get('username')
        senha = request.form.get('senha')
        confirmar = request.form.get('confirmar')


        if senha != confirmar:
            flash('As senhas não coincidem!')
            return redirect(url_for('cadastro'))

        password_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        
        proximo_id = 1
        with open(USUARIOS, mode='r') as arq:
            leitor = csv.DictReader(arq, delimiter=";")
            for linha in leitor:
                proximo_id += 1

        with open(USUARIOS, mode='a', newline='') as arq:
            escrever = csv.writer(arq, delimiter=";")
            escrever.writerow([proximo_id, username, nome, data, password_hash])
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('pagina_login'))
        
    return render_template('cadastro.html')

@app.route("/login", methods=["GET","POST"])
def pagina_login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')

        with open(USUARIOS, mode='r') as arq:
            leitor = csv.DictReader(arq, delimiter=";")
            for linha in leitor:
                if linha['username'] == username:
                    if check_password_hash(linha['password_hash'], senha):
                        usuario = Usuario(linha['id'], linha['username'])
                        login_user(usuario)
                        return redirect(url_for('pagina_perfil'))
        
        flash('Usuário ou senha inválidos')
    return render_template("login.html")

@app.route('/perfil')
@login_required
def pagina_perfil():
    return render_template("perfil.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.')
    return redirect(url_for('pagina_login'))

if __name__ == "__main__":
    app.run(debug=True)