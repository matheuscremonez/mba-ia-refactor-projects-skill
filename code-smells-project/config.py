import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-nao-usar-producao')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'loja.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
