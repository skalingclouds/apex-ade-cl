---
url: "https://docs.landing.ai/ade/ade-extract-api"
title: "Extract Data with the API - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Extraction

Extract Data with the API

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Sample Script: Pass JSON Schema to API](https://docs.landing.ai/ade/ade-extract-api#sample-script%3A-pass-json-schema-to-api)
- [Sample Script: Include JSON Schema in Script](https://docs.landing.ai/ade/ade-extract-api#sample-script%3A-include-json-schema-in-script)
- [Extract Data Based on Document Type (Classification)](https://docs.landing.ai/ade/ade-extract-api#extract-data-based-on-document-type-classification)
- [Sample Script: Classify Documents](https://docs.landing.ai/ade/ade-extract-api#sample-script%3A-classify-documents)

You can extract data when you call the [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) directly.To do this, first create a JSON schema of the fields you want to extract. You can use the [guided schema wizard in the Playground](https://docs.landing.ai/ade/ade-extract-playground) to help you create the schema.After creating the schema, you can either [pass the JSON file](https://docs.landing.ai/ade/ade-extract-api#sample-script-pass-json-schema-to-api) in the API call or [define the JSON schema directly in your script](https://docs.landing.ai/ade/ade-extract-api#sample-script-include-json-schema-in-script).You can also [classify documents](https://docs.landing.ai/ade/ade-extract-api#sample-script-classify-documents) before extracting data, and then extract data based on the document type.

## [​](https://docs.landing.ai/ade/ade-extract-api\#sample-script%3A-pass-json-schema-to-api)  Sample Script: Pass JSON Schema to API

The script below shows how to pass a JSON file with the extraction schema to the API when parsing a document.

Copy

Ask AI

```
import json

VA_API_KEY = <YOUR_VA_API_KEY>  # Replace with your API key
headers = {"Authorization": f"Basic {VA_API_KEY}"}
url = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"

base_pdf_path = "your_pdf_path"  # Replace with the path to the file
pdf_name = "filename.pdf"  # Replace the file
pdf_path = f"{base_pdf_path}/{pdf_name}"

schema_name = "w2-schema.json"  # Replace with the JSON schema
schema_path = f"{base_pdf_path}/{schema_name}"

with open(schema_path, "r") as file:
    schema = json.load(file)

files = [\
    ("pdf", (pdf_name, open(pdf_path, "rb"), "application/pdf")),\
]

payload = {"fields_schema": json.dumps(schema)}

response = requests.request("POST", url, headers=headers, files=files, data=payload)

output_data = response.json()["data"]
extracted_info = output_data["extracted_schema"]
print(extracted_info)

```

## [​](https://docs.landing.ai/ade/ade-extract-api\#sample-script%3A-include-json-schema-in-script)  Sample Script: Include JSON Schema in Script

The script below shows how to define the extraction schema in the call when parsing a document.

Copy

Ask AI

```
import json
import requests

VA_API_KEY = "YOUR_VA_API_KEY"  # Replace with your API key
headers = {"Authorization": f"Basic {VA_API_KEY}"}
url = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"

base_pdf_path = "your_pdf_path"  # Replace with the path to the file
pdf_name = "filename.pdf"  # Replace the file
pdf_path = f"{base_pdf_path}/{pdf_name}"

# Define your schema
schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Student Enrollment Form Extraction Schema",
  "description": "Schema for extracting key fields from a student enrollment form in markdown format.",
  "type": "object",
  "properties": {
    "studentName": {
      "type": "object",
      "title": "Student Name",
      "description": "The full name of the student.",
      "properties": {
        "first": {
          "type": "string",
          "title": "First Name",
          "description": "The student's first name."
        },
        "last": {
          "type": "string",
          "title": "Last Name",
          "description": "The student's last name."
        }
      },
      "required": [\
        "first",\
        "last"\
      ]
    }
  },
  "required": [\
    "studentName"\
  ]
}

files = [\
    ("pdf", (pdf_name, open(pdf_path, "rb"), "application/pdf")),\
]

payload = {"fields_schema": json.dumps(schema)}

response = requests.request("POST", url, headers=headers, files=files, data=payload)

output_data = response.json()["data"]
extracted_info = output_data["extracted_schema"]
print(extracted_info)

```

## [​](https://docs.landing.ai/ade/ade-extract-api\#extract-data-based-on-document-type-classification)  Extract Data Based on Document Type (Classification)

As part of the extraction process, you can classify documents and extract data based on the type of document it is. For example, you can extract different sets of data from Invoices, Receipts, and Waybills.To classify documents, use the `enum` keyword to define the document types in your script. Here is an example:

Copy

Ask AI

```
# Define document types
class_schema = {
    "type": "object",
    "properties": {
        "document_type": {"type": "string", "enum": ["Document Type 1", "Document Type 2", "Document Type 3"]}
    },
    "required": ["document_type"],
}

```

### [​](https://docs.landing.ai/ade/ade-extract-api\#sample-script%3A-classify-documents)  Sample Script: Classify Documents

Let’s say you need to parse three types of documents: Passports, Invoices, and Other. The data you need to extract depends on the document type.The following script shows you how to define your document types, the fields to extract for each document type, and the code to actually parse the documents, classify the documents, and extract the data.

Copy

Ask AI

```
import requests
import json

VA_API_KEY = <YOUR_VA_API_KEY>  # Replace with your API key
headers = {"Authorization": f"Basic {VA_API_KEY}"}
url = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"

base_pdf_path = "your_pdf_path"  # Replace with the path to the file
pdf_name = "filename.pdf"  # Replace the file
pdf_path = f"{base_pdf_path}/{pdf_name}"

# Define document types
class_schema = {
    "type": "object",
    "properties": {
        "document_type": {"type": "string", "enum": ["Passport", "Invoice", "Other"]}
    },
    "required": ["document_type"],
}

# First request: classification
with open(pdf_path, "rb") as f:
    files = [("pdf", (pdf_name, f, "application/pdf"))]
    payload = {"fields_schema": json.dumps(class_schema)}
    classification_response = requests.post(
        url, headers=headers, files=files, data=payload
    )

classification = classification_response.json()["data"]["extracted_schema"][\
    "document_type"\
]

# Define schema based on classification
if classification == "Passport":
    schema = {
        "type": "object",
        "properties": {
            "Given Names": {"type": "string"},
            "Date of birth": {"type": "string"},
            "ID_number": {"type": "number"},
            "Passport Number": {"type": "string"},
        },
        "required": ["Given Names", "Date of birth", "ID_number", "Passport Number"],
    }
elif classification == "Invoice":
    schema = {
        "type": "object",
        "properties": {
            "Bill to": {"type": "string"},
            "Invoice Number": {"type": "string"},
            "Invoice Date": {"type": "string"},
            "Due Date": {"type": "string"},
            "Total": {"type": "string"},
        },
        "required": ["Bill to", "Invoice Number", "Invoice Date", "Due Date", "Total"],
    }
else:
    print("Document type is 'Other'. No extraction schema defined.")
    exit()

# Second request: extraction
with open(pdf_path, "rb") as f:
    files = [("pdf", (pdf_name, f, "application/pdf"))]
    payload = {"fields_schema": json.dumps(schema)}
    response = requests.post(url, headers=headers, files=files, data=payload)

output_data = response.json()["data"]
extracted_info = output_data["extracted_schema"]
print(extracted_info)

```

Was this page helpful?

YesNo

[Schema Wizard: Build Extraction Schemas in the Playground](https://docs.landing.ai/ade/ade-extract-playground) [Extract Data with the Library](https://docs.landing.ai/ade/ade-extract-library)

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