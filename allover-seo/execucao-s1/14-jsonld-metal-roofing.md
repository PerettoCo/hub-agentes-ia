# JSON-LD — /metal-roofing-houston/

## Estratégia
ServicePage → Service + FAQ específicas de metal.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/metal-roofing-houston/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What types of metal roofing do you install?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We install standing seam metal roofs, metal shingles, and corrugated metal panels in steel, aluminum, and copper. Standing seam is the most popular for residential applications due to its clean look and durability."
          }
        },
        {
          "@type": "Question",
          "name": "How long does a metal roof last?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Metal roofs typically last 40 to 70 years depending on the material. Steel with proper coatings lasts 40-50 years, aluminum 50-60 years, and copper 70+ years."
          }
        },
        {
          "@type": "Question",
          "name": "Is a metal roof louder in the rain?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "With proper insulation and attic ventilation, a metal roof is not significantly louder than other materials. The solid decking and insulation dampen sound effectively."
          }
        },
        {
          "@type": "Question",
          "name": "Does a metal roof increase home value?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. Metal roofs typically offer a high return on investment (up to 85%+ according to Remodeling Magazine), lower insurance premiums, and energy savings that appeal to homebuyers."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/metal-roofing-houston/#service",
      "name": "Metal Roofing Houston",
      "serviceType": "Metal Roofing",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": {
        "@type": "City",
        "name": "Houston"
      },
      "description": "Premium metal roofing installation in Houston. Standing seam, metal shingles, and corrugated panels in steel, aluminum, and copper for residential and commercial properties."
    }
  ]
}
```
