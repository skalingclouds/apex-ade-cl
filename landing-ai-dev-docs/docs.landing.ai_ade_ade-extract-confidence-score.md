---
url: "https://docs.landing.ai/ade/ade-extract-confidence-score"
title: "Confidence Scores (Experimental Feature) - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Extraction

Confidence Scores (Experimental Feature)

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Availability](https://docs.landing.ai/ade/ade-extract-confidence-score#availability)
- [Confidence Scores in Output](https://docs.landing.ai/ade/ade-extract-confidence-score#confidence-scores-in-output)
- [Example Workflow: Get Confidence Scores During Field Extraction](https://docs.landing.ai/ade/ade-extract-confidence-score#example-workflow%3A-get-confidence-scores-during-field-extraction)
- [Null Confidence Scores](https://docs.landing.ai/ade/ade-extract-confidence-score#null-confidence-scores)

The [field extraction](https://docs.landing.ai/ade/ade-extract) results include a **confidence score** for each extracted field. This score indicates how certain Agentic Document Extraction is about the accuracy of the extracted data.Having a confidence score allows you to create logic to route fields with low-confidence scores to human reviewers before sending data to downstream systems. For example, you can write a script that sends an extracted field to a human reviewer if the confidence score is lower than a set threshold.The higher the confidence score, the more confident Agentic Document Extraction is that the prediction is accurate.

The confidence score feature is experimental and still in development, and may not return accurate results.

## [​](https://docs.landing.ai/ade/ade-extract-confidence-score\#availability)  Availability

- [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction): Confidence scores are included in extraction results starting July 21, 2025.
- [Library](https://github.com/landing-ai/agentic-doc): Use agentic-doc library v0.3.1 or later to get confidence scores in extraction results.
- [Playground](https://va.landing.ai/demo/doc-extraction): The extraction results in the Playground do not include confidence scores.

## [​](https://docs.landing.ai/ade/ade-extract-confidence-score\#confidence-scores-in-output)  Confidence Scores in Output

The API returns a `confidence` property for each extracted field within the `data.extraction_metadata` object.The sample `extraction_metadata` output below shows how the `confidence` property displays after extraction.

Confidence Score in Output

Copy

Ask AI

```
{
   'patient':{
      'name':{
         'value':'John Doe',
         'chunk_references':[\
            '0a75d377-a435-49d0-b987-ee77e67e746c'\
         ],
         'confidence':0.99
      },
      'address':{
         'value':'123 Main Street',
         'chunk_references':[\
            '1a753ba4-e375-4e70-aaf5-db3834a7d6a7'\
         ],
         'confidence':0.97
      }
   }
}

```

## [​](https://docs.landing.ai/ade/ade-extract-confidence-score\#example-workflow%3A-get-confidence-scores-during-field-extraction)  Example Workflow: Get Confidence Scores During Field Extraction

This example walks you through how to access and identify the `confidence` property during field extraction with Agentic Document Extraction.

1. Download this PDF and save it to a local directory: [Sample Bank Statement](https://docs.landing.ai/examples/estatement.pdf).
2. Copy the Python script below and save it to a local directory:





Sample Python Script for Field Extraction







Copy







Ask AI













```

from __future__ import annotations

from pydantic import BaseModel, Field
from agentic_doc.parse import parse


class SampleExtractionSchema(BaseModel):
       accountHolder: str = Field(
           ...,
           description='The full name of the person who holds the bank account.',
           title='Account Holder Name',
       )
       accountNumber: str = Field(
           ...,
           description='The bank account number associated with the account holder.',
           title='Bank Account Number',
       )

# Parse a file and extract the fields
results = parse("estatement.pdf", extraction_model=SampleExtractionSchema)
fields = results[0].extraction

# Return the value of the extracted fields
print("Extracted Fields:")
print(fields)

# Return the value of the extracted field metadata
print("\nExtraction Metadata:")
print(results[0].extraction_metadata)

```







See all 30 lines

3. Install the [agentic-doc library](https://github.com/landing-ai/agentic-doc).
4. Get your [API key](https://va.landing.ai/settings/api-key) and set it. For more information, go to [API Key](https://docs.landing.ai/ade/agentic-api-key).
5. Run the Python script.
6. Check that the output is similar to the following:





Confidence Score in Output







Copy







Ask AI













```
Extracted Fields:
accountHolder='SUSAN SAMPLE' accountNumber='02782-5094431'

Extraction Metadata:
accountHolder=MetadataType[str](value='SUSAN SAMPLE', chunk_references=['d04c75fd-5b1e-4aab-a859-b4aff17305cc'], confidence=0.9999998063873693) accountNumber=MetadataType[str](value='02782-5094431', chunk_references=['5c06add1-bb8e-4143-9424-e95b5bbaeee5'], confidence=0.9718049806957251)

```


## [​](https://docs.landing.ai/ade/ade-extract-confidence-score\#null-confidence-scores)  Null Confidence Scores

Because the confidence score feature is experimental and still in development, there are certain situations where scores are not available.The confidence score value will be `null` in the following situations:

- **Tables**: Data extracted from tables will have a `null` confidence score.
- **Changes to formatting**: Fields with custom formatting applied during extraction will have a `null` confidence score. For example, reformatting a date from “DD-MM-YYYY” to “MM-DD-YYYY” results in a `null` score.

Was this page helpful?

YesNo

[Extract Data with the Library](https://docs.landing.ai/ade/ade-extract-library) [Troubleshoot: Extraction](https://docs.landing.ai/ade/ade-extract-troubleshoot)

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