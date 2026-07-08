# Módulo Ekyte — V4 Automations

Módulo **opcional e modular**. Se você não usa Ekyte, ignore esta pasta.
Se usa, configure as variáveis e tudo funciona automaticamente.

---

## Setup (10 minutos)

### 1. Obter a API Key do Ekyte

Ekyte → **Minha Empresa** → aba **BI** → copiar a chave de acesso

> Disponível apenas no plano **Performance**.

### 2. Adicionar ao .env

```
EKYTE_API_KEY=sua-chave-aqui
```

### 3. Descobrir os IDs dos seus workspaces e squads

```bash
python scripts/ekyte/connector.py
```

Isso lista todos os workspaces e squads da sua conta.
Copie os IDs e preencha em `config/clientes.json`.

### 4. Preencher clientes.json

Para cada cliente, adicione:

```json
{
  "nome": "Nome do Cliente",
  "ekyte_workspace_id": 101,
  "ekyte_squad_id": 10,
  "ekyte_sprint_project_id": 233113,
  "ekyte_executor_id_am": "uuid-do-am",
  "ekyte_executor_id_gt": "uuid-do-gt",
  "ekyte_executor_id_copy": "uuid-do-copy"
}
```

Para obter os UUIDs dos usuários:

```bash
python -c "
from scripts.ekyte.connector import EkyteClient
e = EkyteClient()
for u in e.get_usuarios():
    print(u.get('id'), u.get('name'))
"
```

### 5. Configurar IDs dos quadros da Base de Conhecimento

Abra `scripts/ekyte/base_conhecimento.py` e preencha `QUADROS_EKYTE`:

```python
QUADROS_EKYTE = {
    "atas_comite": 123,
    "atas_growth": 124,
    "atas_wb": 125,
    "analises": 126,
    "okrs": 127,
}
```

Para ver os IDs dos quadros existentes:

```bash
python scripts/ekyte/base_conhecimento.py --acao listar
```

---

## Scripts disponíveis

### connector.py — Conector base
```bash
# Testa a conexão e lista workspaces
python scripts/ekyte/connector.py
```

### checklist_ekyte.py — Conformidade com dados reais
```bash
# Verifica conformidade de todos os clientes com Ekyte
python scripts/ekyte/checklist_ekyte.py
```

Integrado automaticamente no `coordenador/checklist.py` quando `EKYTE_API_KEY` está configurada.

### sprints.py — Gestão de sprints
```bash
# Resumo da sprint atual de todos os clientes
python scripts/ekyte/sprints.py

# Resumo de um cliente específico
python scripts/ekyte/sprints.py --cliente "Nome do Cliente"

# Cria próxima sprint (ongoing)
python scripts/ekyte/sprints.py --cliente "Nome do Cliente" --acao criar --tipo ongoing

# Cria sprint de onboarding
python scripts/ekyte/sprints.py --cliente "Nome do Cliente" --acao criar --tipo onboarding
```

### fca.py — Criação de FCAs
```bash
# Cria FCA manualmente
python scripts/ekyte/fca.py \
  --cliente "Nome do Cliente" \
  --fato "CAC subiu 40% na última semana" \
  --causa "Fadiga de criativo + CPM elevado" \
  --acao "GT pausa criativos com CTR < 1% até quinta"

# FCA crítica
python scripts/ekyte/fca.py \
  --cliente "Nome do Cliente" \
  --fato "..." --causa "..." --acao "..." \
  --critico
```

FCAs também são criadas **automaticamente** quando `analise_performance.py` detecta desvios críticos.

### base_conhecimento.py — Base de Conhecimento
```bash
# Lista quadros disponíveis
python scripts/ekyte/base_conhecimento.py --acao listar

# Salva ata do Comitê (via stdin)
echo "Decisão: priorizar cliente A. FCA aberta: CAC..." | \
  python scripts/ekyte/base_conhecimento.py --acao salvar-ata --ritual comite

# Salva ata do Growth
python scripts/ekyte/base_conhecimento.py --acao salvar-ata --ritual growth --cliente "Nome"

# Salva ata do Working Backwards
python scripts/ekyte/base_conhecimento.py --acao salvar-ata --ritual wb
```

---

## O que é automatizado vs manual

| Ação | Modo | Quando |
|---|---|---|
| Checklist de conformidade enriquecido com Ekyte | Automático | Sexta 16h (cron) |
| Detecção de tarefas atrasadas | Automático | Parte do checklist |
| Verificação de timesheet | Automático | Parte do checklist |
| Criação de FCA quando anomalia crítica de KPI | Automático | Quando GT detecta desvio |
| Resumo de sprints no briefing do Comitê | Automático | Domingo 20h |
| Criação da próxima sprint | Manual (confirmação humana) | Após fim de sprint |
| Salvar ata de ritual na Base de Conhecimento | Manual | Após cada ritual |

---

## Nota sobre escrita (POST)

A API documentada pelo Ekyte é focada em **leitura** (plano BI).
Os métodos de **criação** (tarefas, sprints, FCAs, notas) usam endpoints POST
que podem requerer permissão adicional.

Se ao executar um método de criação você receber erro 403 ou 404:

1. Entre em contato: **atendimento@ekyte.com**
2. Pergunte: *"Os endpoints POST /tasks, /projects, /tickets e /boards/notes estão disponíveis via API?"*
3. Os métodos GET funcionam sem restrição — toda a leitura e conformidade funciona desde já.

---

## Como usar em outra unidade

1. Copie a pasta `scripts/ekyte/` para o projeto da outra unidade
2. Configure `EKYTE_API_KEY` no `.env`
3. Preencha os `ekyte_workspace_id` em `clientes.json`
4. Pronto — o módulo funciona de forma independente

Não há dependência de nenhum outro módulo da V4 Automations (exceto `connectors.py` para o Claude API).
