# JSON-LD — /gutters-houston/

## Estratégia
ServicePage → Service (Gutter) + FAQ específicas.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/gutters-houston/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What types of gutters do you install?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We install seamless aluminum gutters in a variety of colors and sizes, as well as copper gutters for premium applications. All gutters are custom-formed on-site for a perfect fit."
          }
        },
        {
          "@type": "Question",
          "name": "Do you install gutter guards?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we offer gutter guard and leaf protection systems to reduce maintenance and prevent clogs. Options include mesh screens, reverse-curve systems, and foam inserts."
          }
        },
        {
          "@type": "Question",
          "name": "How do I know if my gutters need replacing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Signs include visible cracks, rust spots, separated seams, sagging sections, water pooling around the foundation, or gutters pulling away from the fascia."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/gutters-houston/#service",
      "name": "Gutter Installation Houston",
      "serviceType": "Gutter Installation",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": {
        "@type": "City",
        "name": "Houston"
      },
      "description": "Custom seamless gutter installation, gutter guard systems, and gutter repair services in Houston. We work with aluminum and copper materials to protect your home's foundation."
    }
  ]
}
```
