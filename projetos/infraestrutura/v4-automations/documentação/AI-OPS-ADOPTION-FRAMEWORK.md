# AI Ops — Framework de Adoção e Operação

**V4 Company — Unidade de Inteligência Artificial Aplicada**

> Documento oficial de arquitetura, governança e operação de AI Ops.
> Alinhado ao Distrito AI Adoption Framework 2026.
> Versão: 1.0.0 — MVP | Maio 2026

---

## Índice

1. [Sumário Executivo](#1-sumário-executivo)
2. [Visão Estratégica](#2-visão-estratégica)
3. [Framework de Adoção (Distrito)](#3-framework-de-adoção)
4. [Arquitetura Técnica](#4-arquitetura-técnica)
5. [Governança de IA](#5-governança-de-ia)
6. [Escalabilidade](#6-escalabilidade)
7. [Esteira de Desenvolvimento](#7-esteira-de-desenvolvimento)
8. [Métricas e KPIs](#8-métricas-e-kpis)
9. [Riscos e Mitigações](#9-riscos-e-mitigações)
10. [Roadmap MVP → Produção](#10-roadmap)
11. [Próximos Passos](#11-próximos-passos)

---

## 1. Sumário Executivo

### Propósito

Este documento define o framework de AI Ops da V4 Company — um conjunto integrado de agentes automatizados, pipelines de dados, governança e processos que operam em escala para transformar a entrega de marketing digital através de inteligência artificial.

### O que é AI Ops na V4

AI Ops (Artificial Intelligence for Operations) é a camada de inteligência que automatiza, aumenta e orquestra as operações de marketing digital. Não substitui pessoas — amplifica a capacidade de cada função:

| Função | Antes | Com AI Ops |
|---|---|---|
| Account / CSM | Check-ins manuais, relatórios sob demanda | Relatórios automáticos, flags de risco, evolução contínua |
| GT (Tráfego) | Análise semanal manual, decisão reativa | Análise preditiva, alertas de anomalia, pace automatizado |
| Copy | Briefing manual, produção sequencial | Pipeline de conteúdo, calendário automatizado, revisão IA |
| Coordenação | Briefings manuais para comitê | Briefing automático com dados reais, checklist de conformidade |

### Escopo MVP (Maio 2026)

- Pipeline de relatórios de tráfego multicanal (Google Ads, Meta Ads, Bing Ads, GA4)
- Envio automático por e-mail com template V4
- Modo sample para demonstração sem APIs
- Setup em comando único
- Governança básica: credenciais segregadas, logs de execução

### Próximas entregas

- Análise preditiva com flags de risco (ROAS, churn, OKR, operação)
- Pipeline de conteúdo editorial completo
- Briefing automático do comitê
- Escalabilidade multi-squad

---

## 2. Visão Estratégica

### 2.1. Northern Star

> "Todo cliente V4 tem um agente de IA dedicado que monitora, analisa e recomenda 24/7 — o time humano executa e decide."

### 2.2. Princípios

1. **Humano no loop** — IA recomenda, humano decide. Nunca automação cega.
2. **Dados reais, decisões reais** — Todo relatório parte de dados de API, nunca de achismo.
3. **Escala desde o dia 1** — Arquitetura preparada para N clientes, N squads, N plataformas.
4. **Governança como requisito** — Segurança, custo e qualidade não são pós-implementação.
5. **Valor visível** — Toda automação precisa responder: quanto tempo economizou? Qual decisão melhorou?

### 2.3. Matriz de Soluções (Distrito)

| Tipo de IA | Aplicação V4 | Status |
|---|---|---|
| **Process Automation** | Coleta de dados de APIs, geração de relatórios, crons | ✅ Operacional |
| **Cognitive Assistance** | Claude API para análise qualitativa, detecção de anomalias | ✅ MVP |
| **Predictive Intelligence** | Flags de risco (ROAS, churn, OKR, operação) | 🔧 Em desenvolvimento |
| **Generative & Strategic AI** | Briefings automáticos, análises estratégicas, recomendações | 🔧 Próximo ciclo |

---

## 3. Framework de Adoção

### 3.1. Mapeamento de Dores vs Oportunidades

Baseado na matriz Distrito de maturidade do processo vs intensidade da dor:

```
                    INTENSIDADE DA DOR
                    Baixa ←──────────→ Alta
         ┌─────────────────────────────────┐
   Alta  │    Otimizações      │  Dores     │
         │    pontuais         │  estratég. │
         │                     │            │
MATURI-  │  Relatórios        │  Decisão   │
DADE DO  │  sob demanda       │  lenta     │
PROCESSO │                     │  sem dados │
         ├─────────────────────┼────────────┤
   Baixa │  Ineficiências     │  Caos      │
         │  latentes          │  operac.   │
         │                     │            │
         │  Planilhas         │  Dados     │
         │  manuais           │  dispersos │
         └─────────────────────────────────┘
```

**Diagnóstico V4:**
- **Caos operacional resolvido:** Coleta manual de dados de anúncios → automática via API
- **Ineficiências latentes em redução:** Relatórios manuais → gerados em segundos
- **Dores estratégicas endereçadas:** Decisão baseada em dados → análise IA + recomendações

### 3.2. Critérios de Avaliação

| Critério | Score V4 | Justificativa |
|---|---|---|
| **Natureza da tarefa** | 4/5 | Tarefas estruturadas com regras claras, alta automação possível |
| **Dados** | 4/5 | APIs oficiais (Google, Meta, Bing), dados estruturados e consistentes |
| **Integração/TI** | 4/5 | APIs REST, OAuth2, SDKs maduros, sem dependência de legado |
| **Risco** | 3/5 | Relatórios são informação — erro não causa dano direto ao cliente |
| **Valor de Negócio** | 5/5 | Economia de horas/dia por account, decisões mais rápidas, escala viável |

### 3.3. Priorização

Seguindo a matriz Distrito:

```
PRIORIDADE 1 — ALTO VALOR / BAIXA COMPLEXIDADE
  ✅ Relatório de tráfego multicanal (MVP atual)
  ✅ Envio automático por e-mail
  ✅ Setup em comando único

PRIORIDADE 2 — ALTO VALOR / MÉDIA COMPLEXIDADE
  🔧 Flags de risco (ROAS, churn, OKR, operação)
  🔧 Pipeline de conteúdo editorial
  🔧 Briefing automático do comitê

PRIORIDADE 3 — MÉDIO VALOR / ALTA COMPLEXIDADE
  🔮 Análise preditiva com machine learning
  🔮 Agentes autônomos por cliente
  🔮 Integração com CRM (HubSpot / Kommo)
```

---

## 4. Arquitetura Técnica

### 4.1. Visão Geral

```
                    ┌──────────────────────────────────────────────┐
                    │              OPENCODE AGENT ORCHESTRA         │
                    │         (12 subagentes · 60+ skills)         │
                    └──────────────────────┬───────────────────────┘
                                           │
                    ┌──────────────────────┼───────────────────────┐
                    │                      │                       │
                    ▼                      ▼                       ▼
        ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
        │   v4-automations  │  │    Builders Hub   │  │     CSM Hub       │
        │   (Python + cron) │  │   (Skills + IA)   │  │  (Customer Suc.)  │
        └─────────┬─────────┘  └───────────────────┘  └───────────────────┘
                  │
     ┌────────────┼────────────┬────────────┬────────────┐
     ▼            ▼            ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Google  │ │  Meta   │ │  Bing   │ │   GA4   │ │  Ekyte  │
│ Ads API │ │ Ads API │ │ Ads API │ │   API   │ │   API   │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### 4.2. Componentes

#### 4.2.1. v4-automations (Core Engine)

**Linguagem:** Python 3.9+
**Agendamento:** Cron (Linux) — scripts em `setup/install_cron.py`
**Conectores:** `scripts/connectors.py` — 7 conectores compartilhados
**Template:** Relatório V4 com logo, sem azul, layout editorial

| Módulo | Scripts | Função |
|---|---|---|
| **GT** | `relatorio_trafego.py`, `analise_performance.py` | Tráfego multicanal |
| **AM/CSM** | `atualizar_okrs.py`, `enviar_nps.py` | OKRs e pesquisa |
| **Copy** | `pipeline_conteudo.py`, `briefing_criativo.py` | Conteúdo editorial |
| **Coord.** | `briefing_comite.py`, `checklist.py` | Comitê e conformidade |
| **Ekyte** | `connector.py`, `sprints.py`, `fca.py` | Gestão de sprints |
| **Config** | `.env`, `clientes.json` | Credenciais e cadastro |

#### 4.2.2. Interface de Agente (OpenCode)

- **12 subagentes** especializados por função
- **60+ skills** compartilhadas no Builders Hub
- Modelos: DeepSeek V4, Gemini 2.5 Flash, GPT-OSS 120B
- Comandos: `/session-save`, `/session-list`, `/session-load`

#### 4.2.3. CSM Hub (Customer Success)

- 5 módulos: csm-principal, flag-roi, flag-churn, flag-okr, flag-operacao
- Cada módulo: SKILL.md + CONTEXT.md + TRIGGERS.md + OUTPUTS.md
- Automação: detector_flags.py (quinta 7h + domingo 20h)

### 4.3. Fluxo de Dados

```
API (Google/Meta/Bing/GA4)
    │
    ▼
connectors.py ───→ coleta_dados()
    │
    ▼
relatorio_trafego.py ───→ gera_html_relatorio()
    │                              │
    ├── formato terminal           │
    ├── formato JSON ──────→ Drive ──────→ cliente
    └── formato HTML ──────→ Gmail ──────→ stakeholder
                                    │
                                    └── Template V4
                                        (logo, sem azul, KPIs)
```

### 4.4. Segurança e Isolamento

- **Credenciais:** `.env` em cada pasta de cliente — gitignored
- **OAuth2:** `token.json` com renovação automática
- **Logs:** `v4-automations/logs/` — sem dados sensíveis
- **Clientes isolados:** `clientes.json` com contas segregadas por cliente

---

## 5. Governança de IA

Alinhado aos 8 pilares do Distrito AI Adoption Framework 2026.

### 5.1. FinOps para IA

| Prática | Implementação V4 |
|---|---|
| Custo por inferência | Tracking por chamada Claude API (modelo, tokens, custo) |
| Orçamento por produto | Definição por script — relatório vs análise vs briefing |
| Right-sizing | Uso de modelos tier: DeepSeek V4 para análise, Gemini Flash para output |
| **Escalabilidade** | Cache V4mos (30min), rate limiting (100 req/min), paginação automática |

### 5.2. TrISM (Trust, Risk & Security Management)

| Prática | Implementação V4 |
|---|---|
| Catálogo de riscos | Matriz por tipo de dado (anúncios = baixo risco, cliente = médio) |
| Prompt injection | Prompts fixos no código (system prompts), sem entrada de usuário |
| Data leakage | .env gitignored, tokens nunca expostos em output |
| Model cards | Skills versionadas com descrição de capacidade e limitação |
| **Escalabilidade** | Auditoria periódica de acessos, revisão de logs |

### 5.3. Observabilidade e Telemetria

| Prática | Implementação V4 |
|---|---|
| Métricas on-line | Logs de execução por script + timestamp |
| Alertas de regressão | Comparação W/W (week-over-week) nos relatórios |
| Circuit breakers | Tratamento de exceção por API — fallback para dados sample |
| Tracing | Request ID da Google Ads API, logs de erro detalhados |
| **Escalabilidade** | Dashboard de saúde dos pipelines (planejado) |

### 5.4. EvalOps (Avaliação e Qualidade)

| Prática | Implementação V4 |
|---|---|
| Conjuntos de avaliação | Dados sample integrados para teste sem API |
| A/B testing | Modo sample vs real — comparação de saída |
| Métricas humanas | Revisor agente validando outputs críticos |
| **Escalabilidade** | Testes de regressão por pipeline a cada deploy |

### 5.5. Segurança de Prompt e Conteúdo

| Prática | Implementação V4 |
|---|---|
| Input hardening | Prompts fixos em system — sem template injection |
| Output filters | Números validados antes de enviar (ROAS, CPA, etc.) |
| PII | Nenhum dado pessoal em relatórios — apenas métricas agregadas |
| **Escalabilidade** | Auditoria de output por amostragem semanal |

### 5.6. ModelOps (Ciclo de Vida)

| Prática | Implementação V4 |
|---|---|
| Gates de aprovação | Skill review + PR no Builders Hub antes de compartilhar |
| Rollout seguro | Modo sample primeiro, depois real, depois automático |
| Versionamento | Skills em git, scripts versionados, changelog por release |
| SBOM de IA | `skills-lock.json` com dependências de cada skill |
| **Escalabilidade** | Registry de skills com status (dev/staging/prod) |

### 5.7. Gestão de Terceiros

| Prática | Implementação V4 |
|---|---|
| Due diligence | Google, Meta, Anthropic, OpenRouter — provedores enterprise |
| Licenças | APIs públicas, licenças MIT/APACHE no código próprio |
| Vulnerabilidades | Dependências Python trackeadas em requirements.txt |
| **Escalabilidade** | Política de vendor lock-in prevention (múltiplos provedores LLM) |

### 5.8. RAG e Governança do Conhecimento

| Prática | Implementação V4 |
|---|---|
| Curadoria de fontes | NotebookLM + bases/ + docs/ como fontes curadas |
| Freshness | Dados de API sempre atualizados (D-3 para Meta, D-0 para Google) |
| Controle de citações | Relatórios citam fonte (Google Ads, Meta Ads) e período |
| Alucinação | Safeguard: dados sample têm flag `simulado: True` visível |
| **Escalabilidade** | Índice de conhecimento por cliente (mission-control + contexto) |

---

## 6. Escalabilidade

### 6.1. Dimensões de Escala

| Dimensão | Hoje (MVP) | Próximo ciclo | Visão |
|---|---|---|---|
| **Clientes** | 1-2 (manual) | 10 (clientes.json) | N (autodescoberta) |
| **Squads** | 1 (Prime) | 3 | Todos |
| **Plataformas** | Google + Meta + Bing | + TikTok, LinkedIn, Pinterest | Qualquer API |
| **Frequência** | Sob demanda + cron semanal | Diária | Streaming em tempo real |
| **Usuários** | Account + GT | + Coord, Copy, CSM, Cliente | Autosserviço |
| **Modelos LLM** | Claude (Anthropic) | Multi-provedor (OpenRouter) | Auto-seleção por tarefa |

### 6.2. Arquitetura para Escala

```
HOJE (MVP)                        PRÓXIMO (CRESCIMENTO)
─────────                         ────────────────────
1 servidor Linux                  Múltiplos workers
Cron local                        Fila de tarefas (Redis)
.env manual                       Vault / Secrets Manager
clientes.json manual              Auto-descoberta via Ekyte
Logs em arquivo                   Logs centralizados (Loki)
Email direto (Gmail API)          Email + Slack + Webhook
```

### 6.3. Multi-cliente

O schema `clientes.json` já foi projetado para escala:

```json
{
  "clientes": [
    {
      "nome": "Cliente A",
      "google_ads_customer_id": "123-456-7890",
      "meta_ad_account_id": "act_123456789",
      "ga4_property_id": "properties/123456789",
      "verba_mensal": 5000,
      "vertical": "ecommerce",
      "okrs": { ... }
    },
    {
      "nome": "Cliente B",
      "google_ads_customer_id": "987-654-3210",
      "meta_ad_account_id": "act_987654321",
      ...
    }
  ]
}
```

**Comando para todos os clientes:**
```bash
python3 scripts/gt/relatorio_trafego.py --all --days 7 --format html --email gt@v4company.com
```

### 6.4. Multi-provedor LLM

A camada de IA usa OpenRouter como provedor principal, permitindo:
- Fallback automático se um modelo falhar
- Seleção do melhor modelo por tarefa (DeepSeek para análise, Gemini para output)
- Controle de custo por modelo
- Sem vendor lock-in

### 6.5. Padrão de Configuração

O setup em comando único (`python3 setup/install_all.py`) garante:
- Nova unidade configurada em <10 minutos
- Todas as variáveis perguntadas no terminal
- Testes automáticos de cada etapa
- Resumo final com comandos úteis

---

## 7. Esteira de Desenvolvimento

Seguindo o ciclo Distrito: Discovery → Afinamento → MVP → Deployment → Escala.

### 7.1. Discovery (Concluído)

- ✅ Mapeamento de dores: coleta manual de dados, relatórios demorados, decisão sem dados
- ✅ Definição de memória: v4-automations + connectors.py
- ✅ Levantamento de bases: Google Ads, Meta Ads, Bing Ads, GA4, Ekyte
- ✅ Framework de adoção: Distrito AI Adoption 2026

### 7.2. Afinamento e MVP (Atual)

- ✅ Design da solução: pipeline de relatórios multicanal
- ✅ Experiência do usuário: comando único de setup, template V4, email automático
- ✅ Seleção do LLM: Claude (Anthropic) + fallback via OpenRouter
- ✅ Implementação inicial: coleta + consolidação + entrega
- ✅ Testes e aprendizados: modo sample para validação sem API

### 7.3. Deployment (Em andamento)

- 🔧 Introdução gradual: vendas → operação → cliente
- 🔧 Ajustes finos: templates, filtros, periodicidade
- 🔧 Monitoramento contínuo: logs de execução, alertas de falha

### 7.4. Escala (Próximo ciclo)

- 🔮 Multi-squad: Prime → Growth → Performance
- 🔮 Agentes autônomos por cliente
- 🔮 Streaming de dados em tempo real
- 🔮 Dashboard de AI Ops (saúde dos pipelines, custo, qualidade)

---

## 8. Métricas e KPIs

### 8.1. Métricas de Sucesso do MVP

| Métrica | Alvo | Como medir |
|---|---|---|
| Tempo de setup | <10 min | Script install_all.py |
| Relatórios gerados | Qualquer cliente, 7/30 dias | Logs de execução |
| Entrega por email | Funcionando | Teste de pipeline |
| Modo sample operacional | Dados ilustrativos sem API | Flag --sample |
| Template V4 | Logo, sem azul, KPIs | Inspeção visual |

### 8.2. Métricas de Governança

| Métrica | Alvo | Frequência |
|---|---|---|
| Custo por relatório | <R$ 0,50 | Semanal |
| Taxa de sucesso de API | >95% | Diária |
| Tempo médio de execução | <30s | Diário |
| Cobertura de clientes | 100% ativos | Mensal |

### 8.3. Métricas de Impacto no Negócio

| Métrica | Hoje (sem IA) | Com AI Ops (projetado) |
|---|---|---|
| Tempo semanal de relatório | 2h/account | 5 min (automático) |
| Decisões baseadas em dados | 30% | 80% |
| Erro de coleta manual | 15% | <1% |
| Cobertura de análise | 1 plataforma | 3+ plataformas |
| Escala por account | 3-5 clientes | 15-20 clientes |

---

## 9. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| API Key exposta | Baixa | Alto | .env gitignored + rotação periódica |
| Token OAuth expirado | Média | Médio | Renovação automática em auth_google.py |
| API rate limit | Média | Baixo | 2s entre requests, paginação automática |
| Dado inconsistente (Meta CTR) | Alta | Médio | ctr_calc corrige, campo documentado |
| Latência Facebook D-3 | Alta | Baixo | Documentado, padding de 3 dias |
| Modelo Claude fora do ar | Baixa | Alto | Fallback para OpenRouter (multi-provedor) |
| Mudança de API (breaking) | Média | Alto | Conectores isolados, testes de regressão |
| Escala não acompanha clientes | Média | Alto | Arquitetura preparada para N, filas e workers |

---

## 10. Roadmap

### Fase 1 — MVP (Maio 2026) ✅

- [x] Setup em comando único
- [x] Relatório de tráfego multicanal
- [x] Template V4 (logo, sem azul)
- [x] Modo sample para demonstração
- [x] Envio por e-mail automático
- [x] Documentação técnica
- [x] Framework de governança

### Fase 2 — Operação (Junho 2026)

- [ ] Flags de risco (ROAS, churn, OKR, operação)
- [ ] Pipeline de conteúdo editorial
- [ ] Briefing automático do comitê
- [ ] Relatório com dados reais de 3+ clientes
- [ ] Dashboard de saúde dos pipelines

### Fase 3 — Escala (Julho-Agosto 2026)

- [ ] Multi-squad (Prime → Growth → Performance)
- [ ] Auto-descoberta de clientes via Ekyte
- [ ] Análise preditiva com ML
- [ ] Integração com Slack para alertas
- [ ] Portal de autosserviço para clientes

### Fase 4 — Maturidade (Setembro+ 2026)

- [ ] Agentes autônomos por cliente
- [ ] Streaming de dados em tempo real
- [ ] Governança automatizada (FinOps, TrISM)
- [ ] Escala para N squads, N clientes, N plataformas

---

## 11. Próximos Passos

### Imediatos (esta semana)

1. **Compartilhar documento** com stakeholders para validação
2. **Exportar NotebookLM** para `bases/v4-foundation/notebooks/`
3. **Configurar credenciais reais** de 1 cliente para teste real
4. **Rodar relatório real** e validar com o time

### Curto prazo (próximas 2 semanas)

5. **Onboarding de nova unidade** via `python3 setup/install_all.py`
6. **Treinamento do time** no uso dos comandos
7. **Feedbacks e ajustes** no template e periodicidade

### Médio prazo (próximo mês)

8. **Flags de risco** em produção
9. **Pipeline de conteúdo** integrado
10. **Dashboard de AI Ops** para liderança

---

## Apêndices

### A. Comandos Rápidos

```bash
# Setup completo
python3 v4-automations/setup/install_all.py

# Relatório sample
python3 v4-automations/scripts/gt/relatorio_trafego.py \
    --cliente "Cliente A" --days 7 --format html --sample

# Relatório real
python3 v4-automations/scripts/gt/relatorio_trafego.py \
    --cliente "Cliente X" --days 7 --format html \
    --email gt@v4company.com

# Relatório para todos
python3 v4-automations/scripts/gt/relatorio_trafego.py \
    --all --days 7 --format html \
    --email gt@v4company.com

# Instalar crons
python3 v4-automations/setup/install_cron.py

# Autenticação Google
python3 v4-automations/setup/auth_google.py
```

### B. Glossário

| Termo | Definição |
|---|---|
| **AI Ops** | Artificial Intelligence for Operations — IA aplicada à operação |
| **TrISM** | Trust, Risk & Security Management — governança de confiança e risco |
| **FinOps** | Financial Operations — gestão de custo de IA |
| **EvalOps** | Evaluation Operations — qualidade e avaliação contínua |
| **ModelOps** | Model Operations — ciclo de vida de modelos |
| **RAG** | Retrieval-Augmented Generation — geração aumentada por recuperação |
| **ROAS** | Return on Ad Spend — retorno sobre investimento em anúncios |
| **CPA** | Cost per Acquisition — custo por aquisição |
| **FCA** | Ficha de Correção de Anomalia — documento de desvio |
| **CHAS** | Chamado de Suporte — ticket de ação corretiva |

### C. Referências

- **Distrito AI Adoption Framework 2026** — `bases/v4-foundation/docs/distrito-ai-adoption-framework.md`
- **Guia de Instalação** — `docs/v4-automations-guia-instalacao.md`
- **Arquitetura de Relatórios** — `v4-automations/docs/ARQUITETURA_RELATORIOS.md`
- **Plano de Implantação** — `PLANO_IMPLANTACAO_AGENTES.md`
- **Manual de Uso** — `MANUAL_DE_USO.md`
- **Builders Hub Skills** — `.agents/skills/` e `.claude/skills/`

---

> **V4 Company — Maio 2026**
>
> Este documento é vivo. Atualize conforme a operação evolui.
> Próxima revisão: Junho 2026.
