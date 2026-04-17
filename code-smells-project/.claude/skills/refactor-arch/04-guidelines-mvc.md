# Referência 04 — Guidelines MVC por Perfil e Linguagem

## Estrutura MVC Alvo

O objetivo de toda refatoração é atingir separação clara de camadas:

| Camada | Responsabilidade | Não deve conter |
|--------|-----------------|------------------|
| **Routes** | Receber request, chamar controller, retornar response | Lógica de negócio, queries SQL |
| **Controllers** | Orquestrar lógica de negócio, validar, chamar models | Queries SQL diretas, código HTTP |
| **Models** | Acesso a dados: queries, ORM, mapeamento | Lógica de negócio, código HTTP |
| **Config** | Variáveis de ambiente, inicialização | Nenhum |
| **Middleware** | Auth, validação cross-cutting, logging | Lógica de domínio |

---

## Perfil MONOLITO — Python/Flask

### Estrutura de Diretórios Alvo

```
projeto/
├── app.py                    # Ponto de entrada: cria app, registra blueprints
├── config.py                 # Configurações via os.environ.get()
├── .env.example              # Variáveis necessárias sem valores reais
├── requirements.txt
├── models/
│   ├── __init__.py
│   └── [dominio].py          # Ex: product.py, user.py, order.py
├── controllers/
│   ├── __init__.py
│   └── [dominio]_controller.py
├── routes/
│   ├── __init__.py
│   └── [dominio]_routes.py   # Blueprint com rotas HTTP
└── utils/
    ├── __init__.py
    └── validators.py
```

### app.py (ponto de entrada)

```python
import os
from flask import Flask
from config import Config
from routes.product_routes import product_bp
from routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
```

### config.py

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-nao-usar-producao')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'app.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    PORT = int(os.environ.get('PORT', 5000))
```

### models/product.py (acesso a dados)

```python
import sqlite3
from config import Config

def get_connection():
    return sqlite3.connect(Config.DATABASE_URL)

def find_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    conn.close()
    return rows

def find_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row
```

### controllers/product_controller.py (lógica de negócio)

```python
from models import product as product_model

def list_products():
    rows = product_model.find_all()
    return [{'id': r[0], 'name': r[1], 'price': r[2]} for r in rows]

def get_product(product_id):
    row = product_model.find_by_id(product_id)
    if not row:
        return None
    return {'id': row[0], 'name': row[1], 'price': row[2]}
```

### routes/product_routes.py (HTTP apenas)

```python
from flask import Blueprint, jsonify
from controllers import product_controller

product_bp = Blueprint('products', __name__, url_prefix='/products')

@product_bp.route('/', methods=['GET'])
def list_products():
    products = product_controller.list_products()
    return jsonify(products), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = product_controller.get_product(product_id)
    if not product:
        return jsonify({'error': 'Produto não encontrado'}), 404
    return jsonify(product), 200
```

---

## Perfil PARCIALMENTE_ORGANIZADO — Node.js/Express

### Estrutura de Diretórios Alvo

```
projeto/
├── src/
│   ├── app.js                # Inicialização do Express, sem lógica de negócio
│   ├── config/
│   │   └── database.js       # Conexão com banco usando process.env
│   ├── models/
│   │   └── [dominio].js      # Queries SQL parametrizadas
│   ├── controllers/
│   │   └── [dominio]Controller.js
│   └── routes/
│       └── [dominio]Routes.js
├── .env.example
└── package.json
```

### src/app.js

```javascript
const express = require('express');
const productRoutes = require('./routes/productRoutes');

const app = express();
app.use(express.json());
app.use('/products', productRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor na porta ${PORT}`));

module.exports = app;
```

### src/config/database.js

```javascript
const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database(
  process.env.DATABASE_PATH || ':memory:',
  (err) => { if (err) console.error('DB error:', err.message); }
);

module.exports = db;
```

### src/models/productModel.js

```javascript
const db = require('../config/database');

function findAll() {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM products', [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function findById(id) {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM products WHERE id = ?', [id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

module.exports = { findAll, findById };
```

### src/controllers/productController.js

```javascript
const productModel = require('../models/productModel');

async function listProducts(req, res) {
  const products = await productModel.findAll();
  return res.json(products);
}

async function getProduct(req, res) {
  const product = await productModel.findById(req.params.id);
  if (!product) return res.status(404).json({ error: 'Produto não encontrado' });
  return res.json(product);
}

module.exports = { listProducts, getProduct };
```

### src/routes/productRoutes.js

```javascript
const express = require('express');
const router = express.Router();
const productController = require('../controllers/productController');

router.get('/', productController.listProducts);
router.get('/:id', productController.getProduct);

module.exports = router;
```

---

## Perfil ESTRUTURADO_COM_PROBLEMAS — Melhorias Cirúrgicas

Para este perfil, NÃO reorganize o que já está correto.
Aplique apenas as correções necessárias conforme os findings da Fase 2.

### Checklist de correções cirúrgicas

- [ ] Credenciais → mover para `config/settings.py` ou `config/env.js` com `os.environ.get` / `process.env`
- [ ] APIs deprecated → substituir apenas as linhas afetadas
- [ ] SQL Injection → parametrizar apenas as queries afetadas
- [ ] Lógica nas routes → extrair para `controllers/` apenas os handlers > 30 linhas
- [ ] Validação duplicada → consolidar nas funções de utils já existentes

### Adicionando controllers/ a projeto existente (Python/Flask)

Se o projeto já tem `models/` e `routes/` mas a lógica está nas routes:

1. Criar `controllers/__init__.py` (vazio)
2. Para cada route com lógica > 30 linhas:
   - Criar `controllers/[dominio]_controller.py`
   - Mover a lógica para funções no controller
   - Na route, importar e chamar o controller

**Não altere** models, utils, ou routes que já estão corretas.

---

## .env.example (qualquer perfil)

Sempre criar `.env.example` na raiz com todas as variáveis necessárias:

```
# Copie este arquivo para .env e preencha com valores reais
SECRET_KEY=
DATABASE_URL=
FLASK_DEBUG=false
PORT=5000
# Node.js apenas:
# PORT=3000
```

**Regras:**
- Nunca coloque valores reais no `.env.example`
- Liste todas as variáveis usadas no código
- Adicione `.env` ao `.gitignore` se ainda não estiver
