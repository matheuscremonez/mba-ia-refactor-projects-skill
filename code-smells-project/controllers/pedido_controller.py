import logging
from models import pedido as pedido_model
from models.pedido import STATUS_VALIDOS

logger = logging.getLogger(__name__)


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return {"erro": "usuario_id é obrigatório"}, 400
    if not itens:
        return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

    resultado = pedido_model.create(usuario_id, itens)
    if "erro" in resultado:
        return resultado, 400

    logger.info("Pedido %s criado para usuário %s", resultado["pedido_id"], usuario_id)
    return resultado, 201


def listar_por_usuario(usuario_id):
    return pedido_model.find_by_usuario(usuario_id), 200


def listar_todos():
    return pedido_model.find_all(), 200


def atualizar_status(pedido_id, dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        return {"erro": "Status inválido"}, 400
    pedido_model.update_status(pedido_id, novo_status)
    logger.info("Pedido %s atualizado para status '%s'", pedido_id, novo_status)
    return {"mensagem": "Status atualizado"}, 200


def relatorio():
    return pedido_model.relatorio_vendas(), 200
