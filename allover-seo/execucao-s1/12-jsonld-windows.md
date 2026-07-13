# JSON-LD — /window-replacement-houston/

## Estratégia
ServicePage → Service (Window Replacement) + FAQ.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/window-replacement-houston/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What types of windows do you offer?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We offer double-hung, casement, sliding, bay, bow, and picture windows in vinyl, wood, and fiberglass frames. Energy-efficient double-pane and triple-pane glass options are available."
          }
        },
        {
          "@type": "Question",
          "name": "How long does window replacement take?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Most window replacements take 30 to 60 minutes per window. A full home installation is typically completed in 1 to 3 days depending on the number of windows."
          }
        },
        {
          "@type": "Question",
          "name": "Will new windows really lower my energy bills?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. ENERGY STAR certified windows can lower household energy bills by an average of 12%. Modern windows with Low-E coatings and gas fills provide superior insulation versus single-pane units."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/window-replacement-houston/#service",
      "name": "Window Replacement Houston",
      "serviceType": "Window Replacement",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": {
        "@type": "City",
        "name": "Houston"
      },
      "description": "Energy-efficient window replacement in Houston. We install double-hung, casement, sliding, bay, and picture windows with vinyl, wood, and fiberglass frames."
    }
  ]
}
```
