import csv
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for,flash
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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
    def __init__(self, username, nome_completo):
        self.id = username
        self.username = username
        self.nome_completo = nome_completo

@login_manager.user_loader
def load_user(user_id):
    with open(USUARIOS, mode='r') as arq:
        leitor = csv.DictReader(arq, delimiter=";")
        for linha in leitor:
            if linha['username'] == user_id:
                return Usuario(linha['username'], linha['nome'])
    return None



#cadastro produtos
def ler_produtos():
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, "r", encoding="utf-8") as arq:
            return [linha.strip() for linha in arq if linha.strip()]
    return[]

def guardar_produtos(produto, nome_imagem, preco, vendedor, username_vendedor, descricao):
    id_novo = 1
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, 'r', encoding='utf-8') as arq:
            leitor = csv.DictReader(arq, delimiter=';')
            ids_existentes = []
            for linha in leitor:
                if linha['id']:
                    ids_existentes.append(int(linha['id']))
            
            # Se houver IDs, o novo será o maior + 1
            if ids_existentes:
                id_novo = max(ids_existentes) + 1

    with open(PRODUTOS, 'a', newline='' , encoding='utf-8') as arq:
        escrever = csv.writer(arq, delimiter=';')
        escrever.writerow([id_novo, produto, nome_imagem, preco, vendedor, username_vendedor, descricao])


# Ler arquivo com produtos

def ler_produtos_card():
    produtos = []
    if not os.path.exists(PRODUTOS):
        return []

    with open(PRODUTOS, 'r', encoding='utf-8') as arq:
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
        
@app.route("/produto/<int:produto_id>")
def produto_descricao(produto_id):
    # Carrega a lista de produtos
    lista_de_produtos = ler_produtos_card()

    # Procura o produto pelo ID
    produto_selecionado = None
    for produto in lista_de_produtos:
        if int(produto['id']) == produto_id:
            produto_selecionado = produto
            break

    if produto_selecionado:
        return render_template("produto_descricao.html", produto=produto_selecionado)
    
    # Se o produto não for encontrado
    flash("Produto não encontrado.")
    return redirect(url_for('pagina_produtos'))


@app.route("/cadastro_produtos", methods=["GET","POST"])
@login_required
def cadastro_produtos():

    if request.method == "POST":
        produto = request.form.get("produto")
        preco = request.form.get("preco")
        vendedor = current_user.nome_completo
        username_vendedor = current_user.username
        descricao = request.form.get("descricao")

        file = request.files.get('imagem')
        nome_imagem = "None"

        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nome_imagem = filename

        if produto and preco and username_vendedor:
            guardar_produtos(produto,nome_imagem,preco,vendedor,username_vendedor,descricao)

        flash("Produto cadastrado com sucesso")
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
        whatsapp_limpo = request.form.get('whatsapp').strip()
#logica para simular unique de um banco de dados/tipo ele ve o arquivo e ve se ja existe um usuario igual ao digitado
        with open(USUARIOS, mode='r') as arq:
            leitor = csv.DictReader(arq, delimiter=";") 
            for linha in leitor:
                if linha['username'].strip().lower() == username.strip().lower():
                    flash('Este nome de usuário já está em uso. Escolha outro.')
                    return redirect(url_for('cadastro'))

        if senha != confirmar:
            flash('As senhas não coincidem!')
            return redirect(url_for('cadastro'))

        password_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        
        whatsapp = ''.join(filter(str.isdigit, whatsapp_limpo))
        if whatsapp and not whatsapp.startswith('55'):
            whatsapp = '55' + whatsapp

        with open(USUARIOS, mode='a', newline='') as arq:
            escrever = csv.writer(arq, delimiter=";")
            escrever.writerow([username, nome, data, whatsapp, password_hash])
        
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
                        usuario = Usuario(linha['username'], linha['nome'])
                        login_user(usuario)
                        return redirect(url_for('pagina_perfil'))
        
        flash('Usuário ou senha inválidos')
    return render_template("login.html")

@app.route('/perfil')
@login_required
def pagina_perfil():
    meus_produtos = []
    
    with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
        leitor = csv.DictReader(arq , delimiter=';')
        for linha in leitor:
            atual = current_user.username.strip().lower()
            vendedor = linha['username_vendedor'].strip().lower()
            if vendedor == atual :
                meus_produtos.append(linha)
    
    return render_template('perfil.html', produtos=meus_produtos)

@app.route('/excluir_produto/<id_produto>', methods=['POST'])
@login_required
def excluir_produto(id_produto):
    linhas_mantidas = []
    campos = ['id', 'nome', 'imagem', 'preco', 'vendedor', 'username_vendedor', 'descricao']

    with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
        leitor = csv.DictReader(arq, delimiter=';')
        for linha in leitor:
            if linha['id'] != str(id_produto) or linha['username_vendedor'] != current_user.username:
                linhas_mantidas.append(linha)

    with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
        escrever = csv.DictWriter(arq, fieldnames=campos, delimiter=';')
        escrever.writeheader()
        escrever.writerows(linhas_mantidas)

    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('pagina_perfil'))

@app.route('/editar_produto/<id_produto>', methods=['GET', 'POST'])
@login_required
def editar_produto(id_produto):
    campos = ['id', 'nome', 'imagem', 'preco', 'vendedor', 'username_vendedor', 'descricao']
    linhas_atualizadas = []
    produto_atual = None

    # 1. Ler o arquivo para encontrar o produto e carregar os outros
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
            leitor = csv.DictReader(arq, delimiter=';')
            for linha in leitor:
                if linha['id'] == str(id_produto):
                    # Verificação de segurança: só o dono edita
                    if linha['username_vendedor'] != current_user.username:
                        flash("Acesso negado!", "danger")
                        return redirect(url_for('pagina_perfil'))
                    produto_atual = linha
                linhas_atualizadas.append(linha)

    if not produto_atual:
        flash("Produto não encontrado!", "danger")
        return redirect(url_for('pagina_perfil'))

    # 2. Processar a atualização (Quando o formulário é enviado)
    if request.method == 'POST':
        for linha in linhas_atualizadas:
            if linha['id'] == str(id_produto):
                linha['nome'] = request.form.get('nome')
                linha['preco'] = request.form.get('preco')
                linha['descricao'] = request.form.get('descricao')

                # Tratamento da Imagem
                file = request.files.get('imagem')
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    linha['imagem'] = filename # Atualiza o nome do arquivo no CSV

        # 3. Salvar de volta no CSV
        with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
            escrever = csv.DictWriter(arq, fieldnames=campos, delimiter=';')
            escrever.writeheader()
            escrever.writerows(linhas_atualizadas)

        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for('pagina_perfil'))

    # Se for GET, mostra o formulário preenchido
    return render_template('editar_produto.html', produto=produto_atual)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.')
    return redirect(url_for('pagina_login'))

if __name__ == "__main__":
    app.run(debug=True)