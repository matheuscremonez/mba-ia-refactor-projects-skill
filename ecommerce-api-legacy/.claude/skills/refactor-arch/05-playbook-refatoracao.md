# Referência 05 — Playbook de Refatoração

Transformações concretas com exemplos antes/depois.
Aplique cada transformação somente quando o anti-pattern correspondente for detectado.

---

## T-01 — Credenciais Hardcoded → Variáveis de Ambiente

**Aplica quando:** AP-02 detectado

**Antes (Python):**
```python
app.config['SECRET_KEY'] = 'super-secret-key-hardcoded'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
```

**Depois (Python):**
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-fallback')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
```

**Antes (Node.js):**
```javascript
const SECRET = 'minha-senha-secreta';
const DB_PATH = '/var/data/app.db';
```

**Depois (Node.js):**
```javascript
const SECRET = process.env.SECRET_KEY;
const DB_PATH = process.env.DATABASE_PATH || ':memory:';
```

**Criar `.env.example`:**
```
SECRET_KEY=
DATABASE_URL=sqlite:///app.db
```

---

## T-02 — SQL Injection → Queries Parametrizadas

**Aplica quando:** AP-01 detectado

**Antes (Python sqlite3):**
```python
email = request.json['email']
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

**Depois (Python sqlite3):**
```python
email = request.json['email']
cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
```

**Antes (Python psycopg2):**
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Depois (Python psycopg2):**
```python
cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
```

**Antes (Node.js):**
```javascript
db.all(`SELECT * FROM products WHERE name = '${name}'`, callback);
```

**Depois (Node.js):**
```javascript
db.all('SELECT * FROM products WHERE name = ?', [name], callback);
```

---

## T-03 — Endpoint Arbitrário → Remoção Completa

**Aplica quando:** AP-03 detectado

**Antes:**
```python
@app.route('/admin/query', methods=['POST'])
def run_query():
    sql = request.json.get('sql')
    result = db.execute(sql)  # VULNERABILIDADE CRITICA
    return jsonify(result.fetchall())
```

**Depois:** Remover o endpoint completamente. Não substituir por versão 'mais segura'.

Se existir necessidade administrativa legítima, implementar via CLI local, não via HTTP.

---

## T-04 — God Class → Separação em Camadas

**Aplica quando:** AP-04 detectado (perfil MONOLITO ou PARCIALMENTE_ORGANIZADO)

**Antes (Node.js — AppManager god class):**
```javascript
class AppManager {
  constructor() {
    this.db = null;
    this.app = express();
  }
  initDb() { /* conecta ao banco */ }
  setupRoutes() { /* define todas as rotas */ }
  calculateTotal(items) { /* lógica de negócio */ }
  generateReport() { /* relatório */ }
}
```

**Depois:** Cada responsabilidade em seu arquivo:
```javascript
// config/database.js — só conecta ao banco
// controllers/orderController.js — só lógica de pedidos
// routes/orderRoutes.js — só define as rotas HTTP
// src/app.js — só inicializa Express e registra routes
```

---

## T-05 — Lógica na Rota → Controller

**Aplica quando:** AP-05 detectado

**Antes (Python/Flask):**
```python
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    if not data.get('user_id'):
        return jsonify({'error': 'user_id obrigatorio'}), 400
    # 40 linhas de lógica: calcular total, aplicar desconto, salvar...
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders ...')
    conn.commit()
    return jsonify({'id': cursor.lastrowid}), 201
```

**Depois:**
```python
# routes/order_routes.py — apenas HTTP
@order_bp.route('/', methods=['POST'])
def create_order():
    result, status = order_controller.create_order(request.json)
    return jsonify(result), status

# controllers/order_controller.py — lógica de negócio
def create_order(data):
    if not data.get('user_id'):
        return {'error': 'user_id obrigatorio'}, 400
    order_id = order_model.create(data)
    return {'id': order_id}, 201

# models/order.py — acesso a dados
def create(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (user_id, total) VALUES (?, ?)',
                  (data['user_id'], data['total']))
    conn.commit()
    return cursor.lastrowid
```

---

## T-06 — Senha Plaintext → bcrypt

**Aplica quando:** AP-06 detectado

**Antes (Python):**
```python
# Cadastro
cursor.execute('INSERT INTO users (password) VALUES (?)', (password,))

# Login
if user['password'] == request.json['password']:
    return jsonify({'token': generate_token()})
```

**Depois (Python):**
```python
import bcrypt

# Cadastro
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute('INSERT INTO users (password) VALUES (?)', (hashed,))

# Login
if bcrypt.checkpw(request.json['password'].encode('utf-8'), user['password']):
    return jsonify({'token': generate_token()})
```

**Antes (Node.js):**
```javascript
// Cadastro
db.run('INSERT INTO users (password) VALUES (?)', [password]);

// Login
if (user.password === password) { /* ... */ }
```

**Depois (Node.js):**
```javascript
const bcrypt = require('bcrypt');

// Cadastro
const hash = await bcrypt.hash(password, 10);
db.run('INSERT INTO users (password) VALUES (?)', [hash]);

// Login
const valid = await bcrypt.compare(password, user.password);
if (valid) { /* ... */ }
```

**Adicionar ao requirements.txt/package.json:**
- Python: `bcrypt`
- Node.js: `bcrypt` (npm)

---

## T-07 — API Deprecated → API Atual (SQLAlchemy)

**Aplica quando:** AP-07 detectado

**Antes:**
```python
user = User.query.get(user_id)
product = Product.query.get(product_id)
```

**Depois (SQLAlchemy 2.x):**
```python
user = db.session.get(User, user_id)
product = db.session.get(Product, product_id)
```

---

## T-08 — N+1 Queries → JOIN

**Aplica quando:** AP-08 detectado

**Antes:**
```python
orders = cursor.execute('SELECT * FROM orders').fetchall()
result = []
for order in orders:
    user = cursor.execute(
        'SELECT * FROM users WHERE id = ?', (order['user_id'],)
    ).fetchone()
    result.append({**order, 'user_name': user['name']})
```

**Depois:**
```python
rows = cursor.execute(
    'SELECT orders.*, users.name as user_name '
    'FROM orders JOIN users ON orders.user_id = users.id'
).fetchall()
result = [dict(row) for row in rows]
```

---

## T-09 — Validação Duplicada → Centralização

**Aplica quando:** AP-09 detectado

**Antes:** Validação repetida em múltiplas rotas
```python
# routes/user_routes.py linha 15
if not data.get('email') or '@' not in data['email']:
    return jsonify({'error': 'Email invalido'}), 400

# routes/order_routes.py linha 42
if not request.json.get('email') or '@' not in request.json['email']:
    return jsonify({'error': 'Email invalido'}), 400
```

**Depois:**
```python
# utils/validators.py
def validate_email(email):
    if not email or '@' not in email:
        return False, 'Email invalido'
    return True, None

# routes/user_routes.py
from utils.validators import validate_email
valid, error = validate_email(data.get('email'))
if not valid:
    return jsonify({'error': error}), 400
```

---

## T-10 — Magic Numbers → Constantes

**Aplica quando:** AP-10 detectado

**Antes:**
```python
total = subtotal * 1.15
if order['status'] == 2:
    send_notification(order)
```

**Depois:**
```python
TAX_RATE = 1.15
ORDER_STATUS_CONFIRMED = 2

total = subtotal * TAX_RATE
if order['status'] == ORDER_STATUS_CONFIRMED:
    send_notification(order)
```

Prefira colocar as constantes em `config.py` ou em um módulo `constants.py`.
