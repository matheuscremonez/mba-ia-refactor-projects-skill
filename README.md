# Criação de Skills — Refatoração Arquitetural Automatizada

Desafio de pós-graduação: criar uma skill genérica do Claude Code que automatiza
análise, auditoria e refatoração de projetos legados para o padrão MVC.

---

## 1. Análise Manual dos Projetos

### code-smells-project — Perfil: MONOLITO

**Stack:** Python 3 + Flask + SQLite

**Estrutura original:** 4 arquivos na raiz, sem subpastas
- `app.py` — rotas Flask
- `models.py` — lógica de negócio + queries SQL (misturadas)
- `controllers.py` — validações
- `requirements.txt`

**Problemas identificados:**
| Anti-Pattern | Arquivo | Severidade |
|---|---|---|
| SQL Injection via concatenação de string | models.py | CRITICAL |
| SECRET_KEY hardcoded | app.py | CRITICAL |
| Senha comparada em texto plano | models.py | HIGH |
| Lógica de negócio fora de controllers dedicados | models.py | HIGH |
| Magic numbers em cálculos de preço | controllers.py | LOW |

### ecommerce-api-legacy — Perfil: PARCIALMENTE_ORGANIZADO

**Stack:** Node.js + Express + SQLite (in-memory)

**Estrutura original:** Tudo concentrado em `AppManager.js` (141 linhas)
- `AppManager.js` — God Class: inicializa banco + define rotas + lógica de checkout + relatórios
- `utils.js` — funções utilitárias com credenciais hardcoded

**Problemas identificados:**
| Anti-Pattern | Arquivo | Severidade |
|---|---|---|
| Credenciais de produção hardcoded | utils.js | CRITICAL |
| God Class com 5+ responsabilidades | AppManager.js | HIGH |
| Lógica de negócio nas rotas | AppManager.js | HIGH |
| SQL via concatenação | AppManager.js | CRITICAL |
| N+1 queries em listagem | AppManager.js | MEDIUM |

### task-manager-api — Perfil: ESTRUTURADO_COM_PROBLEMAS

**Stack:** Python 3 + Flask + SQLAlchemy + SQLite

**Estrutura original:** MVC parcial com subpastas
- `models/` — modelos SQLAlchemy
- `routes/` — rotas Flask com lógica pesada (200+ linhas)
- `services/` — serviços parcialmente usados
- `utils/helpers.py` — validadores não utilizados pelas routes

**Problemas identificados:**
| Anti-Pattern | Arquivo | Severidade |
|---|---|---|
| SECRET_KEY hardcoded | app.py | CRITICAL |
| Lógica de negócio nas routes | routes/task_routes.py | HIGH |
| `User.query.get()` deprecated | routes/user_routes.py | MEDIUM |
| Validações duplicadas entre routes e utils | routes/ + utils/ | MEDIUM |

---

## 2. Design da Skill `refactor-arch`

### Objetivo

Skill genérica que executa três fases em qualquer projeto legado:
1. **Análise** — detecta stack, banco de dados e classifica perfil arquitetural
2. **Auditoria** — varre todos os arquivos contra catálogo de 10 anti-patterns, gera relatório
3. **Refatoração** — reorganiza e corrige o código conforme o perfil detectado

### Decisões de design

**Perfis adaptativos em vez de solução única**

A skill classifica o projeto em 3 perfis (`MONOLITO`, `PARCIALMENTE_ORGANIZADO`,
`ESTRUTURADO_COM_PROBLEMAS`) e aplica estratégias diferentes para cada um.
Isso evita destruir estruturas já corretas e foca o trabalho onde é necessário.

**Gate humano antes da Fase 3**

Após gerar o relatório de auditoria, a skill pausa e pergunta `[s/n]` antes de modificar
qualquer arquivo. O desenvolvedor pode revisar os findings e decidir não prosseguir.

**Documentação separada em 5 arquivos de referência**

O `SKILL.md` orquestra as fases mas delega o conhecimento de domínio para arquivos de referência:
- `01-analise-projeto.md` — heurísticas de detecção e classificação
- `02-catalogo-antipatterns.md` — 10 anti-patterns com severidade e sinais
- `03-template-relatorio.md` — formato exato do relatório de auditoria
- `04-guidelines-mvc.md` — estrutura MVC alvo com exemplos de código
- `05-playbook-refatoracao.md` — 10 transformações com antes/depois

Essa separação permite atualizar regras sem alterar o fluxo principal,
e torna cada arquivo mais legível.

**Agnóstica de linguagem por design**

Cada anti-pattern tem sinais de detecção para Python e Node.js.
Os guidelines MVC têm exemplos para Flask e Express.
A mesma skill funciona nos 3 projetos sem modificação.

### Estrutura dos arquivos da skill

```
.claude/
└── skills/
    └── refactor-arch/
        ├── SKILL.md                    # Orquestrador das 3 fases
        ├── 01-analise-projeto.md       # Heurísticas de detecção
        ├── 02-catalogo-antipatterns.md # 10 anti-patterns com severidade
        ├── 03-template-relatorio.md    # Formato do relatório
        ├── 04-guidelines-mvc.md        # Estrutura MVC por linguagem
        └── 05-playbook-refatoracao.md  # Transformações antes/depois
```

---

## 3. Como Usar a Skill

### Pré-requisito

- Claude Code CLI instalado
- A skill já está presente em cada projeto (pasta `.claude/skills/refactor-arch/`)

### Execução

Navegue até o diretório do projeto e invoque a skill:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

### O que esperar

1. A skill imprime o resumo da **Fase 1** (linguagem, framework, banco, domínio, perfil)
2. Lê todos os arquivos e gera o **relatório de auditoria** (Fase 2)
3. Pergunta `Prosseguir com a refatoração? [s/n]` — responda `s` para continuar
4. Executa a **Fase 3** e ao final imprime checklist de validação manual

### Validação após refatoração

Siga o checklist impresso pela skill ao final da Fase 3. Para projetos Python/Flask:

```bash
pip install -r requirements.txt
cp .env.example .env  # preencher com valores reais
python app.py
curl http://localhost:5000/health
```

---

## 4. Resultados da Execução

Relatórios completos disponíveis em [`reports/`](./reports/).

### code-smells-project

**Perfil detectado:** MONOLITO  
**Findings:** 21 total — 11 CRITICAL, 6 HIGH, 2 MEDIUM, 2 LOW  
**Relatório:** [`reports/audit-project-1.md`](./reports/audit-project-1.md)

**Estrutura antes:**
```
app.py / models.py / controllers.py / database.py
(sem subpastas, tudo misturado)
```

**Estrutura depois:**
```
app.py / config.py / .env.example
models/     → produto.py, usuario.py, pedido.py
controllers/ → produto_controller.py, usuario_controller.py, pedido_controller.py
routes/     → produto_routes.py, usuario_routes.py, pedido_routes.py
utils/      → validators.py
```

**Checklist de validação:**
- [x] Linguagem detectada corretamente (Python + Flask 3.1.1)
- [x] Domínio detectado corretamente (E-commerce API)
- [x] Perfil classificado corretamente (MONOLITO)
- [x] Fase 2 encontrou ≥ 5 findings (21 encontrados)
- [x] Pelo menos 1 CRITICAL detectado (11 CRITICAL)
- [x] Skill pausou e pediu confirmação antes da Fase 3
- [x] Estrutura MVC criada após refatoração
- [x] Credenciais migradas para `config.py` + `.env.example`
- [x] SQL Injection corrigido com queries parametrizadas (`?`)
- [x] Endpoint `/admin/query` removido
- [x] Senhas protegidas com bcrypt

---

### ecommerce-api-legacy

**Perfil detectado:** PARCIALMENTE_ORGANIZADO  
**Findings:** 11 total — 4 CRITICAL, 4 HIGH, 2 MEDIUM, 1 LOW  
**Relatório:** [`reports/audit-project-2.md`](./reports/audit-project-2.md)

**Estrutura antes:**
```
src/AppManager.js  (God Class — 141 linhas: DB + rotas + checkout + relatório)
src/utils.js       (credenciais de produção hardcoded)
```

**Estrutura depois:**
```
src/app.js / .env.example
src/config/     → database.js
src/models/     → userModel.js, courseModel.js, enrollmentModel.js
src/controllers/ → checkoutController.js, reportController.js, userController.js
src/routes/     → checkoutRoutes.js, reportRoutes.js, userRoutes.js
```

**Checklist de validação:**
- [x] Linguagem detectada corretamente (Node.js + Express)
- [x] Domínio detectado corretamente (LMS / Plataforma de Cursos)
- [x] Perfil classificado corretamente (PARCIALMENTE_ORGANIZADO)
- [x] Fase 2 encontrou ≥ 5 findings (11 encontrados)
- [x] Pelo menos 1 CRITICAL detectado (4 CRITICAL)
- [x] Skill pausou e pediu confirmação antes da Fase 3
- [x] God Class `AppManager.js` quebrada em camadas separadas
- [x] Credenciais de produção removidas de `utils.js` → `process.env`
- [x] `badCrypto()` substituída por `bcrypt`
- [x] Estado global mutável (`globalCache`, `totalRevenue`) eliminado

---

### task-manager-api

**Perfil detectado:** ESTRUTURADO_COM_PROBLEMAS  
**Findings:** 9 total — 1 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW  
**Relatório:** [`reports/audit-project-3.md`](./reports/audit-project-3.md)

**Estrutura antes:**
```
app.py (SECRET_KEY hardcoded)
models/ routes/ services/ utils/
(estrutura existente, mas lógica pesada nas routes e APIs deprecated)
```

**Estrutura depois:**
```
app.py / config.py / .env.example
models/      → inalterados (já corretos)
controllers/ → task_controller.py, user_controller.py, report_controller.py  ← NOVO
routes/      → lógica extraída para controllers
services/    → inalterados
utils/       → inalterados
```

**Checklist de validação:**
- [x] Linguagem detectada corretamente (Python + Flask + SQLAlchemy)
- [x] Domínio detectado corretamente (Task Manager API)
- [x] Perfil classificado corretamente (ESTRUTURADO_COM_PROBLEMAS)
- [x] Fase 2 encontrou ≥ 5 findings (9 encontrados)
- [x] Pelo menos 1 CRITICAL detectado (SECRET_KEY hardcoded)
- [x] Skill pausou e pediu confirmação antes da Fase 3
- [x] `User.query.get()` substituído por `db.session.get(User, id)`
- [x] Lógica extraída das routes para `controllers/` (cirurgicamente)
- [x] Estrutura existente preservada onde já estava correta
- [x] MD5 substituído por bcrypt em `models/user.py`
