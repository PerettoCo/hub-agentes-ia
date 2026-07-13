# JSON-LD — /commercial-roofing-houston/

## Estratégia
ServicePage → Service + FAQ específicas de roof plano/TPO/PVC, manutenção comercial.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/commercial-roofing-houston/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What types of commercial roofing do you install?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We install TPO, PVC, EPDM, modified bitumen, and metal roofing systems for commercial buildings. Each system is selected based on the building's structure, usage, and budget."
          }
        },
        {
          "@type": "Question",
          "name": "How often should a commercial roof be inspected?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We recommend commercial roof inspections at least twice a year — once in spring and once in fall — plus after any major storm. Regular inspections extend roof life and catch issues early."
          }
        },
        {
          "@type": "Question",
          "name": "Do you offer commercial roof maintenance programs?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we offer routine maintenance programs for commercial properties including inspections, debris removal, minor repairs, and documentation for warranty compliance."
          }
        },
        {
          "@type": "Question",
          "name": "What is the lifespan of a commercial roof?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Depending on the system, commercial roofs last between 15 and 30 years. TPO and PVC typically last 20-25 years, metal 30+ years, and modified bitumen 15-20 years."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/commercial-roofing-houston/#service",
      "name": "Commercial Roofing Houston",
      "serviceType": "Commercial Roofing",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": [
        {
          "@type": "City",
          "name": "Houston"
        },
        {
          "@type": "State",
          "name": "Texas"
        }
      ],
      "description": "Full-service commercial roofing in Houston including TPO, PVC, metal, and modified bitumen installations, repairs, and maintenance programs for office buildings, warehouses, and retail spaces."
    }
  ]
}
```
