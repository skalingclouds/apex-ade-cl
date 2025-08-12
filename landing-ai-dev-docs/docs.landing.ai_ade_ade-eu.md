---
url: "https://docs.landing.ai/ade/ade-eu"
title: "European Union (EU) - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

General

European Union (EU)

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [GDPR and Compliance](https://docs.landing.ai/ade/ade-eu#gdpr-and-compliance)
- [Differences When Using the EU](https://docs.landing.ai/ade/ade-eu#differences-when-using-the-eu)
- [Create an Account in the EU](https://docs.landing.ai/ade/ade-eu#create-an-account-in-the-eu)
- [Get Your API Key for the EU](https://docs.landing.ai/ade/ade-eu#get-your-api-key-for-the-eu)
- [Call the API Directly in the EU](https://docs.landing.ai/ade/ade-eu#call-the-api-directly-in-the-eu)
- [Use the Library with the EU](https://docs.landing.ai/ade/ade-eu#use-the-library-with-the-eu)
- [Currency](https://docs.landing.ai/ade/ade-eu#currency)

Agentic Document Extraction is available in the European Union (EU).Agentic Document Extraction in the EU provides:

- **Data residency**: All data is stored and processed within the EU
- **GDPR compliance**: Coming soon
- **Regional performance**: Reduced latency for European users

## [​](https://docs.landing.ai/ade/ade-eu\#gdpr-and-compliance)  GDPR and Compliance

Refer to the resources below to learn more about GDPR and compliance.

[**Trust Center** \\
\\
The Trust Center is your central resource for accessing our security documentation, compliance reports, and real-time system status.](https://trust.landing.ai/) [**Security and Compliance** \\
\\
This page outlines our security posture, compliance with industry standards, and the measures we take to safeguard your data across our products and infrastructure.](https://landing.ai/security-at-landingai)

## [​](https://docs.landing.ai/ade/ade-eu\#differences-when-using-the-eu)  Differences When Using the EU

Using Agentic Document Extraction in the EU works the same as the default US deployment, with only a few key differences outlined in this article:

- [Create an account](https://docs.landing.ai/ade/ade-eu#create-an-account-in-the-eu): Use the EU URL
- [Get your API key](https://docs.landing.ai/ade/ade-eu#get-your-api-key-for-the-eu): Use the EU URL
- [Call the API directly](https://docs.landing.ai/ade/ade-eu#call-the-api-directly-in-the-eu): Use the EU endpoint
- [Use the library](https://docs.landing.ai/ade/ade-eu#use-the-library-with-the-eu): Set the EU endpoint as an environment variable
- [Currency](https://docs.landing.ai/ade/ade-eu#currency): All billing is in euros (EU)

### [​](https://docs.landing.ai/ade/ade-eu\#create-an-account-in-the-eu)  Create an Account in the EU

Create an account and access the Playground in the EU here: [https://va.eu-west-1.landing.ai/home](https://va.eu-west-1.landing.ai/home).

### [​](https://docs.landing.ai/ade/ade-eu\#get-your-api-key-for-the-eu)  Get Your API Key for the EU

To get your API key for the EU, go to [https://va.eu-west-1.landing.ai/settings/api-key](https://va.eu-west-1.landing.ai/settings/api-key).Use this API key when using the library or calling the API directly in the EU.API keys are deployment-specific. An API key created in the US will not work for the EU, and vice versa.

### [​](https://docs.landing.ai/ade/ade-eu\#call-the-api-directly-in-the-eu)  Call the API Directly in the EU

To ensure your API calls are processed in the EU, replace the default endpoint with the EU endpoint:

Copy

Ask AI

```
https://api.va.eu-west-1.landing.ai/v1/tools/agentic-document-analysis

```

### [​](https://docs.landing.ai/ade/ade-eu\#use-the-library-with-the-eu)  Use the Library with the EU

To ensure the [agentic-doc library](https://github.com/landing-ai/agentic-doc) connects to the EU deployment, set the endpoint environment variable before using the library:

Copy

Ask AI

```
export ENDPOINT_HOST=https://api.va.eu-west-1.landing.ai

```

### [​](https://docs.landing.ai/ade/ade-eu\#currency)  Currency

The EU uses euro (EUR) for all billing and pricing.

Was this page helpful?

YesNo

[Pricing](https://docs.landing.ai/ade/ade-pricing) [Support](https://docs.landing.ai/ade/ade-support)

Assistant

Responses are generated using AI and may contain mistakes.

\`;

 document.head.insertAdjacentHTML('afterbegin', gtmHeadHTML);
 }

 // Add GTM noscript to body
 function addGTMNoscript() {
 const gtmBodyHTML = \`\`;

 document.body.insertAdjacentHTML('afterbegin', gtmBodyHTML);
 }

 // Initialize GTM when DOM is ready
 function initializeGTM() {
 if (document.readyState === 'loading') {
 document.addEventListener('DOMContentLoaded', function() {
 addGTMScript();
 addGTMNoscript();
 });
 } else {
 addGTMScript();
 addGTMNoscript();
 }
 }

 // Initialize dataLayer if it doesn't exist
 window.dataLayer = window.dataLayer \|\| \[\];

 // Start initialization
 initializeGTM();
})();