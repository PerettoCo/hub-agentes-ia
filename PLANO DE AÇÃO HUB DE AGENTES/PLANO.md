# Plano de Ação — Hub de Agentes (OpenCode + LiteLLM + Login Portal)

## Contexto Geral

Infraestrutura multi-usuário com Login Portal (Express + Supabase), 4 instâncias OpenCode (marcos, fhelipe, csm2, csm3), LiteLLM como proxy de modelos (ZenCode free + paid) e Dokploy/Traefik como orquestrador.

## Bug Principal

Modelo não funciona dentro do OpenCode web. O LiteLLM responde internamente (docker exec funciona), mas o navegador recebe **Cloudflare 524/504 timeout** (>100s).

### Diagnóstico Final (10/07/2026)

- **Não é problema de conectividade** — LiteLLM responde em 15s internamente
- **Não é workspace grande** — workspace está vazio (sem clone do repo)
- **Não é URL externa vs interna** — ambas funcionam quando testadas via curl/node internamente
- **É o processamento do prompt no OpenCode web que demora >100s**, Cloudflare Free corta em 100s

### Causas identificadas

1. `entrypoint.sh` deleta `state.json` e `projects.json` a cada restart → força OpenCode a reindexar workspace do zero
2. Config dos usuários tinha `claude-sonnet-4` (Sofia AI Complex) que **não existe** no LiteLLM — modelo fantasma no seletor
3. `baseURL` nos configs apontava pra URL externa (`https://litellm.fvmarketing.com.br/v1`) quando deveria ser interna (`http://litellm:4000/v1`)
4. Cloudflare Free timeout máximo de 100s

### Correções JÁ APLICADAS (commit `infra-unify`)

- ✅ `entrypoint.sh`: comentado o `rm -f state.json` (persiste estado entre restarts)
- ✅ `opencode-config/*.json`: `baseURL` alterada para `http://litellm:4000/v1`
- ✅ `opencode-config/*.json`: removido `claude-sonnet-4` (modelo fantasma)
- ✅ `server.js`: WS proxy otimizado (não recria middleware a cada upgrade)
- ✅ `docker-compose.agentes.yml`: `OPENAI_API_KEY` + `OPENAI_BASE_URL` por serviço
- ✅ `docker-compose.agentes.yml`: `OPENCODE_DISABLE_MODELS_FETCH: "false"`
- ✅ Virtual keys criadas no LiteLLM (sk-marcos, sk-fhelipe, sk-csm2, sk-csm3)
- ✅ Modelos ZenCode adicionados no LiteLLM (nemotron, mimo, north-mini, big-pickle)

---

## Passo a Passo para Resolver (DO ZERO)

### Se for refazer do zero (deploy limpo):

1. **Dokploy** → Projeto `authopencode-authlogin-ippaei`:
   - Branch: `infra-unify`
   - Clique em **Deploy**
   - Verificar logs do deploy (sem erros)

2. **No servidor** (após deploy), verificar se subiu:
   ```bash
   docker ps | grep -E "opencode|litellm|traefik"
   ```
   Devem aparecer: 5 containers opencode-* + altos 2 litellm + 1 traefik

3. **Verificar virtual keys** (se o deploy não recriou o LiteLLM):
   ```bash
   docker exec litellm-litellm-k1cuim-litellm-1 python -c "
   import urllib.request, json
   req = urllib.request.Request('http://localhost:4000/key/info?key=sk-marcos-virtual-key',
       headers={'Authorization':'Bearer MASTER_KEY_AQUI'})
   print(json.loads(urllib.request.urlopen(req).read()))
   "
   ```

4. **Se LiteLLM foi recriado**, recriar virtual keys:
   ```bash
   docker exec litellm-litellm-k1cuim-litellm-1 python -c "
   import urllib.request, json
   AUTH = 'Bearer MASTER_KEY_AQUI'
   models = ['deepseek-v4-flash-free','nemotron-3-ultra-free','mimo-v2.5-free','north-mini-code-free','big-pickle','sofia-daily']
   for user, key in [('marcos','sk-marcos-virtual-key'),('fhelipe','sk-fhelipe-virtual-key'),('csm2','sk-csm2-virtual-key'),('csm3','sk-csm3-virtual-key')]:
       body = json.dumps({'key':key,'models':models,'metadata':{'user':user}}).encode()
       req = urllib.request.Request('http://localhost:4000/key/generate', data=body,
           headers={'Authorization':AUTH,'Content-Type':'application/json'})
       resp = json.loads(urllib.request.urlopen(req).read())
       print(f'{user}: models={resp.get(\"models\")}')
   "
   ```

5. **Testar comunicação interna**:
   ```bash
   docker exec authopencode-authlogin-ippaei-opencode-marcos-1 node -e "
   fetch('http://litellm:4000/v1/models', {headers:{Authorization:'Bearer sk-marcos-virtual-key'}})
   .then(r=>r.json()).then(d=>d.data?.forEach(m=>console.log(m.id)))
   "
   ```

6. **Acessar no navegador**: `https://ia.fvmarketing.com.br` → login marcos.luciano → selecionar "Sofia AI Daily ♺" → mandar "oi"

---

### Se o timeout persistir (>100s):

1. Aumentar timeout do Traefik no Dokploy:
   - Settings → Advanced → Traefik config → `readTimeout: 300s`
   - Ou via labels no docker-compose:
   ```yaml
   traefik.http.middlewares.oc-timeout.chain.middlewares: oc-readtimeout
   traefik.http.middlewares.oc-readtimeout.forwardauth.authResponseHeadersTimeout: 300
   ```

2. Aumentar timeout do login portal:
   ```javascript
   // Em server.js - timeout do proxy
   const opencodeProxy = createProxyMiddleware({
     timeout: 300000,  // 5min
     proxyTimeout: 300000,
     ...
   });
   ```

---

## Comandos Úteis Rápidos

### Diagnóstico
```bash
# Testar LiteLLM
docker exec authopencode-authlogin-ippaei-opencode-marcos-1 node -e "
fetch('http://litellm:4000/v1/chat/completions',{method:'POST',headers:{'Authorization':'Bearer sk-marcos-virtual-key','Content-Type':'application/json'},body:JSON.stringify({model:'sofia-daily',messages:[{role:'user',content:'oi'}]})}).then(r=>r.json()).then(d=>console.log(d.choices?.[0]?.message?.content))
"

# Ver logs do OpenCode
docker logs authopencode-authlogin-ippaei-opencode-marcos-1 --tail 20

# Ver envs do container
docker exec authopencode-authlogin-ippaei-opencode-marcos-1 node -e "
console.log('OPENAI_API_KEY:', process.env.OPENAI_API_KEY ? 'SET' : 'MISSING');
console.log('OPENAI_BASE_URL:', process.env.OPENAI_BASE_URL);
console.log('DISABLE_FETCH:', process.env.OPENCODE_DISABLE_MODELS_FETCH);
"
```

### Gestão LiteLLM
```bash
# Acessar UI
https://litellm.fvmarketing.com.br/login
# User: peretto / Senha: WmwZz%h!W^R^bpDx!xBt373@

# Listar chaves via API
MASTER_KEY="vcugrh1mpsih4d5wtuhaoi7suo5dxjmcpfpwz2dkcq9purl4xcnwfs0sh1pjr6ui"
docker exec litellm-litellm-k1cuim-litellm-1 python -c "
import urllib.request, json
req = urllib.request.Request('http://localhost:4000/key/list', headers={'Authorization':'Bearer $MASTER_KEY'})
data = json.loads(urllib.request.urlopen(req).read())
for k in data: print(k.get('key','?'), k.get('models',[]))
"
```

### Restart Limpo
```bash
cd /etc/dokploy/compose/authopencode-authlogin-ippaei/code
docker compose -f docker-compose.agentes.yml down
docker compose -f docker-compose.agentes.yml up -d
```

---

## Arquivos Relevantes

| Arquivo | Caminho | Função |
|---|---|---|
| docker-compose.agentes.yml | `/root/docker-compose.agentes.yml` | Orquestração principal |
| server.js | `projetos/infraestrutura/opencode-login/server.js` | Login portal + proxy |
| entrypoint.sh | `projetos/infraestrutura/opencode-login/scripts/entrypoint.sh` | Init container |
| marcos.json | `projetos/infraestrutura/opencode-login/opencode-config/marcos.json` | Config do usuário |
| Dockerfile.opencode | `projetos/infraestrutura/Dockerfile.opencode` | Imagem OpenCode |
| litellm.config.yaml | `projetos/infraestrutura/litellm.config.yaml` | Modelos LiteLLM |
| docker-compose.yml | `/etc/dokploy/compose/litellm-litellm-k1cuim/code/docker-compose.yml` | Stack LiteLLM |

## Credenciais

- **Dokploy**: admin / email do dokploy
- **Supabase**: URL + service_role key no .env
- **LiteLLM UI**: peretto / WmwZz%h!W^R^bpDx!xBt373@
- **LiteLLM Master Key**: vcugrh1mpsih4d5wtuhaoi7suo5dxjmcpfpwz2dkcq9purl4xcnwfs0sh1pjr6ui
- **OpenCode users**: marcos.luciano, fhelipe.aranha, csm2, csm3 (senha no Supabase)
- **Cloudflare**: email/senha padrão - DNS em `ia.fvmarketing.com.br` e `litellm.fvmarketing.com.br`

---

## Próximos Passos (Prioridade)

1. ✅ Commitar + push da branch `infra-unify`
2. ⬜ Deploy no Dokploy com branch `infra-unify`
3. ⬜ Verificar se virtual keys sobreviveram ao deploy
4. ⬜ **No Cloudflare:** confirmar que `ia.fvmarketing.com.br` está **orange** (proxy ativo)
5. ⬜ Testar no navegador com "Sofia AI Daily ♺"
6. ⬜ Se timeout persistir: ajustar timeout Traefik ou login portal
7. ⬜ Verificar UI LiteLLM em `https://litellm.fvmarketing.com.br`
