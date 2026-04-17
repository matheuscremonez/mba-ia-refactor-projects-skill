from models import produto as produto_model
from utils.validators import validate_produto


def listar():
    return produto_model.find_all(), 200


def buscar(produto_id):
    produto = produto_model.find_by_id(produto_id)
    if not produto:
        return {"erro": "Produto não encontrado"}, 404
    return produto, 200


def buscar_por_termo(termo, categoria, preco_min, preco_max):
    resultados = produto_model.search(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados)}, 200


def criar(dados):
    erro = validate_produto(dados)
    if erro:
        return {"erro": erro}, 400
    produto_id = produto_model.create(
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral")
    )
    return {"id": produto_id}, 201


def atualizar(produto_id, dados):
    if not produto_model.find_by_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    erro = validate_produto(dados)
    if erro:
        return {"erro": erro}, 400
    produto_model.update(
        produto_id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral")
    )
    return {"mensagem": "Produto atualizado"}, 200


def deletar(produto_id):
    if not produto_model.find_by_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    produto_model.delete(produto_id)
    return {"mensagem": "Produto deletado"}, 200
