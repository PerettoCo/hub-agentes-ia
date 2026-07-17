# Hub de Agentes de IA — Documentação de Infraestrutura

**V4 Company · Peretto & Co**  
**Data:** 13/07/2026  
**Versão:** 1.0.0

---

## 1. Sobre o OpenCode

OpenCode é um agente de IA de código aberto para programação, disponível como interface web, desktop e terminal. Ele permite que times interajam com modelos de IA em um ambiente controlado e privado, com sessões persistentes, habilidades customizáveis (skills) e suporte a múltiplos provedores.

**Site oficial:** https://opencode.ai  
**Repositório:** https://github.com/anomalyco/opencode

---

## 2. Arquitetura V4

### 2.1 Componentes

```
┌──────────────────────────────────────────────────────────────┐
│  👤 Usuário                                                    │
│  Acessa https://ia.fvmarketing.com.br pelo navegador          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  ① Portal de Login  (ia.fvmarketing.com.br)                  │
│  ──────────────────────────────────────────────              │
│  Digita usuário + senha                                      │
│  Auth App valida contra Supabase (bcrypt)                    │
│  Se OK → cria cookie connect.sid (24h)                       │
│  Redireciona pro subdomínio do usuário                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │  redireciona com cookie
                           ▼
┌──────────────────────────────────────────────────────────────┐
│  🌐 Navegador  https://SEU_NOME.fvmarketing.com.br           │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │  porta 80
                           ▼
┌──────────────────────────────────────────┐
│  ② Nginx Gateway                          │
│  ──────────────────────────────────────  │
│  Verifica cookie connect.sid no request   │
│  Se inválido → redireciona pra login      │
│  Se válido → proxy reverso pro OpenCode   │
└──────────────┬─────────────────────────────┘
               │
               │  proxy reverso
               ▼
┌──────────────────────────────────────┐
│  ③ OpenCode Web                      │
│  Instância por usuário              │
│  ────────────────────────────────   │
│  :4090 marcos · :4091 fhelipe       │
│  :4092 bruno  · :4093 stephanie     │
│  :4094 paolo  · :4095 samuel        │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┬────────────────┐
    │                     │                │
    ▼                     ▼                ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────────────┐
│ ④ LiteLLM   │  │ ⑤ Supabase       │  │ ⑥ MCP Servers            │
│ Proxy:4000  │  │ pgvector          │  │ ────────────────         │
│ Chaves virt.│  │ ────────────      │  │ Google Drive             │
└──────┬───────┘  │ usuários · mem   │  │ Ekyte (API)              │
       │          │ calls · decisões │  └──────────────────────────┘
       ▼          │ clientes         │
┌────────────────┐└──────────────────┘
│ ⑦ Modelos IA  │
│ (alguns free) │
│ + APIs próprias│
└────────────────┘
```

### 2.2 Stack Tecnológica

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| **Gateway** | Nginx | Roteia subdomínios, verifica cookie de sessão |
| **Auth** | Node.js + Express | Login, sessão, dashboard |
| **Agente IA** | OpenCode Web | Interface do agente por usuário |
| **Proxy LLM** | LiteLLM | Roteamento para múltiplos modelos |
| **Modelos disponíveis** | Alguns com marcação Free | Para uso e teste. Futuramente mais modelos podem ser conectados e cada usuário pode usar sua própria API pessoal (Claude, Gemini, GPT, etc.) |
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

## 5. Skills de Eficiência da Operacional Plataforma

Quatro camadas de interação. Cada uma foi projetada com uma metodologia específica por trás — não é só um prompt genérico.

---

### @agentes (especialistas) — delegue tarefas diretas

Cada especialista foi treinado com **frameworks, dados reais e skills específicas** para a função. Você dá o briefing, ele executa e volta com entrega.

| Agente | O que faz | Metodologia / Construção | Por que confiar |
|--------|-----------|--------------------------|-----------------|
| `@analista-dados` | Métricas, OKRs, performance, insights estruturados | Treinado com framework OKR V4 + queries diretas ao Supabase + pipeline de dados reais | Não chuta — puxa dados do banco e cruza com metas documentadas em mission-control |
| `@seo-visibilidade` | Auditoria SEO completa + AI Visibility (GEO/AEO) | Segue o framework FLOW (Find → Leverage → Optimize → Win) + APIs Google (Search Console, PageSpeed, CrUX) + DataForSEO + skills seo-* | Usa dados reais do Google, não achismo. Skills cobrem técnico, conteúdo, backlinks, GEO, schema |
| `@copy-content` | Landing pages, emails, anúncios, redes sociais, lead magnets | Treinado com metodologia de copy V4 (direct response + SEO + persuasão) + pipeline de conteúdo editorial | Escreve baseado em briefing estruturado, pesquisa de concorrência e psicologia de marketing |
| `@cro-otimizacao` | Otimização de conversão em páginas, signups, formulários, onboarding | Metodologia de experimentação baseada em hipóteses (ICE score) + analytics tracking + skills de CRO | Cada recomendação parte de dados de tracking ou padrões validados, não de opinião |
| `@pesquisador` | Pesquisa profunda de mercado, concorrentes, consumidores | Multi-fontes: reviews (G2, Trustpilot), Reddit, redes, consumidores — tudo sintetizado em insights acionáveis | Não faz pesquisa superficial — minera dados públicos reais e cruza com briefing do cliente |
| `@midia-paga` | Estratégia de mídia paga (Meta, Google, LinkedIn, TikTok) | Arquitetura de contas + análise preditiva + teoria das restrições + PNL | Usa dados reais de campanha (V4mos API) e skills de mídia para decisões baseadas em performance |
| `@criacao-design` | Interfaces, imagens, vídeos, apresentações | Treinado no padrão visual V4 (vermelho + dourado + Ubuntu) + geral-frontend-design + skills de imagem/vídeo | Segue identidade visual consistente — não é design aleatório, é design V4 |

**Como escolher:** tarefa única e clara → chame o @especialista direto.

---

### @orquestradores (times coordenados) — 8 times que coordenam especialistas

Diferente dos especialistas (que executam), os orquestradores são **agentes independentes com contexto próprio, modelo e permissões**. Eles internamente delegam tarefas, revisam resultados e consolidam a entrega final pra você.

| Orquestrador | O que coordena | Metodologia / Construção | Por que confiar |
|-------------|----------------|--------------------------|-----------------|
| `@cmoorch` | Estratégia, growth, conteúdo, revenue, launch, dados, revisão | Framework CMO V4 — orquestra marketing completo integrando todos os times | Não é um agente de marketing genérico — entende a operação V4 como um todo e coordena especialistas reais |
| `@growth-team` | Dados, CRO, mídia paga, SEO, copy, receita | Pipeline de growth integrado: experimentos contínuos com hipóteses, design, execução e aprendizado | Conecta CRO + mídia + SEO + conteúdo em ciclo fechado de aprendizado |
| `@content-studio` | Estratégia, copy, design, SEO, pesquisa, revisão | Pipeline editorial completo: pesquisa → estratégia → produção → revisão → publicação | Cada peça de conteúdo passa por múltiplos especialistas antes de sair — não é conteúdo feito por um agente só |
| `@account-orchestrator` | Handoff, check-in roleplay/review, evolução, vendas, pesquisa, flags, dados, revisão | Ciclo completo de saúde do cliente: check-in → mission control → flags → expansão | Integra o ROPRE V4, roleplay realista com personas reais e histórico de check-ins |
| `@csm-orquestrador` | 4 flags (churn, OKR, operação, ROI) + account | Sistema de diagnóstico por flags com gatilhos objetivos: NPS+CSAT, KRs <60%, sprints atrasadas, ROAS abaixo da meta | Cada flag tem critério numérico claro — não é achismo, é alarme objetivo |
| `@launch-pad` | Estratégia, copy, mídia, SEO, design, diretórios | Framework de lançamento estruturado: pré-lançamento → lançamento → pós-lançamento com cobertura multicanal | Cobre todas as frentes de um launch — não só o anúncio, mas SEO, diretórios e conteúdo |
| `@revenue-ops` | Receita, automação, vendas, dados, flags churn/ROI | Engrenagem de receita integrando pricing, churn, referral e automação de operações | Conecta prevenção de churn + programas de referral + operações de receita em um fluxo só |
| `@executor-comite` | n8n, dados, 4 flags, revisão | Briefing automático do Comitê de P&EG com dados reais de OKRs, sprints e FCAs | Gera pauta de comitê com dados vivos, não com relatório manual desatualizado |

**Como escolher:** objetivo que precisa de várias frentes → acione o @orquestrador. Ele delega, revisa e consolida pra você.

---

### /skills (comandos) — instruções pro agente atual

Diferente dos @agentes (que são independentes), os comandos `/skill` são instruções que o **agente que já está conversando com você** executa — sem criar um agente novo.

| Comando | O que faz | Metodologia | Por que confiar |
|---------|-----------|-------------|-----------------|
| `/contexto` | Carrega todo o contexto do projeto/cliente/squad | Escaneia diretórios, lê CLAUDE.md, AGENTS.md, mission-control, docs, git log | Não pula etapa — o agente precisa saber onde está antes de agir |
| `/compactar` | Comprime contexto e tokens quando a conversa está longa | Analisa uso atual, identifica desperdícios, resume histórico | Economiza token budget sem perder informações críticas |
| `/session-save` | Salva a sessão atual em `log/` com metadados | Exporta objetivo, descobertas, próximo passo e comandos úteis em JSON | Nenhum trabalho se perde — a sessão pode ser retomada depois com `RETOMAR` |
| `/session-list` | Lista todas as sessões salvas | Lê diretório `log/` e mostra com data, título e resumo | Visualização rápida do histórico de trabalho |
| `/csm-diagnostico` | Roda diagnóstico CSM completo | Executa as 4 flags (churn, OKR, operação, ROI) em sequência e consolida | Diagnóstico completo em um comando só — sem chamar flag por flag |

---

### /team-* (roteiros de especialistas)

Comandos como `/team-conteudo` e `/team-seo` são **modelos prontos** que instruem o agente atual a chamar uma sequência de @especialistas. Diferente dos @orquestradores (que são agentes independentes), o `/team-*` é um roteiro — o próprio agente que você já está usando coordena a execução.

**Disponíveis:**
- `/team-conteudo` → @estrategia-marketing + @copy-content + @seo-visibilidade + @revisor
- `/team-seo` → @seo-visibilidade + @estrategia-marketing + @analista-dados + @pesquisador

### /opensquad (times customizados)

Use `/opensquad create` para montar seu próprio combo de agentes.

---

**Resumo — como escolher:**
| Situação | Use |
|----------|-----|
| Tarefa única e clara | **@especialista** direto |
| Várias frentes coordenadas por um agente independente | **@orquestrador** |
| Roteiro rápido sem criar agente novo | **/team-*** |
| Instrução pro agente atual | **/skill** |
| Combo personalizado | **/opensquad create** |

---

## 6. Skills Operacionais

Cada skill foi criada para resolver um problema real do dia a dia. O racional por trás de cada uma:

### `geral-log-sessoes`
**Problema:** Sessões do OpenCode expiram e o contexto se perde.
**Solução:** Salva e restaura sessões em `log/` com objetivo, descobertas, próximo passo e comandos úteis — nenhum trabalho se perde.

### `geral-memoria-pgvector`
**Problema:** LLMs não retêm informação entre sessões.
**Solução:** Memória persistente com embeddings no pgvector — busca semântica por conversas, decisões e insights passados. O agente se lembra do que foi discutido antes.

### `geral-leitura-contexto`
**Problema:** O agente precisa entender rápido onde está (qual cliente, projeto, squad).
**Solução:** Escaneia diretórios, lê CLAUDE.md, AGENTS.md, mission-control, git log e produz relatório estruturado — o agente nunca trabalha sem contexto.

### `geral-compactar`
**Problema:** Conversas longas consomem tokens preciosos.
**Solução:** Analisa uso de contexto, comprime prompts longos, resume histórico e elimina desperdício — o agente trabalha mais com menos tokens.

### `geral-leitor-arquivos`
**Problema:** Clientes enviam arquivos nos mais variados formatos (PDF, DOCX, imagens).
**Solução:** Extrator unificado — PDF via pypdf, DOCX via python-docx, imagens via OCR Tesseract. Tudo vira markdown limpo para o agente processar.

### `geral-rag-documentos`
**Problema:** Ler arquivo por arquivo é ineficiente.
**Solução:** Pipeline RAG — chunk, embedding, busca semântica no pgvector. Pergunte em linguagem natural e encontre o documento relevante em segundos.

+ 94 skills no total em `.agents/skills/` cobrindo SEO, CRO, tráfego, CSM, conteúdo, design, growth, receita e automação.

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

## 9. Acesse o Guia Completo

👉 **[perettoco.github.io/hub-agentes/](https://perettoco.github.io/hub-agentes/)** — Hub de Agentes de IA V4

👉 **[perettoco.github.io/hub-agentes/skills/](https://perettoco.github.io/hub-agentes/skills/)** — Catálogo de Skills e Agentes

---

*Documento gerado em 13/07/2026 · V4 Company*
