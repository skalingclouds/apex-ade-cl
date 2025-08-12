---
url: "https://docs.landing.ai/ade/ade-extract"
title: "Overview: Extract Data - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Extraction

Overview: Extract Data

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Classification](https://docs.landing.ai/ade/ade-extract#classification)
- [Get Started: Extraction Workflow](https://docs.landing.ai/ade/ade-extract#get-started%3A-extraction-workflow)
- [Supported Data Types](https://docs.landing.ai/ade/ade-extract#supported-data-types)
- [The Library and API Use Different Schemas Formats](https://docs.landing.ai/ade/ade-extract#the-library-and-api-use-different-schemas-formats)
- [Field Definition and Extraction Guidance](https://docs.landing.ai/ade/ade-extract#field-definition-and-extraction-guidance)
- [Supported Number of Properties](https://docs.landing.ai/ade/ade-extract#supported-number-of-properties)
- [What Counts as a Property?](https://docs.landing.ai/ade/ade-extract#what-counts-as-a-property%3F)

When parsing a document, Agentic Document Extraction can extract data that you specify from a document. This is helpful if you need to extract the same data from multiple documents.For example, if you work for a financial institution and need to extract the `Total Income` field from tens of thousands of loan applications, you can use the Agentic Document Extraction extraction feature to do that.![Extract Data from Documents](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/extract_06_26_2025.png)

## [​](https://docs.landing.ai/ade/ade-extract\#classification)  Classification

As part of the extraction process, you can classify documents and extract data based on the type of document it is.For example, let’s say you work for a financial institution and want to extract a set of data from Loan Applications and another set of data from Income Statements. You can assign a class to each document, and then extract data based on that document’s class.In the JSON schema used in the [Playground](https://va.landing.ai/demo/doc-extraction) and when [calling the API](https://docs.landing.ai/ade/ade-extract-api), use the `enum` keyword to identify the document types.

## [​](https://docs.landing.ai/ade/ade-extract\#get-started%3A-extraction-workflow)  Get Started: Extraction Workflow

We recommend using the schema extraction wizard directly in our [Playground](https://va.landing.ai/demo/doc-extraction) to build and validate an extraction schema. You can then use that schema when parsing documents:

1. Use the schema extraction wizard in our [Playground](https://docs.landing.ai/ade/ade-extract-playground) to build a schema tailored to your documents.
![Build a Schema with the Wizard](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/extract_workflow_1.png)
2. Choose a format to export the schema to: [library](https://docs.landing.ai/ade/ade-extract-library) or [API](https://docs.landing.ai/ade/ade-extract-api).
![Export the Relevant Format](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/extract_workflow_2.png)
3. Include the schema when you call the `parse` function with the [agentic-doc library](https://docs.landing.ai/ade/ade-extract-library) or run the [API](https://docs.landing.ai/ade/ade-extract-api).

You can also extract data in the Playground. We recommend doing this only for testing purposes, since the Playground isn’t designed to handle bulk document processing.

## [​](https://docs.landing.ai/ade/ade-extract\#supported-data-types)  Supported Data Types

When creating an extraction schema, you can specify the following data types:

- boolean
- number: When using the library, this is `float`.
- string
- enum
- date
- integer
- object
- array: The array can include these data types: string, enum, date, boolean, number, integer, object.

These data types are only supported in the library and API:

- byte
- nested objects
- list: This data type from the [`typing`](https://docs.python.org/3/library/typing.html) library is supported if the types within the `list` are valid.
- union: This data type from the [`typing`](https://docs.python.org/3/library/typing.html) library is supported if the types within the `union` are valid.

## [​](https://docs.landing.ai/ade/ade-extract\#the-library-and-api-use-different-schemas-formats)  The Library and API Use Different Schemas Formats

The schema format used in the [library](https://docs.landing.ai/ade/ade-extract-library) and [API](https://docs.landing.ai/ade/ade-extract-api) is different. But no worries; you can build or upload a schema in the [Playground](https://docs.landing.ai/ade/ade-extract-playground) and then choose which format to export it to!Learn more about the schema format for each use case:

[**Use Schemas in the Library** \\
\\
Define the fields that you want to extract using Pydantic models directly in your code.](https://docs.landing.ai/ade/ade-extract-library) [**Use Schemas in the API** \\
\\
Pass the schema in the API call or define the schema directly in your code.](https://docs.landing.ai/ade/ade-extract-api)

## [​](https://docs.landing.ai/ade/ade-extract\#field-definition-and-extraction-guidance)  Field Definition and Extraction Guidance

When you define the data to be extracted, you provide a **Name** for each field. You can also add an optional **Description** to give more context. Both the **Name** and **Description** serve as guidance to help Agentic Document Extraction understand exactly what information to locate and extract from your documents.The more descriptive and specific your field names and descriptions are, the more accurately Agentic Document Extraction can identify the correct data in your documents.

## [​](https://docs.landing.ai/ade/ade-extract\#supported-number-of-properties)  Supported Number of Properties

For optimal performance, include no more than 30 properties in your extraction schema. Performance may degrade as the number of properties increases.

### [​](https://docs.landing.ai/ade/ade-extract\#what-counts-as-a-property%3F)  What Counts as a Property?

A property is a key-value pair in an object and is defined using the `properties` keyword.The schema below has 4 total properties: 1 top-level property ( `employeeInfo`) that organizes the data, plus 3 nested properties ( `name`, `address`, `socialSecurityNumber`) that contain the actual extracted values.

Copy

Ask AI

```
{
  "type": "object",
  "title": "Payroll Document Field Extraction Schema",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "required": [\
    "employeeInfo"\
  ],
  "properties": {
    "employeeInfo": {
      "type": "object",
      "title": "Employee Information",
      "required": [\
        "name",\
        "address",\
        "socialSecurityNumber"\
      ],
      "properties": {
        "name": {
          "type": "string",
          "title": "Employee Name",
          "description": "Full name of the employee."
        },
        "address": {
          "type": "string",
          "title": "Employee Address",
          "description": "Mailing address of the employee."
        },
        "socialSecurityNumber": {
          "type": "string",
          "title": "Social Security Number",
          "description": "Employee's Social Security Number."
        }
      },
      "description": "Key identifying and contact information for the employee."
    }
  },
  "description": "Schema for extracting high-value tabular and form-like fields from a payroll-related markdown document."
}

```

Was this page helpful?

YesNo

[Deprecated Parsing Functions](https://docs.landing.ai/ade/ade-parse-deprecated) [Schema Wizard: Build Extraction Schemas in the Playground](https://docs.landing.ai/ade/ade-extract-playground)

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

![Extract Data from Documents](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/extract_06_26_2025.png)

![Build a Schema with the Wizard](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/extract_workflow_1.png)

![Export the Relevant Format](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/extract_workflow_2.png)