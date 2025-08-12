---
url: "https://docs.landing.ai/ade/ade-extract-playground"
title: "Schema Wizard: Build Extraction Schemas in the Playground - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Extraction

Schema Wizard: Build Extraction Schemas in the Playground

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Start a Schema](https://docs.landing.ai/ade/ade-extract-playground#start-a-schema)
- [Generate a Schema from Smart Suggestions](https://docs.landing.ai/ade/ade-extract-playground#generate-a-schema-from-smart-suggestions)
- [Generate a Schema from a Prompt](https://docs.landing.ai/ade/ade-extract-playground#generate-a-schema-from-a-prompt)
- [Build a Schema from Scratch](https://docs.landing.ai/ade/ade-extract-playground#build-a-schema-from-scratch)
- [Upload a Schema](https://docs.landing.ai/ade/ade-extract-playground#upload-a-schema)
- [Edit and Validate the Schema](https://docs.landing.ai/ade/ade-extract-playground#edit-and-validate-the-schema)
- [Edit or Remove Fields](https://docs.landing.ai/ade/ade-extract-playground#edit-or-remove-fields)
- [Validate a Schema](https://docs.landing.ai/ade/ade-extract-playground#validate-a-schema)
- [Download or Copy Extracted Data](https://docs.landing.ai/ade/ade-extract-playground#download-or-copy-extracted-data)
- [Export the Schema](https://docs.landing.ai/ade/ade-extract-playground#export-the-schema)
- [Start Over (Delete Schema)](https://docs.landing.ai/ade/ade-extract-playground#start-over-delete-schema)

To make it as easy as possible to build an extraction schema, we’ve created a wizard in our [Playground](https://va.landing.ai/demo/doc-extraction) that guides you through the process.Here is the workflow for building a schema in the playground:

[**Start a Schema** \\
\\
Use our AI-powered tools to generate a schema, build one from scratch, or upload an existing schema.](https://docs.landing.ai/ade/ade-extract-playground#start-a-schema) [**Edit & Validate the Schema** \\
\\
Update and edit the schema, and see how it works with your document.](https://docs.landing.ai/ade/ade-extract-playground#edit-and-validate-the-schema) [**Export the Schema** \\
\\
Export your schema to use with our library or API.](https://docs.landing.ai/ade/ade-extract-playground#export-the-schema)

## [​](https://docs.landing.ai/ade/ade-extract-playground\#start-a-schema)  Start a Schema

There are a few ways to start building your extraction schema in the [Playground](https://va.landing.ai/demo/doc-extraction):

- [Generate a schema from smart suggestions](https://docs.landing.ai/ade/ade-extract-playground#generate-a-schema-from-smart-suggestions)
- [Generate a schema from a prompt](https://docs.landing.ai/ade/ade-extract-playground#generate-a-schema-from-a-prompt)
- [Build a schema from scratch](https://docs.landing.ai/ade/ade-extract-playground#build-a-schema-from-scratch)
- [Upload a schema](https://docs.landing.ai/ade/ade-extract-playground#upload-a-schema)

All schemas you create are saved to your chat history. You can access these in **Your Files**.

### [​](https://docs.landing.ai/ade/ade-extract-playground\#generate-a-schema-from-smart-suggestions)  Generate a Schema from Smart Suggestions

After you upload a document to the Playground and open the **Extract** tool, Agentic Document Extraction suggests a schema based on the fields and your document layout. Accept the suggestions and further customize and validate your schema as needed.To create an extraction schema based on smart suggestions:

1. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
2. Upload a file or open an existing chat.
3. Click the **Extract** tab.
4. By default, **Smart Suggestion** is enabled. The app reviews your document and suggests a schema based on the logical structure of the document. To accept the schema and use it as a starting point, click **Start with Suggestions**. You can edit the schema in the next step.
![Smart Suggestions](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/smart_suggestions_1.png)
5. The full suggested schema displays. You can now edit and remove fields as needed.
![Smart Suggestions](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/smart_suggestions_2.png)
6. Click **Run Schema** to see how the extracted data looks. This opens the **Extracted Results** panel, so that you can quickly validate the schema.
![Smart Suggestions](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/smart_suggestions_3.png)
7. You can continue to [edit the schema](https://docs.landing.ai/ade/ade-extract-playground#edit-and-validate-the-schema). Click **Run Schema** to re-validate.
8. When you’re happy with the results, [export the schema](https://docs.landing.ai/ade/ade-extract-playground#export-the-schema).

### [​](https://docs.landing.ai/ade/ade-extract-playground\#generate-a-schema-from-a-prompt)  Generate a Schema from a Prompt

After you upload a document to the Playground and open the **Extract** tool, you can prompt Agentic Document Extraction to extract specific fields.This is useful if you only want to extract certain fields, and not all the data in the document. For example, let’s say that you’re reviewing bank account statements, but you only need to know the account number and the closing balance on the account. In this case, you could prompt Agentic Document Extraction to return only these two fields.To create an extraction schema from a prompt:

01. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
02. Upload a file or open an existing chat.
03. Click the **Extract** tab.
04. Click **Prompt to Schema**.
05. Enter a very clear and detailed prompt. Specify the exact fields you want to extract. Explain how they are labeled in the document, and if you want them labeled differently in the extracted results.
06. Click **Generate Schema**.
    ![Generate Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_prompt_1.png)
07. Agentic Document Extraction creates a schema based on your prompt. You can now edit and remove fields as needed.
    ![View and Edit Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_prompt_2.png)
08. Click **Run Schema** to see how the extracted data looks. This opens the **Extracted Results** panel, so that you can quickly validate the schema.
    ![Run Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_prompt_3.png)
09. You can continue to [edit the schema](https://docs.landing.ai/ade/ade-extract-playground#edit-and-validate-the-schema). Click **Run Schema** to re-validate.
10. When you’re happy with the results, [export the schema](https://docs.landing.ai/ade/ade-extract-playground#export-the-schema).

### [​](https://docs.landing.ai/ade/ade-extract-playground\#build-a-schema-from-scratch)  Build a Schema from Scratch

You can create an extraction schema directly in the Playground user interface.To create an extraction schema from scratch:

01. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
02. Upload a file or open an existing chat.
03. Click the **Extract** tab.
04. Click **Start from Scratch**.
    ![Start from Scratch](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_scratch_1.png)
05. Click **Add New Field**.
06. Enter the **Field Name**.
07. Select the **Data Type**. For a list of supported data types, go to [Supported Data Types](https://docs.landing.ai/ade/ade-extract#supported-data-types).
08. Enter a detailed Description of the field. (Optional)
09. Repeat this step for each field you want to extract.
    ![Create Fields](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_scratch_2.png)
10. Click **Run Schema** to see how the extracted data looks. This opens the **Extracted Results** panel, so that you can quickly validate the schema.
    ![Run Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_scratch_3.png)
11. You can continue to [edit the schema](https://docs.landing.ai/ade/ade-extract-playground#edit-and-validate-the-schema). Click **Run Schema** to re-validate.
12. When you’re happy with the results, [export the schema](https://docs.landing.ai/ade/ade-extract-playground#export-the-schema).

### [​](https://docs.landing.ai/ade/ade-extract-playground\#upload-a-schema)  Upload a Schema

If you have an existing extraction schema you want to edit, you can upload it to the Playground to validate it. Uploaded schemas cannot be edited directly in the Playground.Uploading a schema replaces any existing schema and extracted values.To upload an existing extraction schema:

1. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
2. Upload a file or open an existing chat.
3. Click the **Extract** tab.
4. In the **Schema** panel, click **…** and select **Upload JSON Schema**.
5. Select the JSON file you want to load.
6. The app loads the JSON file and switches to the Code Editor. This opens the **Extracted Results** panel, so that you can quickly validate the schema. (If prompted, click **Run to update**.)

## [​](https://docs.landing.ai/ade/ade-extract-playground\#edit-and-validate-the-schema)  Edit and Validate the Schema

After creating a schema in the [Playground](https://va.landing.ai/demo/doc-extraction), you can edit and validate it. You can add fields, update descriptions, remove fields, and validate the full schema.

### [​](https://docs.landing.ai/ade/ade-extract-playground\#edit-or-remove-fields)  Edit or Remove Fields

1. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
2. Open an existing chat.
3. Click the **Extract** tab.
4. To edit a field: click the element you want to edit. For example, if you want to change a field type from **String** to **Number**, click **String** and select **Number**.
![Edit Field](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_edit_field.png)
5. To remove a field: hover over it and click the **Delete** button. Deleting a field cannot be undone.
![Delete Field](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_delete_field.png)
6. After making any changes to the schema, click **Run Schema** to re-validate.

### [​](https://docs.landing.ai/ade/ade-extract-playground\#validate-a-schema)  Validate a Schema

After creating or editing a schema in the Playground, click **Run Schema** to validate it.Running a schema refreshes the **Extracted Results** panel. The Extracted Results panel displays two sets of content:

- **Data**: This is the list of extracted key-value pairs.
- **Metadata**: This is the list of `chunk_references` for each extracted value.
![Extracted Results](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_extracted_results.png)

## [​](https://docs.landing.ai/ade/ade-extract-playground\#download-or-copy-extracted-data)  Download or Copy Extracted Data

You can download or copy the extracted data from the **Extracted Results** panel. To do this:

1. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
2. Open an existing chat.
3. Click the **Extract** tab.
4. If the **Extracted Results** panel doesn’t display, create or edit a schema and click **Run Schema**.
5. Click the **Download** or **Copy** buttons to get the extracted data.
![Copy the Extracted Values](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_extracted_values_copy.png)

## [​](https://docs.landing.ai/ade/ade-extract-playground\#export-the-schema)  Export the Schema

After creating and validating a schema, you are now ready to export it to use with the Agentic Document Extraction [library](https://docs.landing.ai/ade/ade-extract-library) or [API](https://docs.landing.ai/ade/ade-extract-api).Exporting the schema creates the full code you will need to parse and extract with either the library or API.To export the extraction schema:

1. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
2. Upload open an existing chat.
3. Click the **Extract** tab.
4. Click **Code**.
![View the Schema Code](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_download_1.png)
5. The **View Code** pop-up opens. Click the **Library** or **API** tab to see the code for each extraction method.
6. Click the **Download** or **Copy** buttons to get the code.
![Get the Schema Code](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_download_2.png)
7. You’re now ready to extract data with the [library](https://docs.landing.ai/ade/ade-extract-library) or [API](https://docs.landing.ai/ade/ade-extract-api).

## [​](https://docs.landing.ai/ade/ade-extract-playground\#start-over-delete-schema)  Start Over (Delete Schema)

You can delete the schema you created for a file. This removes all the fields you created and any extracted values. This cannot be undone.

1. Go to the Agentic Document Extraction [Playground](https://va.landing.ai/demo/doc-extraction).
2. Upload a file or open an existing chat.
3. Click the **Extract** tab.
4. In the **Schema** panel, click **…** and select **Start Over**.
![Delete Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_start_over.png)
5. When prompted, click **Clear & Restart**.

Was this page helpful?

YesNo

[Overview: Extract Data](https://docs.landing.ai/ade/ade-extract) [Extract Data with the API](https://docs.landing.ai/ade/ade-extract-api)

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

![Smart Suggestions](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/smart_suggestions_1.png)

![Smart Suggestions](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/smart_suggestions_2.png)

![Smart Suggestions](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/smart_suggestions_3.png)

![Generate Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_prompt_1.png)

![View and Edit Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_prompt_2.png)

![Run Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_prompt_3.png)

![Start from Scratch](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_scratch_1.png)

![Create Fields](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_scratch_2.png)

![Run Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_scratch_3.png)

![Edit Field](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_edit_field.png)

![Delete Field](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_delete_field.png)

![Extracted Results](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_extracted_results.png)

![Copy the Extracted Values](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_extracted_values_copy.png)

![View the Schema Code](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_download_1.png)

![Get the Schema Code](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_download_2.png)

![Delete Schema](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/schema_start_over.png)