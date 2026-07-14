# Hub de Agentes de IA — Documentação de Infraestrutura

**V4 Company · Peretto & Co**  
**Data:** 13/07/2026  
**Versão:** 1.0.0

---

## 1. Sobre o OpenCode

OpenCode é um agente de IA de código aberto para programação, disponível como interface web, desktop e terminal. Ele permite que times interajam com modelos de IA (Claude, GPT, Gemini, DeepSeek, etc.) em um ambiente controlado e privado, com sessões persistentes, habilidades customizáveis (skills) e suporte a múltiplos provedores.

**Site oficial:** https://opencode.ai  
**Repositório:** https://github.com/anomalyco/opencode

---

## 2. Arquitetura V4

### 2.1 Componentes

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Nginx       │────▶│  Auth App    │────▶│  OpenCode    │
│  Gateway     │     │  (Node.js)   │     │  Web Server  │
│  :80         │     │  :3000       │     │  :4090-4095  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                   │
                                          ┌────────┴──────────┐
                                          │  LiteLLM Proxy    │
                                          │  :4000/v1         │
                                          └────────┬──────────┘
                                                   │
                                          ┌────────┴──────────┐
                                          │  Provedores de IA │
                                          │  ZenCode · Claude │
                                          │  GPT · Gemini     │
                                          └───────────────────┘
```

### 2.2 Stack Tecnológica

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| **Gateway** | Nginx | Roteia subdomínios, verifica cookie de sessão |
| **Auth** | Node.js + Express | Login, sessão, dashboard |
| **Agente IA** | OpenCode Web | Interface do agente por usuário |
| **Proxy LLM** | LiteLLM | Roteamento para múltiplos modelos |
| **Modelo free** | deepseek-v4-flash-free (ZenCode) | Uso diário sem custo |
| **Modelos pagos** | Claude Sonnet 5, GPT 5.4, Gemini | Tarefas complexas |
| **Memória** | Supabase + pgvector | RAG e memória persistente |
| **Autenticação** | bcrypt + cookie session | Sessão com expiração em 24h |

---

## 3. Usuários e Instâncias

### 3.1 Tabela de Usuários

| Usuário | Nome | Subdomínio | Squad | Função | Status |
|---------|------|------------|-------|--------|--------|
| `marcos.luciano` | Marcos Luciano | marcos.fvmarketing.com.br | tech | — | ativo |
| `fhelipe.aranha` | Fhelipe Aranha | fhelipe.fvmarketing.com.br | csm | — | ativo |
| `lucas.nunes` | Lucas Nunes | lucasnunes.fvmarketing.com.br | csm | — | ativo |
| `paolo.carmine` | Paolo Carmine | paolo.fvmarketing.com.br | csm | — | ativo |
| `stefanny.santos` | Stefanny Santos | stefanny.fvmarketing.com.br | copy | Copy | ativo |
| `samuel.costa` | Samuel Costa | samuel.fvmarketing.com.br | design | Design | ativo |
| `bruno.lindenmeyer` | Bruno Lindenmeyer | bruno.fvmarketing.com.br | mídia | Gestor de Tráfego | setup |

### 3.2 Cofre Pessoal

Cada usuário tem seu próprio **subdomínio exclusivo** (`nome.fvmarketing.com.br`). Esse é o seu cofre pessoal — um container isolado com instância própria do OpenCode.

O agente mantém memória persistente (pgvector + Supabase). Enquanto você usa, ele acumula contexto. Se a sessão expirar, é só fazer login novamente e continuar de onde parou — a memória persiste no banco vetorial.

**Segurança:** o subdomínio só pode ser acessado depois de logar no portal `ia.fvmarketing.com.br`. Se alguém tentar acessar direto sem estar logado, o Nginx redireciona para a página de login.

---

## 4. Fluxo de Acesso

1. Usuário acessa https://ia.fvmarketing.com.br
2. Digita usuário e senha
3. Auth app valida contra Supabase + users.json (fallback local)
4. Cria cookie `connect.sid` com validade de 24h
5. Redireciona para o dashboard com cards de cada subdomínio

---

## 5. Comandos e Habilidades

Quatro camadas de interação — cada uma com seu nível de complexidade:

### @agentes (especialistas) — delegue tarefas diretas
Chame `@analista-dados` para métricas, `@seo-visibilidade` para auditoria SEO, `@copy-content` para copys, `@cro-otimizacao` para CRO, `@pesquisador` para pesquisa, `@midia-paga` para campanhas, `@criacao-design` para design.

**Quando usar:** tarefa clara que exige um especialista. Você dá o briefing, ele executa e volta com entrega.

### @orquestradores (times coordenados) — 8 times que coordenam especialistas
Cada orquestrador gerencia internamente vários especialistas. Você aciona um só e ele coordena o resto:

| Orquestrador | Especialistas que coordena |
|-------------|---------------------------|
| `@cmoorch` | Estratégia, growth, conteúdo, revenue, launch, dados, revisão |
| `@growth-team` | Dados, CRO, mídia paga, SEO, copy, receita |
| `@content-studio` | Estratégia, copy, design, SEO, pesquisa, revisão |
| `@account-orchestrator` | Handoff, check-in roleplay/review, evolução, vendas, pesquisa, flags, dados, revisão |
| `@csm-orquestrador` | 4 flags (churn, OKR, operação, ROI), account |
| `@launch-pad` | Estratégia, copy, mídia, SEO, design, diretórios, revisão |
| `@revenue-ops` | Receita, automação, vendas, dados, flags churn/ROI |
| `@executor-comite` | n8n, dados, 4 flags, revisão |

**Quando usar:** objetivo que precisa de várias frentes. O orquestrador delega, revisa e consolida pra você.

### /skills (comandos) — instruções pro agente atual
Use `/contexto` pra carregar contexto do projeto, `/compactar` pra economizar tokens, `/session-save` pra salvar conversa, `/session-list` pra ver sessões, `/csm-diagnostico` pra rodar diagnóstico CSM completo.

**Quando usar:** o agente que já está conversando com você precisa executar uma ação útil — sem criar um agente novo.

### /team-* (roteiros de especialistas)
Comandos como `/team-conteudo` e `/team-seo` são **modelos prontos** que instruem o agente atual a chamar uma sequência de @especialistas. Diferente dos @orquestradores (que são agentes independentes com contexto próprio, modelo e permissões), o `/team-*` é só um roteiro — o próprio agente que você já está usando é quem coordena a execução, chamando cada especialista um por vez.

**Disponíveis:**
- `/team-conteudo` → @estrategia-marketing + @copy-content + @seo-visibilidade + @revisor
- `/team-seo` → @seo-visibilidade + @estrategia-marketing + @analista-dados + @pesquisador

### /opensquad (times customizados)
Use `/opensquad create` para montar seu próprio combo de agentes com a composição que fizer sentido pro seu projeto.

**Como escolher:**
- Tarefa única e clara? → chame o **@especialista** direto
- Precisa de várias áreas coordenadas por um agente independente? → acione o **@orquestrador**
- Quer um roteiro rápido de especialistas sem criar agente novo? → use **/team-***
- Quer uma instrução pro agente atual? → use uma **/skill**
- Quer montar seu próprio combo? → use **/opensquad create**

---

## 6. Skills Instaladas

| Skill | Função |
|-------|--------|
| `geral-log-sessoes` | Salva/restaura sessões em `log/` |
| `geral-memoria-pgvector` | Memória persistente com pgvector + Supabase |
| `geral-leitura-contexto` | Leitura profunda do projeto |
| `geral-compactar` | Compressão de contexto e tokens |
| `geral-leitor-arquivos` | Leitura de PDF, DOCX, XLSX, PPTX, imagens (OCR) |
| `geral-rag-documentos` | Ingestão e busca semântica em documentos |

94 skills no total em `.agents/skills/` cobrindo SEO, CRO, tráfego, CSM, conteúdo, etc.

---

## 7. Leitura de Arquivos

| Formato | Motor |
|---------|-------|
| PDF | pypdf / pdftotext |
| DOCX | python-docx |
| XLSX | openpyxl |
| PPTX | python-pptx |
| PNG / JPG / GIF / etc. | Tesseract OCR (pt+en) |
| HTML / CSV | nativo |
| Código (.py, .js, .ts, etc.) | leitura UTF-8 |

### Pipeline RAG

```
Arquivo → file-reader.py → extração de texto → chunk (2000 chars)
→ memory-cli.py store → embedding (text-embedding-3-small)
→ Supabase pgvector → busca semântica
```

---

## 8. Segurança

- **Senhas:** bcrypt com salt, base `P3R3TT0M4RK3T1NG` + 3 chars aleatórios
- **Sessão:** cookie httpOnly, sameSite=lax, domínio `.fvmarketing.com.br`
- **Rate limit:** 20 tentativas de login a cada 15 minutos
- **Gateway:** Nginx bloqueia acesso sem cookie de sessão
- **Modelos:** LiteLLM com chaves virtuais por usuário

---

## 9. Próximos Passos

### Até quarta 16/07

- [ ] **Consultar base atual e modelar schema** — Ler estrutura existente no Supabase, planejar tabelas de calls, clients, decisions — query direta, sem /contexto
- [ ] **Instanciar novos usuários** — Stephanie Santos (copy) · Samuel Costa (design) · Bruno Lindenmeyer (gestor de tráfego) — Authelia + login portal + opencode config
- [ ] **Criar tabelas de calls no Supabase** — `call_history` + `call_transcripts` (pgvector) + pipeline de ingestão do NotebookLM
- [ ] **Configurar Google Drive MCP** — Server MCP pra agentes acessarem arquivos dos clientes diretamente

### Próxima semana

- [ ] **Pipeline Mission Control ↔ Banco** — Sincronizar apostas/combinados do .md com tabelas SQL
- [ ] **Visão consolidada no PerettoOps** — Painel unificado conectando pastas (Drive MCP), contextos (mission control no banco) e dados (calls, decisões)
- [ ] **Onboarding dos novos usuários** — Enviar acessos para Stephanie (copy), Samuel (design) e Bruno (mídia) com texto de boas-vindas

---

*Documento gerado em 13/07/2026 · V4 Company*
