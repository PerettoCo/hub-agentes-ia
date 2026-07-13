# OpenAuth — Arquitetura de Autenticação + Proxy

## Contexto

OpenCode web UI precisa de **SSE** (Server-Sent Events) para streaming de respostas.
Proxy em Node.js (`http-proxy-middleware`) **não funciona** porque:
- Faz buffer da resposta (SSE precisa de streaming contínuo)
- `socket hang up` em conexões longas
- Não lida bem com chunked encoding

OpenCode direto (sem proxy) **funciona comprovadamente**.

---

## Alternativa 1: Subdomínios + BASIC AUTH (RECOMENDADO ✓)

Cada usuário acessa seu container OpenCode diretamente via subdomínio.

```
Browser → marcos.fvmarketing.com.br → Dokploy → opencode-marcos:4096
Browser → fhelipe.fvmarketing.com.br → Dokploy → opencode-fhelipe:4096
```

### Fluxo
1. Usuário acessa `marcos.fvmarketing.com.br`
2. Browser exibe popup BASIC AUTH do OpenCode
3. Usuário entra com `opencode` + senha
4. Web UI carrega e funciona (SSE nativo, sem proxy)

### Dokploy
| Domínio | Service | Porta Container | Porta Host |
|---|---|---|---|
| `marcos.fvmarketing.com.br` | `opencode-marcos` | 4096 | 4090 |
| `fhelipe.fvmarketing.com.br` | `opencode-fhelipe` | 4096 | 4091 |
| `csm2.fvmarketing.com.br` | `opencode-csm2` | 4096 | 4092 |
| `csm3.fvmarketing.com.br` | `opencode-csm3` | 4096 | 4093 |

### Prós
- ✅ **Funciona comprovadamente** (testado por Marcos)
- ✅ Zero proxy — SSE, WS, tudo direto
- ✅ Cada usuário independente
- ✅ Sem dependência entre containers
- ✅ Configuração mínima no Dokploy
- ✅ OpenCode gerencia autenticação

### Contras
- ❌ N subdomínios (1 por usuário)
- ❌ Popup BASIC AUTH (não página de login customizada)
- ❌ Senha genérica para todos (ou configurar individual)

---

## Alternativa 2: Nginx Gateway + auth_request + Supabase

Um único domínio com Nginx fazendo proxy reverso. Login via Supabase.

```
Browser → ia.fvmarketing.com.br → Dokploy → Nginx Gateway (opencode-gateway:80)
                                              ├─ /login → Auth Service (valida Supabase)
                                              ├─ /auth-check (nginx valida sessão)
                                              └─ /* → proxy_pass pro container certo
```

### Componentes

**Nginx Gateway** (`opencode-gateway`):
- Proxy reverso
- `auth_request` para validar sessão no Auth Service
- `proxy_buffering off` + `proxy_http_version 1.1` para SSE
- WebSocket nativo
- Injeta Basic Auth fixo nos containers OpenCode

**Auth Service** (`opencode-auth`):
- Login via Supabase (bcrypt + express-session)
- `/auth-check`: valida sessão, retorna 200 + `X-Opencode-Target` header
- `/api/login`, `/api/me`, `/api/logout`
- Rate limiting
- Recarrega users do Supabase a cada 5min

### Requisitos
- `resolver 127.0.0.11 valid=10s;` no nginx.conf (DNS Docker)
- Nginx usa `proxy_pass $opencode_target` (variável → precisa de resolver)
- Se o resolver não funcionar, usar IP fixo ou `proxy_pass` sem variável

### Estado atual
Código implementado em `infra-unify` commit `989378d`:
- `projetos/infraestrutura/opencode-gateway/nginx.conf` — proxy com auth_request
- `projetos/infraestrutura/opencode-gateway/Dockerfile` — nginx:alpine
- `projetos/infraestrutura/opencode-login/server.js` — auth service
- `docker-compose.agentes.yml` — serviços `opencode-gateway` + `opencode-auth`

**⚠️ NÃO TESTADO.** O 502 Bad Gateway pode ser por:
1. `resolver 127.0.0.11` não funcionar no Docker host
2. Nome do serviço `opencode-auth` não resolvível
3. Container `opencode-auth` não pronto quando nginx inicia

### Para testar (próximo passo)
1. Entrar no container nginx: `docker exec -it authopencode-...-gateway-1 sh`
2. Testar DNS: `nslookup opencode-auth`
3. Testar conexão: `wget -qO- http://opencode-auth:3000/auth-check`
4. Ver logs: `docker logs authopencode-...-gateway-1`

### Prós
- ✅ Domínio único
- ✅ Login via Supabase (BD existente)
- ✅ Página de login customizada (já pronta)

### Contras
- ❌ **NÃO TESTADO** — pode ter problemas de DNS/Docker
- ❌ Complexidade maior (nginx + auth service + OpenCode)
- ❌ Ponto único de falha (nginx)

---

## Alternativa 3: Login Page + Subdomínios (MEIO TERMO)

Página de login unificada em `login.fvmarketing.com.br` que redireciona para subdomínios.

```
1. Browser → login.fvmarketing.com.br → Auth Service (Supabase)
2. Login válido → redireciona para marcos.fvmarketing.com.br
3. Cada subdomínio → BASIC AUTH do OpenCode
```

### Implementação
- Auth Service (Node.js) em `login.fvmarketing.com.br`
- Serve login + redireciona baseado no username
- Cada subdomínio é um container OpenCode independente
- BASIC AUTH no OpenCode (pode ser a mesma senha pra todos ou individual)

### Prós
- ✅ Login unificado com Supabase
- ✅ Cada container roda OpenCode puro (sem proxy)
- ✅ SSE/WS funcionam nativamente
- ✅ Fácil de implementar (auth service já existe)
- ✅ Escalável (adicionar usuário = add container + linha no mapa)

### Contras
- ❌ Dois domínios (login + cada usuário)
- ❌ BASIC AUTH ainda aparece no subdomínio
- ❌ Precisa criar N subdomínios no Dokploy

---

## Resumo

| Critério | Alt 1: Subdomínios | Alt 2: Nginx Gateway | Alt 3: Login + Sub |
|---|---|---|---|
| Funciona hoje | ✅ SIM | ❌ Não testado | ✅ SIM |
| Login unificado | ❌ | ✅ | ✅ |
| Complexidade | Baixa | Alta | Média |
| Domínios | N+1 | 1 | N+1 |
| Proxy | ❌ | ✅ Nginx | ❌ |
| SSE/WS nativo | ✅ | ✅ (nginx) | ✅ |

**Recomendação:** Implementar **Alternativa 3** — Login page + subdomínios. É o melhor dos dois mundos: login unificado com Supabase + OpenCode puro sem proxy.
