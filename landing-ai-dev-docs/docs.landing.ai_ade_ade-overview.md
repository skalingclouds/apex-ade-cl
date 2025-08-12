---
url: "https://docs.landing.ai/ade/ade-overview"
title: "Overview - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Get Started

Overview

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Try Out Agentic Document Extraction](https://docs.landing.ai/ade/ade-overview#try-out-agentic-document-extraction)
- [Features](https://docs.landing.ai/ade/ade-overview#features)
- [Introduction from Andrew Ng](https://docs.landing.ai/ade/ade-overview#introduction-from-andrew-ng)

The Agentic Document Extraction API extracts structured data from unstructured documents like PDFs and images. It identifies elements such as text, tables, and form fields, and returns them in hierarchical JSON with exact page and coordinate references.Agentic Document Extraction understands relationships between elements, like captions linked to images, and works without templates or training.Beyond parsing, Agentic Document Extraction supports [schema-based extraction](https://docs.landing.ai/ade/ade-extract) to pull specific data fields from your documents, and [document classification](https://docs.landing.ai/ade/ade-extract#classification) to extract different sets of data based on document type.The extracted data can be used in downstream applications such as retrieval-augmented generation (RAG), search, or other custom workflows.

## [​](https://docs.landing.ai/ade/ade-overview\#try-out-agentic-document-extraction)  Try Out Agentic Document Extraction

[**Playground** \\
\\
Just getting started? Test out your documents in our demo app.](https://va.landing.ai/demo/doc-extraction) [**Library** \\
\\
Use our Python library to build custom scripts.](https://github.com/landing-ai/agentic-doc)

[**API** \\
\\
Call the API directly for language flexibility and advanced customization.](https://docs.landing.ai/api-reference/tools/agentic-document-extraction)

## [​](https://docs.landing.ai/ade/ade-overview\#features)  Features

- **Layout-agnostic parsing**: Extracts data from complex layouts. No training or templates needed.
- **Element detection**: Identifies specific elements including text, tables, form fields, checkboxes, and more.
- **Understands hierarchical relationships**: Detects how elements relate in structure and meaning. For example, can understand that a line of text is the caption for an image.
- **Precision extraction**: Extracts data accurately, even from complex documents.
- **Flexible output**: Returns results in Markdown and JSON, ready for use in downstream applications like retrieval-augmented generation (RAG).
- **Visual grounding**: The JSON output includes the document, page, and coordinate-level references for each element to support traceability, validation, and compliance workflows.
- **Supports multiple file types**: Can extract data from PDFs and common image formats.

## [​](https://docs.landing.ai/ade/ade-overview\#introduction-from-andrew-ng)  Introduction from Andrew Ng

Agentic Document Extraction \| Intelligent Document Understanding with Visual Context - YouTube

[Photo image of LandingAI](https://www.youtube.com/channel/UCYQS3jkfB79Diyr9sQJAj5Q?embeds_referring_euri=https%3A%2F%2Fdocs.landing.ai%2F)

LandingAI

10.3K subscribers

[Agentic Document Extraction \| Intelligent Document Understanding with Visual Context](https://www.youtube.com/watch?v=Yrj3xqh3k6Y)

LandingAI

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

Full screen is unavailable. [Learn More](https://support.google.com/youtube/answer/6276924)

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

More videos

## More videos

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=Yrj3xqh3k6Y&embeds_referring_euri=https%3A%2F%2Fdocs.landing.ai%2F)

0:00

0:00 / 2:46
•Live

•

Was this page helpful?

YesNo

[Quickstart](https://docs.landing.ai/ade/ade-quickstart)

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