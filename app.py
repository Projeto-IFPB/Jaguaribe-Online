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
    def __init__(self, username, nome_completo, data_nascimento, whatsapp, senha):
        self.id = username
        self.username = username
        self.nome_completo = nome_completo
        self.data = data_nascimento
        self.whatsapp = whatsapp
        self.senha = senha

@login_manager.user_loader
def load_user(user_id):
    with open(USUARIOS, mode='r') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if len(dados) >= 5:
                if dados[0] == user_id:
                    return Usuario(dados[0], dados[1], dados[2], dados[3], dados[4])
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
            linhas = arq.readlines()
            ids_existentes = []
            for linha in linhas[1:]:
                dados = linha.strip().split(';')
                if dados[0]:
                    ids_existentes.append(int(dados[0]))
            
            # Se houver IDs, o novo será o maior + 1
            if ids_existentes:
                id_novo = max(ids_existentes) + 1

    with open(PRODUTOS, 'a', newline='' , encoding='utf-8') as arq:
        linha = f'{id_novo};{produto};{nome_imagem};{preco};{vendedor};{username_vendedor};{descricao}\n'
        arq.write(linha)


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

# Ler todos os usuários cadastrados no sistema
def ler_todos_usuarios():
    usuarios = []
    if not os.path.exists(USUARIOS):
        return []

    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            retorno = Usuario(dados[0], dados[1], dados[2], dados[3], dados[4])
            usuarios.append(retorno)      
    return usuarios

#whatsapp do vendedor 
def buscar_whatsapp(username_vendedor):
    if not os.path.exists(USUARIOS):
        return 'None'
        
    with open(USUARIOS, 'r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == username_vendedor:      
                # Se o campo existir e não for vazio, retorna o número, senão 'None'
                whatsapp = dados[3]
                return whatsapp if whatsapp and whatsapp.strip() != "" else 'None'
    
    return 'None'
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
    for p in lista_de_produtos:
        p['whatsapp_vendedor'] = buscar_whatsapp(p['username_vendedor'])


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
        whatsapp_limpo = request.form.get('whatsapp','').strip()

        with open(USUARIOS, mode='r') as arq:
            linhas = arq.readlines()
            for linha in linhas[1:]:
                dados = linha.strip().split(';')
                if dados[0].strip().lower() == username.strip().lower():
                    flash('Este nome de usuário já está em uso. Escolha outro.')
                    return redirect(url_for('cadastro'))

        if senha != confirmar:
            flash('As senhas não coincidem!')
            return redirect(url_for('cadastro'))

        password_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        
        whatsapp = ''.join(filter(str.isdigit, whatsapp_limpo))
        if not whatsapp:
            whatsapp = 'None'
        elif whatsapp and not whatsapp.startswith('55'):
            whatsapp = '55' + whatsapp

        with open(USUARIOS, mode='a', newline='') as arq:
            linha = f'{username};{nome};{data};{whatsapp};{password_hash}\n'
            arq.write(linha)
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('pagina_login'))
        
    return render_template('cadastro.html')

@app.route("/login", methods=["GET","POST"])
def pagina_login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')

        with open(USUARIOS, mode='r') as arq:
            linhas = arq.readlines()
            for linha in linhas[1:]:
                dados = linha.strip().split(';')
                if dados[0] == username:
                    if check_password_hash(dados[4], senha):
                        usuario = Usuario(dados[0], dados[1], dados[2], dados[3], dados[4])
                        login_user(usuario)
                        return redirect(url_for('pagina_perfil'))
        
        flash('Usuário ou senha inválidos')
    return render_template("login.html")

@app.route('/perfil')
@login_required
def pagina_perfil():
    meus_produtos = []
    
    with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        cabecalho = [c.strip() for c in linhas[0].split(';')]
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            atual = current_user.username.strip().lower()
            vendedor = dados[5].strip().lower()
            if vendedor == atual :
                item = dict(zip(cabecalho, dados))
                meus_produtos.append(item)

        todos_usuarios = ler_todos_usuarios()
    
    return render_template('perfil.html', produtos=meus_produtos, usuarios=todos_usuarios)

@app.route('/excluir_produto/<id_produto>', methods=['POST'])
@login_required
def excluir_produto(id_produto):
    linhas_mantidas = []
    campos = ['id', 'nome', 'imagem', 'preco', 'vendedor', 'username_vendedor', 'descricao']

    with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] != str(id_produto) or dados[5] != current_user.username:
                linhas_mantidas.append(linha.strip())

    with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(";".join(campos) + "\n")
        
        for i in linhas_mantidas:
            arq.write(i + '\n')

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
            linhas = arq.readlines()
            for linha in linhas[1:]:
                dados = linha.strip().split(';')
                if dados[0] == str(id_produto):
                    # Verificação de segurança: só o dono edita
                    if dados[5] != current_user.username:
                        flash("Acesso negado!", "error_editar_produtos")
                        return redirect(url_for('pagina_perfil'))
                    produto_atual = linha
    # 2. Processar a atualização (Quando o formulário é enviado)
                    if request.method == 'POST':
                            if dados[0] == str(id_produto):
                                dados[1] = request.form.get('nome')
                                dados[3] = request.form.get('preco')
                                dados[6] = request.form.get('descricao')

                                # Tratamento da Imagem
                                file = request.files.get('imagem')
                                if file and file.filename != '':
                                    filename = secure_filename(file.filename)
                                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                    dados[2] = filename # Atualiza o nome do arquivo no CSV
                            linha = ';'.join(dados)
                linhas_atualizadas.append(linha)

    if not produto_atual:
        flash("Produto não encontrado!", "danger")
        return redirect(url_for('pagina_perfil'))
    
    # 3. Salvar de volta no CSV
    with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(";".join(campos) + "\n")
        for i in linhas_atualizadas:
            arq.write(i)
    # Se for GET, mostra o formulário preenchido
    return render_template('editar_produto.html', produto=produto_atual)

# Rota que permite que o admin exclua a conta de um vendedor
@app.route('/excluir_usuario/<username>', methods=['POST'])
@login_required
def excluir_vendedor(username):

    # Evitar que o admin exclua a si próprio por acidente
    if username == current_user.username:
        flash('Você não pode excluir sua própria conta de administrador por aqui.', 'dashboard_erro')
        return redirect(url_for('pagina_perfil'))
    
    # --- 2. REMOVER USUÁRIO DO CSV ---
    usuarios_mantidos = []
    campos_usuarios = ['username', 'nome', 'data', 'whatsapp', 'senha']
    
    if os.path.exists(USUARIOS):
        with open(USUARIOS, mode='r', encoding='utf-8') as arq:
            linhas = arq.readlines()
            for linha in linhas[1:]:
                dados = linha.strip().split(';')
                if dados[0] != username:
                    usuarios_mantidos.append(linha)
        
        with open(USUARIOS, mode='w', newline='', encoding='utf-8') as arq:
            arq.write(";".join(campos_usuarios) + "\n")
        
            for i in usuarios_mantidos:
                arq.write(i)

    # --- 3. REMOVER PRODUTOS DO USUÁRIO DO CSV ---
    produtos_mantidos = []
    campos_produtos = ['id', 'nome', 'imagem', 'preco', 'vendedor', 'username_vendedor', 'descricao']
    
    if os.path.exists(PRODUTOS):
        with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
            linhas = arq.readlines()
            for linha in linhas[1:]:
                dados = linha.strip().split(';')
                # Se o username_vendedor for diferente do alvo, nós mantemos o produto
                if dados[5] != username:
                    produtos_mantidos.append(linha)
        
        with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
            arq.write(";".join(campos_produtos) + "\n")
        
            for i in produtos_mantidos:
                arq.write(i)

    flash(f'O usuário "{username}" e todos os seus produtos foram removidos com sucesso.', 'successo')
    return redirect(url_for('pagina_perfil')) # Redireciona de volta para a lista

@app.route('/alterar_username', methods=['POST'])
@login_required
def alterar_username():
    novo_username = request.form.get('novo_username', '').strip()
    username_antigo = current_user.username
    campos_produtos = ['id', 'nome', 'imagem', 'preco', 'vendedor', 'username_vendedor', 'descricao']
    campos_usuarios =['username','nome','data','whatsapp','senha']

    if novo_username == username_antigo:
        flash("Digite um novo username diferente do atual.", "erro_username")
        return redirect(url_for('pagina_perfil'))


    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            usuario = linha.strip().split(';')
            if usuario[0] == novo_username:
                flash("Este username já está em uso por outro usuário!", "erro_username")
                return redirect(url_for('pagina_perfil'))

    linhas_produtos = []
    with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[5] == username_antigo:
                dados[5] = novo_username
            nova_linha = ';'.join(dados)
            linhas_produtos.append(nova_linha)

    with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(';'.join(campos_produtos)+ '\n')
        for i in linhas_produtos:
            arq.write(i +'\n')

    linhas_usuarios = []
    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == username_antigo:
                dados[0] = novo_username
            nova_linha = ';'.join(dados)
            linhas_usuarios.append(nova_linha)

        with open(USUARIOS, mode='w', newline='', encoding='utf-8') as arq:
            arq.write(';'.join(campos_usuarios)+ '\n')
            for i in linhas_usuarios:
                arq.write(i +'\n')

    current_user.id = novo_username  
    current_user.username = novo_username

    login_user(current_user)
    
    flash("Username alterado com sucesso em todo o sistema!", "successo")
    return redirect(url_for('pagina_perfil'))

@app.route('/alterar_nome_vendedor', methods=['POST'])
@login_required
def alterar_nome_vendedor():
    novo_nome = request.form.get('novo_nome', '')
    username = current_user.username 
    nome_antigo = current_user.nome_completo
    campos_produtos = ['id', 'nome', 'imagem', 'preco', 'vendedor', 'username_vendedor', 'descricao']
    campos_usuarios =['username','nome','data','whatsapp','senha']

    
    if novo_nome == nome_antigo:
        flash("O novo nome deve ser diferente do atual.", "erro_nome")
        return redirect(url_for('pagina_perfil'))
    
    linhas_produtos = []
    with open(PRODUTOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(";")
            if dados[5] == username:
                dados[4] = novo_nome
            nova_linha = ';'.join(dados)
            linhas_produtos.append(nova_linha)
    

    with open(PRODUTOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(';'.join(campos_produtos)+ '\n')
        for i in linhas_produtos:
            arq.write(i +'\n')

    linhas_usuarios = []
    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(";")
            if dados[0] == username:
                dados[1] = novo_nome 
            nova_linha = ';'.join(dados)
            linhas_usuarios.append(nova_linha)

    with open(USUARIOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(';'.join(campos_usuarios)+ '\n')
        for i in linhas_usuarios:
            arq.write(i +'\n')

    current_user.nome_completo = novo_nome 
    flash("Nome de vendedor atualizado com sucesso!", "successo")
    return redirect(url_for('pagina_perfil'))

@app.route('/alterar_data_vendedor', methods=['POST'])
@login_required
def alterar_data_vendedor():
    nova_data = request.form.get('nova_data')
    campos_usuarios =['username','nome','data','whatsapp','senha']

    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == current_user.username:
                if dados[2] == nova_data:
                    flash("A nova data deve ser diferente da atual.", "erro_data")
                    return redirect(url_for('pagina_perfil'))

    linhas_usuarios = []
    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == current_user.username:
                dados[2] = nova_data 
            nova_linha = ';'.join(dados)
            linhas_usuarios.append(nova_linha)

    with open(USUARIOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(';'.join(campos_usuarios)+ '\n')
        for i in linhas_usuarios:
            arq.write(i +'\n')

    flash("Data de Nascimento atualizada com sucesso!", "successo")
    return redirect(url_for('pagina_perfil'))

@app.route('/alterar_senha', methods=['POST'])
@login_required
def alterar_senha():
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    campos_usuarios =['username','nome','data','whatsapp','senha']

    if not check_password_hash(current_user.senha, senha_atual):
        flash("A senha atual está incorreta!", "erro_senha")
        return redirect(url_for('pagina_perfil'))

    if check_password_hash(current_user.senha, nova_senha):
        flash("A nova senha não pode ser igual à atual!", "erro_senha")
        return redirect(url_for('pagina_perfil'))

    if nova_senha != confirmar_senha:
        flash("As novas senhas não coincidem!", "erro_senha")
        return redirect(url_for('pagina_perfil'))

    novo_hash = generate_password_hash(nova_senha, method='pbkdf2:sha256')
    
    linhas_usuarios = []
    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == current_user.username:
                dados[4] = novo_hash 
            nova_linha = ';'.join(dados)
            linhas_usuarios.append(nova_linha)
   
    with open(USUARIOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(';'.join(campos_usuarios)+ '\n')
        for i in linhas_usuarios:
            arq.write(i +'\n')

    current_user.senha = novo_hash
    
    flash("Senha alterada com sucesso!", "successo") 
    return redirect(url_for('pagina_perfil'))

@app.route('/alterar_whatsapp', methods=['POST'])
@login_required
def alterar_whatsapp():
    whatsapp = request.form.get('novo_telefone','').strip()
    novo_whatsapp = ''.join(filter(str.isdigit, whatsapp))
    campos_usuarios =['username','nome','data','whatsapp','senha']

    if not novo_whatsapp:
            novo_whatsapp = 'None'
    elif novo_whatsapp and not novo_whatsapp.startswith('55'):
            novo_whatsapp = '55' + novo_whatsapp
    

    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == current_user.username:
                if dados[3] == novo_whatsapp:
                    flash("O novo número deve ser diferente da atual.", "erro_telefone")
                    return redirect(url_for('pagina_perfil'))
    
   


    linhas_usuarios = []
    with open(USUARIOS, mode='r', encoding='utf-8') as arq:
        linhas = arq.readlines()
        for linha in linhas[1:]:
            dados = linha.strip().split(';')
            if dados[0] == current_user.username:
                dados[3] = novo_whatsapp
            nova_linha = ';'.join(dados)
            linhas_usuarios.append(nova_linha)

    with open(USUARIOS, mode='w', newline='', encoding='utf-8') as arq:
        arq.write(';'.join(campos_usuarios)+ '\n')
        for i in linhas_usuarios:
            arq.write(i +'\n')

    flash("Número de telefone alterado com sucesso atualizada com sucesso!", "successo")
    return redirect(url_for('pagina_perfil'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.')
    return redirect(url_for('pagina_login'))

if __name__ == "__main__":
    app.run(debug=True)