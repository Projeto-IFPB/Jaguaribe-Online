#arquivos CSV
import os
from app.models import Usuario

USUARIOS = "data/usuarios.csv"
PRODUTOS = "data/produtos.csv"

#arquivos de texto
ADMIN = "data/admin.txt"

#carregar admin
def carregar_admins():
    with open(ADMIN, 'r') as arq:
        return [linha.strip() for linha in arq.readlines()]
    return []

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

def carregar_produtos_usuario(username):
    todos_produtos = ler_produtos_card()
    produtos_filtrados = []

    for produto in todos_produtos:
        # Usamos .get() para evitar erro caso a chave 'usernamer' não exista
        vendedor_no_csv = produto.get('username_vendedor')

        # Verificação robusta: remove espaços e ignora maiúsculas/minúsculas
        if vendedor_no_csv.strip().lower() == username.strip().lower():
            produtos_filtrados.append(produto)
            
    return produtos_filtrados
