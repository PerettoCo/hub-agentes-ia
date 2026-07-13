# Timeline: Deploy do Login Portal + OpenCode Multi-User com Supabase + LiteLLM

**Data:** 07/07/2026
**Repositório:** PerettoCo/hub-agentes (branch `infra-login`)
**Infraestrutura:** Dokploy, Docker Compose, Cloudflare

---

## 1. Problema Inicial — Porta 3000 ocupada

**Erro:** O deploy falhava porque a porta 3000 já estava em uso pelo próprio Dokploy.

**Solução:** Mudamos a porta mapeada no compose para `3001:3000`.

**Arquivo:** `docker-compose.agentes.yml`

---

## 2. Autenticação: Migração de users.json para Supabase

**Motivação:** O login portal usava um arquivo JSON local (`users.json`) com senhas hasheadas. Isso não era escalável — qualquer alteração exigia rebuild.

**Solução:**
- Criamos tabela `public.users` no Supabase com colunas: `username`, `password_hash`, `name`, `email`, `squad`, `opencode_host`, `opencode_port`
- `server.js` agora faz fetch `GET /rest/v1/users?select=*` com `service_role` key na inicialização
- Mapeamento `snake_case` → `camelCase` no JS (`password_hash` → `passwordHash`, etc.)
- Removido `users.json` e bcrypt inline — agora é `SUPABASE_URL` + `SUPABASE_SERVICE_KEY`

**Seed de usuários:**

| Username | Senha |
|---|---|
| marcos.luciano | `P3R3TT0M4RK3T1NG` |
| fhelipe.aranha | `P3R3TT0M4RK3T1NG@Aranha` |
| csm2 | `P3R3TT0M4RK3T1NG@csm2` |
| csm3 | `P3R3TT0M4RK3T1NG@csm3` |

---

## 3. Session Cookie atrás do Cloudflare

**Erro:** O cookie de sessão tinha `Secure` mas o Express não confiava no proxy — `req.secure` era `false` atrás do Cloudflare, então o cookie não era setado.

**Solução:** `app.set('trust proxy', 1)` no Express.

---

## 4. Proxy para OpenCode — 504 Gateway Timeout

**Erro principal da sessão.** Várias tentativas:

### 4.1 Tentativa — Docker service names
Usamos `opencode-marcos:4096` como target. O login portal não conseguia resolver o nome do serviço porque estavam em redes Docker diferentes.

### 4.2 Tentativa — IP público + host ports
Usamos `2.25.148.214:4090`. Funcionou parcialmente (504 intermitente).

### 4.3 Tentativa — host.docker.internal
Adicionamos `extra_hosts: host.docker.internal:host-gateway` no compose e usamos `host.docker.internal:4090`. O login portal conseguia alcançar as portas expostas do host.

### 4.4 Descoberta — OpenCode crashava

**Logs mostravam:**
```
EACCES: permission denied, mkdir '/home/node/.local/share/opencode/repos'
```

**Causa:** O `Dockerfile.opencode` criava diretórios como `root` mas o container rodava como usuário `node`.

**Solução:** Adicionar `chown -R node:node` após o `mkdir` no Dockerfile.

### 4.5 Erro — Config inválida
```
Configuration is invalid at /home/node/.config/opencode/opencode.json
Unrecognized keys: modelProvider, customProviders
```

**Causa:** O schema do opencode mudou entre versões. O formato antigo usava `modelProvider` + `customProviders`. O novo usa `provider` e o modelo no formato `provider/model`.

**Solução:** Atualizar configs para usar `"provider": { "litellm": { ... } }` e `"model": "litellm/deepseek-v4-flash-free"`.

### 4.6 Erro — xdg-open crash

```
error: Executable not found in $PATH: "xdg-open"
```

**Causa:** `opencode web` tenta abrir o browser no final da inicialização. Em container slim (`node:20-bookworm-slim`), `xdg-open` não existe.

**Tentativa 1:** `--no-browser` — não existe como flag no CLI.

**Solução final:** Instalar `xdg-utils` no Dockerfile.

### 4.7 Proxy funcionou — mas pedia senha do OpenCode

**Causa:** OpenCode usa HTTP Basic Auth. O proxy do portal não enviava as credenciais.

**Solução:** Injetar `Authorization: Basic ...` via middleware Express antes do proxy.

---

## 5. Workspace vazio

**Problema:** O workspace `/workspace` no container estava vazio — sem skills, sem agentes, sem os arquivos do hub.

**Solução:** Entrypoint script que clona o repositório `PerettoCo/hub-agentes` em runtime usando `GITHUB_TOKEN`.

**Evolução:**
1. Criamos entrypoint com `set -e` — mas sem o token configurado, o clone falhava e o container morria (504 de novo)
2. Removemos `set -e` e tornamos o clone opcional
3. Usuário removeu o clone — workspace ficou vazio de novo
4. Restauramos com verificação de `.git` + pull automático

---

## 6. Governança de modelos via LiteLLM

**Problema:** Usuários podiam selecionar qualquer modelo/modo no OpenCode.

**Solução:** Adicionamos `enabled_providers: ["litellm"]` nos configs — só o LiteLLM aparece. A governança (quais modelos cada um pode usar) fica nas virtual keys do LiteLLM Proxy.

**Tokens no Dokploy:**
- `SESSION_SECRET`
- `PUBLIC_URL=https://ia.fvmarketing.com.br`
- `OPENCODE_SERVER_PASSWORD`
- `LITELLM_KEY_MARCOS`, `LITELLM_KEY_FHELIPE`, `LITELLM_KEY_CSM2`, `LITELLM_KEY_CSM3`
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `GITHUB_TOKEN`

---

## 7. Logout

**Problema:** Não havia botão de logout — usuário logado não conseguia sair.

**Solução:**
- Rota GET `/logout` que destrói sessão e redireciona
- Rota POST `/api/logout` (form + fetch)
- Página `/login` quando já logado mostra nome do usuário + botão "Sair"

---

## Arquivos modificados

```
docker-compose.agentes.yml
projetos/infraestrutura/Dockerfile.opencode
projetos/infraestrutura/opencode-login/server.js
projetos/infraestrutura/opencode-login/opencode-config/marcos.json
projetos/infraestrutura/opencode-login/opencode-config/fhelipe.json
projetos/infraestrutura/opencode-login/opencode-config/csm2.json
projetos/infraestrutura/opencode-login/opencode-config/csm3.json
projetos/infraestrutura/opencode-login/scripts/entrypoint.sh (new)
```

---

## Stack final

```
Cloudflare → ia.fvmarketing.com.br → Dokploy → Login Portal (porta 3001)
                                                      ↓
                                              OpenCode (portas 4090-4093)
                                                      ↓
                                              LiteLLM (litellm.fvmarketing.com.br)
                                                      ↓
                                              OpenAI / Anthropic / etc.
```
