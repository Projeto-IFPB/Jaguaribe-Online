
from flask import render_template, request, redirect, url_for, flash, session, current_app
from app.models import Usuario
from app.functions import carregar_admins, ler_produtos, guardar_produtos, ler_produtos_card, buscar_whatsapp 
from app.admin import admin as admin_bp
import os
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Caminhos dos arquivos CSV
USUARIOS = "data/usuarios.csv"
PRODUTOS = "data/produtos.csv"

#arquivos de texto
ADMIN = "data/admin.txt"

# Rota que permite que o admin exclua a conta de um vendedor
@admin_bp.route('/excluir_usuario/<username>', methods=['POST'])
@login_required
def excluir_vendedor(username):

    if session.get('perfil') != 'admin':
        flash("Acesso negado: Você não tem permissão para esta ação.", "dashboard_erro")
        return redirect(url_for('main.pagina_perfil'))
    # Evitar que o admin exclua a si próprio por acidente
    if username == current_user.username:
        flash('Você não pode excluir sua própria conta de administrador por aqui.', 'dashboard_erro')
        return redirect(url_for('main.pagina_perfil'))
    
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
    return redirect(url_for('main.pagina_perfil')) # Redireciona de volta para a lista