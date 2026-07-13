# Implementação: Organization + BreadcrumbList Schema Global

**Cliente:** Metal Indianápolis
**Prioridade:** #5 (Fase 0 — Pré-Lançamento)
**Responsável:** Dev WP
**Esforço estimado:** 4 h

---

## Opção 1 — Rank Math SEO (recomendada, ~30 min)

Plugin mais simples, já faz os dois automaticamente.

### Organization
1. Ir em **Rank Math > Titles & Meta > Local SEO**
2. Marcar `Organization` como schema padrão
3. Preencher:
   - **Nome:** `Metal Indianápolis`
   - **Logo:** fazer upload da logo
   - **URL:** `https://www.metalindianapolis.com.br` (site do cliente)
   - **Redes sociais:** Instagram, Facebook, YouTube da Metal Indianápolis

### BreadcrumbList
1. Ir em **Rank Math > Titles & Meta > Breadcrumbs**
2. Ativar `Enable breadcrumbs`
3. Marcar `Add breadcrumbs in schema markup`
4. Adicionar `<?php rank_math_the_breadcrumb(); ?>` no `header.php` do tema (onde quiser exibir visualmente)

---

## Opção 2 — functions.php (sem plugin, ~1 h)

Sem plugin adicional. Colar no `functions.php` do tema ativo.

### Organization (global, todas as páginas)

```php
add_action('wp_head', function () {
    $org = [
        '@context' => 'https://schema.org',
        '@type'    => 'Organization',
        'name'     => 'Metal Indianápolis',
        'url'      => get_site_url(),
        'logo'     => get_template_directory_uri() . '/assets/images/logo.png',
        'contactPoint' => [
            '@type'       => 'ContactPoint',
            'telephone'   => '+55-11-4649-7722',
            'contactType' => 'customer service',
            'areaServed'  => 'BR',
        ],
        'sameAs' => [
            'https://share.google/YlnhUXjYAAuAoSuuR',
        ],
    ];

    echo '<script type="application/ld+json">'
        . json_encode($org, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)
        . '</script>' . "\n";
});
```

### BreadcrumbList (com Yoast Breadcrumbs)

Se o Yoast SEO estiver instalado:

```php
add_action('wp_head', function () {
    if (!function_exists('yoast_breadcrumb')) return;

    // Pega os breadcrumbs em array via filter
    $crumbs = array_filter((array) apply_filters('wpseo_breadcrumb_links', []));
    if (empty($crumbs)) return;

    $list = [];
    $i = 1;
    foreach ($crumbs as $crumb) {
        $item = [
            '@type'    => 'ListItem',
            'position' => $i,
            'name'     => wp_strip_all_tags($crumb['text']),
        ];
        if (!empty($crumb['url'])) {
            $item['item'] = $crumb['url'];
        }
        $list[] = $item;
        $i++;
    }

    $breadcrumb = [
        '@context'        => 'https://schema.org',
        '@type'           => 'BreadcrumbList',
        'itemListElement' => $list,
    ];

    echo '<script type="application/ld+json">'
        . json_encode($breadcrumb, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)
        . '</script>' . "\n";
});
```

### BreadcrumbList (com WooCommerce Breadcrumbs)

Se for loja WooCommerce sem Yoast:

```php
add_action('wp_head', function () {
    if (!class_exists('WooCommerce')) return;

    add_filter('woocommerce_get_breadcrumb', function ($crumbs) {
        if (empty($crumbs)) return $crumbs;

        $list = [];
        $i = 1;
        global $wp;
        $current_url = home_url(add_query_arg([], $wp->request));

        foreach ($crumbs as $crumb) {
            $item = [
                '@type'    => 'ListItem',
                'position' => $i,
                'name'     => wp_strip_all_tags($crumb[0]),
            ];
            if (!empty($crumb[1])) {
                $item['item'] = $crumb[1];
            }
            $list[] = $item;
            $i++;
        }

        // Último item (página atual) sem link
        $list[] = [
            '@type'    => 'ListItem',
            'position' => $i,
            'name'     => wp_strip_all_tags(end($crumbs)[0]),
        ];

        $breadcrumb = [
            '@context'        => 'https://schema.org',
            '@type'           => 'BreadcrumbList',
            'itemListElement' => $list,
        ];

        echo '<script type="application/ld+json">'
            . json_encode($breadcrumb, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)
            . '</script>' . "\n";

        return $crumbs;
    });
});
```

---

## Validação

Depois de implementar, testar:

1. **Google Rich Results Test** — https://search.google.com/test/rich-results
2. **Schema.org Validator** — https://validator.schema.org
3. **GSC > Enhancements > Breadcrumbs** — acompanhar impressões do rich result

---

## Checklist

- [ ] Nome e logo da Metal Indianápolis corretos no Organization
- [ ] URL canônica correta
- [ ] Telefone real do contato
- [ ] Breadcrumb reflete a hierarquia real do site (Home > Categoria > Produto)
- [ ] Nenhum placeholder ou lero-lero no JSON-LD
- [ ] Testado no Rich Results Test antes de subir em produção
