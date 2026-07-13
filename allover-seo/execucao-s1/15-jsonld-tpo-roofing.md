# JSON-LD — /tpo-roofing/

## Estratégia
ServicePage → Service + FAQ específicas de TPO (sub-serviço de comercial).

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/tpo-roofing/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is TPO roofing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "TPO (Thermoplastic Polyolefin) is a single-ply roofing membrane known for its energy efficiency, durability, and heat-reflective properties. It is one of the most popular commercial roofing systems in Texas."
          }
        },
        {
          "@type": "Question",
          "name": "How long does a TPO roof last?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "A properly installed TPO roof typically lasts 20 to 25 years. Regular inspections and prompt repairs help maximize its lifespan."
          }
        },
        {
          "@type": "Question",
          "name": "Is TPO roofing energy efficient?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. TPO membranes are highly reflective, reducing heat absorption and lowering cooling costs. Many TPO roofs qualify for ENERGY STAR certification and can reduce energy bills by up to 30%."
          }
        },
        {
          "@type": "Question",
          "name": "Can TPO be installed over existing roofing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "In some retrofit applications, TPO can be installed over existing roofing. However, we typically recommend removal of old materials to inspect the deck and ensure proper installation and warranty coverage."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/tpo-roofing/#service",
      "name": "TPO Roofing Houston",
      "serviceType": "TPO Roofing",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": {
        "@type": "City",
        "name": "Houston"
      },
      "description": "Professional TPO roofing installation and repair in Houston. Energy-efficient, durable single-ply roofing for commercial and industrial buildings."
    }
  ]
}
```
