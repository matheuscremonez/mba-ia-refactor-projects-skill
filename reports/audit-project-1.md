# Relatório de Auditoria — code-smells-project

> Gerado pela skill `refactor-arch` — Fase 2

================================================================
FASE 2: RELATÓRIO DE AUDITORIA
================================================================
Projeto:   code-smells-project
Perfil:    MONOLITO
Arquivos:  4 arquivos auditados
Findings:  21 total (11 CRITICAL, 6 HIGH, 2 MEDIUM, 2 LOW)
================================================================

## CRITICAL

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   28
  Trecho:  cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
  Risco:   Parâmetro id manipulável permite dump ou destruição da tabela de produtos

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   47
  Trecho:  "INSERT INTO produtos ... VALUES ('" + nome + "', '" + descricao + "', ..."
  Risco:   Campos nome/descrição/categoria permitem injeção que altera ou destrói o banco

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   57
  Trecho:  "UPDATE produtos SET nome = '" + nome + "', descricao = '" + descricao + "' ..."
  Risco:   Atualização sem parametrização permite sobrescrever registros arbitrários

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   110
  Trecho:  "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
  Risco:   Email com ' OR '1'='1 autentica qualquer usuário sem senha válida

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   127
  Trecho:  "INSERT INTO usuarios ... VALUES ('" + nome + "', '" + email + "', '" + senha + "' ..."
  Risco:   Campos do cadastro permitem injeção que compromete toda a tabela de usuários

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   140
  Trecho:  cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
  Risco:   produto_id do payload de pedido pode injetar SQL dentro da transação de compra

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   280
  Trecho:  "UPDATE pedidos SET status = '" + novo_status + "' WHERE id = " + str(pedido_id)
  Risco:   novo_status recebido via HTTP sem validação completa permite injeção no UPDATE

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   291
  Trecho:  query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
  Risco:   Termo de busca permite injeção que exfiltra dados de qualquer tabela do banco

[AP-02] Credenciais Hardcoded
  Arquivo: app.py
  Linha:   7
  Trecho:  app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
  Risco:   Chave secreta da aplicação exposta no repositório permite forjar sessões/tokens

[AP-02] Credenciais Hardcoded
  Arquivo: controllers.py
  Linha:   289
  Trecho:  "secret_key": "minha-chave-super-secreta-123"
  Risco:   SECRET_KEY retornada no endpoint /health expõe a chave para qualquer chamador

[AP-03] Endpoint de Execução Arbitrária
  Arquivo: app.py
  Linha:   59
  Trecho:  @app.route("/admin/query", methods=["POST"]) ... cursor.execute(query)
  Risco:   Qualquer requisição HTTP pode executar SQL arbitrário; compromisso total do banco

## HIGH

[AP-04] God File
  Arquivo: models.py
  Linha:   1
  Trecho:  (315 linhas: queries SQL + lógica de negócio: validação de estoque, cálculo de total...)
  Risco:   Lógica de negócio em criar_pedido/relatorio_vendas impossibilita testes isolados

[AP-04] God File
  Arquivo: controllers.py
  Linha:   1
  Trecho:  (293 linhas: handlers HTTP + validações + notificações simuladas via print())
  Risco:   Mistura de request/jsonify com regras de negócio impede reutilização fora do HTTP

[AP-05] Lógica de Negócio na Camada de Rotas
  Arquivo: controllers.py
  Linha:   24
  Trecho:  def criar_produto(): ... categorias_validas = [...] if categoria not in categorias_validas:
  Risco:   Validação de categorias e regras de preço hardcoded no handler HTTP, não reutilizável

[AP-06] Criptografia Caseira / Senha em Texto Plano
  Arquivo: models.py
  Linha:   127
  Trecho:  "INSERT INTO usuarios ... VALUES (... '" + senha + "' ...)"
  Risco:   Senhas armazenadas em plaintext; qualquer dump do banco expõe todas as credenciais

[AP-06] Criptografia Caseira / Senha em Texto Plano
  Arquivo: models.py
  Linha:   110
  Trecho:  "SELECT * FROM usuarios WHERE email = '...' AND senha = '" + senha + "'"
  Risco:   Autenticação por comparação direta na query; sem hash nem salt na verificação

[AP-06] Criptografia Caseira / Senha em Texto Plano
  Arquivo: database.py
  Linha:   77
  Trecho:  ("Admin", "admin@loja.com", "admin123", "admin"), ("João Silva", ... "123456", ...)
  Risco:   Seed data com senhas triviais em plaintext; admin123 é a senha do administrador

## MEDIUM

[AP-08] Problema N+1 Queries
  Arquivo: models.py
  Linha:   171
  Trecho:  for row in rows: cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ..."
  Risco:   Para N pedidos, executa N+N*M queries; degrada para inutilizável com volume real

[AP-08] Problema N+1 Queries
  Arquivo: models.py
  Linha:   203
  Trecho:  for row in rows: cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ..."
  Risco:   get_todos_pedidos repete o mesmo padrão N+1 do listar por usuário, sem JOIN

## LOW

[AP-10] Magic Numbers
  Arquivo: models.py
  Linha:   257
  Trecho:  if faturamento > 10000: desconto = faturamento * 0.1
  Risco:   Faixas (10000/5000/1000) e taxas (0.1/0.05/0.02) sem nome; alteração requer grep

[AP-10] Print de Debug
  Arquivo: controllers.py
  Linha:   8
  Trecho:  print("Listando " + str(len(produtos)) + " produtos")
  Risco:   Múltiplos print() em produção poluem stdout; sem nível de log, timestamp ou contexto

================================================================
RESUMO POR ARQUIVO
================================================================
app.py:         3 findings  (AP-02, AP-03, AP-10)
models.py:      14 findings (AP-01 ×8, AP-04, AP-06 ×2, AP-08 ×2, AP-10)
controllers.py: 4 findings  (AP-02, AP-04, AP-05, AP-10)
database.py:    1 finding   (AP-06)
================================================================
