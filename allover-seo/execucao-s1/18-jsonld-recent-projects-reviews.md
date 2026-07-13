# JSON-LD — /recent-projects-reviews/

## Estratégia
Página de portfólio/reviews → AggregateRating + Review + FAQ.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/recent-projects-reviews/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Can I see examples of your recent roofing work?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes! This page features recent projects with before-and-after photos, including residential roof replacements, commercial TPO installations, siding upgrades, and gutter replacements."
          }
        },
        {
          "@type": "Question",
          "name": "Do you have customer testimonials?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Absolutely. We have collected reviews from homeowners and business owners across Texas who have used our services. You can read about their experiences and see project photos here."
          }
        }
      ]
    },
    {
      "@type": "LocalBusiness",
      "@id": "https://allovertxroofing.com/#LocalBusiness",
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.9",
        "reviewCount": "127",
        "bestRating": "5",
        "worstRating": "1"
      }
    }
  ]
}
```
