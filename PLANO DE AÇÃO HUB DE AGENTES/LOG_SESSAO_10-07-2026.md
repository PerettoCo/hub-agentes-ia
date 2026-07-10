# Log da Sessão — 10/07/2026

## Resumo

Sessão focada em diagnosticar e corrigir o bug "modelo não funciona no OpenCode web". Passamos por várias camadas e chegamos na causa raiz.

## Timeline

### 1. Diagnóstico Inicial
- Identificado que `docker-compose.agentes.yml` (raiz) estava desatualizado vs `projetos/infraestrutura/docker-compose.yml`
- **Correção:** Adicionado `OPENAI_API_KEY`, `OPENAI_BASE_URL` e `OPENCODE_DISABLE_MODELS_FETCH=false` nos 4 serviços
- Verificado que o arquivo do servidor estava em `/etc/dokploy/compose/authopencode-authlogin-ippaei/code/`

### 2. Virtual Keys
- LiteLLM usa `STORE_MODEL_IN_DB: "True"` — modelos gerenciados via DB/API, não via config.yaml
- Criadas 4 virtual keys (marcos, fhelipe, csm2, csm3) via API do LiteLLM
- Adicionados modelos ZenCode free faltantes (nemotron, mimo, north-mini, big-pickle)

### 3. Teste de Conectividade
- LiteLLM responde internamente: ✅ (15s)
- OpenCode → LiteLLM via internal URL: ✅
- Login portal proxy: ✅
- **Cloudflare 524:** ❌ (timeout >100s)

### 4. Grey Cloud Experiment
- Testamos `--resolve` bypassing Cloudflare → servidor respondeu em 23ms
- Grey cloud DNS propagou (servidor vê `2.25.148.214`)
- Mas grey cloud quebrou SSL do Traefik (cert não emitido pro IP direto)

### 5. Correções Finais (commit `infra-unify`)
- Entrypoint: parou de resetar state.json
- Configs: baseURL interna + removeu modelo fantasma
- Server.js: WS proxy otimizado

## Descobertas Importantes

1. LiteLLM versão nova NÃO tem UI embutida — acesso via `/` com login `peretto`
2. `STORE_MODEL_IN_DB: "True"` significa que config.yaml é ignorado — modelos via API/DB
3. `claude-sonnet-4` não existe no LiteLLM — era modelo fantasma no seletor
4. Workspace está vazio (GITHUB_TOKEN removido) — não é esse o gargalo
5. O `prompt_async` do OpenCode é o endpoint que dá timeout — provavelmente processamento interno lento

## Perguntas Pendentes

- Aumentar timeout Traefik resolve o 524? (provavelmente sim)
- state.json persistido resolve a lentidão na primeira requisição? (provável)
- UI do LiteLLM precisa de subdomínio separado?

## Links Mentais

- Ontem (09/07): configuramos LiteLLM com ZenCode, criamos virtual keys, ajustamos docker-compose
- Hoje (10/07): debugamos timeout, ajustamos configs, commit infra-unify
- Próxima sessão: deploy Dokploy + teste com Cloudflare orange
