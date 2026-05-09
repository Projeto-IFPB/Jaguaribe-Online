import sys
import os

# Adiciona a raiz ao path para encontrar o main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app

app = create_app()