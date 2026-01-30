from flask import Flask
import os
from flask_login import LoginManager
from dotenv import load_dotenv


login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY', 'chave_MasterCard_Nao_tem_preco')

    #configuração para upload fotos produtos
    UPLOAD_FOLDER = 'static/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # login maneger
    login_manager.init_app(app)
    login_manager.login_view = 'main.pagina_login'

    from app.admin import admin
    from app.main import main

    # Blueprints
    app.register_blueprint(admin)
    app.register_blueprint(main)

    return app

