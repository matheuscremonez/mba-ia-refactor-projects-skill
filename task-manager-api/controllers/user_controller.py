from database import db
from models.user import User
from models.task import Task
from utils.helpers import validate_email, VALID_ROLES, MIN_PASSWORD_LENGTH
import logging

logger = logging.getLogger(__name__)


def create_user(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        return {'error': 'Nome é obrigatório'}, 400
    if not email:
        return {'error': 'Email é obrigatório'}, 400
    if not password:
        return {'error': 'Senha é obrigatória'}, 400

    if not validate_email(email):
        return {'error': 'Email inválido'}, 400

    if len(password) < MIN_PASSWORD_LENGTH:
        return {'error': f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres'}, 400

    if User.query.filter_by(email=email).first():
        return {'error': 'Email já cadastrado'}, 409

    if role not in VALID_ROLES:
        return {'error': 'Role inválido'}, 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        logger.info('Usuário criado: %s - %s', user.id, user.name)
        return user.to_dict(), 201
    except Exception as e:
        db.session.rollback()
        logger.error('Erro ao criar usuário: %s', str(e))
        return {'error': 'Erro ao criar usuário'}, 500


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not validate_email(data['email']):
            return {'error': 'Email inválido'}, 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return {'error': 'Email já cadastrado'}, 409
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return {'error': 'Senha muito curta'}, 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return {'error': 'Role inválido'}, 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return user.to_dict(), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        task_data = t.to_dict()
        task_data['overdue'] = t.is_overdue()
        result.append(task_data)

    return result, 200
