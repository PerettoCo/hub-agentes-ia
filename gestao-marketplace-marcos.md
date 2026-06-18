# PATTERN DETECTION — GESTÃO DE MARKETPLACE

> **Marcos Luciano** — Responsável SEO & AI | Peretto&Co. | V4 Company
> Framework pessoal de gestão de marketplace no Brasil

---

## MANIFESTO

Marketplace no Brasil não é sobre estar em todos os canais. É sobre **integração entre ecossistemas**.

A maior alavanca de GMV e margem não está dentro dos marketplaces — está na conexão entre o D2C e a operação 3P. Cliente pesquisa no Google antes de comprar no MELI. Se a marca não existe na busca, não existe no marketplace.

Opero com uma premissa: **fundação digital primeiro, canais depois**. Já vi operações queimarem verba de mídia em marketplace enquanto 83% do catálogo estava invisível para busca. O problema não é demanda — é descoberta e conversão.

No Brasil, a complexidade é maior: 5+ marketplaces com regras diferentes, dezenas de marcas no mesmo grupo competindo entre si por palavras-chave, operadores logísticos com SLA variável, e uma regulação (ANVISA) que pode derrubar qualquer operação desatenta.

Meu framework existe para isso: identificar padrões, organizar a gestão e separar o urgente do importante.

---

## AS 5 DIMENSÕES DE GESTÃO DE MARKETPLACE

A ordem importa. Não pule dimensões.

```
1. UNIDADE ECONÔMICA → 2. CATÁLOGO & DESCOBERTA → 3. OPERAÇÃO & REPUTAÇÃO → 4. MÍDIA & AQUISIÇÃO → 5. GOVERNANÇA & BI
```

---

### DIMENSÃO 1 — UNIDADE ECONÔMICA POR CANAL

**Pergunta**: Qual a margem real depois de taxas, logística, mídia e devoluções?

| O que eu olho | Indicador Saudável | Alerta |
|---|---|---|
| Taxa efetiva por marketplace | Conhecida por canal (MELI ~18-25%, Amazon ~15-22%, Shopee ~12-18%) | Taxa desconhecida ou só a "cheia" sem deduções |
| Margem de Contribuição Líquida | >25% pós taxas + logística + mídia | Margem negativa ou desconhecida |
| ROAS por frente 1P vs 3P | ROAS separado por modelo (não consolidado) | ROAS >4.0 consolidado mascara canibalização |
| LTV:CAC com payback | >3:1, payback <12 meses | <1:1 (queima caixa) |
| Custo de devolução/troca | Conhecido e provisionado | Desconhecido — surpresa no fechamento |

**Padrão que mais vejo**: ROAS consolidado >4.0 que esconde que o 1P (margem menor) está canibalizando o 3P (margem maior). Decisão de mídia destrói margem líquida.

**Métrica composta que criei — RMPE**:
```
RMPE = (Receita × Margem Bruta) / (Mídia + Taxas MKTP + Logística)
```
Unifica rentabilidade real entre canais em um índice comparável.

---

### DIMENSÃO 2 — CATÁLOGO & DESCOBERTA

**Pergunta**: O produto é encontrável antes de ser vendável?

| O que eu olho | Indicador Saudável | Alerta |
|---|---|---|
| Crawl & Indexação | >70% das URLs indexáveis | <30% = conteúdo invisível |
| Structured Data | JSON-LD server-side em 100% dos produtos | Zero structured data = zero feed compatível |
| 301 vs 302 | 301 em todos os produtos | 302 não passa link equity |
| Duplicatas 3P | Resolvidas na base antes de escalar | Milhares de sellers = duplicata infinita |
| SEO por marca | Autoridade tópica por marca (sem canibalização) | 5 marcas brigando pela mesma keyword |
| AI Visibility/GEO | Citado em ChatGPT, Perplexity, Gemini | Zero citação em LLMs = zero tráfego de IA |
| Core Web Vitals | LCP <2.5s, CLS <0.1, INP <200ms | Homepage 12s de resposta = inviável |

**Padrão operação invisível**: a marca existe mas não é descoberta. Presença digital rasa, structured data zero, confiança cega em mídia paga como única fonte de tráfego.

**Caso real**: Na auditoria da Integralmedica (BRG), crawlei 237 URLs. Apenas 40 indexáveis (16,9%). Structured data zero em 100% das páginas. 302 redirect em todos os produtos. 89 imagens >100KB (45,88%). Homepage com 1,17 MB de HTML e 12s de resposta. O site D2C estava invisível — e sem D2C saudável, o marketplace vende menos.

---

### DIMENSÃO 3 — OPERAÇÃO & REPUTAÇÃO

**Pergunta**: O cliente recebe o que comprou, no prazo, e fala bem?

| O que eu olho | Indicador Saudável | Alerta |
|---|---|---|
| Buy Box | >85% de permanência | Perdendo Buy Box por preço ou reputação |
| Reputação (Review Score) | >4.5 em todos os canais | <4.0 = perde conversão |
| SLA de entrega | Conhecido e cumprido por canal | Avaria ou atraso recorrente |
| SAC | Respondido em <24h (negativas) | Sem SLA de resposta |
| FULL | Operacional com estoque reconciliado | FULL sem integração de estoque = ruptura |
| Devolução | Taxa conhecida e dentro do esperado | Taxa >10% = problema de descrição ou qualidade |

**Padrão reputação negligenciada**: não monitoram avaliações em tempo real. Quando percebem, já perderam Buy Box e conversão por 30 dias.

**3 sinais de operação doente** (qualquer marketplace):
1. Combinados reincidentes com operador logístico sem execução
2. Queda de avaliação sem plano de recuperação
3. SLA de entrega desconhecido ou não medido

---

### DIMENSÃO 4 — MÍDIA & AQUISIÇÃO

**Pergunta**: O investimento em mídia está indo para o lugar certo?

**Minha arquitetura de mídia por canal**:

| Canal | Formato | Alavanca | Estratégia |
|---|---|---|---|
| Mercado Livre | Mercado Ads + Display | FULL + reputação | FULL desde go-live. SP para marcas próprias. Display para conquest de concorrentes |
| Amazon | Sponsored Products + Brands + DSP | Buy Box + reviews | A+ Content para todas as marcas. SB para busca de marca. DSP para retargeting |
| Shopee | Shopee Ads + Live Shopping | Preço + gamificação | Cashback + frete grátis. Catálogo enxuto (top 20 SKUs) |
| Magalu | Magalu Ads + VIP | FULL + reputação | Foco em marcas de distribuição |
| Netshoes/Centauro | Programática + Parceria | Exclusividade | Cross-sell com equipamentos. Espaço de categoria |
| Google | Shopping + YouTube + PMax | Jornada completa | 60%+ das jornadas começam em busca — sem Google, o funil quebra |

**Orçamento: Defesa (60%) vs Conquista (40%)**
- **Defesa**: Lances agressivos em branded keywords. Sponsored Brands ocupando topo da SERP
- **Conquista**: Product targeting em concorrentes. Display conquest

**Dayparting por canal**:
- MELI + Amazon: Sexta a domingo (consumidor fitness pesquisa)
- Shopee: Segunda e terça (ofertas relâmpago)
- Magalu: Quarta e quinta (clube de assinatura)

**3 perguntas que eu faço sobre mídia**:
1. Qual canal entrega o menor CPA no último ciclo completo?
2. O criativo perdeu potência vs média histórica de CTR?
3. A frequência no público-alvo já passou do limiar de exaustão?

**Padrão de desperdício**: manter criativo no ar após o pico de fadiga — CPM sobe, CTR cai, CPA dobra, mas ninguém pausa porque "ainda está dando resultado".

**Canal mais subestimado**: YouTube Ads. Suplemento vende por credibilidade. Vídeos de atletas, reviews e transformação são o ativo de maior prova social.

---

### DIMENSÃO 5 — GOVERNANÇA & BI

**Pergunta**: Quem faz o quê? E como sabemos se está funcionando?

**Documento de Fronteiras (Semana 1)**:

| Frente | Dono | SLA |
|---|---|---|
| Cadastro de Produto | Operação | 24h |
| Precificação | Comercial + Operação | Dinâmica (hub) |
| Mídia | Marketing | Diário |
| Reputação | SAC + Operação | 24h (negativas) |
| Pedidos/Entrega | Operador Logístico | Tempo real |
| Estoque | Operador + Hub | Diário |
| Dados/BI | Analytics | Tempo real |

**Dashboard que eu exijo**: Métrica × Meta × Atingido por canal e consolidado. Baseline de cada KPI antes de qualquer ação.

**KPIs que eu monitoro**:

| KPI | Meta |
|---|---|
| GMV por canal | Baseline +20% 90d |
| ROAS por canal (separado 1P/3P) | >4.0 |
| Margem de Contribuição Líquida | >25% |
| Share of Search (marca vs concorrência) | >40% |
| Buy Box | >85% |
| Review Score | >4.5 |
| Velocidade de Venda (ranking) | Top 10 |
| NPS | >75 |

**3 camadas de maturidade de dados**:
1. **Fundação**: IDs consistentes entre fontes (consegue identificar o mesmo cliente no MELI e no D2C?)
2. **Análise**: Cruzamento entre aquisição, conversão e retenção por canal
3. **Antecipação**: Modelos preditivos que geram ação, não só relatório

**Padrão tracking decorativo**: coleta dados ricos (eventos, leads, vendas), mas eles morrem no silo — nenhum pipeline conecta a uma decisão em tempo real.

---

## ESTUDO DE CASO BRG — A AUDITORIA REAL

Em 2024, recebi o desafio de avaliar a operação de marketplace do Grupo BRG (Integralmedica, Nutrify, Darkness, Optimum Nutrition, BSN) — 5 marcas, 10+ canais, setor de suplementos.

**Antes de propor qualquer movimento, eu auditei de verdade.** Abri o site integralmedica.com.br no Screaming Frog, crawlei 237 URLs e cruzei com dados públicos da operação.

### Achados críticos

| Métrica | Status | Impacto |
|---|---|---|
| Structured data | ZERO em 100% das páginas | Produtos sem schema = sem rich snippets, sem feed de marketplace |
| Homepage | 1,17 MB de HTML, 12s de resposta | Core Web Vitals reprovado, SEO penalizado |
| Meta descriptions duplicadas | 16 páginas com o mesmo texto | CTR orgânico baixo |
| Páginas indexáveis | Apenas 40 de 237 (16,9%) | 83% do conteúdo invisível |
| 302 redirects em produtos | 100% das páginas de produto | 302 não passa link equity |
| Imagens >100KB | 89 imagens (45,88%) | Lentidão em página de produto |
| H1 ausente | 10 páginas sem H1 | Heading perdido |
| Mobile PageSpeed | Não disponível (PSI não respondeu) | Provavelmente crítico |
| Segurança | 78,9% sem X-Frame-Options e Referrer-Policy | Risco para integrações |

### Diagnóstico

A operação tinha uma **âncora digital frágil**. Os problemas técnicos do site D2C se multiplicavam em marketplace porque:
1. Sem structured data, produtos não aparecem com rich snippets nem no Google Shopping
2. 302 nos produtos = link building e mídia apontando para produtos perde autoridade
3. Catálogo com 16,9% indexável = portfólio invisível para busca orgânica
4. SEO inexistente no D2C enfraquece a marca como um todo — e marca fraca em busca vende menos em marketplace

### Plano de 3 movimentos que propus

**S1–30: Fundação Digital**
- Correção dos 302 redirects (substituir por 301)
- Implementação de JSON-LD structured data em todas as páginas de produto
- Correção de meta descriptions duplicadas
- Otimização de imagens (compressão)
- Crawl semanal para monitorar indexação

**S2–60: Governança & Catálogo**
- Documento de fronteiras com After Click (operador logístico)
- Dashboard consolidado (PowerBI)
- Setup de ANYMARKET para automação de catalogação e precificação
- Monitoramento contínuo de reputação em todos os canais
- SLA de resposta para avaliações negativas (max 24h)

**S3–90: Canais & Mídia**
- Go-live FULL no MELI
- Criação de brandstores no MELI, Amazon e Shopee (uma por marca)
- Primeira rodada de Mercado Ads e Amazon Ads
- JBP trimestral com top 3 canais
- Budget: 50% Google ecosystem, 30% MELI+Amazon, 20% programática

---

## DETECTOR DE PADRÕES BRASIL

8 padrões que eu identifico em operações de marketplace no Brasil:

| Padrão | Onde aparece | Antídoto |
|---|---|---|
| **Receita Fantasma** | ROAS consolidado esconde canibalização 1P vs 3P | Decompor MRR/ROAS por frente e por canal |
| **Operação Invisível** | <30% do catálogo indexado, structured data zero | Crawl + schema + conteúdo antes de mídia |
| **Catálogo Canibalizado** | Marcas do mesmo grupo competem pela mesma keyword | Hub-and-spoke com intenções de busca por marca |
| **Reputação Negligenciada** | Não monitoram avaliações em tempo real | SLA 24h para negativas + dashboard de reputação |
| **Tracking Decorativo** | Coleta tudo, não cruza nada, não age | Pipeline Captura → Orquestração → Ativação |
| **JBP sem Baseline** | Negociam verba sem saber KPIs atuais | Baseline 30 dias antes de qualquer JBP |
| **Governança Difusa** | Todo mundo é dono de nada | Documento de fronteiras + dono único por frente |
| **Mídia sem Atribuição** | Não sabem qual canal gerou qual venda | Modelo de atribuição funcional antes de escalar verba |

---

## PLAYBOOK 90 DIAS

### Semana 1
- Crawl completo do ecossistema D2C
- Documento de fronteiras (quem faz o quê)
- Baseline de todos os KPIs por canal

### S1–30: Fundação Digital
- Structured data em 100% das páginas de produto
- 301 redirects (eliminar 302)
- Correção de meta descriptions e H1
- Otimização de imagens e Core Web Vitals
- Setup de tracking e atribuição

### S2–60: Governança
- Dashboard consolidado (Métrica × Meta × Atingido)
- Rotina semanal com operador logístico
- Monitoramento de reputação em tempo real
- Setup de hub de automação (ANYMARKET ou similar)
- Regras de precificação dinâmica

### S3–90: Canais & Mídia
- Ativação dos canais prioritários (MELI FULL, Amazon Brandstore)
- Primeira rodada de mídia com split Defesa/Conquista
- JBP trimestral com top 3 canais
- Calendário sazonal alinhado
- Relatório de resultados vs baseline

---

## MATRIZ DE DIAGNÓSTICO

| Dimensão | Saúde | Alerta | Crítico |
|---|---|---|---|
| **1. Unidade Econômica** | Margem + ROAS conhecidos por canal, LTV:CAC >3:1 | Uma métrica desconhecida | Queima caixa sem saber |
| **2. Catálogo & Descoberta** | >70% indexável, schema 100%, 301 ok | Structured data parcial, crawl <50% | <30% indexável, zero schema |
| **3. Operação & Reputação** | Review >4.5, Buy Box >85%, SLA conhecido | Review caindo, SLA não medido | Review <4.0, Buy Box perdida |
| **4. Mídia & Aquisição** | CPA estável, 3+ canais, atribuição OK | Dependência >70% de 1 canal | Atribuição zero |
| **5. Governança & BI** | Fronteiras claras, dashboard consolidado | Fronteiras existem mas não são seguidas | "Cada um faz do seu jeito" |

---

## AS PERGUNTAS QUE EU FAÇO

Estas são as perguntas que levo para qualquer reunião de avaliação de operação de marketplace:

1. **Qual a margem real** depois de taxas, logística, mídia e devolução? (Se não sabem, a operação é cega)
2. **Quantas URLs do D2C estão indexadas?** (Se <30%, o conteúdo é invisível)
3. **Tem structured data nos produtos?** (Se não, o feed do marketplace não enxerga)
4. **Quem é o dono de cada frente?** (Se todo mundo é dono de nada, a operação trava)
5. **O ROAS é separado por canal e por modelo (1P/3P)?** (Se é consolidado, tem receita fantasma)
6. **Qual o SLA de resposta para avaliação negativa?** (Se não tem, a reputação é reativa)
7. **O tracking conecta a alguma ação ou é decorativo?** (Se é decorativo, os dados são ruído)
8. **Qual decisão, se revertida, derrubaria a operação?** (Se não sabem, não conhecem o próprio negócio)

---

## CONTRIBUIÇÕES DOS 11 AGENTES

### CMO — Arquitetura Estratégica
> *"5 dimensões universais para marketplace: Unidade Econômica, Retenção, Aquisição, Conversão, Eficiência Operacional. Precedência importa — sem economia viável, nada sustenta."*

### Estratégia — Sabatina
> *"Qual decisão, se revertida, derrubaria a operação? Em marketplace, muitas vezes é o SLA com o operador logístico. Um dia de atraso generalizado destrói reputação em todos os canais."*

### Revenue Ops — Financeiro
> *"Receita fantasma é o padrão mais letal em marketplace — ROAS consolidado esconde que 1P está canibalizando 3P. Margem de Contribuição Líquida por SKU por canal é a métrica que salva."*

### Account — Saúde Operacional
> *"3 sinais de operação doente em marketplace: combinados reincidentes sem execução com o operador logístico, queda de avaliação sem plano de recuperação, SLA de entrega desconhecido."*

### Dados — Diagnóstico
> *"3 camadas de maturidade: Fundação (IDs consistentes entre MELI e D2C?), Análise (cruzamento aquisição vs retenção), Antecipação (modelos preditivos). Quebra de rastreabilidade é o padrão mais comum."*

### SEO — Visibilidade Digital
> *"3 pilares para marketplace: Descoberta (é encontrável no Google?), Extraibilidade (schema markup funciona?), Autoridade (backlinks e citações). Operação invisível: existir sem ser descoberto e confiar cegamente em mídia paga."*

### CRO — Conversão
> *"3 gargalos em marketplace: paralisia decisória (excesso ofertas), fricção cognitiva (PDP confusa), déficit de confiança (sem prova social). Atrito invisível: quem desenhou o fluxo acha que o usuário entende o mesmo que ele."*

### Mídia — Aquisição
> *"3 perguntas: menor CPA no ciclo? Criativo perdeu potência? Frequência no limiar? Padrão de desperdício: manter criativo fadigado porque 'ainda dá resultado'. YouTube Ads é o canal mais subestimado para suplementos."*

### Growth — Crescimento
> *"3 alavancas: Aquisição, Monetização, Retenção. Vale da inércia em marketplace: só empurram aquisição enquanto retenção e recompra vazam. Índice de Recorrência é a métrica norte."*

### Marketing — Posicionamento
> *"3 perguntas: para quem você existe (e não existe)? O que ninguém mais faz tão bem? Sentiriam sua falta? Operação-coringa: quer servir todo mundo e não é insubstituível em lugar nenhum."*

### Automação — Infraestrutura
> *"3 camadas: Captura (tracking funciona?), Orquestração (pipelines conectam sistemas?), Ativação (dados geram ação?). Tracking decorativo: coleta tudo no marketplace, não faz nada com os dados."*

---

> **Marcos Luciano** — Peretto&Co. | V4 Company
> Pattern Detection — Gestão de Marketplace | v1.0
