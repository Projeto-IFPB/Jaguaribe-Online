from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from app import login_manager


USUARIOS = "data/usuarios.csv"


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