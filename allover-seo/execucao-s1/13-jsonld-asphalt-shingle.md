# JSON-LD — /asphalt-shingle-roofing-houston/

## Estratégia
ServicePage → Service + FAQ específicas de shingle (sub-serviço de residencial).

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/asphalt-shingle-roofing-houston/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "What is the difference between 3-tab and architectural shingles?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "3-tab shingles are flat, uniform, and more budget-friendly, lasting about 20 years. Architectural shingles are dimensional, thicker, more durable, and last 30+ years. We typically recommend architectural for Houston homes."
          }
        },
        {
          "@type": "Question",
          "name": "Are asphalt shingles good for Texas weather?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. Modern architectural shingles are designed to withstand high winds (up to 130 mph), heavy rain, and extreme heat. Impact-resistant options are available for hail-prone areas."
          }
        },
        {
          "@type": "Question",
          "name": "How long does an asphalt shingle roof last in Houston?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "In the Houston climate, architectural shingles typically last 25 to 30 years, while 3-tab shingles last 15 to 20 years. Proper attic ventilation and regular maintenance help maximize lifespan."
          }
        },
        {
          "@type": "Question",
          "name": "Can I install asphalt shingles over my existing roof?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "In some cases, yes — but we typically recommend a full tear-off for best results. Removing old layers allows us to inspect the decking, install proper underlayment, and ensure the new roof performs as designed."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/asphalt-shingle-roofing-houston/#service",
      "name": "Asphalt Shingle Roofing Houston",
      "serviceType": "Asphalt Shingle Roofing",
      "serviceSubType": "Residential Roofing",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "areaServed": {
        "@type": "City",
        "name": "Houston"
      },
      "description": "Expert asphalt shingle roofing in Houston. We install architectural and 3-tab shingles with proper underlayment and ventilation for maximum durability in Texas weather."
    }
  ]
}
```
