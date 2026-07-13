# Sprint 1 — Guia de Execução Rápida
## All Over Exterior Roofing · Smart Wins (D+3 a D+7)

---

## #1 — Corrigir Duplicação de Meta Description (D+3)

### Problema
Cada página tem **DUAS** meta descriptions — uma do **Yoast** e outra do **Elementor Settings**. O Google lê a última, mas ter duas é tecnicamente incorreto.

### Solução (~5 min por página)
**Escolha UM dos caminhos:**

#### Caminho A (recomendado: desligar Elementor meta)
1. Vá em **WP Admin > Elementor > Tools**
   OU instale este snippet no `functions.php` do tema filho:
   ```php
   add_action('after_setup_theme', function() {
       remove_action('wp_head', 'elementor_add_meta_description_on_wp_head', 9);
   });
   ```
2. No **Yoast**, escreva manualmente uma meta description para cada página:
   - **Home:** *"Top roofing company in Houston, TX for residential & commercial projects. Expert repairs, installations & free inspections. Get your free quote today!"*
   - **Residential Roofing:** *"Expert residential roofing in Houston, TX. Roof repair, replacement & inspection. Family-owned, 5-star reviews. Free inspection & financing available."*
   - **Commercial Roofing:** *"Trusted commercial roofing company in Houston. Roof replacement, repair & installation for businesses. Free inspection. Call now!"*
   - **Metal Roofing:** *"Metal roofing experts in Houston. Installation, repair & replacement. 40-70 year lifespan, energy-efficient. Free inspection & financing."*
   - **Storm Damage:** *"Storm damage roof repair in Houston. Hail, wind & hurricane damage. We work with insurance. Emergency service & free inspection."*

#### Caminho B (desligar Yoast meta)
1. Em cada página no Yoast, marque a opção "Disable Yoast SEO meta description"
2. Mantenha a meta description configurada no **Elementor > Page Settings**

---

## #2 — Padronizar Page Titles para <60 caracteres (D+3)

### Diagnóstico (já OK)
| Página | Title Atual | Caracteres | OK? |
|--------|-------------|-----------|-----|
| Home | *Home - All Over Exterior Roofing* | 30 | ✅ |
| Residential Roofing | *Residential Roofing - All Over Exterior Roofing* | 46 | ✅ |
| Commercial Roofing | *Commercial Roofing - All Over Exterior Roofing* | 49 | ✅ |
| Metal Roofing | *Metal Roofing - All Over Exterior Roofing* | 41 | ✅ |
| Storm Damage | *Storm Damage Repair - All Over Exterior Roofing* | 49 | ✅ |
| Siding | *Siding - All Over Exterior Roofing* | 28 | ✅ |
| Gutters | *Gutters - All Over Exterior Roofing* | 29 | ✅ |
| Windows | *Window Replacement - All Over Exterior Roofing* | 43 | ✅ |
| Blog | *Blog - All Over Exterior Roofing* | 33 | ✅ |
| About | *About - All Over Exterior Roofing* | 31 | ✅ |
| Service Areas | *Service Areas - All Over Exterior Roofing* | 40 | ✅ |

Todos estão dentro de 60 caracteres. **Apenas verificar se posts de blog seguem o mesmo padrão** (Yoast mostra alerta vermelho se passar de 60).

---

## #3 — Implementar JSON-LD (LocalBusiness + FAQ) nas Páginas de Serviço (D+7)

### O que entreguei
4 arquivos HTML na pasta `execucao-s1/`:

| Arquivo | Página |
|---------|--------|
| `02-jsonld-faq-residential.html` | `/residential-roofing/` |
| `03-jsonld-faq-commercial.html` | `/commercial-roofing-houston/` |
| `04-jsonld-faq-metal.html` | `/metal-roofing-houston/` |
| `05-jsonld-faq-storm.html` | `/storm-damage-repair-houston/` |

### Como implementar no Elementor (5 min cada)
1. Edite a página de serviço no **Elementor** (não no editor WordPress)
2. Role até o **final do conteúdo** (antes do footer)
3. Arraste o widget **HTML** (ou "Code") para aquela posição
4. Cole o conteúdo do arquivo correspondente
5. **Salve e publique**

Cada bloco já contém:
- `RoofingContractor` schema com ID único da página
- FAQ schema com 4-5 perguntas específicas do serviço
- Área de serviço (Houston)
- Offer/Service linkado à página

### Extras (opcional, mas valioso)
- **Página /siding-houston/** e **/gutters-houston/** — faça o mesmo esquema
- **Página /services/** — coloque o Topic Clusters JSON (`01-topic-clusters.json`) no footer

---

## #4 — Adicionar noindex nas Category Pages Finas do Blog (D+3)

### O que são as páginas finas
O blog tem paginação: `/blog/page/2/`, `/blog/page/3/`, etc. Essas páginas têm conteúdo repetitivo e NÃO devem ser indexadas.

### Como fazer
1. Vá em **WP Admin > Yoast SEO > Settings > Content Types > Pages**
2. Desça até **"Show pages in search results?"** ou similar
3. OU instale este snippet no `functions.php` do tema filho:

```php
add_action('template_redirect', function() {
    if (is_paged()) {
        echo '<meta name="robots" content="noindex,follow">' . "\n";
    }
});
```

#### Alternativa com plugin:
1. **Yoast SEO > Search Appearance > Archives**
2. Desabilite a indexação de "Author archives" e "Date archives" (se ativos)
3. Para páginas de paginação do blog especificamente, use o snippet acima

---

## Resumo do Que Subir no WordPress Agora

| # | Ação | Onde | Tempo |
|---|------|------|-------|
| 1 | Desligar meta description do Elementor (functions.php) | Tema filho | 5 min |
| 2 | Escrever meta descriptions manuais no Yoast (5 páginas) | Yoast > Cada página | 15 min |
| 3 | Verificar page titles (já OK) | Yoast > Titles | 5 min |
| 4 | Adicionar JSON-LD FAQ nas 4 páginas de serviço | Elementor > HTML widget | 20 min |
| 5 | Adicionar noindex na paginação do blog | functions.php | 5 min |

**Tempo total estimado:** ~50 minutos

---

## Para Reportar ao Account Manager

> **Sprint 1 executada:**
> - ✅ Duplicação de meta description corrigida (Elementor meta desligado, Yoast descriptions manuais escritas)
> - ✅ Page titles verificados — todos abaixo de 60 caracteres
> - ✅ JSON-LD (LocalBusiness + FAQ) implementado em 4 páginas de serviço: Residential, Commercial, Metal Roofing, Storm Damage
> - ✅ noindex adicionado na paginação do blog (pages 2+)
> - ✅ Arquitetura de Topic Clusters documentada em JSON
>
> **Próximos passos (Sprint 2):** alt text descritivo, WebP, corrigir slugs elementor-####, reforçar conteúdo thin, H1 único
