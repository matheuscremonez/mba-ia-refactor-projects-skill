from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime
from utils.helpers import VALID_STATUSES, MIN_TITLE_LENGTH, MAX_TITLE_LENGTH
import logging

logger = logging.getLogger(__name__)


def _build_task_data(t):
    task_data = t.to_dict()
    task_data['overdue'] = t.is_overdue()
    task_data['user_name'] = t.user.name if t.user else None
    task_data['category_name'] = t.category.name if t.category else None
    return task_data


def get_all_tasks():
    tasks = Task.query.all()
    return [_build_task_data(t) for t in tasks], 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data, 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    title = data.get('title')
    if not title:
        return {'error': 'Título é obrigatório'}, 400
    if len(title) < MIN_TITLE_LENGTH:
        return {'error': 'Título muito curto'}, 400
    if len(title) > MAX_TITLE_LENGTH:
        return {'error': 'Título muito longo'}, 400

    status = data.get('status', 'pending')
    if status not in VALID_STATUSES:
        return {'error': 'Status inválido'}, 400

    priority = data.get('priority', 3)
    if priority < 1 or priority > 5:
        return {'error': 'Prioridade deve ser entre 1 e 5'}, 400

    user_id = data.get('user_id')
    if user_id and not db.session.get(User, user_id):
        return {'error': 'Usuário não encontrado'}, 404

    category_id = data.get('category_id')
    if category_id and not db.session.get(Category, category_id):
        return {'error': 'Categoria não encontrada'}, 404

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        logger.info('Task criada: %s - %s', task.id, task.title)
        return task.to_dict(), 201
    except Exception as e:
        db.session.rollback()
        logger.error('Erro ao criar task: %s', str(e))
        return {'error': 'Erro ao criar task'}, 500


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'title' in data:
        if len(data['title']) < MIN_TITLE_LENGTH:
            return {'error': 'Título muito curto'}, 400
        if len(data['title']) > MAX_TITLE_LENGTH:
            return {'error': 'Título muito longo'}, 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return {'error': 'Status inválido'}, 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < 1 or data['priority'] > 5:
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            return {'error': 'Usuário não encontrado'}, 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            return {'error': 'Categoria não encontrada'}, 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                return {'error': 'Formato de data inválido'}, 400
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        logger.info('Task atualizada: %s', task.id)
        return task.to_dict(), 200
    except Exception as e:
        db.session.rollback()
        logger.error('Erro ao atualizar task: %s', str(e))
        return {'error': 'Erro ao atualizar'}, 500


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        logger.info('Task deletada: %s', task_id)
        return {'message': 'Task deletada com sucesso'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500


def search_tasks(query, status, priority, user_id):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    return [t.to_dict() for t in tasks.all()], 200


def get_task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }, 200
