# Referência 02 — Catálogo de Anti-Patterns

## AP-01 — SQL Injection
**Severidade:** CRITICAL  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- String concatenation em queries: `"SELECT * FROM users WHERE id = " + user_id`
- f-string em queries: `f"SELECT * FROM users WHERE name = '{name}'"`
- Template literal em queries: `` `SELECT * FROM users WHERE id = ${id}` ``
- `.format()` em queries SQL: `"WHERE email = '{}'".format(email)`

**Impacto:** Permite extração, modificação ou destruição de qualquer dado do banco.

**Correção:**
- Python (sqlite3): `cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))`
- Python (psycopg2): `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`
- Node.js (sqlite3): `db.get("SELECT * FROM users WHERE id = ?", [id], callback)`

---

## AP-02 — Credenciais Hardcoded
**Severidade:** CRITICAL  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- `SECRET_KEY = "minha-chave-secreta"` ou qualquer string literal em variável de chave
- `password = "admin123"` fora de testes
- `DATABASE_URL = "postgresql://user:pass@host/db"` literal
- `API_KEY = "sk-..."` literal
- Credenciais em arquivos de configuração versionados

**Impacto:** Exposição de credenciais no repositório; comprometimento total em caso de vazamento.

**Correção:**
- Python: `SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-fallback")`
- Node.js: `const SECRET_KEY = process.env.SECRET_KEY`
- Criar `.env.example` com os nomes das variáveis sem valores reais
- Adicionar `.env` ao `.gitignore`

---

## AP-03 — Endpoint de Execução Arbitrária
**Severidade:** CRITICAL  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- Rota que recebe SQL do corpo da requisição e executa diretamente
- Funções de avaliação dinâmica: `eval()` no Python; construtores de função dinâmica no Node.js
- Execução de processos do sistema com dados do request: `subprocess.run()`, `os.system()`
- Rota `/query` ou `/execute` que processa comandos arbitrários recebidos via HTTP

**Impacto:** Execução remota de código ou SQL; comprometimento total do servidor.

**Correção:** Remover o endpoint completamente. Não existe correção segura para execução arbitrária de código/SQL recebido via HTTP.

---

## AP-04 — God Class / God File
**Severidade:** HIGH  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- Uma classe ou arquivo com mais de 100 linhas contendo: inicialização de DB + definição de rotas + lógica de negócio
- Método único que faz: validação + query ao banco + transformação de dados + resposta HTTP
- Classe com mais de 5 responsabilidades distintas
- Arquivo único com `initDb()` + `setupRoutes()` + funções de negócio

**Impacto:** Impossibilidade de testar unidades isoladas; alterações causam efeitos colaterais imprevisíveis.

**Correção:**
- Extrair cada responsabilidade para seu próprio módulo
- Criar camadas: `models/` (acesso a dados), `controllers/` (lógica de negócio), `routes/` (HTTP)
- Cada arquivo deve ter uma única responsabilidade

---

## AP-05 — Lógica de Negócio na Camada de Rotas
**Severidade:** HIGH  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- Função de rota com mais de 30 linhas
- Query SQL diretamente dentro de `@app.route` ou `app.get()`
- Validações, cálculos ou transformações dentro da função de rota
- `cursor.execute()` ou `db.query()` dentro do handler HTTP

**Impacto:** Lógica não reutilizável; impossível testar sem simular requisições HTTP.

**Correção:**
- Criar `controllers/` para conter a lógica de negócio
- Rota deve apenas: parsear request → chamar controller → retornar response
- Controller deve: validar → consultar model → transformar → retornar dado

---

## AP-06 — Criptografia Caseira / Senha em Texto Plano
**Severidade:** HIGH  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- `password == request.form['password']` (comparação direta sem hash)
- `hashlib.md5(password)` ou `hashlib.sha1(password)` para senhas
- Função de hash customizada para autenticação
- Senha armazenada sem hash ou com hash reversível

**Impacto:** Senhas expostas em caso de vazamento do banco de dados.

**Correção:**
- Python: usar `bcrypt.hashpw()` e `bcrypt.checkpw()`
- Node.js: usar `bcrypt.hash()` e `bcrypt.compare()`
- Nunca usar MD5 ou SHA1 para senhas (são hashes, não funções de derivação de chave)

---

## AP-07 — Uso de API Deprecated
**Severidade:** MEDIUM  
**Linguagens:** Python

**Sinais de detecção:**
- `Model.query.get(id)` — deprecated no SQLAlchemy 2.x
- `Model.query.filter_by()` — ainda funciona mas padrão legacy
- `db.session.execute(text(...))` sem `.mappings()` onde era esperado dict
- Imports de módulos marcados como deprecated na versão instalada

**Impacto:** Warnings no console; quebra em upgrades futuros do framework.

**Correção:**
- `Model.query.get(id)` → `db.session.get(Model, id)`
- Verificar `requirements.txt` para versão do SQLAlchemy e aplicar correções correspondentes

---

## AP-08 — Problema N+1 Queries
**Severidade:** MEDIUM  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- Loop que executa query dentro de cada iteração
- `for item in items: db.query("SELECT ... WHERE id = ?", item.id)`
- Múltiplas queries quando uma com JOIN resolveria

**Impacto:** Degradação de performance proporcional ao volume de dados; pode tornar endpoints inutilizáveis em produção.

**Correção:**
- Substituir por query única com JOIN
- Python (sqlite3): `SELECT orders.*, users.name FROM orders JOIN users ON orders.user_id = users.id`
- Usar `.joinedload()` se SQLAlchemy ORM

---

## AP-09 — Validação Duplicada
**Severidade:** MEDIUM  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- Mesma validação (ex: "campo obrigatório", "formato de email") implementada em múltiplos arquivos
- Funções utilitárias em `utils/helpers.py` ou `utils/validators.js` que não são importadas pelas rotas
- Lógica de validação inline nas rotas E em helpers separados

**Impacto:** Divergência de regras entre endpoints; manutenção dobrada.

**Correção:**
- Centralizar validações em `utils/validators.py` ou `middleware/validation.js`
- Garantir que todos os endpoints usem as mesmas funções de validação
- Remover validações inline nas rotas se já existe helper equivalente

---

## AP-10 — Magic Numbers / Print de Debug
**Severidade:** LOW  
**Linguagens:** Python, Node.js

**Sinais de detecção:**
- Números literais sem contexto: `if status == 2:`, `price * 0.15`
- `print()` fora de contexto de debug explícito (Python)
- `console.log()` sem prefixo de contexto (Node.js)
- Strings de mensagem de erro duplicadas em múltiplos arquivos

**Impacto:** Código difícil de entender e manter; logs poluídos em produção.

**Correção:**
- Extrair constantes: `TAX_RATE = 0.15`, `STATUS_ACTIVE = 1`
- Substituir `print()` por logging adequado (`import logging`)
- Remover `console.log()` de debug ou substituir por logger estruturado

---

## Tabela Resumo

| ID    | Anti-Pattern                    | Severidade | Perfis afetados |
|-------|---------------------------------|------------|-----------------|
| AP-01 | SQL Injection                   | CRITICAL   | Todos           |
| AP-02 | Credenciais Hardcoded           | CRITICAL   | Todos           |
| AP-03 | Endpoint Arbitrário             | CRITICAL   | Todos           |
| AP-04 | God Class / God File            | HIGH       | MONOLITO, PARCIALMENTE_ORGANIZADO |
| AP-05 | Lógica de Negócio na Rota       | HIGH       | Todos           |
| AP-06 | Criptografia Caseira            | HIGH       | Todos           |
| AP-07 | API Deprecated                  | MEDIUM     | ESTRUTURADO_COM_PROBLEMAS |
| AP-08 | N+1 Queries                     | MEDIUM     | Todos           |
| AP-09 | Validação Duplicada             | MEDIUM     | ESTRUTURADO_COM_PROBLEMAS |
| AP-10 | Magic Numbers / Print de Debug  | LOW        | Todos           |
