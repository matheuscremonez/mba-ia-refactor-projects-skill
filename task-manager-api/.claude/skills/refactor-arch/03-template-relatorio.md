# Referência 03 — Template do Relatório de Auditoria

## Formato Exato do Relatório (Fase 2)

Gere o relatório exatamente neste formato, sem omitir seções mesmo que vazias.

```
================================================================
FASE 2: RELATÓRIO DE AUDITORIA
================================================================
Projeto:   [nome do diretório]
Perfil:    [MONOLITO | PARCIALMENTE_ORGANIZADO | ESTRUTURADO_COM_PROBLEMAS]
Arquivos:  [N] arquivos auditados
Findings:  [N] total ([N] CRITICAL, [N] HIGH, [N] MEDIUM, [N] LOW)
================================================================

## CRITICAL

[AP-XX] [Nome do Anti-Pattern]
  Arquivo: [caminho/do/arquivo.py ou .js]
  Linha:   [número da linha]
  Trecho:  [linha de código problemática]
  Risco:   [descrição do risco em 1 linha]

[AP-XX] [Nome do Anti-Pattern]
  Arquivo: [caminho/do/arquivo.py ou .js]
  Linha:   [número da linha]
  Trecho:  [linha de código problemática]
  Risco:   [descrição do risco em 1 linha]

## HIGH

[AP-XX] [Nome do Anti-Pattern]
  Arquivo: [caminho/do/arquivo.py ou .js]
  Linha:   [número da linha]
  Trecho:  [linha de código problemática]
  Risco:   [descrição do risco em 1 linha]

## MEDIUM

[AP-XX] [Nome do Anti-Pattern]
  Arquivo: [caminho/do/arquivo.py ou .js]
  Linha:   [número da linha]
  Trecho:  [linha de código problemática]
  Risco:   [descrição do risco em 1 linha]

## LOW

[AP-XX] [Nome do Anti-Pattern]
  Arquivo: [caminho/do/arquivo.py ou .js]
  Linha:   [número da linha]
  Trecho:  [linha de código problemática]
  Risco:   [descrição do risco em 1 linha]

================================================================
RESUMO POR ARQUIVO
================================================================
[arquivo.py]: [N] findings ([lista de IDs, ex: AP-01, AP-02])
[outro.py]:   [N] findings ([lista de IDs])
================================================================

Prosseguir com a refatoração? (Fase 3 irá modificar arquivos do projeto) [s/n]:
```

---

## Regras de Preenchimento

### Contagem de findings
- Cada ocorrência de um anti-pattern em uma linha = 1 finding
- O mesmo anti-pattern em linhas diferentes = findings separados
- Inclua todos os arquivos, mesmo os sem findings (aparecem no RESUMO com 0)

### Seções vazias
Se não houver nenhum finding em uma severidade, imprima:
```
## CRITICAL
(nenhum finding)
```

### Trecho de código
- Mostre apenas a linha problemática, sem contexto adicional
- Se a linha for muito longa (>80 chars), truncar com `...`
- Use o número de linha real do arquivo (não estimativa)

### Risco
- Uma frase descritiva e específica ao contexto do código encontrado
- Não repita a descrição genérica do catálogo — adapte ao contexto real

---

## Exemplo Preenchido

```
================================================================
FASE 2: RELATÓRIO DE AUDITORIA
================================================================
Projeto:   code-smells-project
Perfil:    MONOLITO
Arquivos:  4 arquivos auditados
Findings:  7 total (2 CRITICAL, 3 HIGH, 1 MEDIUM, 1 LOW)
================================================================

## CRITICAL

[AP-01] SQL Injection
  Arquivo: models.py
  Linha:   42
  Trecho:  cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
  Risco:   Permite extração de todos os dados de usuários via manipulação do parâmetro email

[AP-02] Credenciais Hardcoded
  Arquivo: app.py
  Linha:   8
  Trecho:  app.config['SECRET_KEY'] = 'super-secret-key-123'
  Risco:   Chave JWT exposta no repositório permite forjar tokens de autenticação

## HIGH

[AP-04] God Class / God File
  Arquivo: models.py
  Linha:   1
  Trecho:  class ProductManager: (87 linhas, DB + lógica + validação)
  Risco:   Impossível testar lógica de negócio sem conexão com banco de dados

[AP-05] Lógica de Negócio na Rota
  Arquivo: app.py
  Linha:   55
  Trecho:  @app.route('/checkout', methods=['POST']) (47 linhas)
  Risco:   Lógica de desconto e cálculo de total não reutilizável fora do contexto HTTP

[AP-06] Criptografia Caseira
  Arquivo: models.py
  Linha:   31
  Trecho:  if user['password'] == password:
  Risco:   Senhas em texto plano no banco; qualquer vazamento expõe credenciais reais

## MEDIUM

[AP-08] N+1 Queries
  Arquivo: controllers.py
  Linha:   78
  Trecho:  for order in orders: cursor.execute("SELECT * FROM items WHERE order_id=?", ...)
  Risco:   Performance degradada para pedidos com muitos itens; N queries para N pedidos

## LOW

[AP-10] Magic Numbers
  Arquivo: controllers.py
  Linha:   92
  Trecho:  total = subtotal * 1.15
  Risco:   Taxa de imposto de 15% hardcoded sem identificação; alteração requer busca no código

================================================================
RESUMO POR ARQUIVO
================================================================
app.py:         2 findings (AP-02, AP-05)
models.py:      3 findings (AP-01, AP-04, AP-06)
controllers.py: 2 findings (AP-08, AP-10)
utils.py:       0 findings
================================================================

Prosseguir com a refatoração? (Fase 3 irá modificar arquivos do projeto) [s/n]:
```
