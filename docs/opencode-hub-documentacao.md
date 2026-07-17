# OpenCode Hub — Documentação de Auditoria

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
│  :80         │     │  :3000       │     │  :4090-4094  │
└──────────────┘     └──────────────┘     └──────────────┘
       │                                        │
       │                              ┌─────────┴──────────┐
       │                              │  LiteLLM Proxy     │
       │                              │  :4000/v1          │
       │                              └─────────┬──────────┘
       │                                        │
       │                              ┌─────────┴──────────┐
       │                              │  Provedores de IA  │
       │                              │  ZenCode · Claude  │
       │                              │  GPT · Gemini      │
       └──────────────────────────────┘
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

### 2.3 Instâncias

| Usuário | Subdomínio | Porta | Squad |
|---------|-----------|:-----:|-------|
| Marcos Luciano | marcos.fvmarketing.com.br | 4090 | tech |
| Fhelipe Aranha | fhelipe.fvmarketing.com.br | 4091 | csm |
| Lucas Nunes | lucasnunes.fvmarketing.com.br | 4095 | csm |
| Paolo Carmine | paolo.fvmarketing.com.br | 4094 | csm |

---

## 3. Fluxo de Acesso

### 3.1 Login

1. Usuário acessa https://ia.fvmarketing.com.br
2. Digita usuário e senha
3. Auth app valida contra Supabase + users.json (fallback local)
4. Cria cookie `connect.sid` com validade de 24h
5. Redireciona para o dashboard

### 3.2 Dashboard

- Exibe nome, squad e subdomínio do OpenCode
- Cards para acessar OpenCode Web e LiteLLM
- Botão "Sair" com confirmação em tela preta e vermelha

### 3.3 Acesso ao OpenCode

- Cada clique redireciona para o subdomínio específico do usuário
- Nginx verifica cookie `connect.sid` antes de liberar acesso
- OpenCode inicia sessão no workspace compartilhado

### 3.4 Sessão

- Sessão expira após 24h ou ao clicar em "Sair"
- É possível renovar acessando novamente ia.fvmarketing.com.br

---

## 4. Skills Instaladas

Skills são instruções reutilizáveis que o agente carrega sob demanda.

### 4.1 Skills de Infraestrutura

| Skill | Função |
|-------|--------|
| `geral-log-sessoes` | Salva/restaura sessões em `log/` |
| `geral-memoria-pgvector` | Memória persistente com pgvector + Supabase |
| `geral-leitura-contexto` | Leitura profunda do projeto |
| `geral-compactar` | Compressão de contexto e tokens |

### 4.2 Skills de Arquivos e RAG **(novas)**

| Skill | Função |
|-------|--------|
| `geral-leitor-arquivos` | Leitura de PDF, DOCX, XLSX, PPTX, imagens (OCR) |
| `geral-rag-documentos` | Ingestão e busca semântica em documentos |

### 4.3 Skills de Negócio

94 skills em `.agents/skills/` cobrindo SEO, CRO, tráfego, CSM, conteúdo, etc.

---

## 5. Leitura de Arquivos

### 5.1 Formatos Suportados

| Formato | Motor | Script |
|---------|-------|--------|
| PDF | pypdf / pdftotext | `scripts/file-reader.py` |
| DOCX | python-docx | `scripts/file-reader.py` |
| XLSX | openpyxl | `scripts/file-reader.py` |
| PPTX | python-pptx | `scripts/file-reader.py` |
| PNG / JPG / GIF / etc. | Tesseract OCR (pt+en) | `scripts/file-reader.py` |
| HTML / CSV | nativo | `scripts/file-reader.py` |
| Código (.py, .js, .ts, etc.) | leitura UTF-8 | `scripts/file-reader.py` |

### 5.2 Pipeline RAG

```
Arquivo → file-reader.py → extração de texto → chunk (2000 chars)
→ memory-cli.py store → embedding (text-embedding-3-small)
→ Supabase pgvector → busca semântica
```

---

## 6. Comandos Úteis

| Comando | Função |
|---------|--------|
| `/compactar` | Comprime contexto e tokens da sessão atual |
| `/session-save` | Salva sessão atual em `log/` |
| `/session-list` | Lista sessões salvas |
| `/contexto` | Carrega contexto do projeto/cliente |
| `python3 scripts/file-reader.py <arquivo>` | Lê qualquer arquivo |

---

## 7. Segurança

- **Senhas:** bcrypt com salt, base `P3R3TT0M4RK3T1NG` + 3 chars aleatórios
- **Sessão:** cookie httpOnly, sameSite=lax, domínio `.fvmarketing.com.br`
- **Rate limit:** 20 tentativas de login a cada 15 minutos
- **Gateway:** Nginx bloqueia acesso sem cookie de sessão
- **Modelos:** LiteLLM com chaves virtuais por usuário

---

## 8. Próximos Passos

- [ ] Renomear `csm.2` → `bruno.lindenmeyer`
- [ ] Renomear `csm.3` → `stefanny.santos` / `samuel.costa`
- [ ] Completar `csm1` com entrada em `users.json`
- [ ] Popular tabela `users` no Supabase
- [ ] Configurar alerta de sessão expirada

---

*Report gerado em 13/07/2026 · V4 Company*
