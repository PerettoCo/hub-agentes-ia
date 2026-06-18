---
name: ai-search
description: Setor completo de AI Search (AEO + GEO + AI SEO) — diagnose, implementa e gerencia a presenca de marcas em respostas de IA (ChatGPT, Perplexity, Google AI Overviews, Gemini, Claude, Copilot). Use quando o usuario falar em "AI SEO", "AEO", "GEO", "otimizar para IA", "aparecer no ChatGPT", "citacao em IA", "AI Overview", "presenca em inteligencia artificial", "criar produto de AI SEO", "diagnostico AI visibility", "service cart AI", "extractability score", "AI citations", "share of AI voice" ou "otimizacao para mecanismos de resposta". Veja o REGISTRY da skill em ai-visibility-v4/ para POPs, scripts, portal e documentos fundacionais.
aliases: [ai-search, ai-seo, ai-visibility, geo, aeo]
tags: [skill, area-geral, produto, ai-search]
---

# Skill: AI Search (AEO + GEO + AI SEO)

> Produto completo de otimização para mecanismos de resposta e inteligências artificiais. Estrutura modular com 4 pernas independentes (M1-M4) + gestão contínua.

## Arquitetura do Produto

```
ai-visibility-v4/
├── api/              → Vercel Functions (crawl + visibility check)
├── portal/           → Diagnóstico grátis + Service Cart + Proposta
├── docs/
│   ├── fundacional/  → AEO vs GEO, metodologias, métricas, mercado
│   ├── pops/
│   │   ├── junior/   → 4 POPs operacionais
│   │   ├── pleno/    → 4 POPs analíticos
│   │   └── senior/   → 4 POPs estratégicos
│   └── templates/    → Proposta, SOW, matriz de precificação
├── scripts/          → Citation checker, extractability, dashboard
└── workspace/        → Metodologia, métricas, referências
```

## Quando usar esta skill

- Usuário quer **criar, vender ou entregar** um serviço de AI Search
- Usuário quer fazer **diagnóstico gratuito** de AI Visibility (via portal)
- Usuário quer **estruturar o setor** de AI Search na V4
- Usuário menciona AEO, GEO, AI SEO, LLMO, otimização para IAs
- Usuário quer **dimensionar horas** por módulo (time tech mensurado por horas)

## Modelo Comercial

| Módulo | Tipo | Preço | Horas | Prazo |
|---|---|---|---|---|
| M1 Diagnóstico | One-time | R$ 4.900 | 12h | 5 dias |
| M2 Fundação Técnica | One-time | R$ 7.900 | 22h | 15 dias |
| M3 Conteúdo AEO | One-time | R$ 9.900 | 32h | 20 dias |
| M4 Ecossistema | One-time | R$ 5.900 | 16h | 10 dias |
| Gestão Contínua | Mensal | R$ 7.900/mês | 18h/mês | 30 dias |

**Combo completo (M1+M2+M3+M4):** R$ 24.500 (12% de desconto)
**Full Stack + 3m Gestão:** R$ 46.700

## Processo de Entrega

### Fase 0: Diagnóstico Gratuito (lead magnet automático)
O portal em `portal/index.html` permite ao cliente:
1. Colar URL ou nome da marca
2. Receber análise técnica automática (crawl → cheerio)
3. NLP no browser (Transformers.js) — entidades, similaridade, QA
4. Google PSE → verificação de citações em IA
5. Score geral 0-100 + scores por pilar
6. Recomendação automática de módulos
7. Service Cart → proposta comercial inline

### Fase 1: Diagnóstico Completo (M1 — R$ 4.900, 12h)
Ver `docs/pops/senior/01-arquitetura-conhecimento.md` e `docs/fundacional/02-metodologias.md`

1. Crawl técnico completo (5+ páginas)
2. Análise de schema markup, headings, extractability
3. Teste de 20 queries em ChatGPT + Perplexity + Google AI Overviews
4. Benchmark competitivo (3-5 concorrentes)
5. AI Citation Index (baseline)
6. Relatório de 60+ páginas (template em `docs/templates/`)
7. Recomendação de próximos passos

### Fase 2: Fundação Técnica (M2 — R$ 7.900, 22h)
Ver POPs em `docs/pops/junior/` e `docs/pops/pleno/`

- Schema markup (básico + avançado)
- Entity extraction e knowledge graph
- Otimização de extractability
- Liberação de AI crawlers (robots.txt, llms.txt, pricing.md)
- Technical SEO para crawlers de IA

### Fase 3: Conteúdo AEO (M3 — R$ 9.900, 32h)
Ver `docs/pops/pleno/03-estrategia-conteudo-aeo.md`

- Answer-first content architecture
- Cluster de conteúdo (5-10 peças)
- Otimização de conteúdo existente
- Formatos: definition blocks, step-by-step, comparison tables, FAQ, Q&A
- Schema de conteúdo (FAQPage, HowTo, QAPage, Article)

### Fase 4: Ecossistema (M4 — R$ 5.900, 16h)
Ver `docs/pops/junior/04-submissoes-diretorios.md` e `docs/pops/senior/02-otimizacao-ecossistema.md`

- Submissão a diretórios AI (Futurepedia, TAAFT, G2, Capterra, etc.)
- Google Business Profile otimizado
- Perfis em plataformas (LinkedIn, Crunchbase, Wikipedia)
- Guest posts e digital PR
- Backlinks de diretórios

### Gestão Contínua (R$ 7.900/mês, 18h/mês)
Ver `docs/fundacional/02-metodologias.md`

- Monitoramento mensal de AI Citations
- Ajustes técnicos recorrentes
- Produção de conteúdo AEO (2-4 peças/mês)
- Relatório mensal (HTML + PDF)
- QBR trimestral

## Métricas

### Outcome Metrics
| Métrica | Definição | Meta |
|---|---|---|
| AI Citation Count | Citações totais em IA/mês | 15+ em 6 meses |
| Share of AI Voice (SAIV) | % das citações vs concorrentes | 30%+ |
| Query Coverage Rate | % das queries-alvo com citação | 70%+ |
| Citation Sentiment | Tom das citações | 90%+ positivas |
| AI Referral Traffic | Visitas de fontes IA | 10%+ do tráfego orgânico |

### Leading Indicators
| Métrica | Target |
|---|---|
| Extractability Score | 80%+ |
| Schema Coverage | 100% páginas críticas |
| Entity Density | 15+ entidades/500 palavras |
| Freshness Index | 70%+ (< 6 meses) |

## Dimensionamento de Horas (por papel)

| Papel | $/h | M1 | M2 | M3 | M4 | Gestão |
|---|---|---|---|---|---|---|
| Júnior Tech | R$ 80/h | 4h | 8h | 4h | 8h | 4h |
| Pleno Tech | R$ 130/h | — | 10h | 4h | 4h | 4h |
| Copy | R$ 100/h | 4h | 2h | 20h | 4h | 6h |
| Sênior/Coord | R$ 180/h | 4h | 2h | 4h | — | 4h |
| **Total** | | **12h** | **22h** | **32h** | **16h** | **18h** |

## Documentos de Referência

- `ai-visibility-v4/docs/fundacional/01-aeo-vs-geo-conceitual.md`
- `ai-visibility-v4/docs/fundacional/02-metodologias.md`
- `ai-visibility-v4/docs/fundacional/03-metricas.md`
- `ai-visibility-v4/docs/fundacional/04-panorama-mercado.md`
- `ai-visibility-v4/docs/pops/` — Todos os POPs (júnior, pleno, sênior)
- `ai-visibility-v4/docs/templates/` — Proposta, SOW, matriz de precificação
- `ai-visibility-v4/portal/index.html` — Diagnóstico gratuito + Service Cart
- `ai-visibility-v4/scripts/` — Citation checker, extractability, dashboard
- `ai-visibility-v4/api/crawl.js` — Vercel Function de crawl técnico
- `ai-visibility-v4/api/visibility.js` — Vercel Function de citações PSE

## Ferramentas e Stack

| Componente | Tecnologia | Custo |
|---|---|---|
| Crawl técnico | Node.js + cheerio (Vercel Function) | Zero |
| NLP (browser) | Transformers.js (WASM) | Zero |
| Citation check | Google PSE (100 queries/dia grátis) | Zero |
| Frontend | HTML/CSS/JS puro (Vercel static) | Zero |
| Scripts | Node.js + Bash | Zero |
| LLM para scoring | Não usa — heurística pura | Zero |
