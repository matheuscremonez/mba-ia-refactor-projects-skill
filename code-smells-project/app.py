import logging
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from database import get_db
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from routes.pedido_routes import pedido_bp

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)

    @app.route('/login', methods=['POST'])
    def login():
        from controllers import usuario_controller
        dados, status = usuario_controller.login(request.get_json())
        return jsonify({**dados, "sucesso": status < 400}), status

    @app.route('/relatorios/vendas', methods=['GET'])
    def relatorio_vendas():
        from controllers import pedido_controller
        dados, status = pedido_controller.relatorio()
        return jsonify({"dados": dados, "sucesso": True}), status

    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM produtos")
            produtos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            pedidos = cursor.fetchone()[0]
            return jsonify({
                "status": "ok",
                "database": "connected",
                "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
                "versao": "1.0.0"
            }), 200
        except Exception as e:
            return jsonify({"status": "erro", "detalhes": str(e)}), 500

    @app.route('/')
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health"
            }
        })

    return app


if __name__ == '__main__':
    app = create_app()
    get_db()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
