from models import usuario as usuario_model


def listar():
    return usuario_model.find_all(), 200


def buscar(usuario_id):
    usuario = usuario_model.find_by_id(usuario_id)
    if not usuario:
        return {"erro": "Usuário não encontrado"}, 404
    return usuario, 200


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        return {"erro": "Nome, email e senha são obrigatórios"}, 400
    usuario_id = usuario_model.create(nome, email, senha)
    return {"id": usuario_id}, 201


def login(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return {"erro": "Email e senha são obrigatórios"}, 400
    usuario = usuario_model.find_by_email(email)
    if not usuario or not usuario_model.verify_password(senha, usuario["senha"]):
        return {"erro": "Email ou senha inválidos"}, 401
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "tipo": usuario["tipo"]
    }, 200
