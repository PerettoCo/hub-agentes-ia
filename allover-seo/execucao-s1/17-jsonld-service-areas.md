# JSON-LD — /service-areas/

## Estratégia
ServiceAreas → reforçar LocalBusiness com areaServed expandida.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/service-areas/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Does All Over TX Roofing serve Dallas-Fort Worth?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we provide roofing services in Dallas, Fort Worth, and the surrounding DFW metroplex."
          }
        },
        {
          "@type": "Question",
          "name": "Do you serve San Antonio and Austin?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we offer full roofing services in San Antonio, Austin, and the corridor between them."
          }
        },
        {
          "@type": "Question",
          "name": "What areas in Greater Houston do you cover?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We serve all of Greater Houston including Katy, Sugar Land, The Woodlands, Conroe, Pearland, League City, Cypress, Spring, Humble, Kingwood, Missouri City, and all surrounding communities."
          }
        }
      ]
    },
    {
      "@type": "LocalBusiness",
      "@id": "https://allovertxroofing.com/#LocalBusiness",
      "areaServed": [
        {
          "@type": "City",
          "name": "Houston"
        },
        {
          "@type": "City",
          "name": "Dallas"
        },
        {
          "@type": "City",
          "name": "Fort Worth"
        },
        {
          "@type": "City",
          "name": "San Antonio"
        },
        {
          "@type": "City",
          "name": "Austin"
        }
      ]
    }
  ]
}
```
