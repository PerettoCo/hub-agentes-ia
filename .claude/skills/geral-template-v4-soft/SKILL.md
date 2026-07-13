---
name: geral-template-v4-soft
description: Gera reports HTML internos no padrao visual V4 Company (vermelho + dourado + Ubuntu). Use quando o usuario quiser criar um report, relatorio, dashboard, overview, analise, prestacao de contas, ou qualquer documento interno que precise do visual padrao V4. Tambem acione quando o usuario disser "faz igual ao report da Conserva", "mesmo padrao do relatorio de check-in", "visual V4", "padrao de report", "template de relatorio", ou der a entender que quer um documento formatado no estilo V4 — mesmo que nao cite explicitamente "report" ou "template". Cobre: reports de check-in, SEO audit, performance ads, OKRs, overview de cliente, analise de dados, e qualquer consolidado interno.
area: geral
author: Marcos Luciano Rodrigues Vieira
version: 1.0.0
---
# Template V4 Soft — Gerador de Reports HTML

Gera reports HTML completos no padrao visual V4 Company. O report e um unico HTML autonomo (sem dependencias externas alem da font Google), pronto para ser aberto no navegador ou publicado no GitHub Pages.

## Padrao Visual V4

### Identidade Visual

```
Fonte corpo:      Ubuntu (Google Fonts)
Fonte titulo:     Plus Jakarta Sans (Google Fonts, pesos 600-800)
Fonte dados:      JetBrains Mono (opcional, para KPIs/tabelas)

Vermelho:         --red: rgb(229, 9, 20)
                  --red-dark: rgb(180, 7, 16)
Dourado:          --gold: #c9a96e
                  --gold-light: #f5f0e6
                  --gold-border: #e8dcc8
Cinzas:           --gray-50 a --gray-900 (#fafafa → #212121)
Background page:  #f8f7f4
Cores semaforo:   --green: #1a8a3f | --amber: #c97d0e | --blue: #1a4a8c
```

### Estrutura do Report

1. **Cover** — fundo escuro gradiente (`#0d0d0d → #2a2a2a`), label tipo tag, titulo grande, subtitulo, metadados (periodo, autor, cliente). Linha dourada fina no topo e barra dourada abaixo do titulo.

2. **Cards** — sections em fundo branco com `border-radius: 16px` e `box-shadow`. Headers com gradiente vermelho (da esquerda pra direita) + icone + titulo branco. Body com padding 28px.

3. **KPIs** — grid de cards pequenos com borda superior colorida. Valor em fonte bold grande, label em uppercase pequeno.

4. **Timeline** — linha vertical a esquerda com marcadores circulares vermelhos. Datas em dourado. Titulos em negrito.

5. **Tabelas** — cabecalho escuro (`--gray-900`), linhas alternadas clean, hover no body.

6. **Download card** — fundo escuro com borda gradiente dourado-vermelho-dourado no topo. CTA dourado.

7. **Tags** — badges pequenos estilo `display: inline-block` com background colorido suave.

### Mobile

- Cover: padding reduzido, font-size 28px
- KPI grid: 2 colunas em <768px, 1 coluna em <480px
- Container: padding lateral 16px

## Como usar

### Entrada

O usuario fornece:
- **Cliente/projeto** — nome do cliente ou projeto
- **Tipo de report** — check-in, SEO, performance ads, OKR, overview, etc.
- **Dados** — pode ser descritivo (falando o que entrou) ou ja estruturado (tabelas, timeline, KPIs)
- **Periodo** — datas de cobertura

### Processo

1. Extraia os dados mais importantes da conversa ou dos arquivos mencionados
2. Identifique quais secoes sao relevantes para este tipo de report:
   - **Sempre**: cover, pelo menos 2 cards de conteudo
   - **Opcional**: KPIs, timeline, tabela de dados, download card, tags, proximos passos
   - **Nao inclua** secoes que nao tem dados para preencher
3. Monte o HTML com o CSS inline padrao V4

### Regras de estilo

- Nao adicione comentarios no HTML
- Use `pt-BR` como lang
- Mantenha `#f8f7f4` como background do body
- Cores sempre via CSS custom properties (var(--red), var(--gold), etc.)
- Links para GitHub Pages quando aplicavel
- Se houver download de arquivos, use GitHub Release como CDN, nunca link local
- Footer: "Report gerado em {data} · V4 Company"

## Dependencias

- Conexao com internet (Google Fonts CDN)
- `gh` CLI para criar releases (se for publicar)

## Exemplo

**Input do usuario:**
"Faz um report de check-ins da Conserva igual ao que a gente fez, de Out/25 a Mai/26"

**Output esperado:**
HTML completo com cover escuro, KPI cards (44 arquivos, 8 meses, etc.), timeline dividida em 6 fases, tabela de orcamento com evidencias, tabela de temas recorrentes, pontos de atencao, proximos passos, e footer. Link de download pro ZIP dos arquivos via GitHub Release.
