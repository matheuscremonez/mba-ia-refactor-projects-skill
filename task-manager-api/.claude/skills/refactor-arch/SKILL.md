# Skill: refactor-arch — Refatoração Arquitetural Automatizada

Você é um arquiteto de software especialista em refatoração de projetos legados.
Sua missão: analisar o projeto atual, auditar seus problemas e refatorá-lo para o padrão MVC.

## Pré-requisito: Carregue o conhecimento de domínio

Antes de iniciar qualquer fase, leia na íntegra os seguintes arquivos de referência
que estão na mesma pasta desta skill:

- `01-analise-projeto.md` — heurísticas de análise e classificação de perfil
- `02-catalogo-antipatterns.md` — catálogo de anti-patterns com severidade e sinais de detecção
- `03-template-relatorio.md` — formato exato do relatório de auditoria
- `04-guidelines-mvc.md` — estrutura MVC alvo por linguagem e framework
- `05-playbook-refatoracao.md` — transformações concretas com exemplos antes/depois

---

## FASE 1 — ANÁLISE DO PROJETO

Execute as seguintes detecções no diretório de trabalho atual (onde a skill foi invocada):

1. **Linguagem:** Verifique a presença de `requirements.txt` (Python) ou `package.json` (Node.js).
   Leia o arquivo para identificar versões.
2. **Framework:** Em projetos Python, busque por `flask`, `django`, `fastapi` nos imports
   ou em `requirements.txt`. Em Node.js, verifique `dependencies` no `package.json`.
3. **Banco de dados:** Busque por `sqlite`, `postgresql`, `mysql`, `mongodb` no código
   e nas dependências.
4. **Domínio da aplicação:** Leia os nomes das rotas, modelos e tabelas para inferir
   o domínio (e-commerce, LMS, task manager etc.).
5. **Arquivos fonte:** Liste e conte todos os arquivos `.py` ou `.js` relevantes
   (excluindo `node_modules`, `__pycache__`, `.venv`, `migrations`).
6. **Perfil arquitetural:** Classifique conforme `01-analise-projeto.md`:
   - `MONOLITO`
   - `PARCIALMENTE_ORGANIZADO`
   - `ESTRUTURADO_COM_PROBLEMAS`

Imprima o resumo **exatamente** neste formato:

```
================================
FASE 1: ANÁLISE DO PROJETO
================================
Linguagem:      [linguagem e versão]
Framework:      [framework e versão]
Banco de dados: [banco detectado]
Domínio:        [descrição do domínio]
Arquitetura:    [perfil] — [descrição de 1 linha]
Arquivos fonte: [N] arquivos analisados
================================
```

Guarde o perfil detectado internamente — ele será usado nas Fases 2 e 3.

---

## FASE 2 — AUDITORIA

Leia **todos os arquivos fonte** do projeto. Para cada arquivo, cruze o código contra
os 10 anti-patterns do catálogo em `02-catalogo-antipatterns.md`.

**Regras de auditoria:**
- Registre o arquivo e a linha exata de cada ocorrência
- Classifique a severidade conforme o catálogo
- Um mesmo arquivo pode ter múltiplos findings
- Não pule arquivos de configuração (`utils.js`, `settings.py`, `database.py`)

Ao finalizar a varredura, gere o relatório **exatamente** no formato definido
em `03-template-relatorio.md`.

**Salve o relatório em arquivo:**
- Determine o número do projeto: `code-smells-project` → 1, `ecommerce-api-legacy` → 2, `task-manager-api` → 3
- Crie a pasta `../reports/` se não existir (relativa à raiz do repositório, um nível acima do projeto)
- Salve o relatório completo em `../reports/audit-project-[N].md`

Após imprimir o relatório completo e salvá-lo, **pause a execução** e pergunte:

```
Prosseguir com a refatoração? (Fase 3 irá modificar arquivos do projeto) [s/n]:
```

Se a resposta for `n` ou qualquer coisa diferente de `s`/`sim`/`y`/`yes`,
encerre a skill sem modificar nenhum arquivo.

---

## FASE 3 — REFATORAÇÃO

Execute a refatoração conforme:
1. O perfil detectado na Fase 1
2. As guidelines de `04-guidelines-mvc.md`
3. O playbook de `05-playbook-refatoracao.md`

**Ações obrigatórias em qualquer perfil:**
- Extrair credenciais hardcoded para variáveis de ambiente
  (criar `.env.example` com as variáveis necessárias, **sem valores reais**)
- Corrigir SQL Injection com queries parametrizadas
- Remover endpoints perigosos (execução arbitrária de SQL ou código)
- Corrigir uso de APIs deprecated

**Por perfil:**

### MONOLITO
Crie a estrutura MVC completa conforme `04-guidelines-mvc.md`.
Redistribua o código existente nas camadas corretas.
Não delete funcionalidades — apenas reorganize e corrija.

### PARCIALMENTE_ORGANIZADO
Quebre o God Class/God File.
Crie camadas ausentes (controllers se não existirem).
Mova lógica de negócio para fora das rotas.

### ESTRUTURADO_COM_PROBLEMAS
Faça melhorias cirúrgicas:
- Adicione `controllers/` se a lógica de negócio está nas rotas
- Crie `config/settings.py` (ou equivalente) para credenciais via env vars
- Corrija problemas de segurança pontuais
- Resolva APIs deprecated
- Elimine validação duplicada
Não reorganize o que já está correto.

**Ao final da Fase 3**, imprima:

```
================================
FASE 3: REFATORAÇÃO CONCLUÍDA
================================
## Nova Estrutura do Projeto
[árvore de diretórios com os arquivos criados/modificados]

## Checklist de Validação Manual
Execute os comandos abaixo para validar que a aplicação continua funcionando:

### Python/Flask:
  1. Instalar dependências:
     pip install -r requirements.txt

  2. Iniciar a aplicação:
     python app.py
     (esperado: servidor iniciando sem erros na porta 5000)

  3. Testar endpoints principais:
     curl http://localhost:5000/health
     [liste os 3-5 endpoints mais importantes com curl e resposta esperada]

### Node.js/Express:
  1. Instalar dependências:
     npm install

  2. Iniciar a aplicação:
     node src/app.js
     (esperado: servidor iniciando sem erros na porta configurada)

  3. Testar endpoints principais:
     [liste os 3-5 endpoints com curl e resposta esperada]

## Resumo das Mudanças
- [N] arquivos criados
- [N] arquivos modificados
- [N] arquivos removidos
- Anti-patterns corrigidos: [lista resumida]
================================
```
