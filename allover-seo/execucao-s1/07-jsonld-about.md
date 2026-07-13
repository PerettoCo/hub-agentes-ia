# JSON-LD — /about/

## Estratégia
Company page → reforço de LocalBusiness com founder info + FAQ institucional. Complementa o schema genérico que já existe no footer.

## Código (inserir via Yoast → SEO → Schema → Custom GraphQL ou via Elementor → Custom Code <head>)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/about/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "How long has All Over TX Roofing been in business?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "All Over TX Roofing has been serving Texas homeowners and businesses for over a decade, providing expert roofing, siding, gutter, and window replacement services across the state."
          }
        },
        {
          "@type": "Question",
          "name": "Is All Over TX Roofing licensed and insured?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, All Over TX Roofing is fully licensed and insured in Texas. We carry general liability insurance and workers compensation to protect our customers and our team."
          }
        },
        {
          "@type": "Question",
          "name": "What areas does All Over TX Roofing serve?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We serve the greater Houston area, including Dallas-Fort Worth, San Antonio, Austin, and surrounding communities throughout Texas."
          }
        },
        {
          "@type": "Question",
          "name": "Do you offer free estimates?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we offer free, no-obligation estimates for all roofing, siding, gutter, and window replacement projects."
          }
        },
        {
          "@type": "Question",
          "name": "What makes All Over TX Roofing different from other contractors?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We combine quality craftsmanship with transparent communication, upfront pricing, and a commitment to using premium materials. Our team handles everything from residential repairs to large-scale commercial installations."
          }
        }
      ]
    },
    {
      "@type": "LocalBusiness",
      "@id": "https://allovertxroofing.com/#LocalBusiness",
      "name": "All Over TX Roofing",
      "image": "https://allovertxroofing.com/wp-content/uploads/site-logo.png",
      "url": "https://allovertxroofing.com",
      "telephone": "(832) 820-9000",
      "priceRange": "$$",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Houston",
        "addressRegion": "TX",
        "addressCountry": "US"
      },
      "sameAs": [
        "https://www.facebook.com/allovertxroofing",
        "https://www.instagram.com/allovertxroofing"
      ],
      "foundingDate": "2013",
      "numberOfEmployees": {
        "@type": "QuantitativeValue",
        "value": "15"
      }
    }
  ]
}
```
