# Referência 01 — Análise de Projeto

## Detecção de Linguagem e Framework

### Python
- **Sinal:** presença de `requirements.txt` na raiz
- **Flask:** `from flask import Flask` nos imports ou `flask` em `requirements.txt`
- **Django:** `django` em `requirements.txt` ou presença de `manage.py`
- **FastAPI:** `fastapi` em `requirements.txt`
- **Versão:** leia a linha `Flask==X.Y.Z` em `requirements.txt`

### Node.js
- **Sinal:** presença de `package.json` na raiz
- **Express:** `"express"` em `dependencies` no `package.json`
- **NestJS:** `"@nestjs/core"` em `dependencies`
- **Versão:** campo `"version"` no `package.json`; versões das libs em `dependencies`

## Detecção de Banco de Dados

| Sinal encontrado no código ou dependências | Banco |
|---|---|
| `sqlite3`, `SQLite`, `.db` | SQLite |
| `psycopg2`, `pg`, `postgresql` | PostgreSQL |
| `mysql`, `pymysql`, `mysql2` | MySQL |
| `mongoose`, `mongodb` | MongoDB |
| `SQLAlchemy` com URI | Depende da URI (`sqlite:///`, `postgresql://`, etc.) |
| `:memory:` (sqlite3 Node.js) | SQLite in-memory |

## Detecção de Domínio

Leia os nomes de:
- Tabelas SQL (`CREATE TABLE`, `db.Model` subclasses)
- Rotas HTTP (`@app.route`, `app.get`, `app.post`, `router.get`)
- Arquivos e nomes de funções

**Exemplos de inferência:**
- Tabelas `produtos`, `pedidos`, `usuarios` → E-commerce API
- Tabelas `courses`, `enrollments`, `payments` → LMS / Plataforma de cursos
- Tabelas/models `tasks`, `users`, `categories` → Task Manager

## Classificação do Perfil Arquitetural

### MONOLITO
**Critérios — pelo menos 2 devem ser verdadeiros:**
- 5 ou menos arquivos `.py` ou `.js` na raiz sem subpastas relevantes
- Um único arquivo contém rotas, lógica de negócio E acesso ao banco de dados
- Não existe separação entre camadas (sem pastas `models/`, `controllers/`, `routes/`)
- Uma classe ou módulo define rotas E lógica de negócio E queries SQL

**Exemplo real (code-smells-project):**
`app.py` define rotas, `models.py` tem lógica de negócio + queries SQL,
`controllers.py` tem validação — tudo em 4 arquivos, sem subpastas.

---

### PARCIALMENTE_ORGANIZADO
**Critérios — pelo menos 2 devem ser verdadeiros:**
- Existe separação de arquivos MAS com responsabilidades misturadas
- Existe uma classe central (`AppManager`, `App`) que faz tudo: DB + rotas + lógica
- Routes existem mas contêm lógica de negócio pesada (mais de 30 linhas por função)
- Falta camada de controllers separada

**Exemplo real (ecommerce-api-legacy):**
`AppManager.js` com `initDb()` + `setupRoutes()` + lógica de checkout + lógica de
relatório, tudo na mesma classe de 141 linhas.

---

### ESTRUTURADO_COM_PROBLEMAS
**Critérios — pelo menos 2 devem ser verdadeiros:**
- Existem subpastas reconhecíveis: `models/`, `routes/`, `services/`, `utils/`
- Os arquivos têm responsabilidades razoavelmente separadas
- MAS existem problemas de segurança (credenciais hardcoded) ou APIs deprecated
- MAS falta camada de `controllers/` (lógica de negócio nas rotas)
- MAS validações duplicadas entre módulos

**Exemplo real (task-manager-api):**
Tem `models/`, `routes/`, `services/`, `utils/` MAS:
- Lógica de negócio nas routes (task_routes.py com 200+ linhas)
- `SECRET_KEY` hardcoded em `app.py`
- `User.query.get()` deprecated (SQLAlchemy 2.x)
- Validações em `utils/helpers.py` que não são usadas pelas routes

---

## Formato do Resumo da Fase 1

```
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:      Python 3.x
Framework:      Flask 3.1.1
Banco de dados: SQLite (arquivo local)
Domínio:        E-commerce API (produtos, pedidos, usuários)
Arquitetura:    MONOLITO — tudo em 4 arquivos, sem separação de camadas
Arquivos fonte: 4 arquivos analisados
================================
```
