from flask import Blueprint, jsonify, request
from controllers import usuario_controller

usuario_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@usuario_bp.route('/', methods=['GET'])
def listar_usuarios():
    dados, status = usuario_controller.listar()
    return jsonify({"dados": dados, "sucesso": True}), status


@usuario_bp.route('/<int:usuario_id>', methods=['GET'])
def buscar_usuario(usuario_id):
    dados, status = usuario_controller.buscar(usuario_id)
    sucesso = status == 200
    return jsonify({"dados": dados, "sucesso": True} if sucesso else {**dados, "sucesso": False}), status


@usuario_bp.route('/', methods=['POST'])
def criar_usuario():
    dados, status = usuario_controller.criar(request.get_json())
    return jsonify({**dados, "sucesso": status < 400}), status
