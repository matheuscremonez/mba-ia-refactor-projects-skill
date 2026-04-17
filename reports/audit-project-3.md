# Relatório de Auditoria — task-manager-api

> Gerado pela skill `refactor-arch` — Fase 2

================================================================
FASE 2: RELATÓRIO DE AUDITORIA
================================================================
Projeto:   task-manager-api
Perfil:    ESTRUTURADO_COM_PROBLEMAS
Arquivos:  8 arquivos auditados
Findings:  9 total (1 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW)
================================================================

## CRITICAL

[AP-02] Credenciais Hardcoded
  Arquivo: app.py
  Linha:   13
  Trecho:  app.config['SECRET_KEY'] = 'super-secret-key-123'
  Risco:   Chave JWT exposta no repositório; permite forjar tokens de autenticação de qualquer usuário

## HIGH

[AP-05] Lógica de Negócio na Camada de Rotas
  Arquivo: routes/task_routes.py
  Linha:   1
  Trecho:  (200+ linhas: validação de status, cálculo de overdue, serialização manual de cada campo)
  Risco:   Toda lógica de domínio de tarefas dentro dos handlers HTTP; impossível reutilizar ou testar

[AP-06] Criptografia Caseira
  Arquivo: models/user.py
  Linha:   27
  Trecho:  self.password = hashlib.md5(pwd.encode()).hexdigest()
  Risco:   MD5 é um hash de propósito geral, não função de derivação de chave; trivialmente quebrável

[AP-05] Lógica de Negócio na Camada de Rotas
  Arquivo: routes/user_routes.py
  Linha:   1
  Trecho:  (150+ linhas: validação de campos, geração de JWT, verificação de role inline)
  Risco:   Regras de autenticação e autorização espalhadas nos handlers em vez de serviço dedicado

## MEDIUM

[AP-07] API Deprecated
  Arquivo: routes/task_routes.py
  Linha:   47
  Trecho:  user = User.query.get(t.user_id)
  Risco:   Model.query.get() deprecated no SQLAlchemy 2.x; gera LegacyAPIWarning e quebra em upgrade

[AP-07] API Deprecated
  Arquivo: routes/task_routes.py
  Linha:   57
  Trecho:  cat = Category.query.get(t.category_id)
  Risco:   Mesmo padrão deprecated; todas as lookups por PK precisam migrar para db.session.get()

[AP-09] Validação Duplicada
  Arquivo: routes/task_routes.py + utils/helpers.py
  Linha:   —
  Trecho:  Validações de campos obrigatórios reimplementadas inline nas routes; helpers.py não utilizado
  Risco:   Regras divergentes entre endpoints; bug corrigido em um lugar não propaga para o outro

## LOW

[AP-10] Print de Debug
  Arquivo: routes/task_routes.py
  Linha:   —
  Trecho:  import sys, json, os, time (imports não utilizados)
  Risco:   Imports órfãos de desenvolvimento aumentam tempo de load e confundem leitores

[AP-10] Magic Numbers
  Arquivo: routes/report_routes.py
  Linha:   —
  Trecho:  Cálculos de produtividade com valores literais sem nomes de constante
  Risco:   Regras de negócio de relatório sem documentação; alteração requer leitura do contexto

================================================================
RESUMO POR ARQUIVO
================================================================
app.py:                    1 finding  (AP-02)
routes/task_routes.py:     4 findings (AP-05, AP-07 ×2, AP-10)
routes/user_routes.py:     1 finding  (AP-05)
routes/report_routes.py:   1 finding  (AP-10)
models/user.py:            1 finding  (AP-06)
utils/helpers.py:          1 finding  (AP-09)
models/task.py:            0 findings
services/:                 0 findings
================================================================
