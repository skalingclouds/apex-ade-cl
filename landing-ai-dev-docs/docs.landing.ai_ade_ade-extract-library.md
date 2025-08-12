---
url: "https://docs.landing.ai/ade/ade-extract-library"
title: "Extract Data with the Library - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Extraction

Extract Data with the Library

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Sample Script: Extract Fields (extraction\_model)](https://docs.landing.ai/ade/ade-extract-library#sample-script%3A-extract-fields-extraction-model)
- [Sample Script: Extract Nested Subfields](https://docs.landing.ai/ade/ade-extract-library#sample-script%3A-extract-nested-subfields)
- [Extraction Output](https://docs.landing.ai/ade/ade-extract-library#extraction-output)
- [extracted\_schema](https://docs.landing.ai/ade/ade-extract-library#extracted-schema)
- [extraction\_metadata](https://docs.landing.ai/ade/ade-extract-library#extraction-metadata)
- [extraction\_error](https://docs.landing.ai/ade/ade-extract-library#extraction-error)

You can extract specified fields from a document when parsing it with the [agentic-doc library](https://github.com/landing-ai/agentic-doc).There are two methods for running extraction with the library:

- Define the fields that you want to extract using Pydantic models directly in your code. Then pass that definition to the `extraction_model` parameter when running the [`parse`](https://docs.landing.ai/ade/ade-parse-docs) function.
- Input the schema in the `extraction_schema` parameter as a `dict` and receive the answer as `dict` (JSON).

## [​](https://docs.landing.ai/ade/ade-extract-library\#sample-script%3A-extract-fields-extraction-model)  Sample Script: Extract Fields (extraction\_model)

Run this script to extract fields from a local file and return the value of one of the extracted fields. In this scenario, the schema is passed in the `extraction_model` parameter.

Copy

Ask AI

```
from pydantic import BaseModel, Field
from agentic_doc.parse import parse

# Define the fields you want to extract
class ExtractedFields(BaseModel):
    employee_name: str = Field(description="the full name of the employee")
    employee_ssn: str = Field(description="the social security number of the employee")
    gross_pay: float = Field(description="the gross pay of the employee")
    employee_address: str = Field(description="the address of the employee")

# Parse a file and extract the fields
results = parse("mydoc.pdf", extraction_model=ExtractedFields)
fields = results[0].extraction

# Return the value of one of the extracted fields
print(fields.employee_name)

```

## [​](https://docs.landing.ai/ade/ade-extract-library\#sample-script%3A-extract-nested-subfields)  Sample Script: Extract Nested Subfields

You can extract nested subfields from documents. For example, let’s say you have a medical form that has two “name” fields: one for the Patient and one for their Emergency Contact. You can extract both fields by running the script below.The script extracts the nested subfields from a local file and returns their values.

Copy

Ask AI

```
from pydantic import BaseModel, Field
from agentic_doc.parse import parse

# Define the main extraction model with nested subfields
class MedicalField(BaseModel):
    patient: Patient = Field(description="All information pertaining directly to the patient")
    emergency_content: EmergencyContact = Field(description="All information pertaining directly to the patient's emergency contact")

# Define the nested field classes
class Patient(BaseModel):
    name: str = Field(description="Patient name")

class EmergencyContact(BaseModel):
    name: str = Field(description="Emergency contact name")

# Parse a file and extract the fields
results = parse("mydoc.pdf", extraction_model=MedicalField)
fields = results[0].extraction

# Return the values of the extracted nested fields
print(fields.patient.name)
print(fields.emergency_contact.name)

```

## [​](https://docs.landing.ai/ade/ade-extract-library\#extraction-output)  Extraction Output

When you extract fields from a document using the [agentic-doc library](https://github.com/landing-ai/agentic-doc), these fields are returned:

- [`extracted_schema`](https://docs.landing.ai/ade/ade-extract-library#extracted_schema)
- [`extraction_metadata`](https://docs.landing.ai/ade/ade-extract-library#extraction_metadata)
- [`extraction_error`](https://docs.landing.ai/ade/ade-extract-library#extraction_error)

## [​](https://docs.landing.ai/ade/ade-extract-library\#extracted-schema)  `extracted_schema`

This is the same type as the `BaseModel` that is passed in as the argument to `extraction_model`.

## [​](https://docs.landing.ai/ade/ade-extract-library\#extraction-metadata)  `extraction_metadata`

This is the same type as the `BaseModel` that is passed in as the argument to `extraction_model`.It has the same nesting structure as the `BaseModel` except that each field is replaced with a dictionary. This dictionary uses this form:

Copy

Ask AI

```
{"chunk_references": ["chunk-id-1", chunk-id-2", ...]}

```

Here is an example of a returned `extraction_metadata` field:

Copy

Ask AI

```
extraction_metadata = {
    "employee_name": {
        "chunk_references": [\
            "72ba3cca-01e5-407b-9fc4-81f54f9f0c51"\
        ]
    },
    "gross_pay": {
        "chunk_references": [\
            "5b8865b9-1a81-46df-bcf7-0bdbed9130dc"\
        ]
    }
}

```

If you have a more deeply-nested `extraction_model` (like in this [medical form example](https://docs.landing.ai/ade/ade-extract-library#sample-script-extract-nested-subfields)), then you may see something like this:

Copy

Ask AI

```
extraction_metadata = {
    "patient": {
        "name": {
            "chunk_references": [\
                "72ba3cca-01e5-407b-9fc4-81f54f9f0c51"\
            ]
        }
    },
    "emergency_contact": {
        "name": {
            "chunk_references": [\
                "5b8865b9-1a81-46df-bcf7-0bdbed9130dc"\
            ]
        }
    }
}

```

## [​](https://docs.landing.ai/ade/ade-extract-library\#extraction-error)  `extraction_error`

If the extraction function encountered an error, the `extraction_error` field will describe the issue. If there are no errors, the `extraction_error` field returns `None`.

Was this page helpful?

YesNo

[Extract Data with the API](https://docs.landing.ai/ade/ade-extract-api) [Confidence Scores (Experimental Feature)](https://docs.landing.ai/ade/ade-extract-confidence-score)

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