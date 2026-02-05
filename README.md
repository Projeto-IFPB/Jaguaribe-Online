# Feira Comunitária de Jaguaribe

Projeto Acadêmico - IFPB

## Sobre o projeto
Este projeto consiste em uma aplicação web desenvolvida para representar a Feira Pública de Jaguaribe, em João Pessoa. O sistema tem como objetivo divulgar a feira e permitir que vendedores tenham acesso a uma área para cadastrar e exibir seus produtos. O projeto está sendo desenvolvido como trabalho final do primeiro período
do curso de Engenharia de Software do IFPB, integrando as disciplinas de Programação Web I, Introdução a Programação e Introdução a Engenharia de Software.
Os alunos responsáveis por esse projeto são: Antony Conceição, Diogo Silva, Lemuel Duarte e Ryan Enriq.

---

## Tecnologias utilizadas
- HTML5
- CSS3
- JavaScript
- Python
- Flask
- Git e GitHub

---

## Estrutura do projeto
Projeto_IFPB
├── app/                  # Pasta que armazena os módulos do sistema
    ├── admin/
        └── __init__.py  #Criação 
        └── routes.py    # Rotas de administrador
    ├── main/
        └── __init__.py  
        └── routes.py    #Rotas principais
    ├── templates/       # Pasta que armazena todos os templates html
    ├── static/          # Pasta que armazena toda parte estática do sistema
        ├── css/
        ├── images/
        ├── js/
        ├── uploads/
        └── __init__.py
        └── functions.py
        └── models.py
├── data/                # Armazenamento de dados do sistema
├── app.py               # Arquivo principal da aplicação Flask
├── .gitignore           # Área para evitar que alguns arquivos vá para o github
├── README.md            # Documentação principal do projeto
├── requirements.txt     # Dependências do projeto

---

## Como executar o projeto

1- Crie e ative o ambiente virtual
python -m venv venv
source venv/Scripts/activate      #Para o Git Bash

2- Instale as dependências
pip install -r requirements.txt

3- Execute a aplicação
python app.py

4- Acesse no navegador
http://127.0.0.1:5000

---

## Status do projeto
Projeto finalizado - (Sprint 2)

## Arquitetura do Sistema
![Arquitetura do Sistema](https://github.com/user-attachments/assets/4cc3f229-3c6c-4abb-a552-7974312e552a)


## Diagrama de Casos de Uso
![Casos de Uso](https://github.com/user-attachments/assets/26b0ace1-f838-484e-ba8c-d45b049bff04)




