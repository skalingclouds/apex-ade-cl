---
url: "https://docs.landing.ai/ade/ade-changelog"
title: "Changelog - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Updates

Changelog

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [July 21, 2025: Confidence Score](https://docs.landing.ai/ade/ade-changelog#july-21%2C-2025%3A-confidence-score)
- [July 17, 2025: European Union Availability](https://docs.landing.ai/ade/ade-changelog#july-17%2C-2025%3A-european-union-availability)
- [July 9, 2025: agentic-doc v0.3.0](https://docs.landing.ai/ade/ade-changelog#july-9%2C-2025%3A-agentic-doc-v0-3-0)
- [June 6, 2025: agentic-doc v0.2.4](https://docs.landing.ai/ade/ade-changelog#june-6%2C-2025%3A-agentic-doc-v0-2-4)
- [May 29, 2025: agentic-doc v0.2.3](https://docs.landing.ai/ade/ade-changelog#may-29%2C-2025%3A-agentic-doc-v0-2-3)
- [May 20, 2025: agentic-doc v0.2.1](https://docs.landing.ai/ade/ade-changelog#may-20%2C-2025%3A-agentic-doc-v0-2-1)
- [May 14, 2025](https://docs.landing.ai/ade/ade-changelog#may-14%2C-2025)

[​](https://docs.landing.ai/ade/ade-changelog#july-21%2C-2025%3A-confidence-score)

July 21, 2025: Confidence Score

## [​](https://docs.landing.ai/ade/ade-changelog\#confidence-score-for-schema-based-extraction)  Confidence Score for Schema-Based Extraction

The [field extraction](https://docs.landing.ai/ade/ade-extract) results now include a **confidence score** for each extracted field. This score indicates how certain Agentic Document Extraction is about the accuracy of the extracted data.For detailed information about how to get the confidence score, go to [Confidence Scores](https://docs.landing.ai/ade/ade-extract-confidence-score).

[​](https://docs.landing.ai/ade/ade-changelog#july-17%2C-2025%3A-european-union-availability)

July 17, 2025: European Union Availability

## [​](https://docs.landing.ai/ade/ade-changelog\#agentic-document-extraction-now-available-in-europe)  Agentic Document Extraction Now Available in Europe

Agentic Document Extraction is now available in Europe. To learn more, go to [European Union (EU)](https://docs.landing.ai/ade/ade-eu).Agentic Document Extraction in the EU provides:

- **Data residency**: All data is stored and processed within the EU
- **GDPR compliance**: Coming soon; learn more at our [Security and Data](https://landing.ai/security-at-landingai) page
- **Regional performance**: Reduced latency for European users

[​](https://docs.landing.ai/ade/ade-changelog#july-9%2C-2025%3A-agentic-doc-v0-3-0)

July 9, 2025: agentic-doc v0.3.0

## [​](https://docs.landing.ai/ade/ade-changelog\#manage-settings-with-parseconfig)  Manage Settings with ParseConfig

The [agentic-doc library](https://github.com/landing-ai/agentic-doc) v0.3.0 introduces the `ParseConfig` class for the `parse` function. This allows you to pass multiple settings (like `api_key`, `include_marginalia`, and `extraction_model`) in a single `ParseConfig` object.For detailed information, go to [Pass Settings with ParseConfig](https://docs.landing.ai/ade/ade-parseconfig).You can now pass settings, like the API key, to the `parse` function using the new `ParseConfig` class.

## [​](https://docs.landing.ai/ade/ade-changelog\#upcoming-deprecation%3A-settings-class)  Upcoming Deprecation: Settings Class

Setting values directly on `agentic_doc.config.settings` will be deprecated in a future release. Configure settings with `ParseConfig` instead.

[​](https://docs.landing.ai/ade/ade-changelog#june-6%2C-2025%3A-agentic-doc-v0-2-4)

June 6, 2025: agentic-doc v0.2.4

## [​](https://docs.landing.ai/ade/ade-changelog\#load-bytes)  Load Bytes

In addition to supporting PDFs and images, the `parse` function now supports raw bytes from PDF and image files.For more information, go to [Sample Script: Parse Files from Bytes](https://docs.landing.ai/ade/ade-parse-docs#sample-script%3A-parse-files-from-bytes).

[​](https://docs.landing.ai/ade/ade-changelog#may-29%2C-2025%3A-agentic-doc-v0-2-3)

May 29, 2025: agentic-doc v0.2.3

## [​](https://docs.landing.ai/ade/ade-changelog\#consolidated-parsing-function)  Consolidated Parsing Function

We released Agentic Document Extraction [library](https://github.com/landing-ai/agentic-doc) v0.2.3, which includes a new parsing function: `parse`. [chunk types](https://docs.landing.ai/ade/ade-chunk-types).The `parse` function allows you to parse multiple documents, and supports [loading documents from Amazon S3 buckets, Google Drive, and other locations](https://docs.landing.ai/ade/ade-connectors) by using the `connectors` module.To use the new `parse` function and the \`connectors module, upgrade the Agentic Document Extraction [library](https://github.com/landing-ai/agentic-doc) to v0.2.3.The [orginal parsing functions](https://docs.landing.ai/ade/ade-parse-deprecated) will continue to work, but we recommending using `parse` for new projects.

[​](https://docs.landing.ai/ade/ade-changelog#may-20%2C-2025%3A-agentic-doc-v0-2-1)

May 20, 2025: agentic-doc v0.2.1

## [​](https://docs.landing.ai/ade/ade-changelog\#consolidated-chunk-types)  Consolidated Chunk Types

We released Agentic Document Extraction [library](https://github.com/landing-ai/agentic-doc) v0.2.1, which includes consolidated [chunk types](https://docs.landing.ai/ade/ade-chunk-types).The Agentic Document Extraction library now has the following chunk types: `table`, `figure`, `marginalia`, and `text`.These chunk types were consolidated into `marginalia`:

- `page_header`
- `page_footer`
- `page_number`

These chunk types were consolidated into `text`:

- `title`
- `form`
- `key_value`

## [​](https://docs.landing.ai/ade/ade-changelog\#action-required-when-using-library)  Action Required When Using Library

**If you use the library and your scripts or workflows use any of the deprecated chunk types, update your code to use the new types.**How the library handles the deprecated chunk types depends on the version you’re using:

- Upgrade to v0.2.1 to use the new chunk types.
- If using v0.0.13 to v​​0.1.3, the `marginalia` type doesn’t exist and will fallback to `page_header`.
- If using v0.0.12 or earlier, the code **will NOT work after May 22**.

## [​](https://docs.landing.ai/ade/ade-changelog\#action-required-when-calling-the-api-directly)  Action Required When Calling the API Directly

**If you call the API directly and your scripts or workflows use any of the deprecated chunk types, update your code to use the new types.**We are making these same changes (consolidating the chunk types) to the API on **Thursday, May 22**.Starting May 22, the API will stop using the deprecated types in the response. If your code uses the deprecated chunk types, the code will no longer work.

[​](https://docs.landing.ai/ade/ade-changelog#may-14%2C-2025)

May 14, 2025

## [​](https://docs.landing.ai/ade/ade-changelog\#improved-accuracy)  Improved Accuracy

Agentic Document Extraction now delivers higher accuracy when extracting data from complex tables and multi-column layouts.

## [​](https://docs.landing.ai/ade/ade-changelog\#increased-processing-speed)  Increased Processing Speed

Agentic Document Extraction is now significantly faster than before, so you can process thousands of pages per minute.

## [​](https://docs.landing.ai/ade/ade-changelog\#process-longer-pages)  Process Longer Pages

We’ve increased our page limits, so that you can process longer documents.For more information, go to [Rate Limits](https://docs.landing.ai/ade/ade-rate-limits).

## [​](https://docs.landing.ai/ade/ade-changelog\#zero-data-retention)  Zero Data Retention

Users on the Custom plan can enable a zero data retention policy, ensuring all data is deleted immediately after processing—supporting strict privacy and compliance requirements.For more information, [contact us](http://landing.ai/contact-va).

## [​](https://docs.landing.ai/ade/ade-changelog\#consolidated-chunk-types-2)  Consolidated Chunk Types

We consolidated these chunk types into `page_header`:

- `page_header`
- `page_footer`
- `page_number`

We consolidated these chunk types into `form`:

- `form`
- `key_value`

For more information, go to [Chunk Types](https://docs.landing.ai/ade/ade-chunk-types).

Was this page helpful?

YesNo

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