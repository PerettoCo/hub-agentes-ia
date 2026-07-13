---
name: geral-leitura-contexto
aliases: [le-contexto, read-context]
tags: [skill, geral]
description: Leitor profundo de contexto do opencode com CLI real (`scripts/context-reader.py`). Escaneia diretorio, detecta tipo (CLIENTE/SQUAD/PROJETO/GENERICO), le CLAUDE.md, AGENTS.md, mission-control/, .env (so nomes), docs/, git log, skills instaladas e produz relatorio estruturado em markdown ou JSON. Suporta --brief (5 linhas), --watch (observa mudancas), --diff (compara com cache), e --store-memory (salva no Supabase via memory-cli). Use quando o usuario rodar /contexto, quiser que a IA "entenda onde esta", mencionar "le o contexto", "me da um resumo do projeto", "o que tem aqui", "como esta configurado esse cliente", ou sempre que o agente precisar se situar antes de comecar um trabalho. Acione automaticamente se for a primeira interacao numa pasta desconhecida.
---
# Leitura de Contexto do OpenCode

Leitor profundo de contexto com CLI real em `scripts/context-reader.py`. Diferente da skill `contexto` (que **gera** CLAUDE.md/AGENTS.md/mission-control), esta skill **le o que ja existe** e produz um relatorio estruturado.

## CLI — Uso

```bash
# Leitura completa do diretorio atual
python scripts/context-reader.py

# Leitura de uma pasta especifica
python scripts/context-reader.py /caminho/para/cliente

# Resumo compacto (5 linhas)
python scripts/context-reader.py --brief

# Output JSON para processamento
python scripts/context-reader.py --json

# Modo observador (fica monitorando mudancas)
python scripts/context-reader.py --watch

# Comparar com ultima leitura (cache)
python scripts/context-reader.py --diff

# Salvar contexto no Supabase (requer memory-cli.py instalado)
python scripts/context-reader.py --store-memory
```

## O Que e Lido

### Arquivos de Contexto
| Arquivo | O que extrai |
|---|---|
| `CLAUDE.md` | Titulo, secoes, ferramentas detectadas, comandos, refs a .env |
| `AGENTS.md` | Titulo, skills referenciadas |
| `mission-control/` | OKR, apostas vivas, combinados, personas, historico |
| `.env` | **Apenas nomes** das variaveis (NUNCA valores) |
| `package.json` / `pyproject.toml` | Nome, versao, tipo, scripts |
| `git log` | Ultimos 5 commits (hash, data, mensagem) |
| `.agents/skills/` + `.claude/skills/` | Lista de skills instaladas |
| `*.md, *.py, *.ts, *.json, *.yaml` | Index de arquivos importantes |

### Detection de Tipo

O leitor identifica automaticamente:
- **CLIENTE**: tem `calls/`, `docs/`, `campanhas/` ou `mission-control/`
- **SQUAD**: tem `clientes/` (subpasta) + entry point `{nome}.md`
- **PROJETO**: tem `docs/`, `dados/`, `referencias/` ou config de projeto
- **GENERICO**: qualquer outro diretorio

## Output Completo (Markdown)

```markdown
## Resumo de Contexto

**Tipo:** CLIENTE
**Nome:** ADPLAN
**Raiz:** `/home/marcos/Desktop/AI/v4perettoco-main/squads/matriz/clientes/adplan`
**Ultima atualizacao:** 2026-06-22
**Lido em:** 2026-07-07 12:00

### Proposito
Operacao de SDR IA + midia paga para captacao de leads no setor de planos de saude.

### Ferramentas Detectadas
- n8n-as-code (n8nac)
- Supabase
- Docker

### Comandos
- `npx n8nac push <workflow>`

### Skills Instaladas (12)
- `geral-memoria-pgvector`
- `geral-leitura-contexto`
- `n8n-architect`
- `contexto`
- ...

### Estado Atual (Mission Control)
- **okr:** [nao encontrado nos docs]
- **apostas:** 2 ativas
- **combinados_pendentes:** 1
- **ultimo_checkin:** 2026-06-18

### Git Log (recente)
- a1b2c3d 2026-06-22 Correcoes SDR ADPLAN
- e4f5g6h 2026-06-18 Push workflows

### Variaveis de Ambiente (5)
Definidas: OPENAI_API_KEY, SUPABASE_SERVICE_KEY, SUPABASE_URL, ...

### Notas
- Workflow SDR com JS timeout corrigido, pendente push
- Usar skill n8n-architect para gerenciar workflows

### Sugestoes
- Nao encontrei mission-control/ — considere rodar /contexto

### Arquivos (23)
- 📋 `CLAUDE.md` (85 linhas, 3.2KB)
- 🤖 `AGENTS.md` (120 linhas, 4.1KB)
- 🐍 `scripts/memory-cli.py` (430 linhas, 12KB)
- 📄 `docs/README.md` (20 linhas, 1.1KB)
- ...
```

## Output JSON

```bash
python scripts/context-reader.py --json | jq '.state'
{
  "okr": "[nao encontrado nos docs disponiveis]",
  "apostas": "2 ativas",
  "combinados_pendentes": 1,
  "ultimo_checkin": "2026-06-18"
}
```

## Modos Avancados

### `--watch`: Modo observador

Fica monitorando `CLAUDE.md`, `AGENTS.md`, `.env` e `mission-control/` a cada 5 segundos. Printa alerta quando algo muda:

```bash
python scripts/context-reader.py --watch
# [INFO] Watch mode ativo em: /caminho (intervalo=5s)
# [INFO] Mudanca detectada em CLAUDE.md
```

### `--diff`: Comparacao com cache

Compara o contexto atual com o ultimo lido (salvo em `~/.cache/context-reader-cache.json`):

```bash
python scripts/context-reader.py --diff
# Mudancas detectadas:
# - Proposito mudou
# - Ferramentas adicionadas: Docker
# - Skills: 10 → 12
# - Estado do Mission Control mudou
```

### `--store-memory`: Salva no Supabase

Apos ler o contexto, salva um resumo no Supabase via `geral-memoria-pgvector`:

```bash
# Salva o contexto atual como uma memoria do tipo 'context' no pgvector
python scripts/context-reader.py --store-memory
# [INFO] Contexto salvo na memoria pgvector.
```

## Integracao com Skills

| Skill | Como se complementam |
|---|---|
| `contexto` | Esta skill LE contexto existente. `contexto` GERA/ATUALIZA CLAUDE.md + mission-control. |
| `geral-memoria-pgvector` | Leitura da contexto estatico (arquivos) + pgvector para memoria dinamica (sessoes). Use `--store-memory` para conectar os dois. |
| `geral-log-sessoes` | Se houver `log/` no diretorio, o context-reader menciona quantas sessoes existem. |

## Regras

1. **NUNCA exiba valores de .env ou credenciais.** Mostre apenas nomes.
2. **Nao leia 50 arquivos se 3 resolvem.** Profundidade nos certos > quantidade.
3. **Priorize o que mudou.** Git log recente vai pro resumo.
4. **Nao duplique `contexto`.** Esta skill LE. Se precisar CRIAR/ATUALIZAR, recomende `/contexto`.
5. **Seja conciso.** Resumo ideal: 15-30 linhas. `--brief`: 5 linhas.
6. **Indique fontes.** Cada info mostra de onde veio.

## Dependencias

```bash
pip install python-dotenv pyyaml
```

## Referencia

- `scripts/context-reader.py` — CLI completa (400+ linhas)
