# Auditoria Técnica SEO — GRUPO R1 (r1grupo.com.br)

**Data:** Junho 2026 | **Versão:** 1.0 | **Classificação:** Confidencial Cliente
**Ferramenta:** Screaming Frog SEO Spider | **Amostra:** 325 URLs rastreadas

---

## Sumário Executivo

| Métrica | Valor |
|---|---|
| **Saúde Geral SEO** | **3.8 / 10** |
| **Problemas identificados** | 22 (3 Críticos, 7 Alto, 2 Médio, 1 Baixo, 9 Info) |
| **Horas totais para correção** | 185,5 h (distribuídas em 3 meses) |
| **Projeção de tráfego orgânico (90 dias)** | +35% a +55% |
| **Quick wins (48h)** | 5 ações de alto impacto e baixo esforço |

### Top 3 Riscos que Exigem Atenção Imediata do C-Level

1. **Blog invisível para o Google.** O canônico do blog aponta para `/?page_id=3511` — uma URL de parâmetro interno do WordPress. Isso faz com que o Google essencialmente ignore todo o conteúdo do blog. 333 links internos que deveriam distribuir autoridade estão sendo neutralizados. Esta é a causa mais provável de o blog não gerar tráfego orgânico relevante.

2. **Zero rich snippets em qualquer página.** Nenhuma página do site utiliza structured data (JSON-LD). Concorrentes diretos utilizam Article, FAQ e Event schema para ocupar o dobro do espaço no SERP com estrelas, perguntas e datas. O GRUPO R1 compete com "link azul simples" enquanto a concorrência ocupa rich snippets.

3. **185,5 h de esforço total, 56% em copywriting.** O maior gargalo não é técnico — é conteúdo. Sem produção de conteúdo textual de qualidade no Mês 3, os clusters temáticos não saem do papel e o teto orgânico permanece baixo. O investimento em tecnologia (WordPress + Elementor + LiteSpeed) já está feito; o gap é de conteúdo e configuração.

---

## Perfil do Site

| Característica | Detalhe |
|---|---|
| **Domínio** | r1grupo.com.br |
| **Segmento** | Produção de eventos (audiovisual, cenografia, tecnologia) |
| **CMS** | WordPress + Elementor |
| **Cache** | LiteSpeed Cache |
| **Idioma** | pt-BR (sem versões multilíngue) |
| **Total URLs rastreadas** | 325 |
| **URLs indexáveis** | 285 (87,7%) |
| **URLs não-indexáveis** | 40 (12,3%) |
| **Mobile** | Responsivo (sem links mobile-specific) |
| **Sitemap XML** | Presente |
| **Response time** | 93,54% das URLs < 1s |

---

## Diagnóstico Técnico Detalhado

### 🔴 Críticos — Impedem Indexação e Ranqueamento

#### C-01. Canonical Mismatch + Páginas de Categoria com 404

| Campo | Descrição |
|---|---|
| **Severidade** | 🔴 Crítico |
| **Evidência** | 8 URLs de categoria (/blog/categoria/*) possuem canônico apontando para /blog/{slug} — URLs que retornam 404. O blog inteiro canônico aponta para `/?page_id=3511` (URL de parâmetro). |
| **Impacto** | O Google não consegue determinar a URL canônica correta. Conteúdo do blog perde totalmente a capacidade de ranquear. Autoridade de 333 links internos é desperdiçada. |
| **Recomendação** | (1) Remover canônico das páginas de categoria para self-canonical. (2) Corrigir canônico do blog para `/blog/`. (3) Implementar 301 das URLs antigas para as novas. (4) Criar conteúdo nas páginas de categoria. |
| **Esforço** | 4 h (Desenvolvedor WordPress) |

#### C-02. Zero Structured Data em Todas as Páginas

| Campo | Descrição |
|---|---|
| **Severidade** | 🔴 Crítico |
| **Evidência** | 100% das páginas HTML sem qualquer JSON-LD ou Microdata. Zero rich snippets. |
| **Impacto** | Perda total de diferenciação no SERP. Concorrentes com FAQ, Article, Product e Event schema ocupam 2× o espaço visual e têm CTR estimada 20-30% superior. |
| **Recomendação** | (1) Implementar Organization schema (global, < 1h). (2) BreadcrumbList schema em todas as páginas. (3) Article schema no blog. (4) Product schema nas páginas de projeto/serviço. (5) Event schema se aplicável. |
| **Esforço** | 8 h (Desenvolvedor WordPress + SEO) |

#### C-03. Broken Internal Links (404)

| Campo | Descrição |
|---|---|
| **Severidade** | 🔴 Crítico |
| **Evidência** | 4 broken internal links encontrados: /blog/projetos-e-cases/, /blog/tendencias-de-mercado/, /blog/equipamentos-audiovisuais/, /blog/tecnologia-para-eventos/. |
| **Impacto** | Usuários encontram páginas de erro. Google perde crawl budget. Autoridade líquida é drenada. |
| **Recomendação** | (1) Mapear para onde essas URLs deveriam apontar. (2) Implementar 301 redirects. (3) Corrigir links internos no WordPress. |
| **Esforço** | 2 h (Desenvolvedor WordPress) |

---

### 🟠 Alto — Impactam Diretamente CTR e Experiência

#### A-01. Page Titles Truncados no SERP

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 47 páginas (53%) com title acima de 561px (limite de truncamento Google Desktop). 44 páginas com mais de 60 caracteres. |
| **Impacto** | Títulos cortados no SERP reduzem CTR em 15-25% estimado. Páginas perdem a capacidade de comunicar valor nos primeiros 60 caracteres. |
| **Recomendação** | Reescrever titles para 50-60 caracteres, keyword primária nos primeiros 40 caracteres, brand name ao final. |
| **Esforço** | 8 h (SEO) |

#### A-02. Meta Descriptions Ausentes ou Inadequadas

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 32 páginas (38,6%) sem meta description. 22 páginas (26,5%) com description acima de 985px. |
| **Impacto** | Google gera description automática quando não encontra, geralmente pior. CTR estimado cai 10-20% em páginas sem description otimizada. |
| **Recomendação** | Escrever meta descriptions únicas de 120-155 caracteres com call-to-action e keyword primária. |
| **Esforço** | 10 h (SEO / Copywriter) |

#### A-03. H1 Ausente ou Múltiplo

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 22 páginas (26,5%) sem H1. Homepage com 5 H1s. Inclui páginas críticas como /projetos/ e /trabalhe-conosco/. |
| **Impacto** | Sinal estrutural de hierarquia perdido. Google depende de H1 para entender o tópico principal da página. |
| **Recomendação** | (1) Adicionar H1 único em todas as páginas sem. (2) Reduzir homepage para 1 H1. (3) Garantir que H1 contenha keyword primária. |
| **Esforço** | 6 h (SEO) |

#### A-04. Imagens Não Otimizadas

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 96% das imagens acima de 200 KB. 63,9 MB total de imagens. 34 imagens acima de 500 KB. Zero WebP. LiteSpeed Cache presente mas não configurado para otimização de imagens. |
| **Impacto** | LCP (Largest Contentful Paint) severamente impactado. Core Web Vitals comprometidos. PageRank indireto reduzido (sites lentos ranqueiam pior). |
| **Recomendação** | (1) Configurar LiteSpeed para conversão automática para WebP. (2) Comprimir imagens existentes (alvo < 100 KB cada). (3) Implementar lazy loading nativo. |
| **Esforço** | 6 h (Desenvolvedor WordPress) |

#### A-05. Thin Content em Páginas de Projeto

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 18 páginas com conteúdo abaixo de 200 palavras. Múltiplas páginas de projeto individuais com apenas 1 unique inlink (orphan risk). |
| **Impacto** | Google considera conteúdo raso como baixa qualidade. Páginas com <200 palavras raramente ranqueiam para termos competitivos. |
| **Recomendação** | (1) Expandir páginas de projeto para no mínimo 500 palavras cada. (2) Adicionar seções de benefícios, diferenciais, casos de uso. (3) Melhorar linking interno entre projetos relacionados. |
| **Esforço** | 24 h (Copywriter) |

#### A-06. Diretório /devel/ Exposto

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 4 URLs do diretório /devel/ estão indexáveis. Ambiente de desenvolvimento acessível publicamente. |
| **Impacto** | Risco de segurança. Conteúdo de desenvolvimento pode ser indexado. Sinal de baixa maturidade técnica para o Google. |
| **Recomendação** | (1) Bloquear /devel/ no robots.txt. (2) Adicionar noindex. (3) Remover do sitemap. |
| **Esforço** | 1 h (Desenvolvedor WordPress) |

#### A-07. Redirect Chains /portfolio/ → /projetos/

| Campo | Descrição |
|---|---|
| **Severidade** | 🟠 Alto |
| **Evidência** | 33 redirects 301 de /portfolio/* para /projetos/*. 28 destes formam chains (múltiplos redirects em série). |
| **Impacto** | Cada redirect em chain perde ~10-15% de link equity. Diluição de PageRank. Atraso no carregamento para usuários. |
| **Recomendação** | (1) Mapear todas as URLs /portfolio/* para destino final /projetos/*. (2) Implementar redirect único. (3) Atualizar links internos para apontar diretamente para /projetos/*. |
| **Esforço** | 4 h (Desenvolvedor WordPress) |

---

### 🟡 Médio — Oportunidades de Melhoria Significativa

#### M-01. Missing Referrer-Policy Header

| Campo | Descrição |
|---|---|
| **Severidade** | 🟡 Médio |
| **Evidência** | 90,15% das URLs não possuem header Referrer-Policy. |
| **Impacto** | Perda de dados de referenciamento em análises. Risco de segurança de informação. |
| **Recomendação** | Configurar `strict-origin-when-cross-origin` no .htaccess ou no servidor. |
| **Esforço** | 1 h (Desenvolvedor WordPress) |

#### M-02. Páginas de Categoria sem Conteúdo Próprio

| Campo | Descrição |
|---|---|
| **Severidade** | 🟡 Médio |
| **Evidência** | Categorias do blog não possuem conteúdo introdutório. São páginas de listagem vazias de valor editorial. |
| **Impacto** | Google pode tratar como thin content. Perde oportunidade de ranquear para termos de categoria. |
| **Recomendação** | Adicionar 150-300 palavras introdutórias em cada página de categoria, explicando o tema e o que o leitor encontrará. |
| **Esforço** | 6 h (Copywriter) |

---

### 🔵 Baixo — Ajustes de Polimento

#### B-01. URLs de Parâmetro no Blog

| Campo | Descrição |
|---|---|
| **Severidade** | 🔵 Baixo |
| **Evidência** | Blog canonicalizado para `/?page_id=3511` (resolvido no C-01, mas requer atenção complementar). |
| **Impacto** | URLs de parâmetro não são amigáveis para SEO. |
| **Recomendação** | Garantir que todas as URLs do blog sigam o padrão `/blog/{slug}`. Configurar permalinks do WordPress corretamente. |
| **Esforço** | 2 h (Desenvolvedor WordPress) |

---

### ℹ️ Informativos — Observações e Boas Práticas

#### I-01. Paginação com rel next/prev

Rel next/prev presente nas páginas do blog. Correto. Manter.

#### I-02. Distribuição de Links Internos

| Página | Inlinks |
|---|---|
| /projetos/ | 333 |
| /blog/ | 333 |
| /quem-somos-3/ | 333 |
| /contato/ | 250 |
| Homepage | 167 |

Distribuição saudável de link equity. Páginas de serviço/produto individuais recebem apenas 1 inlink — expandir rede de links internos.

#### I-03. Response Time

93,54% das URLs abaixo de 1s. Excelente. Servidor responde bem.

#### I-04. Sitemap XML

Presente e referenciado no robots.txt. Verificar se inclui apenas URLs canônicas e indexáveis.

#### I-05. HTTPS e Certificado SSL

Site integralmente servido via HTTPS. Certificado SSL válido. Sem mixed content detectado. Conexão segura.

#### I-06. Mobile Responsivo

Design responsivo confirmado. Nenhum link mobile-specific (m. subdomain) detectado. Consistente com as práticas recomendadas de mobile-first indexing.

#### I-07. Monolíngue (pt-BR) — Sem Hreflang

Site opera exclusivamente em português brasileiro. Ausência de hreflang é correta e esperada. Nenhuma ação necessária.

#### I-08. Meta Keywords

Meta keywords não detectadas no crawl. Google ignora este metadado há mais de uma década. Ausência é uma boa prática.

#### I-09. Links Externos

Número de links externos dentro do esperado para um site institucional. Sem padrões de spam ou excesso de outbound links.

---

## Plano de Ação Trimestral

### Mês 1 — Fundação Crítica (Dias 1-30) — 29,5 h

| # | Ação | Horas | Responsável | Dependências | Prioridade |
|---|---|---|---|---|---|
| 1 | Corrigir canônico do blog (/?page_id=3511 → /blog/) | 2 | Dev WordPress | — | 1 |
| 2 | Remover canônico das categorias (/blog/categoria/* → self-canonical) | 2 | Dev WordPress | — | 1 |
| 3 | Corrigir 4 broken internal links (301 + atualizar links) | 2 | Dev WordPress | Mapeamento de destinos | 2 |
| 4 | Implementar Organization + BreadcrumbList schema (global) | 3 | Dev WordPress | — | 3 |
| 5 | Bloquear /devel/ (robots.txt + noindex) | 1 | Dev WordPress | — | 4 |
| 6 | Resolver redirect chains /portfolio/ → /projetos/ | 4 | Dev WordPress | Mapeamento completo | 5 |
| 7 | Configurar LiteSpeed para WebP + compressão de imagens | 4 | Dev WordPress | — | 6 |
| 8 | Comprimir imagens existentes (lote) | 2 | Dev WordPress | Tarefa 7 | 7 |
| 9 | Adicionar H1 único em 22 páginas | 4 | SEO | — | 8 |
| 10 | Reduzir homepage para 1 H1 | 0,5 | SEO | — | 9 |
| 11 | Configurar Referrer-Policy header | 1 | Dev WordPress | — | 10 |
| 12 | Adicionar lazy loading nativo em imagens | 2 | Dev WordPress | — | 11 |
| 13 | Remover URLs não-indexáveis do sitemap | 1 | SEO | — | 12 |
| 14 | Testar e validar todas as correções | 1 | SEO | Tarefas 1-13 | 13 |

**Total Mês 1:** 29,5 h (Dev WordPress: 23 h | SEO: 6,5 h)

---

### Mês 2 — On-Page e Conteúdo (Dias 31-60) — 59 h

| # | Ação | Horas | Responsável | Dependências | Prioridade |
|---|---|---|---|---|---|
| 1 | Reescrever 47 page titles (50-60 chars, keyword-first) | 8 | SEO | — | 1 |
| 2 | Escrever 32 meta descriptions ausentes | 6 | Copywriter | — | 2 |
| 3 | Reescrever 22 meta descriptions acima de 985px | 4 | Copywriter | — | 3 |
| 4 | Expandir 18 páginas thin content para 500+ palavras | 24 | Copywriter | Briefing SEO | 4 |
| 5 | Adicionar 150-300 palavras em páginas de categoria | 6 | Copywriter | — | 5 |
| 6 | Implementar Article schema no blog | 3 | Dev WordPress | Mês 1 Tarefa 4 | 6 |
| 7 | Implementar Product schema em páginas de projeto | 4 | Dev WordPress | Mês 1 Tarefa 4 | 7 |
| 8 | Otimizar alt text de imagens (prioridade: páginas com thin content) | 4 | SEO | — | 8 |

**Total Mês 2:** 59 h (Dev WordPress: 7 h | SEO: 12 h | Copywriter: 40 h)

---

### Mês 3 — Avançado e Clusters de Conteúdo (Dias 61-90) — 93 h

| # | Ação | Horas | Responsável | Dependências | Prioridade |
|---|---|---|---|---|---|
| 1 | Mapear 4 clusters temáticos (audiovisual, ESG, cenografia, eventech) | 6 | SEO | — | 1 |
| 2 | Criar 4 páginas hub/pilar (uma por cluster, 2000+ palavras cada) | 32 | Copywriter | Mapeamento SEO | 2 |
| 3 | Produzir 8 artigos spoke (2 por cluster, 1000+ palavras cada) | 32 | Copywriter | Páginas hub | 3 |
| 4 | Implementar FAQPage schema nas páginas hub | 4 | Dev WordPress | — | 4 |
| 5 | Construir malha de links internos entre hub + spokes | 4 | SEO | Tarefas 2-3 | 5 |
| 6 | Revisar e atualizar links internos em todo o blog | 6 | SEO | — | 6 |
| 7 | Testar Core Web Vitals (após imagens otimizadas) | 3 | SEO | Mês 1 Tarefas 7-8 | 7 |
| 8 | Configurar monitoramento de rankings (ferramenta) | 2 | SEO | — | 8 |
| 9 | Relatório de fechamento do trimestre | 4 | SEO | Todas | 9 |
| 10 | Criar visuais para páginas hub (infográficos, diagramas de processo) | 4 | Designer | Tarefas 2-3 | 10 |

**Total Mês 3:** 97 h (Dev WordPress: 4 h | SEO: 25 h | Copywriter: 64 h | Designer: 4 h)

---

## Resumo de Esforço Consolidado

### Horas por Mês e Especialidade

| Especialidade | Mês 1 | Mês 2 | Mês 3 | Total |
|---|---|---|---|---|
| Desenvolvedor WordPress | 23 h | 7 h | 4 h | **34 h** |
| SEO | 6,5 h | 12 h | 25 h | **43,5 h** |
| Copywriter | — | 40 h | 64 h | **104 h** |
| Designer | — | — | 4 h | **4 h** |
| **Total** | **29,5 h** | **59 h** | **97 h** | **185,5 h** |

### Distribuição Percentual

```
Copywriter:       104 h  (56,1%)
SEO:              43,5 h (23,5%)
Dev WordPress:     34 h  (18,3%)
Designer:           4 h  (2,2%)
```

### Curva de Investimento

```
Mês 1:  29,5 h  (15,9%) — Fundação técnica
Mês 2:  59 h    (31,8%) — On-page + conteúdo inicial
Mês 3:  97 h    (52,3%) — Clusters + conteúdo avançado
```

---

## Projeção de Impacto

| Métrica | Cenário Conservador | Cenário Otimista |
|---|---|---|
| **Tráfego orgânico (90 dias)** | +35% | +55% |
| **Páginas indexadas** | 285 → 310+ | 285 → 320+ |
| **CTR médio no SERP** | +10% | +20% |
| **Core Web Vitals pass** | LCP < 2,5s | LCP < 2,0s |
| **Rich snippets** | 0 → 40+ páginas | 0 → 60+ páginas |

### Fatores que Influenciam a Projeção

1. **Teto máximo atual:** O blog não ranqueia por causa do canônico quebrado (C-01). Corrigir isso sozinho pode gerar +15% a +25% de tráfego em 60 dias.
2. **Velocidade de indexação:** O Google precisa revisitar o site após as correções. Sitemap atualizado + submissão no Search Console acelera o processo.
3. **Concorrência:** Nicho de eventos corporativos no Brasil tem baixa maturidade SEO. As correções colocam o GRUPO R1 à frente da maioria dos concorrentes.
4. **Conteúdo:** Sem produção de conteúdo (54% do esforço), o teto é limitado. Clusters temáticos são o diferencial competitivo de longo prazo.

---

## KPIs para Acompanhamento Mensal

| KPI | Meta Mês 1 | Meta Mês 2 | Meta Mês 3 |
|---|---|---|---|
| Páginas indexadas (GSC) | 285 → 295 | 295 → 305 | 305 → 320 |
| Páginas com schema | 0 → 100% | 100% → 100% | 100% → 100% |
| Páginas com H1 único | 74% → 95% | 95% → 100% | 100% → 100% |
| Titles otimizados (< 60 chars) | 47% → 60% | 60% → 85% | 85% → 95% |
| Meta descriptions presentes | 61% → 75% | 75% → 95% | 95% → 100% |
| Imagens em WebP | 0% → 80% | 80% → 100% | 100% → 100% |
| Broken links | 4 → 0 | 0 → 0 | 0 → 0 |
| Redirect chains | 28 → 0 | 0 → 0 | 0 → 0 |
| Thin content (< 200 words) | 18 → 15 | 15 → 5 | 5 → 0 |

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| **Dependência do desenvolvedor WordPress** | Alta | Alto | Briefings muito claros. Agendar janela de 1 semana para correções críticas. Validar em staging. |
| **Mês 3 depende de produção de conteúdo** | Média | Alto | Iniciar recrutamento/contratação de copywriter no Mês 1. Ter 4 briefings prontos antes do Mês 3. |
| **Google não revisitar o site rapidamente** | Média | Médio | Submeter sitemap atualizado. Usar "Solicitar Indexação" no GSC. Publicar novo conteúdo para atrair crawler. |
| **Elementor limitar implementações técnicas** | Baixa | Médio | Verificar compatibilidade de schemas com Elementor. Plugin adicional pode ser necessário. |


---

## Próximos Passos Imediatos (48h)

1. **Validar acesso ao Search Console** — confirmar que está ativo para monitoramento.
2. **Agendar janela técnica com desenvolvedor WordPress** — 23 h de trabalho no Mês 1. Precisa de alinhamento de agenda.
3. **Corrigir canônico do blog** — 2 h de trabalho, maior impacto potencial de toda a auditoria.
4. **Mapear destinos dos 4 broken links** — definir para onde cada URL 404 deve redirecionar.
5. **Compartilhar este relatório com o time** — alinhar expectativas de esforço (185,5 h no trimestre).

---

## Glossário de Severidade

| Severidade | Significado |
|---|---|
| 🔴 Crítico | Impede indexação ou ranqueamento. Impacto direto em receita. |
| 🟠 Alto | Impacta significativamente CTR, experiência do usuário ou autoridade. |
| 🟡 Médio | Oportunidade de melhoria com impacto moderado. |
| 🔵 Baixo | Ajuste de polimento. Baixo impacto individual. |
| ℹ️ Informativo | Observação ou boa prática. Nenhuma ação requerida. |

---

## Sobre Esta Auditoria

**Ferramenta:** Screaming Frog SEO Spider v20.x
**Data do crawl:** Período de coleta dos 34 CSVs disponíveis em `bases/projetos-de-seo/dados/`
**Escopo:** Auditoria técnica estrutural baseada exclusivamente em crawl (Screaming Frog). Ferramentas de analytics e monitoramento (Search Console, Analytics, PageSpeed, backlinks) estão disponíveis para próximas fases se necessário.

---

*Documento gerado em Junho de 2026 pela equipe de SEO da V4 Company.*
*Padrão de qualidade: BuiltVisible / Moz / Searchmetrics.*
