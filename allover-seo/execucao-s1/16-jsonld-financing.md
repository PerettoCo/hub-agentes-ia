# JSON-LD — /financing/

## Estratégia
Financial page não tem schema pré-definido. Usar FAQ + Offer + Service com hasOfferCatalog.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/financing/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What financing options are available for roofing projects?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We offer flexible financing options through trusted partners, including low monthly payment plans, deferred interest options, and fixed-rate financing for qualified customers."
          }
        },
        {
          "@type": "Question",
          "name": "Do you offer 0% APR financing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we periodically offer promotional 0% APR financing for qualified applicants. Contact us for current promotional rates and terms."
          }
        },
        {
          "@type": "Question",
          "name": "Can I finance my roof replacement with no money down?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, many of our financing options require $0 down payment, making it possible to start your roofing project with no upfront cost."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/financing/#service",
      "name": "Roofing Financing Houston",
      "serviceType": "Financing Service",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Roofing Financing Options",
        "itemListElement": [
          {
            "@type": "Offer",
            "itemOffered": {
              "@type": "Service",
              "name": "Roof Financing"
            },
            "priceSpecification": {
              "@type": "PriceSpecification",
              "description": "Contact for current rates and terms"
            }
          }
        ]
      }
    }
  ]
}
```
