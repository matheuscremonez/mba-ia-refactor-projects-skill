# Relatório de Auditoria — ecommerce-api-legacy

> Gerado pela skill `refactor-arch` — Fase 2

================================================================
FASE 2: RELATÓRIO DE AUDITORIA
================================================================
Projeto:   ecommerce-api-legacy
Perfil:    PARCIALMENTE_ORGANIZADO
Arquivos:  3 arquivos auditados (app.js, src/AppManager.js, src/utils.js)
Findings:  11 total (4 CRITICAL, 4 HIGH, 2 MEDIUM, 1 LOW)
================================================================

## CRITICAL

[AP-02] Credenciais Hardcoded
  Arquivo: src/utils.js
  Linha:   2
  Trecho:  dbPass: "senha_super_secreta_prod_123",
  Risco:   Senha do banco de dados de produção exposta no repositório público

[AP-02] Credenciais Hardcoded
  Arquivo: src/utils.js
  Linha:   3
  Trecho:  paymentGatewayKey: "pk_live_1234567890abcdef",
  Risco:   Chave de gateway de pagamento em produção (pk_live_) exposta; permite cobranças fraudulentas

[AP-06] Criptografia Caseira
  Arquivo: src/utils.js
  Linha:   16
  Trecho:  function badCrypto(pwd) { hash += Buffer.from(pwd).toString('base64')... }
  Risco:   Função de "hash" customizada trivialmente reversível; senhas nunca estão seguras

[AP-06] Criptografia Caseira / Senha em Texto Plano
  Arquivo: src/AppManager.js
  Linha:   20
  Trecho:  this.db.run("INSERT INTO users ... VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')")
  Risco:   Seed com senha '123' em plaintext; usuário administrador sem proteção alguma

## HIGH

[AP-04] God Class
  Arquivo: src/AppManager.js
  Linha:   1
  Trecho:  class AppManager { initDb() + setupRoutes() + processPayment + report + delete } (141 linhas)
  Risco:   5 responsabilidades distintas na mesma classe; impossível testar checkout sem banco real

[AP-05] Lógica de Negócio na Camada de Rotas
  Arquivo: src/AppManager.js
  Linha:   30
  Trecho:  app.post('/api/checkout', ...) { validação + criação de usuário + pagamento + matrícula + log }
  Risco:   Handler de 60+ linhas mistura autenticação, pagamento e matrícula sem separação

[AP-05] Lógica de Negócio na Camada de Rotas
  Arquivo: src/AppManager.js
  Linha:   82
  Trecho:  app.get('/api/admin/financial-report', ...) { queries aninhadas + cálculo de revenue }
  Risco:   Lógica de relatório financeiro dentro do handler HTTP; não reutilizável nem testável

[AP-04] God Class — Estado Global Mutável
  Arquivo: src/utils.js
  Linha:   8
  Trecho:  let globalCache = {}; let totalRevenue = 0;
  Risco:   Estado global compartilhado entre requisições; causa race conditions em carga concorrente

## MEDIUM

[AP-08] Problema N+1 Queries
  Arquivo: src/AppManager.js
  Linha:   95
  Trecho:  courses.forEach(c => { this.db.all("SELECT * FROM enrollments WHERE course_id = ?", ...)
  Risco:   Para cada curso, executa query de matrículas + query de usuário + query de pagamento

[AP-08] Problema N+1 Queries
  Arquivo: src/AppManager.js
  Linha:   107
  Trecho:  enrollments.forEach(enr => { this.db.get("SELECT name FROM users WHERE id = ?", enr.user_id)
  Risco:   N queries de usuário dentro do loop de matrículas; degrada com volume de alunos

## LOW

[AP-10] Print de Debug / Log sem Contexto
  Arquivo: src/AppManager.js
  Linha:   49
  Trecho:  console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)
  Risco:   Número de cartão e chave de pagamento logados em stdout; exposição em logs de servidor

================================================================
RESUMO POR ARQUIVO
================================================================
app.js:           0 findings
src/AppManager.js: 7 findings (AP-04 ×2, AP-05 ×2, AP-06, AP-08 ×2, AP-10)
src/utils.js:     4 findings (AP-02 ×2, AP-04, AP-06)
================================================================
