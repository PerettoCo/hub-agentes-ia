# JSON-LD — /residential-roofing/

## Estratégia
ServicePage → Service schema + FAQPage com perguntas específicas de residencial.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/residential-roofing/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "How long does a residential roof replacement take?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Most residential roof replacements take 1 to 3 days depending on the size of the home, roof complexity, and weather conditions. Our team works efficiently while maintaining quality."
          }
        },
        {
          "@type": "Question",
          "name": "What roofing materials do you offer for homes?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We offer asphalt shingles (architectural and 3-tab), metal roofing, tile, and slate-look options. We help homeowners choose the best material for their budget, style, and durability needs."
          }
        },
        {
          "@type": "Question",
          "name": "Do you work with insurance claims for roof damage?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we assist homeowners with insurance claims from start to finish. We help document damage, work with adjusters, and ensure you receive fair coverage for your roof replacement."
          }
        },
        {
          "@type": "Question",
          "name": "Is there a warranty on residential roofing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. We offer both manufacturer warranties (covering materials) and our workmanship warranty (covering installation). Typical coverage ranges from 10 to 50 years depending on the material."
          }
        },
        {
          "@type": "Question",
          "name": "Can you repair a roof instead of replacing it?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Absolutely. If the damage is localized and your roof is in good condition overall, we can perform targeted repairs. We always provide an honest assessment of whether repair or replacement makes more sense."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/residential-roofing/#service",
      "name": "Residential Roofing Houston",
      "serviceType": "Residential Roofing",
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
      "description": "Expert residential roofing services including roof replacement, repair, and installation for homes in Houston and throughout Texas. We work with asphalt shingles, metal, tile, and more."
    }
  ]
}
```
