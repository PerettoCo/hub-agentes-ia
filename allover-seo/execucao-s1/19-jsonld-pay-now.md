# JSON-LD — /pay-now/

## Estratégia
Página transacional → minimal — apenas ServeAction + referência à LocalBusiness.

## Código

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "FAQPage",
      "@id": "https://allovertxroofing.com/pay-now/#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "How do I make a payment to All Over TX Roofing?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "You can make a secure online payment through this page using a credit card or debit card. We accept Visa, Mastercard, American Express, and Discover."
          }
        },
        {
          "@type": "Question",
          "name": "Is online payment secure?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes. Our payment page uses industry-standard SSL encryption to protect your information."
          }
        }
      ]
    },
    {
      "@type": "Service",
      "@id": "https://allovertxroofing.com/pay-now/#service",
      "name": "Online Payment",
      "serviceType": "Payment Processing",
      "provider": {
        "@id": "https://allovertxroofing.com/#LocalBusiness"
      },
      "potentialAction": {
        "@type": "PayAction",
        "target": "https://allovertxroofing.com/pay-now/"
      }
    }
  ]
}
```
