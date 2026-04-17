from flask import Blueprint, jsonify, request
from controllers import produto_controller

produto_bp = Blueprint('produtos', __name__, url_prefix='/produtos')


@produto_bp.route('/', methods=['GET'])
def listar_produtos():
    dados, status = produto_controller.listar()
    return jsonify({"dados": dados, "sucesso": True}), status


@produto_bp.route('/busca', methods=['GET'])
def buscar_produtos():
    termo = request.args.get('q', '')
    categoria = request.args.get('categoria')
    preco_min = request.args.get('preco_min', type=float)
    preco_max = request.args.get('preco_max', type=float)
    dados, status = produto_controller.buscar_por_termo(termo, categoria, preco_min, preco_max)
    return jsonify({**dados, "sucesso": True}), status


@produto_bp.route('/<int:produto_id>', methods=['GET'])
def buscar_produto(produto_id):
    dados, status = produto_controller.buscar(produto_id)
    sucesso = status == 200
    return jsonify({"dados": dados, "sucesso": sucesso} if sucesso else {**dados, "sucesso": False}), status


@produto_bp.route('/', methods=['POST'])
def criar_produto():
    dados, status = produto_controller.criar(request.get_json())
    return jsonify({**dados, "sucesso": status < 400}), status


@produto_bp.route('/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    dados, status = produto_controller.atualizar(produto_id, request.get_json())
    return jsonify({**dados, "sucesso": status < 400}), status


@produto_bp.route('/<int:produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    dados, status = produto_controller.deletar(produto_id)
    return jsonify({**dados, "sucesso": status < 400}), status
