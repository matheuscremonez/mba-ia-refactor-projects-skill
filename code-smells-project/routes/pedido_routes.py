from flask import Blueprint, jsonify, request
from controllers import pedido_controller

pedido_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')


@pedido_bp.route('/', methods=['POST'])
def criar_pedido():
    dados, status = pedido_controller.criar(request.get_json())
    return jsonify({**dados, "sucesso": status < 400}), status


@pedido_bp.route('/', methods=['GET'])
def listar_todos_pedidos():
    dados, status = pedido_controller.listar_todos()
    return jsonify({"dados": dados, "sucesso": True}), status


@pedido_bp.route('/usuario/<int:usuario_id>', methods=['GET'])
def listar_pedidos_usuario(usuario_id):
    dados, status = pedido_controller.listar_por_usuario(usuario_id)
    return jsonify({"dados": dados, "sucesso": True}), status


@pedido_bp.route('/<int:pedido_id>/status', methods=['PUT'])
def atualizar_status_pedido(pedido_id):
    dados, status = pedido_controller.atualizar_status(pedido_id, request.get_json())
    return jsonify({**dados, "sucesso": status < 400}), status
