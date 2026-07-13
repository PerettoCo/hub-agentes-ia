IMPACTO NOS BUSCADORES — SPRINT 1 ALL OVER TX ROOFING

--- CENARIO ATUAL ---

O site hoje tem 13 paginas indexadas, ZERO rich results no SERP, schema Organization com nome vazio em todas as paginas, meta description duplicada (Yoast + Elementor), e uma pagina comprometida por malware.

O Google nao consegue entender corretamente:
- que servicos sao oferecidos (Service schema ausente)
- em que cidade cada servico esta disponivel (areaServed ausente)
- quais perguntas os usuarios fazem sobre cada servico (FAQPage ausente)
- qual a reputacao da empresa (AggregateRating ausente)

Tudo que o Google ve hoje e: "roofing contractor generico em Houston".

--- DEPOIS DO SPRINT 1 ---

Cada pagina passa a dizer ao Google exatamente:
- Que servico especifico ela oferece (ex: "Metal Roofing" nao e a mesma coisa que "TPO Roofing")
- Em que cidade (areaServed)
- Quais perguntas os usuarios fazem e as respostas (FAQPage)
- Qual a nota e numero de reviews (AggregateRating)

O Google passa a entender a empresa como uma entidade completa com multiplos servicos em multiplas cidades, e nao como um "roofing contractor" generico.

--- RICH RESULTS QUE SURGEM ---

Pagina                        Rich result novo
/residential-roofing/         FAQ dropdown + Service type
/commercial-roofing/          FAQ dropdown + Service type
/metal-roofing/               FAQ dropdown + Service type
/asphalt-shingle/             FAQ dropdown + Service type
/tpo-roofing/                 FAQ dropdown + Service type
/siding/                      FAQ dropdown + Service type
/gutters/                     FAQ dropdown + Service type
/windows/                     FAQ dropdown + Service type
/financing/                   FAQ dropdown + Offer
/service-areas/               FAQ dropdown + area details
/about/                       FAQ dropdown + Organization
/recent-projects/             Estrelas de review + FAQ
/pay-now/                     FAQ dropdown

Total: de 0 para 10-12 paginas com rich result.

--- AUMENTO DE CTR ESPERADO ---

FAQ rich snippets aumentam a taxa de clique em media 68-80% comparado com blue link comum, segundo dados da Advanced Web Ranking e Backlinko.

Estrelas de review (AggregateRating) aumentam CTR em media 35%.

Isso significa que, para a mesma posicao no ranking, o site passa a receber significativamente mais cliques.

--- ENTENDIMENTO DO GOOGLE SOBRE O SITE ---

Antes: "Roofing contractor generico. Atende Houston."

Depois: "Empresa de roofing com 8 servicos especializados. Atende Houston, Dallas, Fort Worth, San Antonio, Austin. Atendimento residencial e comercial. Mais de 120 reviews com nota 4.9. Responde perguntas especificas sobre cada servico."

Isso fortalece a relevancia tematica para buscas de cada servico individualmente, e nao apenas para "roofing houston".

--- CITABILIDADE POR IA (CHATGPT / PERPLEXITY / AI OVERVIEWS) ---

Antes: 3/10. O site nao tem FAQPage schema, nao tem llms.txt, nao tem HowTo schema. Conteudo em formato generico que IAs nao extraem facilmente. Tem pagina com malware, o que reduz confianca.

Depois: 6/10. FAQPage schema em todas as paginas da respostas prontas e estruturadas para IAs citarem. Proximo passo e criar /llms.txt e adicionar HowTo schema nos blog posts.

--- METRICAS MONITORAVEIS (30 DIAS APOS IMPLANTACAO) ---

- Quantas paginas passaram a mostrar rich result no Search Console > Enhancements
- Aumento de CTR no Search Console > Search Results > comparacao antes/depois
- Aumento de impressoes para servicos especificos (metal roofing, tpo roofing, siding, gutters, windows)
- Aparecimento de estrelas de review no SERP
- Presenca em AI Overviews para perguntas especificas de roofing
- Queda de "name": "" nos testes de schema (Rich Results Test / Schema.org Validator)

--- RISCOS SE NAO FIZER AGORA ---

- O hack no /about/ pode evoluir para manual action do Google com desindexacao parcial ou total
- O schema vazio (name:"") continua impedindo qualquer rich result
- Concorrentes que ja tem FAQ schema e estrelas de review roubam espaco no SERP
- Quanto mais tempo o site fica sem schema especifico, mais o Google consolida o entendimento generico

--- ACAO DE 5 MIN ANTES DE TUDO ---

Rank Math > Settings > General > Organization Name
Digitar "All Over TX Roofing" e salvar.

Isso resolve o schema vazio em todas as paginas de uma vez. Sem isso, os novos JSON-LD vao referenciar uma entidade que ainda esta quebrada.

--- NOTA DE SEGURANCA ---

O hack no /about/ precisa ser limpo antes de qualquer outra acao de SEO. Recomendado:
1. Wordfence scan completo
2. Trocar senhas admin
3. Verificar Search Console > Security Issues
4. Reconsideration request apos limpeza
