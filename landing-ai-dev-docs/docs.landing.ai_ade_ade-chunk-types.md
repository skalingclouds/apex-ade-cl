---
url: "https://docs.landing.ai/ade/ade-chunk-types"
title: "Chunk Types - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Parsing

Chunk Types

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Chunk Definition](https://docs.landing.ai/ade/ade-chunk-types#chunk-definition)
- [Chunk Overview](https://docs.landing.ai/ade/ade-chunk-types#chunk-overview)
- [Semantic Chunking](https://docs.landing.ai/ade/ade-chunk-types#semantic-chunking)
- [Why Do We Create Chunks?](https://docs.landing.ai/ade/ade-chunk-types#why-do-we-create-chunks%3F)
- [Chunk Types](https://docs.landing.ai/ade/ade-chunk-types#chunk-types)
- [Text](https://docs.landing.ai/ade/ade-chunk-types#text)
- [Ouput for Key-Value Pairs](https://docs.landing.ai/ade/ade-chunk-types#ouput-for-key-value-pairs)
- [Example: Paragraph](https://docs.landing.ai/ade/ade-chunk-types#example%3A-paragraph)
- [Example: Lists](https://docs.landing.ai/ade/ade-chunk-types#example%3A-lists)
- [Table](https://docs.landing.ai/ade/ade-chunk-types#table)
- [Output](https://docs.landing.ai/ade/ade-chunk-types#output)
- [Example: Receipt](https://docs.landing.ai/ade/ade-chunk-types#example%3A-receipt)
- [Example: Earnings Statement](https://docs.landing.ai/ade/ade-chunk-types#example%3A-earnings-statement)
- [Marginalia](https://docs.landing.ai/ade/ade-chunk-types#marginalia)
- [Example: Header and Page Number](https://docs.landing.ai/ade/ade-chunk-types#example%3A-header-and-page-number)
- [Figure](https://docs.landing.ai/ade/ade-chunk-types#figure)
- [Example: Medical Imaging](https://docs.landing.ai/ade/ade-chunk-types#example%3A-medical-imaging)
- [Example: Bar Chart](https://docs.landing.ai/ade/ade-chunk-types#example%3A-bar-chart)
- [Deprecated Chunk Types](https://docs.landing.ai/ade/ade-chunk-types#deprecated-chunk-types)
- [Action Required When Using Library](https://docs.landing.ai/ade/ade-chunk-types#action-required-when-using-library)
- [Action Required When Calling the API Directly](https://docs.landing.ai/ade/ade-chunk-types#action-required-when-calling-the-api-directly)

## [​](https://docs.landing.ai/ade/ade-chunk-types\#chunk-definition)  Chunk Definition

A **chunk** is a discrete element extracted from a document, such as a block of text, a table, or a figure.

## [​](https://docs.landing.ai/ade/ade-chunk-types\#chunk-overview)  Chunk Overview

When you send a document to the Agentic Document Extraction API, it analyzes the content on each page, breaks it down into meaningful elements, and returns each one as a chunk.Each chunk includes structured data that describes the content of the chunk and the location of the chunk in the document. This structure makes it easier to understand the extracted data and use it for downstream tasks.Extracted chunks are included in both the [JSON](https://docs.landing.ai/ade/ade-json-response) and [Markdown](https://docs.landing.ai/ade/ade-markdown-response) outputs.

## [​](https://docs.landing.ai/ade/ade-chunk-types\#semantic-chunking)  Semantic Chunking

The Agentic Document Extraction API uses semantic chunking, which means it intelligently groups content based on meaning rather than just layout or formatting.Instead of splitting documents at arbitrary points like fixed lengths or paragraph breaks, the API identifies coherent units of information (like complete ideas, logical sections, or related data) and extracts them as individual chunks.Semantic chunking improves the relevance and usability of the extracted content, especially in downstream tasks like search, retrieval, and analysis.

## [​](https://docs.landing.ai/ade/ade-chunk-types\#why-do-we-create-chunks%3F)  Why Do We Create Chunks?

Chunking makes downstream tasks faster, more accurate, and easier to scale. It serves several key purposes:

- **Enables downstream apps to process large documents efficiently**: Chunking allows applications like RAG systems and LLMs to index and retrieve smaller, meaningful segments instead of full documents. This helps avoid input size constraints, such as token limits.
- **Improves retrieval granularity**: Smaller, semantically meaningful units allow for more accurate and relevant results in downstream tasks like question answering and summarization.
- **Supports downstream semantic search and embeddings**: Well-structured chunks provide better inputs for embedding and make it easier to index and retrieve information during search.
- **Maintains human readability**: Chunking reflects how a human would naturally read the document, maintaining the visual and logical relationships between elements on the page.

## [​](https://docs.landing.ai/ade/ade-chunk-types\#chunk-types)  Chunk Types

Each chunk is labeled with a chunk type ( `chunk_type`), which identifies what kind of content it represents.The chunk types returned by Agentic Document Extraction are:

- [`text`](https://docs.landing.ai/ade/ade-chunk-types#text)
- [`table`](https://docs.landing.ai/ade/ade-chunk-types#table)
- [`marginalia`](https://docs.landing.ai/ade/ade-chunk-types#marginalia)
- [`figure`](https://docs.landing.ai/ade/ade-chunk-types#figure)

## [​](https://docs.landing.ai/ade/ade-chunk-types\#text)  Text

A `text` chunk type is an element that consists entirely of characters (letters and numbers), such as:

- paragraphs
- titles and headings
- lists
- form fields
- checkboxes
- radio buttons
- equations
- code blocks
- handwritten text

### [​](https://docs.landing.ai/ade/ade-chunk-types\#ouput-for-key-value-pairs)  Ouput for Key-Value Pairs

If the `text` content has key-value pairs, like form fields, the extracted data will be returnd as key-value pairs separated by line breaks ( `\n`).Here is an example JSON output for a `text` chunk that has form fields:

Copy

Ask AI

```
    {
      "text": "Social Security Number: 999-99-9999\nTaxable Marital Status: Married\nExemptions/Allowances:\n  Federal: 3, $25 Additional Tax\n  State: 2\n  Local: 2",
      "grounding": [\
        {\
          "box": {\
            "l": 0.1897532343864441,\
            "t": 0.17260606586933136,\
            "r": 0.39956772327423096,\
            "b": 0.2404632717370987\
          },\
          "page": 0\
        }\
      ],
      "chunk_type": "text",
      "chunk_id": "6bfe9850-6a12-456e-b355-afe9bdd9b1f5"
    }

```

### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-paragraph)  Example: Paragraph

Here is an example of the API marking a paragraph as a `text` chunk:
![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-3.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-3-md-light.png)

### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-lists)  Example: Lists

Here is an example of the API marking a list as a `text` chunk:
![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-2.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-2-md.png)

## [​](https://docs.landing.ai/ade/ade-chunk-types\#table)  Table

A `table` chunk type is a grid of rows and columns containing data.Agentic Document Extraction doesn’t require gridlines to be present, and typically interprets well-aligned sets of data to be part of a table. For example, part of a receipt can be extracted as a table if the purchased items align with the costs.

### [​](https://docs.landing.ai/ade/ade-chunk-types\#output)  Output

When a chunk is extracted, the chunk description is included in the `text` object. For `table` chunk types, the chunk is returned as HTML.Here is an example JSON output for a `table` chunk:

Copy

Ask AI

```
{
      "text": "<table><tbody><tr><td>1</td><td>Americano</td><td>$3.19</td></tr><tr><td>1</td><td>Almond Scone</td><td>$1.99</td></tr><tr><td>1</td><td>16oz Bottle Water</td><td>$2.99</td></tr></tbody></table>",
      "grounding": [\
        {\
          "box": {\
            "l": 0.04332852363586426,\
            "t": 0.36108696460723877,\
            "r": 0.8898441195487976,\
            "b": 0.47052615880966187\
          },\
          "page": 0\
        }\
      ],
      "chunk_type": "table",
      "chunk_id": "a2948002-f9b9-4afd-8534-8f2ff8947d74"
    }

```

### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-receipt)  Example: Receipt

Here is an example of the API marking receipt line items as a `table` chunk:
![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-receipt.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-receipt-md.png)

### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-earnings-statement)  Example: Earnings Statement

Here is an example of the API marking part of an earnings statement as a `table` chunk:
![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-2.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-2-md.png)

## [​](https://docs.landing.ai/ade/ade-chunk-types\#marginalia)  Marginalia

A `marginalia` chunk type is a set of text in the top, bottom, or side margins of a document, including:

- page headers
- page footers
- page numbers
- handwritten notes in margins
- line numbers on one side of a page

#### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-header-and-page-number)  Example: Header and Page Number

Here is an example of the API marking a header and page number as a `page_header` chunk:
![Chunk Type: Page Header](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-marginalia-1.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Page Header](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-marginalia-1-md.png)

## [​](https://docs.landing.ai/ade/ade-chunk-types\#figure)  Figure

A `figure` chunk type is an element that contains visual or graphical non-text content, including:

- logos
- pictures
- graphs (bar graphs, line graphs, etc.)
- flowcharts
- diagrams
- QR codes
- barcodes
- stamps
- signatures
- ID cards

### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-medical-imaging)  Example: Medical Imaging

Here is an example of the API marking a pathology image as a `figure` chunk:
![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-3.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-3-md.png)

### [​](https://docs.landing.ai/ade/ade-chunk-types\#example%3A-bar-chart)  Example: Bar Chart

Here is an example of the API marking a bar chart as a `figure` chunk:
![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-4.png)Here is the rendered Markdown for that chunk:
![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-4-md.png)

## [​](https://docs.landing.ai/ade/ade-chunk-types\#deprecated-chunk-types)  Deprecated Chunk Types

Some chunk types were deprecated and consolidated into other types. These changes were introduced in the Agentic Document Extraction [library](https://github.com/landing-ai/agentic-doc) v0.2.1, and will be rolled out to the API on Thursday, May 22.These chunk types were consolidated into `marginalia`:

- `page_header`
- `page_footer`
- `page_number`

These chunk types were consolidated into `text`:

- `title`
- `form`
- `key_value`

### [​](https://docs.landing.ai/ade/ade-chunk-types\#action-required-when-using-library)  Action Required When Using Library

**If you use the library and your scripts or workflows use any of the deprecated chunk types, update your code to use the new types.**How the library handles the deprecated chunk types depends on the version you’re using:

- Upgrade to v0.2.1 to use the new chunk types.
- If using v0.0.13 to v​​0.1.3, the `marginalia` type doesn’t exist and will fallback to `page_header`.
- If using v0.0.12 or earlier, the code **will NOT work after May 22**.

### [​](https://docs.landing.ai/ade/ade-chunk-types\#action-required-when-calling-the-api-directly)  Action Required When Calling the API Directly

**If you call the API directly and your scripts or workflows use any of the deprecated chunk types, update your code to use the new types.**We are making these same changes (consolidating the chunk types) to the API on **Thursday, May 22**.Starting May 22, the API will stop using the deprecated types in the response. If your code uses the deprecated chunk types, the code will no longer work.

Was this page helpful?

YesNo

[Parse Documents from Amazon S3, Google Drive, and More](https://docs.landing.ai/ade/ade-connectors) [JSON Response](https://docs.landing.ai/ade/ade-json-response)

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

![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-3.png)

![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-3-md-light.png)

![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-2.png)

![Chunk Type: Text](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-text-2-md.png)

![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-receipt.png)

![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-receipt-md.png)

![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-2.png)

![Chunk Type: Table](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-table-2-md.png)

![Chunk Type: Page Header](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-marginalia-1.png)

![Chunk Type: Page Header](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-marginalia-1-md.png)

![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-3.png)

![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-3-md.png)

![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-4.png)

![Chunk Type: Figure](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/images/ade-figure-4-md.png)