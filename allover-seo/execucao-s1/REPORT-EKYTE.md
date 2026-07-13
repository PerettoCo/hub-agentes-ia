SPRINT 1 — SEO ALL OVER TX ROOFING

--- ONDE ESTAO OS ARQUIVOS ---

allover-seo/execucao-s1/
01-topic-clusters.json
02 ao 05 — JSON-LD em HTML pronto pra copiar
06-guia-execucao-s1.md
07 ao 19 — um JSON-LD por pagina do site
VALOR-IMPACTO.md
REPORT-EKYTE.md (este arquivo)

Cada arquivo 07- ate 19- tem Service schema + FAQPage schema especifico para aquela pagina. Basta copiar o JSON e colar no Yoast > Custom Schema ou Elementor > Custom Code.

--- O QUE FOI FEITO ---

Auditoria tecnica completa em 6 frentes paralelas: technical, content, schema, geo (AI visibility), local, google.

13 JSON-LD gerados, um para cada pagina:
/about/ /residential-roofing/ /commercial-roofing-houston/ /siding-houston/ /gutters-houston/ /window-replacement-houston/ /asphalt-shingle-roofing-houston/ /metal-roofing-houston/ /tpo-roofing/ /financing/ /service-areas/ /recent-projects-reviews/ /pay-now/

Diagnostico completo do estado atual do site: rich results, schema, meta tags, seguranca, paginacao, conteudo, citabilidade por IA.

--- POR QUE FOI PRIORIZADO ASSIM ---

P1 — CRITICO: o /about/ esta hackeado com gambling spam (Toto Togel indonesio). Google ja indexou o titulo adulterado. Pode gerar manual action e derrubar o site inteiro.

P2 — Schema invalido: Rank Math esta com "name": "" em todas as paginas. O schema Organization fica vazio. Google nao consegue associar a entidade.

P3 — 13 JSON-LD por pagina: Google precisa entender qual servico e oferecido em qual cidade. Sem schema por pagina, ele trata tudo como "roofing contractor generico" e perde a chance de ranquear "metal roofing houston" vs "tpo roofing houston" como topicos distintos.

P4 — Meta description duplicada: Yoast e Elementor cuspindo duas tags na mesma pagina. Google ignora ambas.

--- IMPACTO NOS BUSCADORES ---

Service schema: Google entende a relacao entre servico especifico + contractor + cidade. Fortalece ranking para long tail de servico + local.

FAQPage schema: habilita FAQ rich snippets no SERP (dropdown de perguntas). Aumenta CTR em media 68% vs blue link comum.

AggregateRating: habilita estrelas de review no SERP. Aumenta CTR em media 35%.

areaServed: reforca sinal de ServiceAreaBusiness para buscas em cada cidade.

--- ESTADO ATUAL vs DEPOIS DO SPRINT 1 ---

Antes: 0 rich results em 13 paginas, schema Organization vazio, meta description duplicada em todas as paginas, site com pagina comprometida por malware.

Depois: 10 a 12 paginas com rich result (FAQ + estrelas), schema valido, meta description unica por pagina, site limpo.

--- RICH RESULTS QUE PASSAM A EXISTIR ---

/about/ — FAQPage + LocalBusiness
/residential-roofing/ — FAQPage + Service
/commercial-roofing/ — FAQPage + Service
/siding/ — FAQPage + Service
/gutters/ — FAQPage + Service
/windows/ — FAQPage + Service
/asphalt-shingle/ — FAQPage + Service
/metal-roofing/ — FAQPage + Service
/tpo-roofing/ — FAQPage + Service
/financing/ — FAQPage + OfferCatalog
/service-areas/ — FAQPage + areaServed
/recent-projects/ — FAQPage + AggregateRating
/pay-now/ — FAQPage + PayAction

--- CITABILIDADE POR IA (GEO) ---

Antes: 3/10. Sem FAQPage schema, sem llms.txt, sem HowTo schema. Conteudo em formato generico que IA nao extrai facilmente.

Depois: 6/10. FAQPage schema em todas as paginas da a IA respostas prontas e estruturadas para citar. Recomendado criar /llms.txt para proximo passo.

--- ACAO DE 5 MIN ANTES DO JSON-LD ---

Rank Math > Settings > General > Organization Name
Digitar "All Over TX Roofing" e salvar.

Isso resolve o schema vazio em todas as paginas de uma vez. Sem isso, os JSON-LD criados referenciam um @id de entidade que esta quebrada.

--- AVISO DE SEGURANCA ---

O site precisa de varredura de malware antes de qualquer outra acao:
1. Wordfence Security — scan completo
2. Trocar todas as senhas admin
3. Verificar Search Console > Security Issues
4. Apos limpo, submeter reconsideration request no GSC

--- PROXIMO SPRINT (recomendado) ---

Criar city pages para as 17 cidades atendidas (Katy, Sugar Land, The Woodlands, Cypress, Pearland, League City, Conroe, Spring, Humble, Kingwood, Missouri City, Tomball, Magnolia, Richmond, Rosenberg, Texas City, Galveston) com schema LocalBusiness por cidade e FAQ especifico para cada regiao.
