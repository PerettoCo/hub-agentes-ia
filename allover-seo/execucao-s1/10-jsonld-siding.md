# JSON-LD — /siding-houston/

## Estratégia
ServicePage → Service (Siding) + FAQ específicas de revestimento.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/siding-houston/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What siding materials do you offer?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We offer vinyl siding, fiber cement (HardiePlank), engineered wood (LP SmartSide), and metal siding. Each option provides different benefits in durability, maintenance, and curb appeal."
          }
        },
        {
          "@type": "Question",
          "name": "How long does siding installation take?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Most residential siding installations take 3 to 7 days depending on the home size, material chosen, and complexity of the architecture."
          }
        },
        {
          "@type": "Question",
          "name": "Does new siding improve energy efficiency?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. Modern siding with proper insulation can significantly reduce energy loss, lower heating and cooling costs, and help regulate indoor temperatures year-round."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/siding-houston/#service",
      "name": "Siding Installation Houston",
      "serviceType": "Siding Installation",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": {
        "@type": "City",
        "name": "Houston"
      },
      "description": "Professional siding installation and replacement in Houston. We install vinyl, fiber cement, engineered wood, and metal siding for residential and commercial properties."
    }
  ]
}
```
