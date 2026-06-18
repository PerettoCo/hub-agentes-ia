---
name: geral-log-sessoes
description: >-
  Configura o sistema de log de sessões do OpenCode no repositório local. Cria a pasta log/, scripts de export/import, comandos /session-save, /session-list e /session-load, e registra instruções de auto-save no AGENTS.md. Use quando o usuário quiser salvar sessões, continuar de onde parou, carregar contexto de sessões anteriores, ou replicar a estrutura de logging em outro repositório. Também acione quando mencionar "session log", "log de sessões", "sessão anterior", "carregar contexto", "continuar sessão", "/session-save", "/session-load", "exportar sessão", ou "sessões persistentes".
area: geral
author: Marcos Luciano Rodrigues Vieira
version: 1.0.0
---

Configura o sistema completo de log de sessões do OpenCode no repositório atual.

## Visão geral

O sistema armazena todas as sessões do OpenCode como JSON na pasta `log/` no raiz do projeto, permitindo que qualquer sessão nova carregue contexto de sessões anteriores. Três comandos customizados (`/session-save`, `/session-list`, `/session-load`) gerenciam o ciclo de vida.

## Arquivos criados

```
log/                              # Sessões exportadas (gitignored)
  YYYY-MM-DD_HH-MM-SS_TITULO.json
scripts/
  session-save.sh                 # Exporta sessão atual via opencode CLI
  session-context.sh              # Extrai resumo legível de uma sessão salva
.opencode/commands/
  session-save.md                 # Comando /session-save
  session-list.md                 # Comando /session-list
  session-load.md                 # Comando /session-load
```

## Setup

### 1. Criar pastas e scripts

Crie as pastas:

```bash
mkdir -p log scripts .opencode/commands
```

### 2. Criar scripts

**scripts/session-save.sh** — exporta a sessão atual para `log/`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/log"
SESSION_ID="${1:-}"

if [ -z "$SESSION_ID" ]; then
  SESSION_ID=$(opencode session list --format json 2>/dev/null | python3 -c "
import sys, json
sessions = json.load(sys.stdin)
if sessions:
    print(sessions[0]['id'])
" 2>/dev/null || true)
fi

if [ -z "$SESSION_ID" ]; then
  echo "Nenhuma sessão encontrada."
  exit 1
fi

TITLE=$(opencode session list --format json 2>/dev/null | python3 -c "
import sys, json
sessions = json.load(sys.stdin)
for s in sessions:
    if s['id'] == '$SESSION_ID':
        title = s.get('title', 'untitled').replace('/', '_').replace(' ', '_')
        from datetime import datetime
        ts = s.get('created', 0) / 1000
        print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S') + '_' + title)
        break
" 2>/dev/null || echo "unknown")

FILENAME="$LOG_DIR/$TITLE.json"

opencode export "$SESSION_ID" --sanitize 2>/dev/null > "$FILENAME"

echo "Sessão salva: $FILENAME"
echo "ID: $SESSION_ID"
wc -c "$FILENAME" | awk '{print "Tamanho: " $1 " bytes"}'
```

**scripts/session-context.sh** — extrai resumo legível de uma sessão salva:

```bash
#!/usr/bin/env bash
set -euo pipefail

FILE="$1"

if [ ! -f "$FILE" ]; then
  echo "Arquivo não encontrado: $FILE"
  exit 1
fi

python3 -c "
import json, sys

with open('$FILE') as f:
    data = json.load(f)

info = data.get('info', {})
msgs = data.get('messages', [])

title = info.get('title', 'Untitled')
created = info.get('created', 0)
model = info.get('model', info.get('provider', 'unknown'))

from datetime import datetime
ts = datetime.utcfromtimestamp(created / 1000) if created > 0 else datetime.utcnow()

print(f'=== Sessão Anterior ===')
print(f'Título: {title}')
print(f'Data:   {ts.strftime(\"%Y-%m-%d %H:%M:%S\")}')
print(f'Modelo: {model}')
print(f'Msgs:   {len(msgs)}')
print()

user_msgs = []
assistant_msgs = []
for m in msgs:
    parts = m.get('parts', [])
    role = m.get('info', {}).get('role', '')
    if not role:
        for p in parts:
            if isinstance(p, dict) and p.get('type') == 'text':
                text = p.get('text', '')[:300]
                if m.get('info', {}).get('isUser', False):
                    user_msgs.append(text)
                else:
                    assistant_msgs.append(text)

if user_msgs:
    print('--- Principais perguntas/tarefas do usuário ---')
    for i, msg in enumerate(user_msgs[-5:], 1):
        print(f'{i}. {msg}')
        print()

if assistant_msgs:
    print('--- Principais respostas/entregas ---')
    for i, msg in enumerate(assistant_msgs[-3:], 1):
        print(f'{i}. {msg}')
        print()
" 2>/dev/null
```

Torne-os executáveis:
```bash
chmod +x scripts/session-save.sh scripts/session-context.sh
```

### 3. Criar comandos do OpenCode

**`.opencode/commands/session-save.md`:**

```markdown
---
description: Exporta a sessão atual para a pasta log/
---

Exporte a sessão atual do OpenCode para a pasta `log/` no diretório central do projeto usando:

!`bash <root>/scripts/session-save.sh`

Depois de salvar, liste o arquivo gerado e confirme que foi salvo corretamente.
```

**`.opencode/commands/session-list.md`:**

```markdown
---
description: Lista todas as sessões salvas na pasta log/
---

Liste as sessões salvas anteriormente na pasta `log/`:

!`ls -lh <root>/log/*.json 2>/dev/null | awk '{print $5, $6, $7, $8, $9}'`

Liste também as sessões ativas do OpenCode:

!`opencode session list --format table 2>/dev/null`

Apresente um resumo organizado das sessões disponíveis, com data, título e tamanho. Pergunte ao usuário se ele quer carregar alguma.
```

**`.opencode/commands/session-load.md`:**

```markdown
---
description: Carrega contexto de uma sessão anterior salva em log/
---

Primeiro, liste as sessões disponíveis em `log/`:

!`ls -1t <root>/log/*.json 2>/dev/null | head -20`

O usuário vai escolher uma sessão pelo nome do arquivo (ou número). Carregue o arquivo escolhido, extraia o resumo das mensagens e apresente o contexto relevante para a sessão atual.

Se o usuário pedir para carregar uma sessão específica que não está em `log/`, tente exportá-la primeiro com `/session-save` e depois carregue.
```

### 4. Adicionar ao .gitignore

Acrescente ao `.gitignore`:

```
# Sessões exportadas
/log/*.json
/log/*.jsonc
```

### 5. Registrar comandos no opencode config

Adicione ao `~/.config/opencode/opencode.jsonc` (global) ou `opencode.json` (local do projeto):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "command": {
    "session-save": {
      "description": "Exporta a sessão atual para a pasta log/",
      "template": "Exporte a sessão atual do OpenCode para a pasta log/ do projeto. Use o comando: opencode export $(opencode session list --format json | python3 -c \"import sys,json;s=json.load(sys.stdin);print(s[0]['id'] if s else '')\") --sanitize > log/session-$(date +%Y-%m-%d_%H-%M-%S).json"
    },
    "session-list": {
      "description": "Lista todas as sessões salvas na pasta log/",
      "template": "Liste as sessões salvas anteriormente na pasta log/ com ls -lh log/*.json e também as sessões ativas do OpenCode com opencode session list. Apresente um resumo organizado com data, título e tamanho."
    },
    "session-load": {
      "description": "Carrega contexto de uma sessão anterior salva em log/",
      "template": "Liste as sessões em log/, peça para o usuário escolher uma, leia o arquivo JSON e apresente o resumo do contexto (título, data, principais mensagens do usuário e entregas) para a sessão atual."
    }
  }
}
```

### 6. Adicionar instruções ao AGENTS.md / CLAUDE.md

Adicione esta seção no `AGENTS.md` e `CLAUDE.md` do projeto:

```markdown
## Sistema de Log de Sessões

Toda sessão deve ser salva obrigatoriamente na pasta `log/` no raiz do projeto.

### Funcionamento

- **Salvar sessão atual**: `/session-save` — exporta a sessão atual do OpenCode para `log/` como JSON
- **Listar sessões salvas**: `/session-list` — mostra todas as sessões em `log/` + sessões ativas no OpenCode
- **Carregar contexto**: `/session-load` — exibe as sessões disponíveis e carrega o contexto de uma anterior

### Regras obrigatórias

1. **Sempre salve a sessão ao final** de cada interação significativa. Execute `/session-save` automaticamente quando o usuário indicar que a sessão está terminando ou quando o trabalho principal foi concluído.
2. **Sempre verifique sessões anteriores** quando o usuário mencionar um tópico que parece ter sido trabalhado antes. Use `/session-list` para ver o que existe e `/session-load` para carregar contexto relevante.
3. **Sessões exportadas** ficam em `log/YYYY-MM-DD_HH-MM-SS_TITULO.json` e são ignoradas pelo git (`.gitignore`).
4. **Nunca commite** arquivos da pasta `log/`.
5. Quando o usuário disser que quer "continuar de onde parou", carregue a sessão mais recente de `log/` com `/session-load` e use o contexto para retomar o trabalho.
```

## Uso diário

- `/session-save` — salva a sessão atual em `log/`
- `/session-list` — lista todas as sessões salvas
- `/session-load` — escolhe uma sessão e carrega o contexto

O sistema é idempotente — pode ser executado várias vezes sem danos.

## Dependências

- `opencode` CLI instalado e configurado
- `bash` e `python3` disponíveis
