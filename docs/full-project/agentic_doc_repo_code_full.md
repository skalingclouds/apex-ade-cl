Repository: landing-ai/agentic-doc
Files analyzed: 21

Estimated tokens: 66.6k

Directory structure:
└── landing-ai-agentic-doc/
    ├── README.md
    ├── LICENSE
    ├── pyproject.toml
    ├── .flake8
    ├── agentic_doc/
    │   ├── __init__.py
    │   ├── common.py
    │   ├── config.py
    │   ├── connectors.py
    │   ├── parse.py
    │   └── utils.py
    ├── tests/
    │   ├── README.md
    │   ├── conftest.py
    │   ├── integ/
    │   │   └── test_parse_integ.py
    │   └── unit/
    │       ├── test_common.py
    │       ├── test_config.py
    │       ├── test_connectors.py
    │       ├── test_parse.py
    │       └── test_utils.py
    └── .github/
        └── workflows/
            ├── ci-integ.yml
            ├── ci-unit.yml
            └── release.yml


================================================
FILE: README.md
================================================
<div align="center">

# Agentic Document Extraction – Python Library

[![Unit test status](https://github.com/landing-ai/agentic-doc/actions/workflows/ci-unit.yml/badge.svg)](https://github.com/landing-ai/agentic-doc/actions/workflows/ci-unit.yml)
[![Integration test status](https://github.com/landing-ai/agentic-doc/actions/workflows/ci-integ.yml/badge.svg)](https://github.com/landing-ai/agentic-doc/actions/workflows/ci-integ.yml)
[![](https://dcbadge.vercel.app/api/server/wPdN8RCYew?compact=true&style=flat)](https://discord.gg/RVcW3j9RgR)
[![PyPI version](https://badge.fury.io/py/agentic-doc.svg)](https://badge.fury.io/py/agentic-doc)

**[Web App](https://va.landing.ai/demo/doc-extraction) · [Discord](https://discord.com/invite/RVcW3j9RgR) · [Blog](https://landing.ai/blog/going-beyond-ocrllm-introducing-agentic-document-extraction) · [Docs](https://support.landing.ai/docs/document-extraction)**

</div>

## Overview

The LandingAI **Agentic Document Extraction** API pulls structured data out of visually complex documents—think tables, pictures, and charts—and returns a hierarchical JSON with exact element locations.

This Python library wraps that API to provide:

* **Long‑document support** – process 100+ page PDFs in a single call
* **Auto‑retry / paging** – handles concurrency, time‑outs, and rate limits
* **Helper utilities** – bounding‑box snippets, visual debuggers, and more

### Features

- 📦 **Batteries‑included install:** `pip install agentic-doc` – nothing else needed → see [Installation](#installation)
- 🗂️ **All file types:** parse PDFs of *any* length, single images, or URLs → see [Supported Files](#supported-files)
- 📚 **Long‑doc ready:** auto‑split & parallel‑process 1000+ page PDFs, then stitch results → see [Parse Large PDF Files](#parse-large-pdf-files)
- 🧩 **Structured output:** returns hierarchical JSON plus ready‑to‑render Markdown → see [Result Schema](#result-schema)
- 👁️ **Ground‑truth visuals:** optional bounding‑box snippets and full‑page visualizations → see [Save Groundings as Images](#save-groundings-as-images)
- 🏃 **Batch & parallel:** feed a list; library manages threads & rate limits (`BATCH_SIZE`, `MAX_WORKERS`) → see [Parse Multiple Files in a Batch](#parse-multiple-files-in-a-batch)
- 🔄 **Resilient:** exponential‑backoff retries for 408/429/502/503/504 and rate‑limit hits → see [Automatically Handle API Errors and Rate Limits with Retries](#automatically-handle-api-errors-and-rate-limits-with-retries)
- 🛠️ **Drop‑in helpers:** `parse_documents`, `parse_and_save_documents`, `parse_and_save_document` → see [Main Functions](#main-functions)
- ⚙️ **Config via env / .env:** tweak parallelism, logging style, retry caps—no code changes → see [Configuration Options](#configuration-options)
- 🌐 **Raw API ready:** advanced users can still hit the REST endpoint directly → see the [API Docs](https://support.landing.ai/docs/document-extraction)


## Quick Start

### Installation

```bash
pip install agentic-doc
```

### Requirements
- Python version 3.9, 3.10, 3.11 or 3.12
- LandingAI agentic AI API key (get the key [here](https://va.landing.ai/settings/api-key))

### Set the API Key as an Environment Variable
After you get the LandingAI agentic AI API key, set the key as an environment variable (or put it in a `.env` file):

```bash
export VISION_AGENT_API_KEY=<your-api-key>
```

### Supported Files
The library can extract data from:
- PDFs (any length)
- Images that are supported by OpenCV-Python (i.e. the `cv2` library)
- URLs pointing to PDF or image files

### Basic Usage

#### Extract Data from One Document
Run the following script to extract data from one document and return the results in both markdown and structured chunks.

```python
from agentic_doc.parse import parse

# Parse a local file
result = parse("path/to/image.png")
print(result[0].markdown)  # Get the extracted data as markdown
print(result[0].chunks)  # Get the extracted data as structured chunks of content

# Parse a document from a URL
result = parse("https://example.com/document.pdf")
print(result[0].markdown)

# Legacy approach (still supported)
from agentic_doc.parse import parse_documents
results = parse_documents(["path/to/image.png"])
parsed_doc = results[0]
```

#### Extract Data from Multiple Documents
Run the following script to extract data from multiple documents.

```python
from agentic_doc.parse import parse

# Parse multiple local files
file_paths = ["path/to/your/document1.pdf", "path/to/another/document2.pdf"]
results = parse(file_paths)
for result in results:
    print(result.markdown)

# Parse and save results to a directory
results = parse(file_paths, result_save_dir="path/to/save/results")
result_paths = []
for result in results:
    result_paths.append(result.result_path)
# result_paths: ["path/to/save/results/document1_20250313_070305.json", ...]
```


#### Using field extraction

```python
from pydantic import BaseModel, Field
from agentic_doc.parse import parse

class ExtractedFields(BaseModel):
    employee_name: str = Field(description="the full name of the employee")
    employee_ssn: str = Field(description="the social security number of the employee")
    gross_pay: float = Field(description="the gross pay of the employee")
    employee_address: str = Field(description="the address of the employee")

results = parse("mydoc.pdf", extraction_model=ExtractedFields)
fields = results[0].extraction
metadata = results[0].extraction_metadata
print(f"Field value: {fields.employee_name}, confidence: {metadata.employee_name.confidence}")
```


#### Extract Data Using Connectors
The library now supports various connectors to easily access documents from different sources:

##### Google Drive Connector

**Prerequisites: Follow the [Google Drive API Python Quickstart](https://developers.google.com/workspace/drive/api/quickstart/python) tutorial first to set up your credentials.**

The Google Drive API quickstart will guide you through:
1. Creating a Google Cloud project
2. Enabling the Google Drive API
3. Setting up OAuth 2.0 credentials

After completing the quickstart tutorial, you can use the Google Drive connector as follows:

```python
from agentic_doc.parse import parse
from agentic_doc.connectors import GoogleDriveConnectorConfig

# Using OAuth credentials file (from quickstart tutorial)
config = GoogleDriveConnectorConfig(
    client_secret_file="path/to/credentials.json",
    folder_id="your-google-drive-folder-id"  # Optional
)

# Parse all documents in the folder
results = parse(config)

# Parse with filtering
results = parse(config, connector_pattern="*.pdf")
```

##### Amazon S3 Connector
```python
from agentic_doc.parse import parse
from agentic_doc.connectors import S3ConnectorConfig

config = S3ConnectorConfig(
    bucket_name="your-bucket-name",
    aws_access_key_id="your-access-key",  # Optional if using IAM roles
    aws_secret_access_key="your-secret-key",  # Optional if using IAM roles
    region_name="us-east-1"
)

# Parse all documents in the bucket
results = parse(config)

# Parse documents in a specific prefix/folder
results = parse(config, connector_path="documents/")
```

##### Local Directory Connector
```python
from agentic_doc.parse import parse
from agentic_doc.connectors import LocalConnectorConfig

config = LocalConnectorConfig()

# Parse all supported documents in a directory
results = parse(config, connector_path="/path/to/documents")

# Parse with pattern filtering
results = parse(config, connector_path="/path/to/documents", connector_pattern="*.pdf")

# Parse all supported documents in a directory recursively (search subdirectories as well)
config = LocalConnectorConfig(recursive=True)
results = parse(config, connector_path="/path/to/documents")
```

##### URL Connector
```python
from agentic_doc.parse import parse
from agentic_doc.connectors import URLConnectorConfig

config = URLConnectorConfig(
    headers={"Authorization": "Bearer your-token"},  # Optional
    timeout=60  # Optional
)

# Parse document from URL
results = parse(config, connector_path="https://example.com/document.pdf")
```

#### Raw Bytes Input

```python
from agentic_doc.parse import parse

# Load a PDF or image file as bytes
with open("document.pdf", "rb") as f:
    raw_bytes = f.read()

# Parse the document from bytes
results = parse(raw_bytes)
```

You can also parse image bytes:

```python
with open("image.png", "rb") as f:
    image_bytes = f.read()

results = parse(image_bytes)
```

This is useful when documents are already loaded into memory (e.g., from an API response or uploaded via a web interface). The parser will auto-detect the file type from the bytes.


## Why Use It?

- **Simplified Setup:** No need to manage API keys or handle low-level REST calls.
- **Automatic Large File Processing:** Splits large PDFs into manageable parts and processes them in parallel.
- **Built-In Error Handling:** Automatically retries requests with exponential backoff and jitter for common HTTP errors.
- **Parallel Processing:** Efficiently parse multiple documents at once with configurable parallelism.

## Main Features

With this library, you can do things that are otherwise hard to do with the Agentic Document Extraction API alone.
This section describes some of the key features this library offers.

### Parse Large PDF Files

**A single REST API call can only handle up to certain amount of pages at a time** (see [rate limits](https://docs.landing.ai/ade/ade-rate-limits#maximum-pages-per-document)). This library automatically splits a large PDF into multiple calls, uses a thread pool to process the calls in parallel, and stitches the results back together as a single result.

We've used this library to successfully parse PDFs that are 1000+ pages long.

### Parse Multiple Files in a Batch

You can parse multiple files in a single function call with this library. The library processes files in parallel.

> **NOTE:** You can change the parallelism by setting the `batch_size` setting.

### Save Groundings as Images

The library can extract and save the visual regions (groundings) of the document where each chunk of content was found. This is useful for visualizing exactly what parts of the document were extracted and for debugging extraction issues.

Each grounding represents a bounding box in the original document, and the library can save these regions as individual PNG images. The images are organized by page number and chunk ID.

Here's how to use this feature:

```python
from agentic_doc.parse import parse_documents

# Save groundings when parsing a document
results = parse_documents(
    ["path/to/document.pdf"],
    grounding_save_dir="path/to/save/groundings"
)

# The grounding images will be saved to:
# path/to/save/groundings/document_TIMESTAMP/page_X/CHUNK_TYPE_CHUNK_ID_Y.png
# Where X is the page number, CHUNK_ID is the unique ID of each chunk,
# and Y is the index of the grounding within the chunk

# Each chunk's grounding in the result will have the image_path set
for chunk in results[0].chunks:
    for grounding in chunk.grounding:
        if grounding.image_path:
            print(f"Grounding saved to: {grounding.image_path}")
```

This feature works with all parsing functions: `parse_documents`, `parse_and_save_documents`, and `parse_and_save_document`.

### Visualize Parsing Result

The library provides a visualization utility that creates annotated images showing where each chunk of content was extracted from the document. This is useful for:
- Verifying the accuracy of the extraction
- Debugging extraction issues

Here's how to use the visualization feature:

```python
from agentic_doc.parse import parse
from agentic_doc.utils import viz_parsed_document
from agentic_doc.config import VisualizationConfig

# Parse a document
results = parse("path/to/document.pdf")
parsed_doc = results[0]

# Create visualizations with default settings
# The output images have a PIL.Image.Image type
images = viz_parsed_document(
    "path/to/document.pdf",
    parsed_doc,
    output_dir="path/to/save/visualizations"
)

# Or customize the visualization appearance
viz_config = VisualizationConfig(
    thickness=2,  # Thicker bounding boxes
    text_bg_opacity=0.8,  # More opaque text background
    font_scale=0.7,  # Larger text
    # Custom colors for different chunk types
    color_map={
        ChunkType.TITLE: (0, 0, 255),  # Red for titles
        ChunkType.TEXT: (255, 0, 0),  # Blue for regular text
        # ... other chunk types ...
    }
)

images = viz_parsed_document(
    "path/to/document.pdf",
    parsed_doc,
    output_dir="path/to/save/visualizations",
    viz_config=viz_config
)

# The visualization images will be saved as:
# path/to/save/visualizations/document_viz_page_X.png
# Where X is the page number
```

The visualization shows:
- Bounding boxes around each extracted chunk
- Chunk type and index labels
- Different colors for different types of content (titles, text, tables, etc.)
- Semi-transparent text backgrounds for better readability

### Automatically Handle API Errors and Rate Limits with Retries

The REST API endpoint imposes rate limits per API key. This library automatically handles the rate limit error or other intermittent HTTP errors with retries.

For more information, see [Error Handling](#error-handling) and [Configuration Options](#configuration-options).

### Error Handling

This library implements a retry mechanism for handling API failures:

- Retries are performed for these HTTP status codes: 408, 429, 502, 503, 504.
- Exponential backoff with jitter is used for retry wait time.
- The initial retry wait time is 1 second, which increases exponentially.
- Retry will stop after `max_retries` attempts. Exceeding the limit raises an exception and results in a failure for this request.
- Retry wait time is capped at `max_retry_wait_time` seconds.
- Retries include a random jitter of up to 10 seconds to distribute requests and prevent the thundering herd problem.

### Parsing Errors

If the REST API request encounters an unrecoverable error during parsing (either from client-side or server-side), the library includes an [errors](./agentic_doc/common.py#L75) field in the final result for the affected page(s).
Each error contains the error message, error_code and corresponding page number.

## Configuration Options

The library uses a [`Settings`](./agentic_doc/config.py) object to manage configuration. You can customize these settings either through environment variables or a `.env` file:

Below is an example `.env` file that customizes the configurations:

```bash
# Number of files to process in parallel, defaults to 4
BATCH_SIZE=4
# Number of threads used to process parts of each file in parallel, defaults to 5.
MAX_WORKERS=2
# Maximum number of retry attempts for failed intermittent requests, defaults to 100
MAX_RETRIES=80
# Maximum wait time in seconds for each retry, defaults to 60
MAX_RETRY_WAIT_TIME=30
# Logging style for retry, defaults to log_msg
RETRY_LOGGING_STYLE=log_msg
```

### Max Parallelism

The maximum number of parallel requests is determined by multiplying `BATCH_SIZE` × `MAX_WORKERS`.

> **NOTE:** The maximum parallelism allowed by this library is 100.

Specifically, increasing `MAX_WORKERS` can speed up the processing of large individual files, while increasing `BATCH_SIZE` improves throughput when processing multiple files.

> **NOTE:** Your job's maximum processing throughput may be limited by your API rate limit. If your rate limit isn't high enough, you may encounter rate limit errors, which the library will automatically handle through retries.

The optimal values for `MAX_WORKERS` and `BATCH_SIZE` depend on your API rate limit and the latency of each REST API call. For example, if your account has a rate limit of 5 requests per minute, and each REST API call takes approximately 60 seconds to complete, and you're processing a single large file, then `MAX_WORKERS` should be set to 5 and `BATCH_SIZE` to 1.

You can find your REST API latency in the logs. If you want to increase your rate limit, schedule a time to meet with us [here](https://scheduler.zoom.us/d/56i81uc2/landingai-document-extraction).

### Set `RETRY_LOGGING_STYLE`

The `RETRY_LOGGING_STYLE` setting controls how the library logs the retry attempts.

- `log_msg`: Log the retry attempts as a log messages. Each attempt is logged as a separate message. This is the default setting.
- `inline_block`: Print a yellow progress block ('█') on the same line. Each block represents one retry attempt. Choose this if you don't want to see the verbose retry logging message and still want to track the number of retries that have been made.
- `none`: Do not log the retry attempts.


## Troubleshooting & FAQ

### Common Issues
- **API Key Errors:**
  Ensure your API key is correctly set as an environment variable.
- **Rate Limits:**
  The library automatically retries requests if you hit the API rate limit. Adjust `BATCH_SIZE` or `MAX_WORKERS` if you encounter frequent rate limit errors.
- **Parsing Failures:**
  If a document fails to parse, an error chunk will be included in the result, detailing the error message and page index.
- **URL Access Issues:**
  If you're having trouble accessing documents from URLs, check that the URLs are publicly accessible and point to supported file types (PDF or images).

### Note on `include_marginalia` and `include_metadata_in_markdown`

- `include_marginalia`: If True, the parser will attempt to extract and include marginalia (footer notes, page number, etc.) from the document in the output.
- `include_metadata_in_markdown`: If True, the output markdown will include metadata.

Both parameters default to True. You can set them to False to exclude these elements from the output.

#### Example: Using the new parameters

```python
from agentic_doc.parse import parse

results = parse(
    "path/to/document.pdf",
    include_marginalia=False,  # Exclude marginalia from output
    include_metadata_in_markdown=False  # Exclude metadata from markdown
)
```



================================================
FILE: LICENSE
================================================
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.



================================================
FILE: pyproject.toml
================================================
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "agentic-doc"
version = "0.3.1"
description = "A Python library that wraps around VisionAgent document extraction REST API to make documents extraction easy."
authors = ["Landing AI <dev@landing.ai>"]
readme = "README.md"
packages = [{include = "agentic_doc"}]

[tool.poetry.urls]
"Homepage" = "https://va.landing.ai/demo/doc-extraction"
"repository" = "https://github.com/landing-ai/agentic-doc"
"documentation" = "https://github.com/landing-ai/agentic-doc"

[tool.poetry.dependencies]  # main dependency group
python = ">=3.9,<4.0"

tqdm = ">=4.64.0,<5.0.0"
typing_extensions = "4.*"
pydantic = ">=2.8.0"
pydantic-settings = "^2.2.1"
tenacity = ">=8.0.0"
pillow = ">=10.0.0"
pillow-heif = ">=0.17.0"
pypdf = "^5.3.1"
structlog = "^25.2.0"
httpx = "^0.28.1"
pymupdf = "^1.25.5"
opencv-python-headless = "^4.11.0.86"
google-api-python-client = "^2.170.0"
google-auth-oauthlib = "^1.2.2"
google-auth = "^2.40.2"
boto3 = "^1.38.23"
jsonschema = "^4.24.0"
types-jsonschema = "^4.24.0.20250528"
requests = "^2.32.4"
protobuf = "^6.31.1"


[tool.poetry.group.dev.dependencies]
autoflake = "1.*"
pytest = "^7.0.0"
black = ">=23,<25"
isort = "5.*"
responses = "^0.23.1"
mypy = "<1.8.0"
types-requests = "^2.31.0.0"
types-pillow = "^9.5.0.4"
data-science-types = "^0.2.23"
types-tqdm = "^4.65.0.1"
setuptools = ">=70,<79"
mkdocs = "^1.5.3"
mkdocstrings = {extras = ["python"], version = "^0.23.0"}
mkdocs-material = "^9.4.2"
pre-commit = "^3.8.0"
flake8 = "^7.1.2"
reportlab = "^4.3.1"
pytest-xdist = "^3.6.1"

[tool.pytest.ini_options]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"

[tool.black]
exclude = '.vscode|.eggs|venv'
line-length = 88  # suggested by black official site

[tool.isort]
line_length = 88
profile = "black"

[tool.mypy]
plugins = "pydantic.mypy"

exclude = "tests"
show_error_context = true
pretty = true
check_untyped_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
strict_optional = true
strict_equality = true
extra_checks = true
warn_redundant_casts = true
warn_unused_configs = true
warn_unused_ignores = true
warn_return_any = true
show_error_codes = true

[[tool.mypy.overrides]]
ignore_missing_imports = true
module = [
    "cv2.*",
    "pymupdf.*",
]



================================================
FILE: .flake8
================================================
[flake8]
extend-ignore = E501,E203
max-line-length = 88
max-complexity = 15
per-file-ignores = __init__.py:F401



================================================
FILE: agentic_doc/__init__.py
================================================
import logging
import os
import sys

import structlog
from structlog.dev import better_traceback

_LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())

logging.basicConfig(
    format="%(message)s (%(filename)s:%(lineno)d)",
    stream=sys.stdout,
    level=_LOG_LEVEL,
    force=True,
)
# prevent logging during interpreter shutdown
logging.raiseExceptions = False


structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.filter_by_level,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(
            exception_formatter=better_traceback,
            colors=True,
            level_styles={
                "warning": structlog.dev.ConsoleRenderer.get_default_level_styles()[
                    "warning"
                ],
                "error": structlog.dev.ConsoleRenderer.get_default_level_styles()[
                    "error"
                ],
            },
        ),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(_LOG_LEVEL),
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=False,
)



================================================
FILE: agentic_doc/common.py
================================================
import inspect
import time
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

import httpx
from pydantic import BaseModel, Field, create_model


class ChunkType(str, Enum):
    table = "table"
    figure = "figure"
    text = "text"
    marginalia = "marginalia"


class ChunkGroundingBox(BaseModel):
    """
    A bounding box of a chunk.

    The coordinates are in the format of [left, top, right, bottom].
    """

    l: float  # noqa: E741
    t: float
    r: float
    b: float


class ChunkGrounding(BaseModel):
    page: int
    box: ChunkGroundingBox
    # NOTE: image_path doesn't come from the server API, so it's null by default
    image_path: Union[Path, None] = None


class Chunk(BaseModel):
    text: str
    grounding: list[ChunkGrounding]
    chunk_type: ChunkType
    chunk_id: str


class PageError(BaseModel):
    page_num: int
    error: str
    error_code: int


T = TypeVar("T", bound=BaseModel)
VT = TypeVar("VT")


class MetadataType(BaseModel, Generic[VT]):
    value: Optional[VT] = None
    chunk_references: List[str]
    confidence: Optional[float] = None


def create_metadata_model(model: type[BaseModel]) -> type[BaseModel]:
    """
    Recursively creates a new Pydantic model from an existing one,
    replacing all leaf-level field types with MetadataType.
    """
    fields: Dict[str, Any] = {}
    for name, field in model.model_fields.items():
        field_type = field.annotation

        origin = get_origin(field_type)

        # Handle Optional/Union types
        if origin is Union:
            args = get_args(field_type)
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                if inspect.isclass(non_none_type) and issubclass(
                    non_none_type, BaseModel
                ):
                    metadata_type = create_metadata_model(non_none_type)
                    fields[name] = (Optional[metadata_type], Field(default=None))
                else:
                    fields[name] = (
                        Optional[MetadataType[non_none_type]],  # type: ignore[valid-type]
                        Field(default=None),
                    )
                continue

        # Handle lists
        if origin is list:
            inner_type = get_args(field_type)[0]
            if inspect.isclass(inner_type) and issubclass(inner_type, BaseModel):
                metadata_inner_type = create_metadata_model(inner_type)
                fields[name] = (
                    List[metadata_inner_type],  # type: ignore[valid-type]
                    Field(default_factory=list),  # type: ignore[arg-type]
                )
            else:
                fields[name] = (
                    List[MetadataType[inner_type]],  # type: ignore[valid-type]
                    Field(default_factory=list),  # type: ignore[arg-type]
                )
            continue

        # Handle nested models
        if inspect.isclass(field_type) and issubclass(field_type, BaseModel):
            fields[name] = (create_metadata_model(field_type), Field())
        else:
            # Replace primitive leaf with MetadataType[original type]
            fields[name] = (
                MetadataType[field_type],  # type: ignore[valid-type]
                Field(),
            )

    return create_model(f"{model.__name__}Metadata", **fields)


class ParsedDocument(BaseModel, Generic[T]):
    markdown: str
    chunks: list[Chunk]
    extraction: Optional[Union[T, Dict[str, Any]]] = None
    extraction_metadata: Optional[Union[Dict[str, Any], BaseModel]] = None
    start_page_idx: int
    end_page_idx: int
    doc_type: Literal["pdf", "image"]
    result_path: Optional[Path] = None
    errors: list[PageError] = Field(default_factory=list)
    extraction_error: Optional[str] = None


class RetryableError(Exception):
    def __init__(self, response: httpx.Response):
        self.response = response
        self.reason = f"{response.status_code} - {response.text}"

    def __str__(self) -> str:
        return self.reason


class Document(BaseModel):
    file_path: Path = Field(description="The local file path to the document file")
    start_page_idx: int = Field(
        description="The index of the first page in the file", ge=0
    )
    end_page_idx: int = Field(
        description="The index of the last page in the file", ge=0
    )

    def __str__(self) -> str:
        return f"File name: {self.file_path.name}\tPage: [{self.start_page_idx}:{self.end_page_idx}]"


class Timer:
    """A context manager for timing code execution in a thread-safe manner."""

    def __init__(self) -> None:
        self.elapsed = 0.0

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed = time.perf_counter() - self.start



================================================
FILE: agentic_doc/config.py
================================================
import json
import logging
from typing import Literal, Any, Optional, Iterator
import cv2
import structlog
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from agentic_doc.common import ChunkType, T
import warnings

_LOGGER = structlog.get_logger(__name__)
_MAX_PARALLEL_TASKS = 200
# Colors in BGR format (OpenCV uses BGR)
_COLOR_MAP = {
    ChunkType.marginalia: (128, 0, 255),  # Purple for marginalia
    ChunkType.table: (139, 69, 19),  # Brown for tables
    ChunkType.figure: (50, 205, 50),  # Lime green for figures
    ChunkType.text: (255, 0, 0),  # Blue for regular text
}


class ParseConfig:
    """
    Configuration class for the parse function.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        include_marginalia: Optional[bool] = None,
        include_metadata_in_markdown: Optional[bool] = None,
        extraction_model: Optional[type[T]] = None,
        extraction_schema: Optional[dict[str, Any]] = None,
        split_size: Optional[int] = None,
        extraction_split_size: Optional[int] = None,
    ) -> None:
        self.api_key = api_key
        self.include_marginalia = include_marginalia
        self.include_metadata_in_markdown = include_metadata_in_markdown
        self.extraction_model = extraction_model
        self.extraction_schema = extraction_schema
        self.split_size = split_size
        self.extraction_split_size = extraction_split_size


class SettingsOverrides:
    def __init__(self) -> None:
        object.__setattr__(self, "_overrides", {})

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_overrides":
            object.__setattr__(self, name, value)
            return

        warnings.warn(
            (
                "Setting values directly on agentic_doc.config.settings will be "
                "deprecated in a future release. Please, call "
                "parse(..., config=ParseConfig(api_key='xxx')) instead."
            ),
            DeprecationWarning,
        )
        self._overrides[name] = value

    def __getattr__(self, name: str) -> Any:
        if name in self._overrides:
            return self._overrides[name]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        return iter(self._overrides.items())

    def __str__(self) -> str:
        # Create a copy of dict with redacted API key
        settings_dict = get_settings().model_dump()
        if "vision_agent_api_key" in settings_dict:
            settings_dict["vision_agent_api_key"] = (
                settings_dict["vision_agent_api_key"][:5] + "[REDACTED]"
            )
        return f"{json.dumps(settings_dict, indent=2)}"


class Settings(BaseSettings):
    endpoint_host: str = Field(
        default="https://api.va.landing.ai",
        description="The host of the endpoint to use",
    )
    vision_agent_api_key: str = Field(
        description="API key for the vision agent",
        default="",
    )
    batch_size: int = Field(
        default=4,
        description="Number of documents to process in parallel",
        ge=1,
    )
    max_workers: int = Field(
        default=5,
        description="Maximum number of workers to use for parallel processing for each document",
        ge=1,
    )
    max_retries: int = Field(
        default=100,
        description="Maximum number of retries for a failed request",
        ge=0,
    )
    max_retry_wait_time: int = Field(
        default=60,
        description="Maximum wait time for a retry",
        ge=0,
    )
    retry_logging_style: Literal["none", "log_msg", "inline_block"] = Field(
        default="log_msg",
        description="Logging style for retries",
    )
    pdf_to_image_dpi: int = Field(
        default=96,
        description="DPI for converting PDF pages to images",
        ge=1,
    )
    split_size: int = Field(
        default=10,
        description="Pages per chunk for splitting the document",
        ge=1,
        le=100,
    )
    extraction_split_size: int = Field(
        default=50,
        description="Pages per chunk for splitting the document when field extraction is enabled",
        ge=1,
        le=50,
    )
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    def __str__(self) -> str:
        # Create a copy of dict with redacted API key
        settings_dict = self.model_dump()
        if "vision_agent_api_key" in settings_dict:
            settings_dict["vision_agent_api_key"] = (
                settings_dict["vision_agent_api_key"][:5] + "[REDACTED]"
            )
        return f"{json.dumps(settings_dict, indent=2)}"


# Global settings instance to hold overrides
# This is a temporary solution to avoid breaking changes in the API, since there
# are users doing `agentic_doc.config.settings.vision_agent_api_key = 'xxx'` today.
# The internal code should use `get_settings()` to retrieve the default settings instance,
# and end users should call `parse(..., settings=Settings(api_key='xxx'))` to override
# the global "env-vars-based" settings.
settings = SettingsOverrides()


def get_settings() -> Settings:
    """
    Get the settings instance, applying any overrides set on the settings global object.
    """
    new_settings = Settings()
    for k, v in settings:
        setattr(new_settings, k, v)
    return new_settings


_LOGGER.info(f"Settings loaded: {settings}")

if get_settings().batch_size * get_settings().max_workers > _MAX_PARALLEL_TASKS:
    raise ValueError(
        f"Batch size * max workers must be less than {_MAX_PARALLEL_TASKS}."
        " Please reduce the batch size or max workers."
        " Current settings: batch_size={settings.batch_size}, max_workers={settings.max_workers}"
    )
if get_settings().retry_logging_style == "inline_block":
    logging.getLogger("httpx").setLevel(logging.WARNING)


class VisualizationConfig(BaseSettings):
    thickness: int = Field(
        default=1,
        description="Thickness of the bounding box and text",
        ge=0,
    )
    text_bg_color: tuple[int, int, int] = Field(
        default=(211, 211, 211),  # Light gray
        description="Background color of the text, in BGR format",
    )
    text_bg_opacity: float = Field(
        default=0.7,
        description="Opacity of the text background",
        ge=0.0,
        le=1.0,
    )
    padding: int = Field(
        default=1,
        description="Padding of the text background box",
        ge=0,
    )
    font_scale: float = Field(
        default=0.5,
        description="Font scale of the text",
        ge=0.0,
    )
    font: int = Field(
        default=cv2.FONT_HERSHEY_SIMPLEX,
        description="Font of the text",
    )
    color_map: dict[ChunkType, tuple[int, int, int]] = Field(
        default=_COLOR_MAP,
        description="Color map for each chunk type",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )



================================================
FILE: agentic_doc/connectors.py
================================================
import fnmatch
import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import httpx
import structlog
from pydantic import BaseModel

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

import boto3  # type: ignore
from botocore.client import ClientCreator  # type: ignore
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseDownload  # type: ignore

_LOGGER = structlog.getLogger(__name__)


class ConnectorConfig(BaseModel):
    """Base configuration for connectors."""

    connector_type: str


class LocalConnectorConfig(ConnectorConfig):
    """Configuration for local file connector."""

    connector_type: str = "local"
    recursive: bool = False


class GoogleDriveConnectorConfig(ConnectorConfig):
    """Configuration for Google Drive connector."""

    connector_type: str = "google_drive"
    client_secret_file: Optional[str] = None
    folder_id: Optional[str] = None


class S3ConnectorConfig(ConnectorConfig):
    """Configuration for S3 connector."""

    connector_type: str = "s3"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    region_name: str = "us-east-1"
    bucket_name: str


class URLConnectorConfig(ConnectorConfig):
    """Configuration for URL connector."""

    connector_type: str = "url"
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30


class BaseConnector(ABC):
    """Abstract base class for document connectors."""

    _VALID_EXTENSIONS = [
        ".bmp",
        ".dib",
        ".dcx",
        ".eps",
        ".ps",
        ".gif",
        ".icns",
        ".ico",
        ".im",
        ".jpeg",
        ".jpg",
        ".jpe",
        ".pcd",
        ".pcx",
        ".png",
        ".pbm",
        ".pgm",
        ".ppm",
        ".pnm",
        ".sgi",
        ".rgb",
        ".rgba",
        ".bw",
        ".spider",
        ".tga",
        ".targa",
        ".tif",
        ".tiff",
        ".webp",
        ".xbm",
        ".jp2",
        ".j2k",
        ".jpf",
        ".jpx",
        ".j2c",
        ".pdf",
        ".heif",
        ".heic",
    ]

    def __init__(self, config: ConnectorConfig):
        self.config = config

    @abstractmethod
    def list_files(
        self, path: Optional[str] = None, pattern: Optional[str] = None
    ) -> List[str]:
        """
        List available files from the connector.

        Args:
            path: Optional base path to list files from.
            pattern: Optional glob-style pattern to filter results (ignored for URL connectors).

        Returns:
            A list of file identifiers or paths.
        """
        pass

    @abstractmethod
    def download_file(self, file_id: str, local_path: Optional[str] = None) -> Path:
        """
        Download a file to local storage.

        Args:
            file_id: Identifier for the file to download. Format varies by connector:
                - Local: File system path (e.g., "/path/to/file.pdf")
                - Google Drive: Google Drive file ID (e.g., "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
                - S3: S3 object key/path (e.g., "documents/report.pdf")
                - URL: Complete HTTP/HTTPS URL (e.g., "https://example.com/file.pdf")
            local_path: Optional local path to save to

        Returns:
            Path to the downloaded file

        Note:
            Use list_files() to get valid file_id values for each connector type.
        """
        pass

    @abstractmethod
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata about a file.

        Args:
            file_id: Identifier for the file

        Returns:
            Dictionary containing file metadata
        """
        pass


class LocalConnector(BaseConnector):
    """Connector for local files."""

    def __init__(self, config: LocalConnectorConfig):
        super().__init__(config)
        self.config: LocalConnectorConfig = config

    def list_files(
        self, path: Optional[str] = None, pattern: Optional[str] = None
    ) -> List[str]:
        """List local files."""
        search_path = Path(path) if path else Path.cwd()

        if not search_path.exists():
            raise FileNotFoundError(f"Path does not exist: {search_path}")

        if search_path.is_file():
            return [str(search_path)]

        globber = search_path.rglob if self.config.recursive else search_path.glob
        if pattern:
            files = list(globber(pattern))
        else:
            files = [
                f
                for f in globber("*")
                if f.is_file() and f.suffix.lower() in LocalConnector._VALID_EXTENSIONS
            ]

        return [str(f) for f in files if f.is_file()]

    def download_file(self, file_id: str, local_path: Optional[str] = None) -> Path:
        """For local files, just return the path if it exists."""
        file_path = Path(file_id)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get local file metadata."""
        file_path = Path(file_id)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = file_path.stat()
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "suffix": file_path.suffix,
        }


class GoogleDriveConnector(BaseConnector):
    """Connector for Google Drive files."""

    def __init__(self, config: GoogleDriveConnectorConfig):
        super().__init__(config)
        self.config: GoogleDriveConnectorConfig = config
        self._service: Optional[Resource] = None

    def _get_service(self) -> Resource:
        """Initialize Google Drive service with user-friendly OAuth."""
        if self._service is None:
            scopes = ["https://www.googleapis.com/auth/drive.readonly"]
            creds = None

            # Check if we have stored credentials
            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json", scopes)

            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if self.config.client_secret_file:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.config.client_secret_file, scopes=scopes
                        )
                        creds = flow.run_local_server(port=0)
                    else:
                        raise ValueError("client_secret_file must be provided")

                # Save credentials for next time
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

            self._service = build("drive", "v3", credentials=creds)
        return self._service

    def list_files(
        self, path: Optional[str] = None, pattern: Optional[str] = None
    ) -> List[str]:
        """List files in Google Drive"""
        service = self._get_service()

        # Build query
        query_parts = []
        if self.config.folder_id:
            query_parts.append(f"'{self.config.folder_id}' in parents")
        elif path:
            query_parts.append(f"'{path}' in parents")

        # Filter by file types
        file_types = ["mimeType='application/pdf'", "mimeType contains 'image/'"]
        query_parts.append(f"({' or '.join(file_types)})")

        query = " and ".join(query_parts)

        try:
            results = (
                service.files()
                .list(q=query, fields="files(id, name, mimeType, size)")
                .execute()
            )
            files = results.get("files", [])

            # Apply glob pattern filtering
            if pattern:
                files = [f for f in files if fnmatch.fnmatch(f["name"], pattern)]

            return [file["id"] for file in files]
        except Exception as e:
            _LOGGER.error(f"Error listing Google Drive files: {e}")
            raise

    def download_file(self, file_id: str, local_path: Optional[str] = None) -> Path:
        """Download file from Google Drive."""
        service = self._get_service()

        try:
            # Get file metadata
            file_metadata = service.files().get(fileId=file_id).execute()
            file_name = file_metadata["name"]

            # Create local path if not provided
            if local_path is None:
                temp_dir = tempfile.mkdtemp()
                local_path_obj: Path = Path(temp_dir) / file_name
            else:
                local_path_obj = Path(local_path)
                local_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            request = service.files().get_media(fileId=file_id)
            with open(local_path_obj, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

            _LOGGER.info(f"Downloaded Google Drive file {file_id} to {local_path_obj}")
            return local_path_obj

        except Exception as e:
            _LOGGER.error(f"Error downloading Google Drive file {file_id}: {e}")
            raise

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get Google Drive file metadata."""
        service = self._get_service()

        try:
            file_metadata = (
                service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, mimeType, size, createdTime, modifiedTime",
                )
                .execute()
            )

            return {
                "id": file_metadata["id"],
                "name": file_metadata["name"],
                "mimeType": file_metadata["mimeType"],
                "size": int(file_metadata.get("size", 0)),
                "created": file_metadata.get("createdTime"),
                "modified": file_metadata.get("modifiedTime"),
            }

        except Exception as e:
            _LOGGER.error(f"Error getting Google Drive file info for {file_id}: {e}")
            raise


class S3Connector(BaseConnector):
    """Connector for Amazon S3 files."""

    def __init__(self, config: S3ConnectorConfig):
        super().__init__(config)
        self.config: S3ConnectorConfig = config
        self._client: Optional[ClientCreator] = None

    def _get_client(self) -> ClientCreator:
        """Initialize S3 client if not already done."""
        if self._client is None:
            kwargs = {"region_name": self.config.region_name}

            if self.config.aws_access_key_id:
                kwargs["aws_access_key_id"] = self.config.aws_access_key_id
            if self.config.aws_secret_access_key:
                kwargs["aws_secret_access_key"] = self.config.aws_secret_access_key
            if self.config.aws_session_token:
                kwargs["aws_session_token"] = self.config.aws_session_token

            self._client = boto3.client("s3", **kwargs)

        return self._client

    def list_files(
        self, path: Optional[str] = None, pattern: Optional[str] = None
    ) -> List[str]:
        """List files in S3 bucket"""
        client = self._get_client()

        try:
            kwargs = {"Bucket": self.config.bucket_name}
            if path:
                kwargs["Prefix"] = path

            response = client.list_objects_v2(**kwargs)

            files = []
            for obj in response.get("Contents", []):
                key = obj["Key"]

                # Filter by file extension (documents and images)
                if any(
                    key.lower().endswith(ext) for ext in S3Connector._VALID_EXTENSIONS
                ):
                    # Apply glob pattern filtering
                    if not pattern or fnmatch.fnmatch(key, pattern):
                        files.append(key)

            return files

        except Exception as e:
            _LOGGER.error(f"Error listing S3 files: {e}")
            raise

    def download_file(self, file_id: str, local_path: Optional[str] = None) -> Path:
        """Download file from S3."""
        client = self._get_client()

        try:
            # Create local path if not provided
            if local_path is None:
                temp_dir = tempfile.mkdtemp()
                file_name = Path(file_id).name
                local_path_obj = Path(temp_dir) / file_name
            else:
                local_path_obj = Path(local_path)
                local_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            client.download_file(self.config.bucket_name, file_id, str(local_path_obj))

            _LOGGER.info(f"Downloaded S3 file {file_id} to {local_path_obj}")
            return local_path_obj

        except Exception as e:
            _LOGGER.error(f"Error downloading S3 file {file_id}: {e}")
            raise

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get S3 file metadata."""
        client = self._get_client()

        try:
            response = client.head_object(Bucket=self.config.bucket_name, Key=file_id)

            return {
                "key": file_id,
                "size": response["ContentLength"],
                "last_modified": response["LastModified"],
                "etag": response["ETag"],
                "content_type": response.get("ContentType"),
            }

        except Exception as e:
            _LOGGER.error(f"Error getting S3 file info for {file_id}: {e}")
            raise


class URLConnector(BaseConnector):
    """Connector for files accessible via HTTP/HTTPS URLs."""

    def __init__(self, config: URLConnectorConfig):
        super().__init__(config)
        self.config: URLConnectorConfig = config

    def list_files(
        self, path: Optional[str] = None, pattern: Optional[str] = None
    ) -> List[str]:
        """For URL connector, just return the provided path as a single file."""
        if path:
            return [path]
        return []

    def download_file(self, file_id: str, local_path: Optional[str] = None) -> Path:
        """Download file from URL."""
        try:
            # Create local path if not provided
            if local_path is None:
                temp_dir = tempfile.mkdtemp()
                file_name = Path(file_id).name or "downloaded_file"
                local_path_obj = Path(temp_dir) / file_name
            else:
                local_path_obj = Path(local_path)
                local_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            headers = self.config.headers or {}

            with httpx.stream(
                "GET", file_id, headers=headers, timeout=self.config.timeout
            ) as response:
                response.raise_for_status()

                with open(local_path_obj, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            _LOGGER.info(f"Downloaded URL {file_id} to {local_path_obj}")
            return local_path_obj

        except Exception as e:
            _LOGGER.error(f"Error downloading URL {file_id}: {e}")
            raise

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get file info from URL headers."""
        try:
            headers = self.config.headers or {}

            response = httpx.head(file_id, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            return {
                "url": file_id,
                "content_length": response.headers.get("content-length"),
                "content_type": response.headers.get("content-type"),
                "last_modified": response.headers.get("last-modified"),
            }

        except Exception as e:
            _LOGGER.error(f"Error getting URL file info for {file_id}: {e}")
            raise


def create_connector(config: ConnectorConfig) -> BaseConnector:
    """Factory function to create appropriate connector based on config type."""
    connector_map: Dict[str, Type[BaseConnector]] = {
        "local": LocalConnector,
        "google_drive": GoogleDriveConnector,
        "s3": S3Connector,
        "url": URLConnector,
    }

    connector_class = connector_map.get(config.connector_type)
    if not connector_class:
        raise ValueError(f"Unknown connector type: {config.connector_type}")

    return connector_class(config)



================================================
FILE: agentic_doc/parse.py
================================================
import copy
import importlib.metadata
import json
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import httpx
import structlog
import tenacity
from pydantic_core import Url
from tqdm import tqdm
import jsonschema
from pypdf import PdfReader

from agentic_doc.common import (
    Document,
    PageError,
    ParsedDocument,
    RetryableError,
    T,
    Timer,
    create_metadata_model,
)
from agentic_doc.config import Settings, get_settings, ParseConfig
from agentic_doc.connectors import BaseConnector, ConnectorConfig, create_connector
from agentic_doc.utils import (
    check_endpoint_and_api_key,
    download_file,
    get_file_type,
    is_valid_httpurl,
    log_retry_failure,
    save_groundings_as_images,
    split_pdf,
)

_LOGGER = structlog.getLogger(__name__)
_LIB_VERSION = importlib.metadata.version("agentic-doc")


def _get_endpoint_url(settings: Settings) -> str:
    return f"{settings.endpoint_host}/v1/tools/agentic-document-analysis"


def parse(
    documents: Union[
        bytes,
        str,
        Path,
        Url,
        List[Union[str, Path, Url]],
        BaseConnector,
        ConnectorConfig,
    ],
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    result_save_dir: Optional[Union[str, Path]] = None,
    grounding_save_dir: Optional[Union[str, Path]] = None,
    connector_path: Optional[str] = None,
    connector_pattern: Optional[str] = None,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> List[ParsedDocument[T]]:
    """
    Universal parse function that can handle single documents, lists of documents,
    or documents from various connectors.

    Args:
        documents: Can be:
            - Single document path/URL (str, Path, Url)
            - List of document paths/URLs
            - Connector instance (BaseConnector)
            - Connector configuration (ConnectorConfig)
            - Raw bytes of a document (either PDF or Image bytes)
        include_marginalia: Whether to include marginalia in the analysis
        include_metadata_in_markdown: Whether to include metadata in markdown output
        result_save_dir: Directory to save results
        grounding_save_dir: Directory to save grounding images
        connector_path: Path for connector to search (when using connectors)
        connector_pattern: Pattern to filter files (when using connectors)
        extraction_model: Pydantic model schema for field extraction (optional)
        extraction_schema: JSON schema for field extraction (optional)

    Returns:
        List[ParsedDocument]
    """
    settings = get_settings()
    if config and config.include_marginalia:
        include_marginalia = config.include_marginalia
    if config and config.include_metadata_in_markdown:
        include_metadata_in_markdown = config.include_metadata_in_markdown
    if config and config.extraction_model:
        extraction_model = config.extraction_model
    if config and config.extraction_schema:
        extraction_schema = config.extraction_schema

    check_endpoint_and_api_key(
        _get_endpoint_url(settings),
        api_key=(
            config.api_key
            if config and config.api_key
            else settings.vision_agent_api_key
        ),
    )

    # Convert input to list of document paths
    doc_paths = _get_document_paths(documents, connector_path, connector_pattern)

    if not doc_paths:
        _LOGGER.warning("No documents to parse")
        return []

    if extraction_schema and extraction_model:
        raise ValueError(
            "extraction_model and extraction_schema cannot be used together, you must provide only one of them"
        )

    # Parse all documents
    parse_results = _parse_document_list(
        doc_paths,
        include_marginalia=include_marginalia,
        include_metadata_in_markdown=include_metadata_in_markdown,
        result_save_dir=result_save_dir,
        grounding_save_dir=grounding_save_dir,
        extraction_model=extraction_model,
        extraction_schema=extraction_schema,
        config=config,
    )

    # Convert results to ParsedDocument objects
    return _convert_to_parsed_documents(parse_results, result_save_dir)


def _get_document_paths(
    documents: Union[
        bytes,
        str,
        Path,
        Url,
        List[Union[str, Path, Url]],
        BaseConnector,
        ConnectorConfig,
    ],
    connector_path: Optional[str] = None,
    connector_pattern: Optional[str] = None,
) -> Sequence[Union[str, Path, Url]]:
    """Convert various input types to a list of document paths."""
    if isinstance(documents, (BaseConnector, ConnectorConfig)):
        return _get_paths_from_connector(documents, connector_path, connector_pattern)
    elif isinstance(documents, (str, Path, Url)):
        return [documents]
    elif isinstance(documents, list):
        return documents
    elif isinstance(documents, bytes):
        return _get_documents_from_bytes(documents)
    else:
        raise ValueError(f"Unsupported documents type: {type(documents)}")


def _get_paths_from_connector(
    connector_or_config: Union[BaseConnector, ConnectorConfig],
    connector_path: Optional[str],
    connector_pattern: Optional[str],
) -> List[Path]:
    """Download files from connector and return local paths."""
    connector = (
        connector_or_config
        if isinstance(connector_or_config, BaseConnector)
        else create_connector(connector_or_config)
    )

    file_list = connector.list_files(connector_path, connector_pattern)
    if not file_list:
        return []

    local_paths = []
    for file_id in file_list:
        try:
            local_path = connector.download_file(file_id)
            local_paths.append(local_path)
        except Exception as e:
            _LOGGER.error(f"Failed to download file {file_id}: {e}")

    return local_paths


def _get_documents_from_bytes(doc_bytes: bytes) -> List[Path]:
    """Save raw bytes to a temporary file and return its path."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(doc_bytes)
        temp_file_path = Path(temp_file.name)
    return [temp_file_path]


def _convert_to_parsed_documents(
    parse_results: Union[List[ParsedDocument[T]], List[Path]],
    result_save_dir: Optional[Union[str, Path]],
) -> List[ParsedDocument[T]]:
    """Convert parse results to ParsedDocument objects."""
    parsed_docs = []

    for result in parse_results:
        if isinstance(result, ParsedDocument):
            parsed_docs.append(result)
        elif isinstance(result, Path):
            with open(result, encoding="utf-8") as f:
                data = json.load(f)
            parsed_doc: ParsedDocument[T] = ParsedDocument.model_validate(data)
            if result_save_dir:
                parsed_doc.result_path = result
            parsed_docs.append(parsed_doc)
        else:
            raise ValueError(f"Unexpected result type: {type(result)}")

    return parsed_docs


def _parse_document_list(
    documents: Sequence[Union[str, Path, Url]],
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    result_save_dir: Optional[Union[str, Path]] = None,
    grounding_save_dir: Optional[Union[str, Path]] = None,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> Union[List[ParsedDocument[T]], List[Path]]:
    """Helper function to parse a list of documents."""
    documents_list = list(documents)
    if result_save_dir:
        return parse_and_save_documents(
            documents_list,
            result_save_dir=result_save_dir,
            grounding_save_dir=grounding_save_dir,
            include_marginalia=include_marginalia,
            include_metadata_in_markdown=include_metadata_in_markdown,
            extraction_model=extraction_model,
            extraction_schema=extraction_schema,
            config=config,
        )
    else:
        return parse_documents(
            documents_list,
            include_marginalia=include_marginalia,
            include_metadata_in_markdown=include_metadata_in_markdown,
            grounding_save_dir=grounding_save_dir,
            extraction_model=extraction_model,
            extraction_schema=extraction_schema,
            config=config,
        )


def parse_documents(
    documents: list[Union[str, Path, Url]],
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    grounding_save_dir: Union[str, Path, None] = None,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> list[ParsedDocument[T]]:
    """
    Parse a list of documents using the Landing AI Agentic Document Analysis API.

    Args:
        documents (list[str | Path | Url]): The list of documents to parse. Each document can be a local file path, a URL string, or a Pydantic `Url` object.
        grounding_save_dir (str | Path): The local directory to save the grounding images.
        extraction_model (type[BaseModel] | None): Schema for field extraction.
    Returns:
        list[ParsedDocument]: The list of parsed documents. The list is sorted by the order of the input documents.
    """
    _LOGGER.info(f"Parsing {len(documents)} documents")
    _parse_func: Callable[[Union[str, Path, Url]], ParsedDocument[T]] = partial(
        _parse_document_without_save,
        include_marginalia=include_marginalia,
        include_metadata_in_markdown=include_metadata_in_markdown,
        grounding_save_dir=grounding_save_dir,
        extraction_model=extraction_model,
        extraction_schema=extraction_schema,
        config=config,
    )
    with ThreadPoolExecutor(max_workers=get_settings().batch_size) as executor:
        return list(
            tqdm(
                executor.map(_parse_func, documents),
                total=len(documents),
                desc="Parsing documents",
            )
        )


def _parse_document_without_save(
    document: Union[str, Path, Url],
    include_marginalia: bool,
    include_metadata_in_markdown: bool,
    grounding_save_dir: Union[str, Path, None],
    extraction_model: Optional[type[T]],
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> ParsedDocument[T]:
    """Wrapper to ensure parse_and_save_document returns ParsedDocument when no save dir."""
    result = parse_and_save_document(
        document,
        include_marginalia=include_marginalia,
        include_metadata_in_markdown=include_metadata_in_markdown,
        result_save_dir=None,
        grounding_save_dir=grounding_save_dir,
        extraction_model=extraction_model,
        extraction_schema=extraction_schema,
        config=config,
    )
    # When result_save_dir is None, parse_and_save_document returns ParsedDocument[T]
    assert isinstance(result, ParsedDocument)
    return result


def parse_and_save_documents(
    documents: list[Union[str, Path, Url]],
    *,
    result_save_dir: Union[str, Path],
    grounding_save_dir: Union[str, Path, None] = None,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> list[Path]:
    """
    Parse a list of documents and save the results to a local directory.

    Args:
        documents (list[str | Path | Url]): The list of documents to parse. Each document can be a local file path, a URL string, or a Pydantic `Url` object.
        result_save_dir (str | Path): The local directory to save the results.
        grounding_save_dir (str | Path): The local directory to save the grounding images.
        extraction_model (type[BaseModel] | None): Schema for field extraction.
    Returns:
        list[Path]: A list of json file paths to the saved results. The file paths are sorted by the order of the input file paths.
            The file name is the original file name with a timestamp appended. E.g. "document.pdf" -> "document_20250313_123456.json".
    """
    _LOGGER.info(f"Parsing {len(documents)} documents")

    _parse_func: Callable[[Union[str, Path, Url]], Path] = partial(
        _parse_document_with_save,
        include_marginalia=include_marginalia,
        include_metadata_in_markdown=include_metadata_in_markdown,
        result_save_dir=result_save_dir,
        grounding_save_dir=grounding_save_dir,
        extraction_model=extraction_model,
        extraction_schema=extraction_schema,
        config=config,
    )
    with ThreadPoolExecutor(max_workers=get_settings().batch_size) as executor:
        return list(
            tqdm(
                executor.map(_parse_func, documents),
                total=len(documents),
                desc="Parsing documents",
            )
        )


def _parse_document_with_save(
    document: Union[str, Path, Url],
    include_marginalia: bool,
    include_metadata_in_markdown: bool,
    result_save_dir: Union[str, Path],
    grounding_save_dir: Union[str, Path, None],
    extraction_model: Optional[type[T]],
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> Path:
    """Wrapper to ensure parse_and_save_document returns Path when save dir provided."""
    result = parse_and_save_document(
        document,
        include_marginalia=include_marginalia,
        include_metadata_in_markdown=include_metadata_in_markdown,
        result_save_dir=result_save_dir,
        grounding_save_dir=grounding_save_dir,
        extraction_model=extraction_model,
        extraction_schema=extraction_schema,
        config=config,
    )
    # When result_save_dir is provided, parse_and_save_document returns Path
    assert isinstance(result, Path)
    return result


def parse_and_save_document(
    document: Union[str, Path, Url],
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    result_save_dir: Union[str, Path, None] = None,
    grounding_save_dir: Union[str, Path, None] = None,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> Union[Path, ParsedDocument[T]]:
    """
    Parse a document and save the results to a local directory.

    Args:
        document (str | Path | Url): The document to parse. It can be a local file path, a URL string, or a Pydantic `Url` object.
        result_save_dir (str | Path): The local directory to save the results. If None, the parsed document data is returned.
        extraction_model (type[BaseModel] | None): Schema for field extraction.
    Returns:
        Path | ParsedDocument: The file path to the saved result or the parsed document data.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        if isinstance(document, str) and is_valid_httpurl(document):
            document = Url(document)

        if isinstance(document, Url):
            output_file_path = Path(temp_dir) / Path(str(document)).name
            download_file(document, str(output_file_path))
            document = output_file_path
        else:
            document = Path(document)
            if isinstance(document, Path) and not document.exists():
                raise FileNotFoundError(f"File not found: {document}")

        file_type = get_file_type(document)

        if file_type == "image":
            result = _parse_image(
                document,
                include_marginalia=include_marginalia,
                include_metadata_in_markdown=include_metadata_in_markdown,
                extraction_model=extraction_model,
                extraction_schema=extraction_schema,
                config=config,
            )
        elif file_type == "pdf":
            result = _parse_pdf(
                document,
                include_marginalia=include_marginalia,
                include_metadata_in_markdown=include_metadata_in_markdown,
                extraction_model=extraction_model,
                extraction_schema=extraction_schema,
                config=config,
            )
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_name = f"{Path(document).stem}_{ts}"
        if grounding_save_dir:
            grounding_save_dir = Path(grounding_save_dir) / result_name
            save_groundings_as_images(
                document, result.chunks, grounding_save_dir, inplace=True
            )
        if not result_save_dir:
            return result

        result_save_dir = Path(result_save_dir)
        result_save_dir.mkdir(parents=True, exist_ok=True)
        save_path = result_save_dir / f"{result_name}.json"
        save_path.write_text(result.model_dump_json(), encoding="utf-8")
        _LOGGER.info(f"Saved the parsed result to '{save_path}'")

        return save_path


def _parse_pdf(
    file_path: Union[str, Path],
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> ParsedDocument[T]:
    settings = get_settings()
    with tempfile.TemporaryDirectory() as temp_dir:
        if extraction_model or extraction_schema is not None:
            total_pages = 0
            with open(file_path, "rb") as file:
                reader = PdfReader(file)
                total_pages = len(reader.pages)
            split_size = (
                config.extraction_split_size
                if config and config.extraction_split_size
                else settings.extraction_split_size
            )
            if total_pages > split_size:
                raise ValueError(
                    f"Document has {total_pages} pages, which exceeds the maximum of {settings.extraction_split_size} pages "
                    "allowed when using field extraction. "
                    f"Please use a document with {split_size} pages or fewer."
                )
        else:
            split_size = (
                config.split_size
                if config and config.split_size
                else settings.split_size
            )

        parts = split_pdf(file_path, temp_dir, split_size)
        file_path = Path(file_path)
        part_results = _parse_doc_in_parallel(
            parts,
            doc_name=file_path.name,
            include_marginalia=include_marginalia,
            include_metadata_in_markdown=include_metadata_in_markdown,
            extraction_model=extraction_model,
            extraction_schema=extraction_schema,
            config=config,
        )
        return _merge_part_results(part_results)


def _parse_image(
    file_path: Union[str, Path],
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> ParsedDocument[T]:
    try:
        result_raw = _send_parsing_request(
            str(file_path),
            include_marginalia=include_marginalia,
            include_metadata_in_markdown=include_metadata_in_markdown,
            extraction_model=extraction_model,
            extraction_schema=extraction_schema,
            config=config,
        )
        result_raw = {
            **result_raw["data"],
            "errors": result_raw.get("errors", []),
            "extraction_error": result_raw.get("extraction_error", None),
            "doc_type": "image",
            "start_page_idx": 0,
            "end_page_idx": 0,
        }

        # Handle extraction validation and assignment
        if (
            extraction_model
            and "extracted_schema" in result_raw
            and result_raw["extracted_schema"]
        ):
            result_raw["extraction"] = extraction_model.model_validate(
                result_raw["extracted_schema"]
            )
        elif (
            extraction_schema
            and "extracted_schema" in result_raw
            and result_raw["extracted_schema"]
        ):
            jsonschema.validate(
                instance=result_raw["extracted_schema"],
                schema=extraction_schema,
            )
            result_raw["extraction"] = result_raw["extracted_schema"]

        if (
            extraction_model
            and "extraction_metadata" in result_raw
            and result_raw["extraction_metadata"]
        ):
            metadata_model = create_metadata_model(extraction_model)
            result_raw["extraction_metadata"] = metadata_model.model_validate(
                result_raw["extraction_metadata"]
            )

        if extraction_schema:
            return ParsedDocument[Any].model_validate(result_raw)
        else:
            return ParsedDocument.model_validate(result_raw)
    except Exception as e:
        error_msg = str(e)
        _LOGGER.error(f"Error parsing image '{file_path}' due to: {error_msg}")
        return ParsedDocument(
            markdown="",
            chunks=[],
            extraction_metadata=None,
            extraction=None,
            start_page_idx=0,
            end_page_idx=0,
            doc_type="image",
            result_path=None,
            errors=[PageError(page_num=0, error=error_msg, error_code=-1)],
        )


def _merge_part_results(results: list[ParsedDocument[T]]) -> ParsedDocument[T]:
    if not results:
        _LOGGER.warning(
            f"No results to merge: {results}, returning empty ParsedDocument"
        )
        return ParsedDocument(
            markdown="",
            chunks=[],
            extraction_metadata=None,
            extraction=None,
            start_page_idx=0,
            end_page_idx=0,
            doc_type="pdf",
            result_path=None,
        )

    init_result = copy.deepcopy(results[0])
    for i in range(1, len(results)):
        _merge_next_part(init_result, results[i])

    return init_result


def _merge_next_part(curr: ParsedDocument[T], next: ParsedDocument[T]) -> None:
    curr.markdown += "\n\n" + next.markdown
    next_chunks = next.chunks
    for chunk in next_chunks:
        for grounding in chunk.grounding:
            grounding.page += next.start_page_idx

    curr.chunks.extend(next_chunks)
    curr.end_page_idx = next.end_page_idx
    curr.errors.extend(next.errors)


def _parse_doc_in_parallel(
    doc_parts: list[Document],
    *,
    doc_name: str,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> list[ParsedDocument[T]]:
    _parse_func: Callable[[Document], ParsedDocument[T]] = partial(
        _parse_doc_parts,
        include_marginalia=include_marginalia,
        include_metadata_in_markdown=include_metadata_in_markdown,
        extraction_model=extraction_model,
        extraction_schema=extraction_schema,
        config=config,
    )
    with ThreadPoolExecutor(max_workers=get_settings().max_workers) as executor:
        return list(
            tqdm(
                executor.map(_parse_func, doc_parts),
                total=len(doc_parts),
                desc=f"Parsing document parts from '{doc_name}'",
            )
        )


def _parse_doc_parts(
    doc: Document,
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> ParsedDocument[T]:
    try:
        _LOGGER.info(f"Start parsing document part: '{doc}'")
        result = _send_parsing_request(
            str(doc.file_path),
            include_marginalia=include_marginalia,
            include_metadata_in_markdown=include_metadata_in_markdown,
            extraction_model=extraction_model,
            extraction_schema=extraction_schema,
            config=config,
        )
        _LOGGER.info(f"Successfully parsed document part: '{doc}'")
        result_data = {
            **result["data"],
            "errors": result.get("errors", []),
            "extraction_error": result.get("extraction_error", None),
            "start_page_idx": doc.start_page_idx,
            "end_page_idx": doc.end_page_idx,
            "doc_type": "pdf",
        }

        if (
            extraction_model
            and "extracted_schema" in result_data
            and result_data["extracted_schema"]
        ):
            result_data["extraction"] = extraction_model.model_validate(
                result_data["extracted_schema"]
            )
        elif (
            extraction_schema
            and "extracted_schema" in result_data
            and result_data["extracted_schema"]
        ):
            jsonschema.validate(
                instance=result_data["extracted_schema"],
                schema=extraction_schema,
            )
            result_data["extraction"] = result_data["extracted_schema"]

        if (
            extraction_model
            and "extraction_metadata" in result_data
            and result_data["extraction_metadata"]
        ):
            metadata_model = create_metadata_model(extraction_model)
            result_data["extraction_metadata"] = metadata_model.model_validate(
                result_data["extraction_metadata"]
            )

        if extraction_schema:
            return ParsedDocument[Any].model_validate(result_data)
        else:
            return ParsedDocument.model_validate(result_data)
    except Exception as e:
        error_msg = str(e)
        _LOGGER.error(f"Error parsing document '{doc}' due to: {error_msg}")
        errors = [
            PageError(page_num=i, error=error_msg, error_code=-1)
            for i in range(doc.start_page_idx, doc.end_page_idx + 1)
        ]
        return ParsedDocument(
            markdown="",
            chunks=[],
            extraction_metadata=None,
            extraction=None,
            start_page_idx=doc.start_page_idx,
            end_page_idx=doc.end_page_idx,
            doc_type="pdf",
            result_path=Path(doc.file_path),
            errors=errors,
        )


# TODO: read retry settings at runtime (not at import time)
@tenacity.retry(
    wait=tenacity.wait_exponential_jitter(
        exp_base=1.5, initial=1, max=get_settings().max_retry_wait_time, jitter=10
    ),
    stop=tenacity.stop_after_attempt(get_settings().max_retries),
    retry=tenacity.retry_if_exception_type(RetryableError),
    after=log_retry_failure,
)
def _send_parsing_request(
    file_path: str,
    *,
    include_marginalia: bool = True,
    include_metadata_in_markdown: bool = True,
    extraction_model: Optional[type[T]] = None,
    extraction_schema: Optional[dict[str, Any]] = None,
    config: Optional[ParseConfig] = None,
) -> dict[str, Any]:
    """
    Send a parsing request to the Landing AI Agentic Document Analysis API.

    Args:
        file_path (str): The path to the document file.
        include_marginalia (bool, optional): Whether to include marginalia in the analysis. Defaults to True.
        include_metadata_in_markdown (bool, optional): Whether to include metadata in the markdown output. Defaults to True.
        extraction_model (type[BaseModel] | None): Schema for field extraction. If provided, ensures the response matches this schema.

    Returns:
        dict[str, Any]: The parsed document data.
    """
    settings = get_settings()
    with Timer() as timer:
        file_type = "pdf" if Path(file_path).suffix.lower() == ".pdf" else "image"
        # TODO: check if the file extension is a supported image type
        with open(file_path, "rb") as file:
            files = {file_type: file}
            data: dict[str, Any] = {
                "include_marginalia": include_marginalia,
                "include_metadata_in_markdown": include_metadata_in_markdown,
            }

            def resolve_refs(obj: Any, defs: Dict[str, Any]) -> Any:
                if isinstance(obj, dict):
                    if "$ref" in obj:
                        ref_name = obj["$ref"].split("/")[-1]
                        return resolve_refs(copy.deepcopy(defs[ref_name]), defs)
                    return {k: resolve_refs(v, defs) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [resolve_refs(item, defs) for item in obj]
                return obj

            if extraction_model is not None:
                schema = extraction_model.model_json_schema()
                defs = schema.pop("$defs", {})
                schema = resolve_refs(schema, defs)
                data["fields_schema"] = json.dumps(schema)
            elif extraction_schema is not None:
                data["fields_schema"] = json.dumps(extraction_schema)

            api_key = (
                config.api_key
                if config and config.api_key
                else settings.vision_agent_api_key
            )
            headers = {
                "Authorization": f"Basic {api_key}",
                "runtime_tag": f"agentic-doc-v{_LIB_VERSION}",
            }

            response = httpx.post(
                _get_endpoint_url(settings),
                files=files,
                data=data,
                headers=headers,
                timeout=None,
            )
            if response.status_code in [408, 429, 502, 503, 504]:
                raise RetryableError(response)

            response.raise_for_status()

    _LOGGER.info(
        f"Time taken to successfully parse a document chunk: {timer.elapsed:.2f} seconds"
    )
    result: dict[str, Any] = response.json()

    return result



================================================
FILE: agentic_doc/utils.py
================================================
import math
import os
from collections import defaultdict
from pathlib import Path
from typing import Literal, Union, Optional
from urllib.parse import urlparse

import cv2
import httpx
import numpy as np
import pymupdf
import requests
import structlog
from PIL import Image
from pydantic_core import Url
from pypdf import PdfReader, PdfWriter
from tenacity import RetryCallState

from agentic_doc.common import Chunk, ChunkGroundingBox, Document, ParsedDocument
from agentic_doc.config import VisualizationConfig, get_settings

_LOGGER = structlog.getLogger(__name__)


def check_endpoint_and_api_key(endpoint_url: str, api_key: str) -> None:
    """Check if the API key is valid and if the endpoint is up."""
    if not api_key:
        raise ValueError("API key is not set. Please provide a valid API key.")

    headers = {"Authorization": f"Basic {api_key}"}

    try:
        response = requests.head(endpoint_url, headers=headers, timeout=5)
    except requests.exceptions.ConnectionError:
        raise ValueError(f'The endpoint URL "{endpoint_url}" is down or invalid.')

    if response.status_code == 404:
        raise ValueError("API key is not valid for this endpoint.")
    elif response.status_code == 401:
        raise ValueError("API key is invalid")

    _LOGGER.info("API key is valid.")


def get_file_type(file_path: Path) -> Literal["pdf", "image"]:
    """Get the file type of the input file by checking its magic number.

    PDF files start with '%PDF-' (25 50 44 46 2D in hex)
    """
    try:
        with open(file_path, "rb") as f:
            # Read the first 5 bytes to check for PDF magic number
            header = f.read(5)
            if header == b"%PDF-":
                return "pdf"
            return "image"
    except Exception as e:
        _LOGGER.warning(f"Error checking file type: {e}")
        # Fallback to extension check if file reading fails
        return "pdf" if file_path.suffix.lower() == ".pdf" else "image"


def save_groundings_as_images(
    file_path: Path,
    chunks: list[Chunk],
    save_dir: Path,
    inplace: bool = True,
) -> dict[str, list[Path]]:
    """
    Save the chunks as images based on the bounding box in each chunk.

    Args:
        file_path (Path): The path to the input document file.
        chunks (list[Chunk]): The chunks to save or update.
        save_dir (Path): The directory to save the images of the chunks.
        inplace (bool): Whether to update the input chunks in place.

    Returns:
        dict[str, Path]: The dictionary of saved image paths. The key is the chunk id and the value is the path to the saved image.
    """
    file_type = get_file_type(file_path)
    _LOGGER.info(
        f"Saving {len(chunks)} chunks as images to '{save_dir}'",
        file_path=file_path,
        file_type=file_type,
    )
    result: dict[str, list[Path]] = {}
    save_dir.mkdir(parents=True, exist_ok=True)
    if file_type == "image":
        img = cv2.imread(str(file_path))
        return _crop_groundings(img, chunks, save_dir, inplace)

    assert file_type == "pdf"
    chunks_by_page_idx = defaultdict(list)
    for chunk in chunks:
        page_idx = chunk.grounding[0].page
        chunks_by_page_idx[page_idx].append(chunk)

    with pymupdf.open(file_path) as pdf_doc:
        for page_idx, chunks in sorted(chunks_by_page_idx.items()):
            page_img = page_to_image(pdf_doc, page_idx)
            page_result = _crop_groundings(page_img, chunks, save_dir, inplace)
            result.update(page_result)

    return result


def page_to_image(
    pdf_doc: pymupdf.Document, page_idx: int, dpi: int = get_settings().pdf_to_image_dpi
) -> np.ndarray:
    """Convert a PDF page to an image. We specifically use pymupdf because it is self-contained and correctly renders annotations."""
    page = pdf_doc[page_idx]
    # Scale image and use RGB colorspace
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB)
    img: np.ndarray = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.h, pix.w, -1
    )
    # Ensure the image has 3 channels (sometimes it may include an alpha channel)
    if img.shape[-1] == 4:  # If RGBA, drop the alpha channel
        img = img[..., :3]

    return img


def get_chunk_from_reference(chunk_id: str, chunks: list[dict]) -> Optional[dict]:
    return next((chunk for chunk in chunks if chunk.get("chunk_id") == chunk_id), None)


def _crop_groundings(
    img: np.ndarray,
    chunks: list[Chunk],
    crop_save_dir: Path,
    inplace: bool = True,
) -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = defaultdict(list)
    for c in chunks:
        for i, grounding in enumerate(c.grounding):
            if grounding.box is None:
                _LOGGER.error(
                    "Grounding has no bounding box in non-error chunk",
                    grounding=grounding,
                    chunk=c,
                )
                continue

            cropped = _crop_image(img, grounding.box)
            # Convert the cropped image to PNG bytes
            is_success, buffer = cv2.imencode(".png", cropped)
            if not is_success:
                _LOGGER.error(
                    "Failed to encode cropped image as PNG",
                    grounding=grounding,
                )
                continue

            page = f"page_{grounding.page}"
            crop_save_path = (
                crop_save_dir / page / f"{c.chunk_type}_{c.chunk_id}_{i}.png"
            )
            crop_save_path.parent.mkdir(parents=True, exist_ok=True)
            crop_save_path.write_bytes(buffer.tobytes())
            assert c.chunk_id is not None
            result[c.chunk_id].append(crop_save_path)
            if inplace:
                c.grounding[i].image_path = crop_save_path

    return result


def _crop_image(image: np.ndarray, bbox: ChunkGroundingBox) -> np.ndarray:
    # Extract coordinates from the bounding box
    xmin_f, ymin_f, xmax_f, ymax_f = bbox.l, bbox.t, bbox.r, bbox.b

    # Convert normalized coordinates to absolute coordinates
    height, width = image.shape[:2]

    # Throw warning if coordinates are out of bounds
    if (
        xmin_f < 0
        or ymin_f < 0
        or xmax_f > 1
        or ymax_f > 1
        or xmin_f > xmax_f
        or ymin_f > ymax_f
    ):
        _LOGGER.warning(
            "Coordinates are out of bounds",
            bbox=bbox,
        )

    # Clamp coordinates to valid range [0, 1]
    xmin_f = max(0, min(1, xmin_f))
    ymin_f = max(0, min(1, ymin_f))
    xmax_f = max(0, min(1, xmax_f))
    ymax_f = max(0, min(1, ymax_f))

    xmin = math.floor(xmin_f * width)
    xmax = math.ceil(xmax_f * width)
    ymin = math.floor(ymin_f * height)
    ymax = math.ceil(ymax_f * height)

    # Ensure coordinates are valid
    xmin = max(0, xmin)
    ymin = max(0, ymin)
    xmax = min(width, xmax)
    ymax = min(height, ymax)

    result: np.ndarray = image[ymin:ymax, xmin:xmax]
    return result


def split_pdf(
    input_pdf_path: Union[str, Path],
    output_dir: Union[str, Path],
    split_size: int = 10,
) -> list[Document]:
    """
    Splits a PDF file into smaller PDFs, each with at most max_pages pages.

    Args:
        input_pdf_path (str | Path): Path to the input PDF file.
        output_dir (str | Path): Directory where mini PDF files will be saved.
        split_size (int): Maximum number of pages per mini PDF file (default is 10).
    """
    input_pdf_path = Path(input_pdf_path)
    assert input_pdf_path.exists(), f"Input PDF file not found: {input_pdf_path}"
    assert (
        0 < split_size <= 100
    ), "split_size must be greater than 0 and less than or equal to 100"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_dir = str(output_dir)

    pdf_reader = PdfReader(input_pdf_path)
    total_pages = len(pdf_reader.pages)
    _LOGGER.info(
        f"Splitting PDF: '{input_pdf_path}' into {total_pages // split_size} parts under '{output_dir}'"
    )
    file_count = 1

    output_pdfs = []
    # Process the PDF in chunks of max_pages pages
    for start in range(0, total_pages, split_size):
        pdf_writer = PdfWriter()
        # Add up to max_pages pages to the new PDF writer
        for page_num in range(start, min(start + split_size, total_pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        output_pdf = os.path.join(output_dir, f"{input_pdf_path.stem}_{file_count}.pdf")
        with open(output_pdf, "wb") as out_file:
            pdf_writer.write(out_file)
        _LOGGER.info(f"Created {output_pdf}")
        file_count += 1
        output_pdfs.append(
            Document(
                file_path=output_pdf,
                start_page_idx=start,
                end_page_idx=min(start + split_size - 1, total_pages - 1),
            )
        )

    return output_pdfs


def log_retry_failure(retry_state: RetryCallState) -> None:
    settings = get_settings()
    if retry_state.outcome and retry_state.outcome.failed:
        if settings.retry_logging_style == "log_msg":
            exception = retry_state.outcome.exception()
            func_name = (
                retry_state.fn.__name__ if retry_state.fn else "unknown_function"
            )
            # TODO: add a link to the error FAQ page
            _LOGGER.debug(
                f"'{func_name}' failed on attempt {retry_state.attempt_number}. Error: '{exception}'.",
            )
        elif settings.retry_logging_style == "inline_block":
            # Print yellow progress block that updates on the same line
            print(
                f"\r\033[33m{'█' * retry_state.attempt_number}\033[0m",
                end="",
                flush=True,
            )
        elif settings.retry_logging_style == "none":
            pass
        else:
            raise ValueError(
                f"Invalid retry logging style: {settings.retry_logging_style}"
            )


def viz_parsed_document(
    file_path: Union[str, Path],
    parsed_document: ParsedDocument,
    *,
    output_dir: Union[str, Path, None] = None,
    viz_config: Union[VisualizationConfig, None] = None,
) -> list[Image.Image]:
    if viz_config is None:
        viz_config = VisualizationConfig()

    viz_result_np: list[np.ndarray] = []
    file_path = Path(file_path)
    file_type = get_file_type(file_path)
    _LOGGER.info(f"Visualizing parsed document of: '{file_path}'")
    if file_type == "image":
        img = _read_img_rgb(str(file_path))
        viz_np = viz_chunks(img, parsed_document.chunks, viz_config)
        viz_result_np.append(viz_np)
    else:
        with pymupdf.open(file_path) as pdf_doc:
            for page_idx in range(
                parsed_document.start_page_idx, parsed_document.end_page_idx + 1
            ):
                img = page_to_image(pdf_doc, page_idx)
                chunks = [
                    chunk
                    for chunk in parsed_document.chunks
                    if chunk.grounding[0].page == page_idx
                ]
                viz_np = viz_chunks(img, chunks, viz_config)
                viz_result_np.append(viz_np)

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for i, viz_np in enumerate(viz_result_np):
            viz_np = cv2.cvtColor(viz_np, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_dir / f"{file_path.stem}_viz_page_{i}.png"), viz_np)

    return [Image.fromarray(viz_np) for viz_np in viz_result_np]


def viz_chunks(
    img: np.ndarray,
    chunks: list[Chunk],
    viz_config: Union[VisualizationConfig, None] = None,
) -> np.ndarray:
    if viz_config is None:
        viz_config = VisualizationConfig()

    viz = img.copy()
    viz = cv2.cvtColor(viz, cv2.COLOR_RGB2BGR)
    height, width = img.shape[:2]
    for i, chunk in enumerate(chunks):
        show_grounding_idx = len(chunk.grounding) > 1
        for j, grounding in enumerate(chunk.grounding):
            assert grounding.box is not None
            xmin, ymin, xmax, ymax = (
                max(0, math.floor(grounding.box.l * width)),
                max(0, math.floor(grounding.box.t * height)),
                min(width, math.ceil(grounding.box.r * width)),
                min(height, math.ceil(grounding.box.b * height)),
            )
            box = (xmin, ymin, xmax, ymax)
            idx = f"{i}-{j}" if show_grounding_idx else f"{i}"
            _place_mark(
                viz,
                box,
                text=f"{idx} {chunk.chunk_type}",
                color_bgr=viz_config.color_map[chunk.chunk_type],
                viz_config=viz_config,
            )

    viz = cv2.cvtColor(viz, cv2.COLOR_BGR2RGB)
    return viz


def _place_mark(
    img: np.ndarray,
    box_xyxy: tuple[int, int, int, int],
    text: str,
    *,
    color_bgr: tuple[int, int, int],
    viz_config: VisualizationConfig,
) -> None:
    text_color = color_bgr
    (text_width, text_height), baseline = cv2.getTextSize(
        text, viz_config.font, viz_config.font_scale, viz_config.thickness
    )
    text_x = int((box_xyxy[0] + box_xyxy[2] - text_width) // 2)
    text_y = int((box_xyxy[1] + box_xyxy[3] + text_height) // 2)

    # Draw the text background with opacity
    overlay = img.copy()
    cv2.rectangle(
        overlay,
        (text_x - viz_config.padding, text_y - text_height - viz_config.padding),
        (
            text_x + text_width + viz_config.padding,
            text_y + baseline + viz_config.padding,
        ),
        viz_config.text_bg_color,
        -1,
    )
    cv2.addWeighted(
        overlay, viz_config.text_bg_opacity, img, 1 - viz_config.text_bg_opacity, 0, img
    )

    # Draw the text on top
    cv2.putText(
        img,
        text,
        (text_x, text_y),
        viz_config.font,
        viz_config.font_scale,
        text_color,
        viz_config.thickness,
        cv2.LINE_AA,
    )
    # Draw the bounding box
    cv2.rectangle(img, box_xyxy[:2], box_xyxy[2:], color_bgr, viz_config.thickness)


def _read_img_rgb(img_path: str) -> np.ndarray:
    """
    Read a image given its path.
    Arguments:
        img_path : image file path
    Returns:
        img (H, W, 3): a numpy array image in RGB format
    """
    img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
    if img.shape[-1] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[-1] == 4:
        img = img[..., :3]
    return img


def download_file(file_url: Url, output_filepath: str) -> None:
    """
    Downloads a file from the given media URL to the specified local path.

    Parameters:
    media_url (Url): The URL of the media file to download.
    path (str): The local file system path where the file should be saved.

    Raises:
    Exception: If the download fails (non-200 status code).
    """
    _LOGGER.info(f"Downloading file from '{file_url}' to '{output_filepath}'")
    with httpx.stream("GET", str(file_url), timeout=None) as response:
        if response.status_code != 200:
            raise Exception(
                f"Download failed for '{file_url}'. Status code: {response.status_code} {response.text}"
            )

        with open(output_filepath, "wb") as f:
            for chunk in response.iter_bytes(chunk_size=1024):
                f.write(chunk)


def is_valid_httpurl(url: str) -> bool:
    """Check if the given URL is a valid HTTP URL."""
    try:
        parsed_url = urlparse(url)
        return parsed_url.scheme in ["http", "https"]
    except Exception:
        return False



================================================
FILE: tests/README.md
================================================
# Agentic-Doc Tests

This directory contains tests for the Agentic-Doc project.

## Test Structure

- `unit/`: Unit tests for individual components
- `integ/`: Integration tests that test multiple components together
- `conftest.py`: Global test fixtures and utilities

## Running Tests

To run the tests, first install the development requirements:

```bash
poetry install --all-extras
poetry shell
```

Then run the tests with pytest:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_parse_document.py

# Run a specific test
pytest tests/unit/test_parse_document.py::TestParseAndSaveDocument::test_parse_single_page_pdf

# For integration test, you need VA API Key
vision_agent_api_key=xxxx poetry run pytest tests/integ/test_parse_integ.py::test_parse_and_save_documents_multiple_inputs
```

## Adding New Tests

When adding new tests:

1. Place unit tests in the `unit/` directory
2. Place integration tests in the `integ/` directory
3. Add any needed fixtures to the relevant `conftest.py` file
4. Follow the existing patterns (Arrange-Act-Assert format) 


================================================
FILE: tests/conftest.py
================================================
import tempfile
from pathlib import Path

import httpx
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
)

from agentic_doc.common import (
    Chunk,
    ChunkGrounding,
    ChunkGroundingBox,
    ChunkType,
    ParsedDocument,
)


@pytest.fixture(scope="session")
def sample_pdf_path():
    # Uncomment below to test a more complex pdf
    # file_url = "https://upload.wikimedia.org/wikipedia/commons/8/85/I-20-sample.pdf"
    file_url = "https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf"
    file_path = Path(__file__).parent.parent / "temp_test_data" / "sample.pdf"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        file_path.unlink()

    with httpx.stream("GET", file_url) as r:
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=8192):
                f.write(chunk)

    return file_path


@pytest.fixture(scope="session")
def sample_image_path():
    file_url = "https://upload.wikimedia.org/wikipedia/commons/3/34/Sample_web_form.png"
    file_path = Path(__file__).parent.parent / "temp_test_data" / "sample.png"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        file_path.unlink()

    with httpx.stream("GET", file_url) as r:
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=8192):
                f.write(chunk)

    return file_path


@pytest.fixture
def results_dir(tmp_path):
    results = tmp_path / "results"
    results.mkdir()
    return results


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def multi_page_pdf(temp_dir):
    """Create a multi-page PDF with text."""
    pdf_path = temp_dir / "multi_page.pdf"
    num_pages = 5
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    for i in range(num_pages):
        elements.append(
            Paragraph(
                f"This is page {i + 1} of a multi-page document.", styles["Normal"]
            )
        )
        if i < num_pages - 1:  # Don't add page break after the last page
            elements.append(PageBreak())

    doc.build(elements)
    return pdf_path


@pytest.fixture
def complex_pdf(temp_dir):
    """Create a complex PDF with text, table, and image."""
    # First create a simple test image
    from PIL import Image as PILImage
    from PIL import ImageDraw

    img_path = temp_dir / "complex_image.png"
    img = PILImage.new("RGB", (200, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 180, 180], outline=(0, 0, 0), fill=(200, 200, 200))
    draw.text((40, 90), "Complex PDF", fill=(0, 0, 0))
    img.save(img_path)

    # Now create PDF with mixed content
    pdf_path = temp_dir / "complex.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("This is a complex PDF with multiple elements", styles["Heading1"]),
        Paragraph("This page contains text, a table, and an image.", styles["Normal"]),
        Table(
            data=[
                ["Type", "Description"],
                ["Text", "Regular paragraphs"],
                ["Table", "Structured data"],
                ["Image", "Visual element"],
            ],
            style=TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 1, (0, 0, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
                ]
            ),
        ),
        Paragraph("Below is an image:", styles["Normal"]),
        Image(str(img_path), width=300, height=200),
        PageBreak(),
        Paragraph("This is page 2 of the complex document", styles["Heading2"]),
        Paragraph("This demonstrates a multi-page complex document.", styles["Normal"]),
    ]

    doc.build(elements)
    return pdf_path


@pytest.fixture
def mock_parsed_document():
    """Return a mock ParsedDocument object."""
    return ParsedDocument(
        markdown="# Test Document\n\nThis is a test document.",
        chunks=[
            Chunk(
                text="Test Document",
                chunk_type=ChunkType.text,
                chunk_id="11111",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            ),
            Chunk(
                text="This is a test document.",
                chunk_type=ChunkType.text,
                chunk_id="22222",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                    )
                ],
            ),
        ],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="pdf",
    )


@pytest.fixture
def mock_multi_page_parsed_document():
    """Return a mock ParsedDocument object for a multi-page document."""
    return ParsedDocument(
        markdown="# Multi-page Document\n\nPage 1 content.\n\n## Page 2\n\nPage 2 content.\n\nPage 3 content.",
        chunks=[
            Chunk(
                text="Multi-page Document",
                chunk_type=ChunkType.text,
                chunk_id="11111",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            ),
            Chunk(
                text="Page 1 content.",
                chunk_type=ChunkType.text,
                chunk_id="22222",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                    )
                ],
            ),
            Chunk(
                text="Page 2",
                chunk_type=ChunkType.text,
                chunk_id="33333",
                grounding=[
                    ChunkGrounding(
                        page=1, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            ),
            Chunk(
                text="Page 2 content.",
                chunk_type=ChunkType.figure,
                chunk_id="44444",
                grounding=[
                    ChunkGrounding(
                        page=1, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                    )
                ],
            ),
            Chunk(
                text="Page 3 content.",
                chunk_type=ChunkType.text,
                chunk_id="55555",
                grounding=[
                    ChunkGrounding(
                        page=2, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                    )
                ],
            ),
        ],
        start_page_idx=0,
        end_page_idx=2,
        doc_type="pdf",
    )



================================================
FILE: tests/integ/test_parse_integ.py
================================================
import json
import os

import pytest
from pydantic import BaseModel, Field

from agentic_doc.common import ChunkType, ParsedDocument, MetadataType
from agentic_doc.config import settings, get_settings, ParseConfig
from agentic_doc.parse import (
    parse,
    parse_and_save_document,
    parse_and_save_documents,
    parse_documents,
)


def test_parse_and_save_documents_multiple_inputs(sample_image_path, results_dir):
    # Arrange
    input_file = sample_image_path

    # Act
    result_paths = parse_and_save_documents(
        [
            input_file,
            "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        ],
        result_save_dir=results_dir,
        grounding_save_dir=results_dir,
    )

    # Assert
    assert len(result_paths) == 2
    for result_path in result_paths:
        result_path = result_paths[0]
        assert result_path.exists()

        # Verify the saved JSON can be loaded and has expected structure
        with open(result_path) as f:
            result_data = json.load(f)

        parsed_doc = ParsedDocument.model_validate(result_data)
        assert parsed_doc.markdown
        assert len(parsed_doc.chunks) > 0
        assert parsed_doc.start_page_idx == 0
        assert parsed_doc.end_page_idx == 0
        assert len(parsed_doc.errors) == 0


def test_parse_and_save_documents_single_pdf(sample_pdf_path, results_dir):
    # Arrange
    input_file = sample_pdf_path

    # Act
    result_paths = parse_and_save_documents(
        [input_file],
        result_save_dir=results_dir,
        grounding_save_dir=results_dir,
    )

    # Assert
    assert len(result_paths) == 1
    result_path = result_paths[0]
    assert result_path.exists()

    # Verify the saved JSON can be loaded and has expected structure
    with open(result_path) as f:
        result_data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(result_data)
    assert parsed_doc.markdown
    assert parsed_doc.start_page_idx == 0
    assert parsed_doc.end_page_idx == 3
    assert parsed_doc.doc_type == "pdf"
    assert len(parsed_doc.chunks) >= 10
    # Verify that chunks are ordered by page number
    for i in range(1, len(parsed_doc.chunks)):
        prev_page = parsed_doc.chunks[i - 1].grounding[0].page
        curr_page = parsed_doc.chunks[i].grounding[0].page
        assert (
            curr_page >= prev_page
        ), f"Chunks not ordered by page: chunk {i - 1} (page {prev_page}) followed by chunk {i} (page {curr_page})"

    # Verify that there were no errors
    assert len(parsed_doc.errors) == 0

    # Verify that there were no errors
    assert len(parsed_doc.errors) == 0

    # Verify that grounding images were saved
    for chunk in parsed_doc.chunks:
        for grounding in chunk.grounding:
            assert grounding.image_path.exists()


def test_parse_single_image(sample_image_path):
    # Act
    result = parse_documents([sample_image_path])

    # Assert
    assert len(result) == 1
    parsed_doc = result[0]

    # Check basic structure
    assert parsed_doc.doc_type == "image"
    assert parsed_doc.start_page_idx == 0
    assert parsed_doc.end_page_idx == 0
    assert parsed_doc.markdown
    assert len(parsed_doc.chunks) > 0

    # Check chunk structure
    for chunk in parsed_doc.chunks:
        assert chunk.text
        assert len(chunk.grounding) > 0
        for grounding in chunk.grounding:
            assert grounding.page == 0
            if grounding.box:
                assert 0 <= grounding.box.l <= 1
                assert 0 <= grounding.box.t <= 1
                assert 0 <= grounding.box.r <= 1
                assert 0 <= grounding.box.b <= 1


@pytest.mark.skipif(
    not get_settings().vision_agent_api_key,
    reason="API key not set, skipping integration test that requires actual API call",
)
def test_parse_and_save_document_with_url(results_dir):
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

    # Act
    result_path = parse_and_save_document(
        url, result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    # Assert
    assert result_path.exists()
    assert result_path.suffix == ".json"

    # Verify JSON content
    with open(result_path) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)
    assert parsed_doc.doc_type == "pdf"
    assert parsed_doc.markdown

    # Check for non-error chunks
    non_error_chunks = [c for c in parsed_doc.chunks]
    assert len(non_error_chunks) > 0

    # Check groundings
    for chunk in non_error_chunks:
        for grounding in chunk.grounding:
            if grounding.image_path:
                assert os.path.isfile(grounding.image_path)


def test_parse_multipage_pdf(multi_page_pdf, results_dir):
    # Act
    result = parse_and_save_document(
        multi_page_pdf, result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    # Assert
    assert result.exists()

    # Verify JSON content
    with open(result) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)
    assert parsed_doc.doc_type == "pdf"

    # Multi-page PDF should have end_page_idx > 0
    assert parsed_doc.start_page_idx == 0
    assert parsed_doc.end_page_idx > 0

    # Check that there are chunks from multiple pages
    page_indices = set(
        grounding.page for chunk in parsed_doc.chunks for grounding in chunk.grounding
    )

    # There should be at least 2 pages with content
    assert len(page_indices) > 1, "Expected chunks from multiple pages"

    # Page indices should be consecutive
    assert page_indices == set(range(min(page_indices), max(page_indices) + 1))


def test_parse_complex_pdf_with_table_and_image(complex_pdf, results_dir):
    # Act
    result = parse_and_save_document(
        complex_pdf, result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    # Assert
    assert result.exists()

    # Verify JSON content
    with open(result) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)

    # Check for specific chunk types that should be present in a complex PDF
    chunk_types = [chunk.chunk_type for chunk in parsed_doc.chunks]

    # The complex PDF fixture has text, table, and potentially a figure
    assert ChunkType.text in chunk_types, "Text chunk not found"
    assert ChunkType.table in chunk_types, "Table chunk not found"

    # Count chunks by type
    type_counts = {}
    for chunk in parsed_doc.chunks:
        if chunk.chunk_type not in type_counts:
            type_counts[chunk.chunk_type] = 0
        type_counts[chunk.chunk_type] += 1

    # Print chunk type counts for debugging if test fails
    print(f"Chunk type counts: {type_counts}")

    # Check that there are multiple text chunks (since the PDF has multiple text sections)
    assert type_counts.get(ChunkType.text, 0) >= 1, "Expected at least one text chunk"

    # Check that there is at least one table chunk
    assert type_counts.get(ChunkType.table, 0) >= 1, "Expected at least one table chunk"


@pytest.mark.skipif(
    not get_settings().vision_agent_api_key,
    reason="API key not set, skipping integration test that requires actual API call",
)
def test_parse_multiple_documents_batch(
    multi_page_pdf, complex_pdf, sample_image_path, results_dir
):
    # Arrange - mix of different document types
    input_files = [
        multi_page_pdf,
        complex_pdf,
        sample_image_path,
    ]

    # Act
    result_paths = parse_and_save_documents(
        input_files, result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    # Assert
    assert len(result_paths) == 3

    # Check that all files were saved
    for path in result_paths:
        assert path.exists()
        assert path.suffix == ".json"

    # Verify each result has the correct structure
    file_types = []
    for i, path in enumerate(result_paths):
        with open(path) as f:
            data = json.load(f)

        parsed_doc = ParsedDocument.model_validate(data)
        file_types.append(parsed_doc.doc_type)

        # Check basic doc properties
        assert parsed_doc.markdown
        assert len(parsed_doc.chunks) > 0

        # Check for non-error chunks
        non_error_chunks = [c for c in parsed_doc.chunks]
        assert len(non_error_chunks) > 0, f"Document {i} has only error chunks"

    # Make sure we got the expected mix of document types
    assert "pdf" in file_types
    assert "image" in file_types


def test_parse_documents_error_handling_mixed_valid_invalid(
    sample_image_path, results_dir
):
    # Test parsing a mix of valid and invalid document paths
    input_files = [
        sample_image_path,  # Valid image
        "/path/to/nonexistent.pdf",  # Invalid path
    ]

    # Should raise FileNotFoundError for the invalid file
    with pytest.raises(FileNotFoundError):
        parse_and_save_documents(input_files, result_save_dir=results_dir)


def test_parse_pdf_chunks_have_sequential_pages(sample_pdf_path, results_dir):
    # Test that PDF chunks are correctly ordered by page
    result_paths = parse_and_save_documents(
        [sample_pdf_path], result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    assert len(result_paths) == 1
    result_path = result_paths[0]

    with open(result_path) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)

    # Collect all page numbers from chunks
    all_page_numbers = []
    for chunk in parsed_doc.chunks:
        for grounding in chunk.grounding:
            all_page_numbers.append(grounding.page)

    # Pages should be in order and start from 0
    unique_pages = sorted(set(all_page_numbers))
    assert unique_pages[0] == 0
    assert unique_pages == list(range(len(unique_pages)))  # Sequential pages


def test_parse_documents_markdown_not_empty(sample_image_path, results_dir):
    # Test that parsed documents have non-empty markdown
    result_paths = parse_and_save_documents(
        [sample_image_path], result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    assert len(result_paths) == 1
    result_path = result_paths[0]

    with open(result_path) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)

    # Markdown should not be empty for a valid document
    assert parsed_doc.markdown.strip() != ""
    assert len(parsed_doc.markdown) > 0


def test_parse_documents_chunk_ids_unique(multi_page_pdf, results_dir):
    # Test that all chunk IDs within a document are unique
    result_paths = parse_and_save_documents(
        [multi_page_pdf], result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    assert len(result_paths) == 1
    result_path = result_paths[0]

    with open(result_path) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)

    # Collect all chunk IDs
    chunk_ids = [chunk.chunk_id for chunk in parsed_doc.chunks]

    # All chunk IDs should be unique
    assert len(chunk_ids) == len(set(chunk_ids)), "Found duplicate chunk IDs"

    # All chunk IDs should be non-empty strings
    for chunk_id in chunk_ids:
        assert isinstance(chunk_id, str)
        assert len(chunk_id) > 0


def test_parse_and_save_documents_with_invalid_file(sample_pdf_path, results_dir):
    # Arrange
    input_files = [
        sample_pdf_path.parent / "invalid.pdf",  # Non-existent file
        sample_pdf_path,
    ]

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        parse_and_save_documents(input_files, result_save_dir=results_dir)


def test_parse_documents_grounding_boxes_valid(sample_image_path, results_dir):
    # Test that all grounding boxes have valid coordinates
    result_paths = parse_and_save_documents(
        [sample_image_path], result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    assert len(result_paths) == 1
    result_path = result_paths[0]

    with open(result_path) as f:
        data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(data)

    for chunk in parsed_doc.chunks:
        for grounding in chunk.grounding:
            box = grounding.box

            # All coordinates should be between 0 and 1
            assert 0 <= box.l <= 1, f"Invalid left coordinate: {box.l}"
            assert 0 <= box.t <= 1, f"Invalid top coordinate: {box.t}"
            assert 0 <= box.r <= 1, f"Invalid right coordinate: {box.r}"
            assert 0 <= box.b <= 1, f"Invalid bottom coordinate: {box.b}"

            # Right should be greater than left, bottom should be greater than top
            assert box.r > box.l, f"Right ({box.r}) should be > left ({box.l})"
            assert box.b > box.t, f"Bottom ({box.b}) should be > top ({box.t})"


def test_parse_with_document_bytes(sample_pdf_path, results_dir):
    with open(sample_pdf_path, "rb") as f:
        doc_bytes = f.read()

    # Act
    result_docs = parse(
        doc_bytes, result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    # Assert
    assert len(result_docs) == 1
    result_path = result_docs[0].result_path
    assert result_path.exists()

    # Verify the saved JSON can be loaded and has expected structure
    with open(result_path) as f:
        result_data = json.load(f)

    parsed_doc = ParsedDocument.model_validate(result_data)
    assert parsed_doc.markdown
    assert len(parsed_doc.chunks) > 0
    assert parsed_doc.start_page_idx == 0
    assert parsed_doc.end_page_idx == 3


def test_parse_with_image_bytes(sample_image_path, results_dir):
    with open(sample_image_path, "rb") as f:
        doc_bytes = f.read()

    result = parse(
        doc_bytes, result_save_dir=results_dir, grounding_save_dir=results_dir
    )

    assert len(result) == 1
    parsed_doc = result[0]

    # Check basic structure
    assert parsed_doc.doc_type == "image"
    assert parsed_doc.start_page_idx == 0
    assert parsed_doc.end_page_idx == 0
    assert parsed_doc.markdown
    assert len(parsed_doc.chunks) > 0

    # Check chunk structure
    for chunk in parsed_doc.chunks:
        assert chunk.text
        assert len(chunk.grounding) > 0
        for grounding in chunk.grounding:
            assert grounding.page == 0
            if grounding.box:
                assert 0 <= grounding.box.l <= 1
                assert 0 <= grounding.box.t <= 1
                assert 0 <= grounding.box.r <= 1
                assert 0 <= grounding.box.b <= 1


def test_parse_with_extraction_model(sample_image_path):
    class SampleFormFields(BaseModel):
        eye_color: str = Field(description="Eye color")

    result_path = parse(sample_image_path, extraction_model=SampleFormFields)

    extraction_results = result_path[0].extraction
    assert extraction_results.eye_color == "green"


def test_extraction_metadata_simple(sample_image_path):
    class SampleFormFields(BaseModel):
        eye_color: str = Field(description="Eye color")

    result = parse(sample_image_path, extraction_model=SampleFormFields)

    assert len(result) == 1
    parsed_doc = result[0]
    assert parsed_doc.extraction is not None
    assert isinstance(parsed_doc.extraction, SampleFormFields)

    assert hasattr(parsed_doc.extraction_metadata, "eye_color")
    assert isinstance(parsed_doc.extraction_metadata.eye_color, MetadataType)
    assert hasattr(parsed_doc.extraction_metadata.eye_color, "chunk_references")
    assert isinstance(parsed_doc.extraction_metadata.eye_color.chunk_references, list)


def test_extraction_metadata_nested(sample_pdf_path):
    class Invoices(BaseModel):
        invoices_by_date: int = Field(description="Invoices by date")
        trans_date: str = Field(description="Transaction date")

    class Type(BaseModel):
        invoices_by_type: int = Field(description="Invoices by type")
        trans_type: str = Field(description="Transaction type")

    class Amount(BaseModel):
        invoices_by_trans_amount: int = Field(
            description="Invoices by transaction amount"
        )
        trans_amount: str = Field(description="Transaction amount")

    class SampleBookmarkFile(BaseModel):
        invoices: Invoices
        type: Type
        amount: Amount

    class SampleDataFile(BaseModel):
        invoices: Invoices
        type: Type
        amount: Amount

    class Files(BaseModel):
        sample_bookmark_file: SampleBookmarkFile
        sample_data_file: SampleDataFile

    def check_structure_matches(obj, model_class, is_metadata=False):
        """
        Recursively verify that obj has the same structure as model_class.
        If is_metadata=True, leaf values should be dict[str, list[str]],
        otherwise they should match the model's field types.
        """
        field_annotations = model_class.model_fields

        for field_name, field_info in field_annotations.items():
            assert hasattr(obj, field_name), f"Missing field: {field_name}"

            field_value = getattr(obj, field_name)
            field_type = field_info.annotation

            if hasattr(field_type, "__bases__") and BaseModel in field_type.__bases__:
                if is_metadata:
                    # Recursively check the nested structure
                    check_structure_matches(field_value, field_type, is_metadata=True)
                else:
                    # For extraction, should be actual model instances
                    assert isinstance(
                        field_value, field_type
                    ), f"Field {field_name} should be {field_type}"
                    check_structure_matches(field_value, field_type, is_metadata=False)
            else:
                # This is a leaf field
                if is_metadata:
                    assert isinstance(
                        field_value, MetadataType
                    ), f"Leaf field {field_name} should be MetadataType in metadata"
                    if hasattr(field_value, "value") and field_value.value != None:
                        assert isinstance(
                            field_value.value, field_type
                        ), f"Field {field_name}.value should be {field_type}"
                else:
                    # For extraction, check against the actual field type
                    assert isinstance(
                        field_value, field_type
                    ), f"Field {field_name} should be {field_type}"

    result = parse(sample_pdf_path, extraction_model=Files)

    assert len(result) == 1
    parsed_doc = result[0]

    # Check that extraction has the exact same type as Files
    assert parsed_doc.extraction is not None
    assert isinstance(parsed_doc.extraction, Files)
    check_structure_matches(parsed_doc.extraction, Files, is_metadata=False)

    # Check that extraction_metadata has the same structure but with dict[str, list[str]] leaves
    assert parsed_doc.extraction_metadata is not None
    check_structure_matches(parsed_doc.extraction_metadata, Files, is_metadata=True)


def test_extraction_schema_simple(sample_image_path):
    extraction_schema = {
        "type": "object",
        "properties": {"eye_color": {"type": "string", "description": "Eye color"}},
    }

    result = parse(sample_image_path, extraction_schema=extraction_schema)

    assert len(result) == 1
    extraction_result = result[0]
    assert extraction_result.extraction is not None
    assert isinstance(extraction_result.extraction, dict)
    assert extraction_result.extraction["eye_color"] == "green"
    assert isinstance(extraction_result.extraction_metadata, dict)


def test_extraction_schema_nested(sample_pdf_path):
    extraction_schema = {
        "type": "object",
        "properties": {
            "sample_bookmark_file": {
                "type": "object",
                "properties": {
                    "invoices": {
                        "type": "object",
                        "properties": {
                            "invoices_by_date": {
                                "type": "integer",
                                "description": "Invoices by date",
                            },
                            "trans_date": {
                                "type": "string",
                                "description": "Transaction date",
                            },
                        },
                    },
                    "type": {
                        "type": "object",
                        "properties": {
                            "invoices_by_type": {
                                "type": "integer",
                                "description": "Invoices by type",
                            },
                            "trans_type": {
                                "type": "string",
                                "description": "Transaction type",
                            },
                        },
                    },
                    "amount": {
                        "type": "object",
                        "properties": {
                            "invoices_by_trans_amount": {
                                "type": "integer",
                                "description": "Invoices by transaction amount",
                            },
                            "trans_amount": {
                                "type": "string",
                                "description": "Transaction amount",
                            },
                        },
                    },
                },
            },
            "sample_data_file": {
                "type": "object",
                "properties": {
                    "invoices": {
                        "type": "object",
                        "properties": {
                            "invoices_by_date": {
                                "type": "integer",
                                "description": "Invoices by date",
                            },
                            "trans_date": {
                                "type": "string",
                                "description": "Transaction date",
                            },
                        },
                    },
                    "type": {
                        "type": "object",
                        "properties": {
                            "invoices_by_type": {
                                "type": "integer",
                                "description": "Invoices by type",
                            },
                            "trans_type": {
                                "type": "string",
                                "description": "Transaction type",
                            },
                        },
                    },
                    "amount": {
                        "type": "object",
                        "properties": {
                            "invoices_by_trans_amount": {
                                "type": "integer",
                                "description": "Invoices by transaction amount",
                            },
                            "trans_amount": {
                                "type": "string",
                                "description": "Transaction amount",
                            },
                        },
                    },
                },
            },
        },
    }

    result = parse(sample_pdf_path, extraction_schema=extraction_schema)

    assert len(result) == 1
    extraction_result = result[0]
    assert extraction_result.extraction is not None
    assert isinstance(extraction_result.extraction, dict)
    assert "sample_bookmark_file" in extraction_result.extraction
    assert "sample_data_file" in extraction_result.extraction
    assert (
        "invoices_by_date"
        in extraction_result.extraction["sample_bookmark_file"]["invoices"]
    )
    assert (
        "invoices_by_type"
        in extraction_result.extraction["sample_bookmark_file"]["type"]
    )
    assert (
        "invoices_by_trans_amount"
        in extraction_result.extraction["sample_bookmark_file"]["amount"]
    )
    assert (
        "invoices_by_date"
        in extraction_result.extraction["sample_data_file"]["invoices"]
    )
    assert (
        "invoices_by_type" in extraction_result.extraction["sample_data_file"]["type"]
    )
    assert (
        "invoices_by_trans_amount"
        in extraction_result.extraction["sample_data_file"]["amount"]
    )
    assert isinstance(extraction_result.extraction_metadata, dict)


================================================
FILE: tests/unit/test_common.py
================================================
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from agentic_doc.common import (
    Chunk,
    ChunkGrounding,
    ChunkGroundingBox,
    ChunkType,
    Document,
    ParsedDocument,
    RetryableError,
    Timer,
    create_metadata_model,
    MetadataType,
)

from typing import List, Optional
from pydantic import BaseModel


def test_chunk_type_enum():
    # Test all the enumeration values
    assert ChunkType.table == "table"
    assert ChunkType.figure == "figure"
    assert ChunkType.text == "text"
    assert ChunkType.marginalia == "marginalia"


def test_chunk_grounding_box():
    # Test creating a ChunkGroundingBox
    box = ChunkGroundingBox(l=0.1, t=0.2, r=0.8, b=0.9)

    # Check attributes
    assert box.l == 0.1
    assert box.t == 0.2
    assert box.r == 0.8
    assert box.b == 0.9

    # Test serialization/deserialization
    box_dict = box.model_dump()
    box2 = ChunkGroundingBox.model_validate(box_dict)
    assert box2.l == box.l
    assert box2.t == box.t
    assert box2.r == box.r
    assert box2.b == box.b


def test_chunk_grounding():
    # Test creating a ChunkGrounding with box
    box = ChunkGroundingBox(l=0.1, t=0.2, r=0.8, b=0.9)
    grounding = ChunkGrounding(page=0, box=box)

    # Check attributes
    assert grounding.page == 0
    assert grounding.box == box
    assert grounding.image_path is None

    # Test with image_path
    image_path = Path("/path/to/image.png")
    grounding_with_image = ChunkGrounding(page=0, box=box, image_path=image_path)
    assert grounding_with_image.image_path == image_path

    # Note: box field is required in ChunkGrounding, so we can't test with None box

    # Test serialization/deserialization
    grounding_dict = grounding.model_dump()
    grounding2 = ChunkGrounding.model_validate(grounding_dict)
    assert grounding2.page == grounding.page
    assert grounding2.box.l == grounding.box.l
    assert grounding2.image_path == grounding.image_path


def test_chunk():
    # Test creating a Chunk
    box = ChunkGroundingBox(l=0.1, t=0.2, r=0.8, b=0.9)
    grounding = ChunkGrounding(page=0, box=box)
    chunk = Chunk(
        text="Test Text",
        grounding=[grounding],
        chunk_type=ChunkType.text,
        chunk_id="123",
    )

    # Check attributes
    assert chunk.text == "Test Text"
    assert len(chunk.grounding) == 1
    assert chunk.grounding[0] == grounding
    assert chunk.chunk_type == ChunkType.text
    assert chunk.chunk_id == "123"

    # Test creating a Chunk with multiple groundings
    grounding2 = ChunkGrounding(page=1, box=box)
    chunk_multi = Chunk(
        text="Multi Page",
        grounding=[grounding, grounding2],
        chunk_type=ChunkType.text,
        chunk_id="456",
    )
    assert len(chunk_multi.grounding) == 2

    # Note: chunk_id is required in the Chunk model, so we can't test with None

    # Test serialization/deserialization
    chunk_dict = chunk.model_dump()
    chunk2 = Chunk.model_validate(chunk_dict)
    assert chunk2.text == chunk.text
    assert chunk2.chunk_type == chunk.chunk_type
    assert chunk2.chunk_id == chunk.chunk_id
    assert len(chunk2.grounding) == len(chunk.grounding)


def test_page_error():
    # Test creating a PageError
    from agentic_doc.common import PageError

    error_msg = "Test error message"
    page_num = 42
    error_code = -1

    page_error = PageError(page_num=page_num, error=error_msg, error_code=error_code)

    # Check the error
    assert page_error.page_num == page_num
    assert page_error.error == error_msg
    assert page_error.error_code == error_code


def test_parsed_document():
    # Create test chunks
    box = ChunkGroundingBox(l=0.1, t=0.2, r=0.8, b=0.9)
    grounding1 = ChunkGrounding(page=0, box=box)
    grounding2 = ChunkGrounding(page=1, box=box)

    chunk1 = Chunk(
        text="Title", grounding=[grounding1], chunk_type=ChunkType.text, chunk_id="1"
    )

    chunk2 = Chunk(
        text="Content", grounding=[grounding2], chunk_type=ChunkType.text, chunk_id="2"
    )

    # Create ParsedDocument
    doc = ParsedDocument(
        markdown="# Title\n\nContent",
        chunks=[chunk1, chunk2],
        start_page_idx=0,
        end_page_idx=1,
        doc_type="pdf",
    )

    # Check attributes
    assert doc.markdown == "# Title\n\nContent"
    assert len(doc.chunks) == 2
    assert doc.chunks[0] == chunk1
    assert doc.chunks[1] == chunk2
    assert doc.start_page_idx == 0
    assert doc.end_page_idx == 1
    assert doc.doc_type == "pdf"

    # Test with image doc_type
    image_doc = ParsedDocument(
        markdown="Image content",
        chunks=[chunk1],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="image",
    )
    assert image_doc.doc_type == "image"

    # Test serialization/deserialization
    doc_dict = doc.model_dump()
    doc2 = ParsedDocument.model_validate(doc_dict)
    assert doc2.markdown == doc.markdown
    assert len(doc2.chunks) == len(doc.chunks)
    assert doc2.start_page_idx == doc.start_page_idx
    assert doc2.end_page_idx == doc.end_page_idx
    assert doc2.doc_type == doc.doc_type


def test_retryable_error():
    # Create a mock response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"

    # Create a RetryableError
    error = RetryableError(mock_response)

    # Check the error
    assert error.response == mock_response
    assert error.reason == "429 - Rate limit exceeded"
    assert str(error) == "429 - Rate limit exceeded"


def test_document():
    # Create a Document
    file_path = Path("/path/to/file.pdf")
    doc = Document(file_path=file_path, start_page_idx=0, end_page_idx=5)

    # Check attributes
    assert doc.file_path == file_path
    assert doc.start_page_idx == 0
    assert doc.end_page_idx == 5

    # Test string representation
    assert str(doc) == "File name: file.pdf\tPage: [0:5]"

    # Test validation
    with pytest.raises(ValueError):
        # start_page_idx must be >= 0
        Document(file_path=file_path, start_page_idx=-1, end_page_idx=5)

    with pytest.raises(ValueError):
        # end_page_idx must be >= 0
        Document(file_path=file_path, start_page_idx=0, end_page_idx=-1)


def test_timer():
    # Test the Timer context manager
    timer = Timer()

    # Time should be 0 initially
    assert timer.elapsed == 0.0

    # Test with a short sleep
    with patch("time.perf_counter") as mock_time:
        # Setup mock to simulate time passing
        mock_time.side_effect = [0.0, 1.5]  # start=0.0, end=1.5

        with timer:
            pass  # timer is running

        # After context, elapsed should be updated
        assert timer.elapsed == 1.5

    # Test normal usage
    with timer:
        time.sleep(0.01)  # Small sleep

    # Verify elapsed time is positive
    assert timer.elapsed > 0


def test_create_metadata_model():
    # Simple nested model
    class Researcher(BaseModel):
        age: int
        name: str

    class TopLevelModel(BaseModel):
        id: int
        researcher: Researcher

    MetadataModel = create_metadata_model(TopLevelModel)
    metadata_instance = MetadataModel(
        id={"confidence": 0.5, "chunk_references": ["dummy"], "value": 5},
        researcher={
            "age": {
                "confidence": 0.5,
                "chunk_references": ["dummy", "dummy"],
                "value": 5,
            },
            "name": {
                "confidence": 0.5,
                "chunk_references": ["dummy"],
                "value": "john doe",
            },
        },
    )

    assert isinstance(metadata_instance.id, MetadataType[int])
    assert isinstance(metadata_instance.researcher.age, MetadataType[int])
    assert isinstance(metadata_instance.researcher.name, MetadataType[str])

    # Test with Optional fields
    class ModelWithOptional(BaseModel):
        required_field: str
        optional_field: Optional[str] = None

    MetadataWithOptional = create_metadata_model(ModelWithOptional)

    optional_instance = MetadataWithOptional(
        required_field={
            "confidence": 0.5,
            "chunk_references": ["dummy"],
            "value": "dummy",
        },
        optional_field=None,
    )

    assert isinstance(optional_instance.required_field, MetadataType[str])
    assert optional_instance.optional_field is None

    # Test with list fields
    class ModelWithList(BaseModel):
        items: List[Researcher]

    MetadataWithList = create_metadata_model(ModelWithList)

    list_instance = MetadataWithList(
        items=[
            {
                "age": {"chunk_references": ["dummy"]},
                "name": {"chunk_references": ["dummy"]},
            },
            {
                "age": {"chunk_references": ["dummy"]},
                "name": {"chunk_references": ["dummy"]},
            },
        ]
    )

    assert isinstance(list_instance.items, list)
    assert len(list_instance.items) == 2
    assert isinstance(list_instance.items[0].age, MetadataType[int])

    # Test with list of primitive types
    class ModelWithPrimitiveList(BaseModel):
        tags: List[str]

    MetadataWithPrimitiveList = create_metadata_model(ModelWithPrimitiveList)

    primitive_list_instance = MetadataWithPrimitiveList(
        tags=[{"chunk_references": ["dummy"]}, {"chunk_references": ["dummy"]}]
    )

    assert isinstance(primitive_list_instance.tags, list)
    assert len(primitive_list_instance.tags) == 2
    assert isinstance(primitive_list_instance.tags[0], MetadataType[str])
    assert "chunk_references" in primitive_list_instance.tags[0].__class__.model_fields


def test_extraction_metadata_type_validation():
    class NestedModel(BaseModel):
        field1: str
        field2: int

    class ComplexModel(BaseModel):
        simple_field: str
        optional_field: Optional[int] = None
        nested_field: NestedModel
        list_field: List[str]
        nested_list_field: List[NestedModel]

    # Create the metadata model
    MetadataModel = create_metadata_model(ComplexModel)

    metadata_instance = MetadataModel(
        simple_field={
            "confidence": 0.5,
            "chunk_references": ["text"],
            "value": "string",
        },
        optional_field={"confidence": 0.4, "chunk_references": ["low"]},
        nested_field={
            "field1": {"chunk_references": ["table"]},
            "field2": {"chunk_references": ["high"]},
        },
        list_field=[
            {"chunk_references": ["text1"]},
            {"chunk_references": ["text2"]},
        ],  # List of primitive metadata
        nested_list_field=[
            {
                "field1": {"chunk_references": ["page1"]},
                "field2": {"chunk_references": ["medium"]},
            }
        ],
    )

    # Verify types
    assert isinstance(metadata_instance.simple_field, MetadataType[str])
    assert isinstance(metadata_instance.optional_field, MetadataType[int])
    assert hasattr(metadata_instance.nested_field, "field1")
    assert hasattr(metadata_instance.nested_field, "field2")
    assert isinstance(metadata_instance.nested_field.field1, MetadataType[str])
    assert isinstance(metadata_instance.nested_field.field2, MetadataType[int])
    assert isinstance(metadata_instance.list_field, list)
    if len(metadata_instance.list_field) > 0:
        assert isinstance(metadata_instance.list_field[0], MetadataType[str])
    assert isinstance(metadata_instance.nested_list_field, list)

    metadata_with_none = MetadataModel(
        simple_field={"chunk_references": ["text"]},
        optional_field=None,
        nested_field={
            "field1": {"chunk_references": ["table"]},
            "field2": {"chunk_references": ["high"]},
        },
        list_field=[],
        nested_list_field=[],
    )

    assert metadata_with_none.optional_field is None



================================================
FILE: tests/unit/test_config.py
================================================
import json
import os
from unittest.mock import MagicMock, patch

import cv2
import pytest

from agentic_doc.common import ChunkType
from agentic_doc.config import (
    _COLOR_MAP,
    _MAX_PARALLEL_TASKS,
    get_settings,
    Settings,
    VisualizationConfig,
)


def test_default_config():
    settings = get_settings()
    assert settings.retry_logging_style == "log_msg"
    assert settings.batch_size > 0
    assert settings.max_workers > 0
    assert settings.max_retries > 0
    assert settings.max_retry_wait_time > 0
    assert settings.endpoint_host == "https://api.va.landing.ai"
    assert settings.pdf_to_image_dpi == 96


def test_custom_config(monkeypatch):
    # Set environment variables
    monkeypatch.setenv("BATCH_SIZE", "10")
    monkeypatch.setenv("MAX_WORKERS", "8")
    monkeypatch.setenv("MAX_RETRIES", "50")
    monkeypatch.setenv("MAX_RETRY_WAIT_TIME", "30")
    monkeypatch.setenv("RETRY_LOGGING_STYLE", "inline_block")
    monkeypatch.setenv("ENDPOINT_HOST", "https://custom-endpoint.example.com")
    monkeypatch.setenv("PDF_TO_IMAGE_DPI", "150")

    settings = get_settings()

    # Verify settings were loaded from environment variables
    assert settings.batch_size == 10
    assert settings.max_workers == 8
    assert settings.max_retries == 50
    assert settings.max_retry_wait_time == 30
    assert settings.retry_logging_style == "inline_block"
    assert settings.endpoint_host == "https://custom-endpoint.example.com"
    assert settings.pdf_to_image_dpi == 150


def test_settings_validation():
    # Test that max_retries can't be negative
    with pytest.raises(ValueError):
        Settings(max_retries=-1)

    # Test that batch_size can't be less than 1
    with pytest.raises(ValueError):
        Settings(batch_size=0)

    # Test that max_workers can't be less than 1
    with pytest.raises(ValueError):
        Settings(max_workers=0)

    # Test that max_retry_wait_time can't be negative
    with pytest.raises(ValueError):
        Settings(max_retry_wait_time=-1)

    # Test pdf_to_image_dpi can't be less than 1
    with pytest.raises(ValueError):
        Settings(pdf_to_image_dpi=0)


def test_settings_str_method():
    # Create settings with an API key
    settings = Settings(vision_agent_api_key="abcde12345")

    # Convert to string and verify API key is redacted
    settings_str = str(settings)
    assert "vision_agent_api_key" in settings_str
    assert "abcde[REDACTED]" in settings_str
    assert "12345" not in settings_str

    # Verify other settings are included
    assert "batch_size" in settings_str
    assert "max_workers" in settings_str
    assert "max_retries" in settings_str
    assert "max_retry_wait_time" in settings_str
    assert "retry_logging_style" in settings_str


def test_visualization_config_defaults():
    # Test default visualization config
    viz_config = VisualizationConfig()

    # Check defaults
    assert viz_config.thickness == 1
    assert viz_config.text_bg_opacity == 0.7
    assert viz_config.padding == 1
    assert viz_config.font_scale == 0.5
    assert viz_config.font == cv2.FONT_HERSHEY_SIMPLEX

    # Check that the color map contains all relevant chunk types
    expected_chunk_types = set(ChunkType)
    for chunk_type in expected_chunk_types:
        assert chunk_type in viz_config.color_map, f"Missing chunk type: {chunk_type}"


def test_visualization_config_custom():
    # Test custom visualization config
    custom_viz_config = VisualizationConfig(
        thickness=2,
        text_bg_opacity=0.5,
        padding=3,
        font_scale=0.8,
        font=cv2.FONT_HERSHEY_PLAIN,
        color_map={ChunkType.text: (255, 0, 0), ChunkType.table: (0, 255, 0)},
    )

    # Check custom values
    assert custom_viz_config.thickness == 2
    assert custom_viz_config.text_bg_opacity == 0.5
    assert custom_viz_config.padding == 3
    assert custom_viz_config.font_scale == 0.8
    assert custom_viz_config.font == cv2.FONT_HERSHEY_PLAIN

    # Check that the custom color map contains only the specified chunk types
    assert custom_viz_config.color_map[ChunkType.text] == (255, 0, 0)
    assert custom_viz_config.color_map[ChunkType.table] == (0, 255, 0)


def test_visualization_config_validation():
    # Test that text_bg_opacity must be between 0 and 1
    with pytest.raises(ValueError):
        VisualizationConfig(text_bg_opacity=-0.1)

    with pytest.raises(ValueError):
        VisualizationConfig(text_bg_opacity=1.1)

    # Test that thickness can't be negative
    with pytest.raises(ValueError):
        VisualizationConfig(thickness=-1)

    # Test that padding can't be negative
    with pytest.raises(ValueError):
        VisualizationConfig(padding=-1)

    # Test that font_scale can't be negative
    with pytest.raises(ValueError):
        VisualizationConfig(font_scale=-0.1)


# ParseConfig Tests
def test_parse_config_default_instantiation():
    from agentic_doc.config import ParseConfig
    
    config = ParseConfig()
    
    assert config.api_key is None
    assert config.include_marginalia is None
    assert config.include_metadata_in_markdown is None
    assert config.extraction_model is None
    assert config.extraction_schema is None
    assert config.split_size is None
    assert config.extraction_split_size is None


def test_parse_config_custom_instantiation():
    from agentic_doc.config import ParseConfig
    from pydantic import BaseModel
    
    class TestModel(BaseModel):
        field1: str
        field2: int
    
    test_schema = {"type": "object", "properties": {"test": {"type": "string"}}}
    
    config = ParseConfig(
        api_key="test_key_123",
        include_marginalia=False,
        include_metadata_in_markdown=True,
        extraction_model=TestModel,
        extraction_schema=test_schema,
        split_size=5,
        extraction_split_size=25
    )
    
    assert config.api_key == "test_key_123"
    assert config.include_marginalia is False
    assert config.include_metadata_in_markdown is True
    assert config.extraction_model == TestModel
    assert config.extraction_schema == test_schema
    assert config.split_size == 5
    assert config.extraction_split_size == 25


def test_parse_config_partial_instantiation():
    from agentic_doc.config import ParseConfig
    
    config = ParseConfig(
        api_key="partial_key",
        include_marginalia=True,
        split_size=15
    )
    
    assert config.api_key == "partial_key"
    assert config.include_marginalia is True
    assert config.include_metadata_in_markdown is None
    assert config.extraction_model is None
    assert config.extraction_schema is None
    assert config.split_size == 15
    assert config.extraction_split_size is None


def test_parse_config_settings_integration():
    from agentic_doc.config import ParseConfig, Settings

    config = ParseConfig(
        api_key="config_api_key",
        split_size=20,
        extraction_split_size=30
    )
    
    custom_settings = Settings(
        vision_agent_api_key="settings_api_key",
        split_size=25,
        extraction_split_size=35
    )

    assert config.api_key == "config_api_key"
    assert config.split_size == 20
    assert config.extraction_split_size == 30
    assert custom_settings.vision_agent_api_key == "settings_api_key"
    assert custom_settings.split_size == 25
    assert custom_settings.extraction_split_size == 35


def test_parse_config_precedence_logic():
    from agentic_doc.config import ParseConfig
    
    # Test the logic used in parse function for precedence
    # config values should take precedence over settings when not None
    config = ParseConfig(
        include_marginalia=False,
        include_metadata_in_markdown=True,
        split_size=12,
        extraction_split_size=18
    )
    
    include_marginalia = config.include_marginalia if config.include_marginalia is not None else True
    include_metadata_in_markdown = config.include_metadata_in_markdown if config.include_metadata_in_markdown is not None else True
    split_size = config.split_size if config.split_size is not None else 10
    extraction_split_size = config.extraction_split_size if config.extraction_split_size is not None else 50
    
    assert include_marginalia is False
    assert include_metadata_in_markdown is True 
    assert split_size == 12
    assert extraction_split_size == 18
    
    config_none = ParseConfig()
    
    include_marginalia_none = config_none.include_marginalia if config_none.include_marginalia is not None else True
    include_metadata_in_markdown_none = config_none.include_metadata_in_markdown if config_none.include_metadata_in_markdown is not None else True
    split_size_none = config_none.split_size if config_none.split_size is not None else 10
    extraction_split_size_none = config_none.extraction_split_size if config_none.extraction_split_size is not None else 50
    
    assert include_marginalia_none is True
    assert include_metadata_in_markdown_none is True
    assert split_size_none == 10
    assert extraction_split_size_none == 50


================================================
FILE: tests/unit/test_connectors.py
================================================
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from agentic_doc.connectors import (
    GoogleDriveConnector,
    GoogleDriveConnectorConfig,
    LocalConnector,
    LocalConnectorConfig,
    S3Connector,
    S3ConnectorConfig,
    URLConnector,
    URLConnectorConfig,
    create_connector,
)


class TestLocalConnector:
    """Test LocalConnector functionality."""

    def test_list_files_in_directory(self, temp_dir):
        """Test listing files in a directory."""
        # Create test files
        (temp_dir / "test1.pdf").touch()
        (temp_dir / "test2.png").touch()
        (temp_dir / "test3.txt").touch()

        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        files = connector.list_files(str(temp_dir))

        # Should only return supported file types
        assert len(files) == 2
        assert str(temp_dir / "test1.pdf") in files
        assert str(temp_dir / "test2.png") in files
        assert str(temp_dir / "test3.txt") not in files

    def test_list_files_with_pattern(self, temp_dir):
        """Test listing files with a pattern."""
        (temp_dir / "doc1.pdf").touch()
        (temp_dir / "doc2.pdf").touch()
        (temp_dir / "image.png").touch()

        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        files = connector.list_files(str(temp_dir), "*.pdf")

        assert len(files) == 2
        assert all(f.endswith(".pdf") for f in files)

    def test_list_files_recursive(self, temp_dir):
        """Test listing files with a pattern."""
        (temp_dir / "doc1.pdf").touch()
        (temp_dir / "doc2.pdf").touch()
        (temp_dir / "image1.png").touch()
        (temp_dir / "subdir1").mkdir()
        (temp_dir / "subdir1" / "doc3.pdf").touch()
        (temp_dir / "subdir1" / "doc4.pdf").touch()
        (temp_dir / "subdir1" / "image2.png").touch()
        (temp_dir / "subdir1" / "subdir2").mkdir()
        (temp_dir / "subdir1" / "subdir2" / "image3.png").touch()
        (temp_dir / "subdir1" / "subdir2" / "doc5.pdf").touch()

        config = LocalConnectorConfig(recursive=True)
        connector = LocalConnector(config)

        files = connector.list_files(str(temp_dir))

        assert len(files) == 8

    def test_list_files_recursive_with_pattern(self, temp_dir):
        """Test listing files with a pattern."""
        (temp_dir / "doc1.pdf").touch()
        (temp_dir / "doc2.pdf").touch()
        (temp_dir / "image1.png").touch()
        (temp_dir / "subdir1").mkdir()
        (temp_dir / "subdir1" / "doc3.pdf").touch()
        (temp_dir / "subdir1" / "doc4.pdf").touch()
        (temp_dir / "subdir1" / "image2.png").touch()
        (temp_dir / "subdir1" / "subdir2").mkdir()
        (temp_dir / "subdir1" / "subdir2" / "image3.png").touch()
        (temp_dir / "subdir1" / "subdir2" / "doc5.pdf").touch()

        config = LocalConnectorConfig(recursive=True)
        connector = LocalConnector(config)

        files = connector.list_files(str(temp_dir), "*.pdf")

        assert len(files) == 5
        assert all(f.endswith(".pdf") for f in files)

    def test_list_files_single_file(self, temp_dir):
        """Test listing a single file."""
        test_file = temp_dir / "test.pdf"
        test_file.touch()

        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        files = connector.list_files(str(test_file))

        assert len(files) == 1
        assert files[0] == str(test_file)

    def test_list_files_nonexistent_path(self):
        """Test listing files from non-existent path."""
        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        with pytest.raises(FileNotFoundError):
            connector.list_files("/nonexistent/path")

    def test_download_file(self, temp_dir):
        """Test downloading (returning) a local file."""
        test_file = temp_dir / "test.pdf"
        test_file.write_text("test content")

        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        result_path = connector.download_file(str(test_file))

        assert result_path == test_file
        assert result_path.exists()

    def test_download_nonexistent_file(self):
        """Test downloading non-existent file."""
        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        with pytest.raises(FileNotFoundError):
            connector.download_file("/nonexistent/file.pdf")

    def test_get_file_info(self, temp_dir):
        """Test getting file metadata."""
        test_file = temp_dir / "test.pdf"
        test_file.write_text("test content")

        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        info = connector.get_file_info(str(test_file))

        assert info["name"] == "test.pdf"
        assert info["path"] == str(test_file)
        assert info["size"] == len("test content")
        assert info["suffix"] == ".pdf"
        assert "modified" in info


class TestGoogleDriveConnector:
    """Test GoogleDriveConnector functionality."""

    @pytest.fixture
    def config(self):
        """Basic configuration fixture."""
        return GoogleDriveConnectorConfig(client_secret_file="test.json")

    @pytest.fixture
    def config_with_folder(self):
        """Configuration with folder ID."""
        return GoogleDriveConnectorConfig(
            client_secret_file="test.json", 
            folder_id="test_folder_id"
        )

    @pytest.fixture
    def mock_credentials(self):
        """Mock credentials object."""
        credentials = MagicMock()
        credentials.valid = False
        credentials.expired = True
        credentials.refresh_token = True
        return credentials

    @pytest.fixture
    def mock_valid_credentials(self):
        """Mock valid credentials object."""
        credentials = MagicMock()
        credentials.valid = True
        return credentials

    @pytest.fixture
    def mock_service(self):
        """Mock Google Drive service."""
        return MagicMock()

    @pytest.fixture
    def mock_files_response(self):
        """Mock file listing response."""
        return {
            "files": [
                {"id": "file1", "name": "document1.pdf", "mimeType": "application/pdf", "size": "1024"},
                {"id": "file2", "name": "image1.png", "mimeType": "image/png", "size": "2048"},
                {"id": "file3", "name": "document2.pdf", "mimeType": "application/pdf", "size": "3072"},
            ]
        }

    @pytest.fixture
    def mock_file_metadata(self):
        """Mock file metadata response."""
        return {
            "id": "file_id_123",
            "name": "test_document.pdf",
            "mimeType": "application/pdf",
            "size": "1024",
            "createdTime": "2023-01-01T00:00:00Z",
            "modifiedTime": "2023-01-02T00:00:00Z"
        }

    @pytest.fixture
    def mock_auth_patches(self):
        """Common authentication patches."""
        with patch('agentic_doc.connectors.build') as mock_build, \
             patch('agentic_doc.connectors.InstalledAppFlow') as mock_flow, \
             patch('agentic_doc.connectors.Credentials') as mock_creds, \
             patch('agentic_doc.connectors.Request') as mock_request, \
             patch('builtins.open', new_callable=mock_open), \
             patch('os.path.exists') as mock_exists:
            
            yield {
                'build': mock_build,
                'flow': mock_flow,
                'credentials': mock_creds,
                'request': mock_request,
                'exists': mock_exists
            }

    def setup_auth_mocks(self, patches, credentials, service, token_exists=False, needs_refresh=False):
        """Helper to set up authentication mocks."""
        patches['exists'].return_value = token_exists
        patches['credentials'].from_authorized_user_file.return_value = credentials
        patches['build'].return_value = service
        
        if not token_exists or (not credentials.valid and not needs_refresh):
            # Setup flow for new authentication
            mock_flow_instance = MagicMock()
            mock_flow_instance.run_local_server.return_value = credentials
            patches['flow'].from_client_secrets_file.return_value = mock_flow_instance

    def test_init_with_config(self, config):
        """Test initialization with config."""
        connector = GoogleDriveConnector(config)
        assert connector.config.client_secret_file == "test.json"

    def test_init_with_folder_id(self, config_with_folder):
        """Test initialization with folder ID."""
        connector = GoogleDriveConnector(config_with_folder)
        assert connector.config.folder_id == "test_folder_id"

    def test_get_service_new_credentials(self, config, mock_credentials, mock_service, mock_auth_patches):
        """Test service initialization with new credentials."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        
        connector = GoogleDriveConnector(config)
        service = connector._get_service()
        
        assert service == mock_service
        mock_auth_patches['build'].assert_called_once_with("drive", "v3", credentials=mock_credentials)

    def test_get_service_existing_credentials(self, config, mock_valid_credentials, mock_service, mock_auth_patches):
        """Test service initialization with existing valid credentials."""
        self.setup_auth_mocks(mock_auth_patches, mock_valid_credentials, mock_service, token_exists=True)
        
        connector = GoogleDriveConnector(config)
        service = connector._get_service()
        
        assert service == mock_service
        mock_auth_patches['build'].assert_called_once_with("drive", "v3", credentials=mock_valid_credentials)

    def test_get_service_refresh_credentials(self, config, mock_credentials, mock_service, mock_auth_patches):
        """Test service initialization with expired credentials that need refresh."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=True, needs_refresh=True)
        
        connector = GoogleDriveConnector(config)
        service = connector._get_service()
        
        assert service == mock_service
        mock_credentials.refresh.assert_called_once_with(mock_auth_patches['request'].return_value)

    def test_get_service_missing_client_secret(self):
        """Test service initialization without client secret file."""
        config = GoogleDriveConnectorConfig()  # No client_secret_file
        
        with patch('os.path.exists', return_value=False):
            connector = GoogleDriveConnector(config)
            
            with pytest.raises(ValueError, match="client_secret_file must be provided"):
                connector._get_service()

    def setup_file_listing_mocks(self, patches, service, files_response):
        """Helper to set up file listing mocks."""
        mock_files_list = MagicMock()
        mock_files_list.list.return_value.execute.return_value = files_response
        service.files.return_value = mock_files_list
        return mock_files_list

    def test_list_files_with_folder_id(self, config_with_folder, mock_credentials, mock_service, 
                                       mock_files_response, mock_auth_patches):
        """Test listing files with folder ID."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        mock_files_list = self.setup_file_listing_mocks(mock_auth_patches, mock_service, mock_files_response)
        
        connector = GoogleDriveConnector(config_with_folder)
        files = connector.list_files()
        
        expected_query = "'test_folder_id' in parents and (mimeType='application/pdf' or mimeType contains 'image/')"
        mock_files_list.list.assert_called_once_with(
            q=expected_query, 
            fields="files(id, name, mimeType, size)"
        )
        assert files == ["file1", "file2", "file3"]

    def test_list_files_with_path(self, config, mock_credentials, mock_service, 
                                  mock_files_response, mock_auth_patches):
        """Test listing files with path parameter."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        
        # Use only first file for this test
        single_file_response = {"files": [mock_files_response["files"][0]]}
        mock_files_list = self.setup_file_listing_mocks(mock_auth_patches, mock_service, single_file_response)
        
        connector = GoogleDriveConnector(config)
        files = connector.list_files(path="path_folder_id")
        
        expected_query = "'path_folder_id' in parents and (mimeType='application/pdf' or mimeType contains 'image/')"
        mock_files_list.list.assert_called_once_with(
            q=expected_query, 
            fields="files(id, name, mimeType, size)"
        )
        assert files == ["file1"]

    def test_list_files_with_pattern(self, config, mock_credentials, mock_service, 
                                     mock_files_response, mock_auth_patches):
        """Test listing files with pattern filtering."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        mock_files_list = self.setup_file_listing_mocks(mock_auth_patches, mock_service, mock_files_response)
        
        connector = GoogleDriveConnector(config)
        files = connector.list_files(pattern="*.pdf")
        
        # Should only return PDF files
        assert files == ["file1", "file3"]

    def test_list_files_api_error(self, config, mock_credentials, mock_service, mock_auth_patches):
        """Test listing files when API call fails."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        
        mock_files_list = MagicMock()
        mock_files_list.list.return_value.execute.side_effect = Exception("API Error")
        mock_service.files.return_value = mock_files_list
        
        connector = GoogleDriveConnector(config)
        
        with pytest.raises(Exception, match="API Error"):
            connector.list_files()

    def setup_download_mocks(self, patches, service, metadata, downloader_chunks=None):
        """Helper to set up download mocks."""
        if downloader_chunks is None:
            downloader_chunks = [(0.5, False), (1.0, True)]
        
        mock_files_get = MagicMock()
        mock_files_get.get.return_value.execute.return_value = metadata
        mock_files_get.get_media.return_value = MagicMock()
        service.files.return_value = mock_files_get
        
        mock_downloader = MagicMock()
        mock_downloader.next_chunk.side_effect = downloader_chunks
        
        return mock_files_get, mock_downloader

    def test_download_file(self, config, mock_credentials, mock_service, mock_file_metadata, 
                           mock_auth_patches, temp_dir):
        """Test downloading a file from Google Drive."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        mock_files_get, mock_downloader = self.setup_download_mocks(
            mock_auth_patches, mock_service, mock_file_metadata
        )
        
        with patch('agentic_doc.connectors.MediaIoBaseDownload', return_value=mock_downloader):
            connector = GoogleDriveConnector(config)
            result_path = connector.download_file("file_id_123")
            
            assert isinstance(result_path, Path)
            assert result_path.name == "test_document.pdf"
            
            mock_files_get.get.assert_called_once_with(fileId="file_id_123")
            mock_files_get.get_media.assert_called_once_with(fileId="file_id_123")

    def test_download_file_with_local_path(self, config, mock_credentials, mock_service, 
                                           mock_file_metadata, mock_auth_patches, temp_dir):
        """Test downloading a file to a specific local path."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        mock_files_get, mock_downloader = self.setup_download_mocks(
            mock_auth_patches, mock_service, mock_file_metadata, downloader_chunks=[(1.0, True)]
        )
        
        with patch('agentic_doc.connectors.MediaIoBaseDownload', return_value=mock_downloader):
            connector = GoogleDriveConnector(config)
            local_path = str(temp_dir / "custom_name.pdf")
            result_path = connector.download_file("file_id_123", local_path)
            
            assert result_path == Path(local_path)

    def test_download_file_api_error(self, config, mock_credentials, mock_service, mock_auth_patches):
        """Test downloading a file when API call fails."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        
        mock_files_get = MagicMock()
        mock_files_get.get.return_value.execute.side_effect = Exception("Download failed")
        mock_service.files.return_value = mock_files_get
        
        connector = GoogleDriveConnector(config)
        
        with pytest.raises(Exception, match="Download failed"):
            connector.download_file("file_id_123")

    def test_get_file_info(self, config, mock_credentials, mock_service, mock_file_metadata, mock_auth_patches):
        """Test getting file metadata."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        
        mock_files_get = MagicMock()
        mock_files_get.get.return_value.execute.return_value = mock_file_metadata
        mock_service.files.return_value = mock_files_get
        
        connector = GoogleDriveConnector(config)
        info = connector.get_file_info("file_id_123")
        
        mock_files_get.get.assert_called_once_with(
            fileId="file_id_123",
            fields="id, name, mimeType, size, createdTime, modifiedTime"
        )
        
        assert info["id"] == "file_id_123"
        assert info["name"] == "test_document.pdf"
        assert info["mimeType"] == "application/pdf"
        assert info["size"] == 1024
        assert info["created"] == "2023-01-01T00:00:00Z"
        assert info["modified"] == "2023-01-02T00:00:00Z"

    def test_get_file_info_api_error(self, config, mock_credentials, mock_service, mock_auth_patches):
        """Test getting file info when API call fails."""
        self.setup_auth_mocks(mock_auth_patches, mock_credentials, mock_service, token_exists=False)
        
        mock_files_get = MagicMock()
        mock_files_get.get.return_value.execute.side_effect = Exception("API Error")
        mock_service.files.return_value = mock_files_get
        
        connector = GoogleDriveConnector(config)
        
        with pytest.raises(Exception, match="API Error"):
            connector.get_file_info("file_id_123")


class TestURLConnector:
    """Test URLConnector functionality."""

    def test_init_with_headers(self):
        """Test initialization with custom headers."""
        config = URLConnectorConfig(
            headers={"Authorization": "Bearer token"}, timeout=60
        )
        connector = URLConnector(config)

        assert connector.config.headers == {"Authorization": "Bearer token"}
        assert connector.config.timeout == 60

    def test_list_files(self):
        """Test listing files (should return the URL)."""
        config = URLConnectorConfig()
        connector = URLConnector(config)

        files = connector.list_files("https://example.com/document.pdf")

        assert len(files) == 1
        assert files[0] == "https://example.com/document.pdf"


class TestConnectorFactory:
    """Test the connector factory function."""

    def test_create_local_connector(self):
        """Test creating a local connector."""
        config = LocalConnectorConfig()
        connector = create_connector(config)

        assert isinstance(connector, LocalConnector)

    def test_create_google_drive_connector(self):
        """Test creating a Google Drive connector."""
        config = GoogleDriveConnectorConfig(client_secret_file="test")
        connector = create_connector(config)

        assert isinstance(connector, GoogleDriveConnector)

    def test_create_s3_connector(self):
        """Test creating an S3 connector."""
        config = S3ConnectorConfig(bucket_name="test-bucket")
        connector = create_connector(config)

        assert isinstance(connector, S3Connector)

    def test_create_url_connector(self):
        """Test creating a URL connector."""
        config = URLConnectorConfig()
        connector = create_connector(config)

        assert isinstance(connector, URLConnector)

    def test_create_unknown_connector(self):
        """Test creating an unknown connector type."""
        config = LocalConnectorConfig()
        config.connector_type = "unknown"

        with pytest.raises(ValueError, match="Unknown connector type"):
            create_connector(config)


class TestConnectorConfigs:
    """Test connector configuration models."""

    def test_local_connector_config_defaults(self):
        """Test LocalConnectorConfig defaults."""
        config = LocalConnectorConfig()
        assert config.connector_type == "local"

    def test_google_drive_connector_config_defaults(self):
        """Test GoogleDriveConnectorConfig defaults."""
        config = GoogleDriveConnectorConfig()
        assert config.connector_type == "google_drive"
        assert config.folder_id is None

    def test_s3_connector_config_defaults(self):
        """Test S3ConnectorConfig defaults."""
        config = S3ConnectorConfig(bucket_name="test-bucket")
        assert config.connector_type == "s3"
        assert config.region_name == "us-east-1"
        assert config.bucket_name == "test-bucket"

    def test_url_connector_config_defaults(self):
        """Test URLConnectorConfig defaults."""
        config = URLConnectorConfig()
        assert config.connector_type == "url"
        assert config.headers is None
        assert config.timeout == 30



================================================
FILE: tests/unit/test_parse.py
================================================
import json
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch
from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from agentic_doc.common import (
    Chunk,
    ChunkGrounding,
    ChunkGroundingBox,
    ChunkType,
    Document,
    ParsedDocument,
    MetadataType,
)
from agentic_doc.connectors import (
    LocalConnector,
    LocalConnectorConfig,
)
from agentic_doc.parse import (
    _merge_next_part,
    _merge_part_results,
    _parse_doc_in_parallel,
    _parse_doc_parts,
    _parse_image,
    _parse_pdf,
    _send_parsing_request,
    parse,
    parse_and_save_document,
    parse_and_save_documents,
    parse_documents,
)

from agentic_doc.config import ParseConfig

@pytest.fixture(autouse=True)
def patch_check_api_key():
    with patch("agentic_doc.parse.check_endpoint_and_api_key"):
        yield


def test_parse_and_save_documents_empty_list(results_dir):
    # Act
    result_paths = parse_and_save_documents([], result_save_dir=results_dir)

    # Assert
    assert result_paths == []


def test_parse_documents_with_file_paths(mock_parsed_document):
    # Setup mock for _parse_pdf and _parse_image
    with patch("agentic_doc.parse.parse_and_save_document") as mock_parse:
        mock_parse.return_value = mock_parsed_document

        # Create test file paths
        file_paths = [
            "/path/to/document1.pdf",
            "/path/to/document2.jpg",
        ]

        # Call the function under test
        results = parse_documents(file_paths)

        # Check that parse_and_save_document was called for each file
        assert mock_parse.call_count == 2

        # Check the results
        assert len(results) == 2
        assert results[0] == mock_parsed_document
        assert results[1] == mock_parsed_document


def test_parse_documents_with_grounding_save_dir(mock_parsed_document, temp_dir):
    # Setup mock for parse_and_save_document
    with patch("agentic_doc.parse.parse_and_save_document") as mock_parse:
        mock_parse.return_value = mock_parsed_document

        # Call the function under test with grounding_save_dir
        results = parse_documents(
            ["/path/to/document.pdf"], grounding_save_dir=temp_dir
        )

        # Check that the grounding_save_dir was passed to parse_and_save_document
        mock_parse.assert_called_once_with(
            "/path/to/document.pdf",
            grounding_save_dir=temp_dir,
            include_marginalia=True,
            include_metadata_in_markdown=True,
            result_save_dir=None,
            extraction_model=None,
            extraction_schema=None,
            config=None,
        )


def test_parse_and_save_documents_with_url(mock_parsed_document, temp_dir):
    # Setup mock for parse_and_save_document
    with patch("agentic_doc.parse.parse_and_save_document") as mock_parse:
        # Configure mock to return a file path
        mock_file_path = Path(temp_dir) / "result.json"
        mock_parse.return_value = mock_file_path

        # Call the function under test with a URL
        result_paths = parse_and_save_documents(
            ["https://example.com/document.pdf"],
            include_marginalia=True,
            include_metadata_in_markdown=True,
            result_save_dir=temp_dir,
            grounding_save_dir=temp_dir,
            extraction_model=None,
            extraction_schema=None,
        )

        # Check that parse_and_save_document was called with the URL and the right parameters
        mock_parse.assert_called_once_with(
            "https://example.com/document.pdf",
            include_marginalia=True,
            include_metadata_in_markdown=True,
            result_save_dir=temp_dir,
            grounding_save_dir=temp_dir,
            extraction_model=None,
            extraction_schema=None,
            config=None,
        )

        # Check the results
        assert len(result_paths) == 1
        assert result_paths[0] == mock_file_path


def test_parse_and_save_document_with_local_file(temp_dir, mock_parsed_document):
    # Create a test file
    test_file = temp_dir / "test.pdf"
    with open(test_file, "wb") as f:
        f.write(b"%PDF-1.7\n")

    # Mock _parse_pdf function
    with patch("agentic_doc.parse._parse_pdf", return_value=mock_parsed_document):
        # Call function without result_save_dir (should return parsed document)
        result = parse_and_save_document(test_file)
        assert isinstance(result, ParsedDocument)
        assert result == mock_parsed_document

        # Call function with result_save_dir (should return file path)
        result_dir = temp_dir / "results"
        result = parse_and_save_document(test_file, result_save_dir=result_dir)
        assert isinstance(result, Path)
        assert result.exists()
        assert result.suffix == ".json"

        # Check that the result JSON contains the expected data
        with open(result) as f:
            result_data = json.load(f)
            assert "markdown" in result_data
            assert "chunks" in result_data
            assert "start_page_idx" in result_data
            assert "end_page_idx" in result_data
            assert "doc_type" in result_data


def test_parse_and_save_document_with_url(temp_dir, mock_parsed_document):
    # Mock download_file and _parse_pdf functions
    with (
        patch("agentic_doc.parse.download_file") as mock_download,
        patch("agentic_doc.parse.get_file_type", return_value="pdf"),
        patch("agentic_doc.parse._parse_pdf", return_value=mock_parsed_document),
    ):
        # Call function with URL
        result = parse_and_save_document("https://example.com/document.pdf")

        # Check that download_file was called
        mock_download.assert_called_once()

        # Check that the result is the parsed document
        assert isinstance(result, ParsedDocument)
        assert result == mock_parsed_document


def test_parse_and_save_document_with_invalid_file_type(temp_dir):
    # Create a test file that isn't a PDF or image
    test_file = temp_dir / "test.txt"
    with open(test_file, "w") as f:
        f.write("This is not a PDF or image")

    # Mock get_file_type to return an unsupported file type
    with patch("agentic_doc.parse.get_file_type", return_value="txt"):
        # Call function and check that it raises ValueError
        with pytest.raises(ValueError) as exc_info:
            parse_and_save_document(test_file)

        assert "Unsupported file type" in str(exc_info.value)


def test_parse_pdf(temp_dir, mock_parsed_document):
    # Create a test PDF file
    pdf_path = temp_dir / "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    # Mock split_pdf and _parse_doc_in_parallel functions
    with (
        patch("agentic_doc.parse.split_pdf") as mock_split,
        patch("agentic_doc.parse._parse_doc_in_parallel") as mock_parse_parts,
    ):
        # Setup mocks
        mock_split.return_value = [
            Document(
                file_path=temp_dir / "test_1.pdf", start_page_idx=0, end_page_idx=1
            ),
            Document(
                file_path=temp_dir / "test_2.pdf", start_page_idx=2, end_page_idx=3
            ),
        ]
        mock_parse_parts.return_value = [mock_parsed_document, mock_parsed_document]

        # Call the function under test
        result = _parse_pdf(pdf_path)

        # Check that split_pdf was called with the right arguments
        mock_split.assert_called_once()

        # Check that _parse_doc_in_parallel was called
        mock_parse_parts.assert_called_once()

        # Check that the result is a ParsedDocument
        assert isinstance(result, ParsedDocument)


def test_parse_image(temp_dir, mock_parsed_document):
    # Create a test image file
    img_path = temp_dir / "test.jpg"
    with open(img_path, "wb") as f:
        f.write(b"JFIF")

    # Mock _send_parsing_request function
    with patch("agentic_doc.parse._send_parsing_request") as mock_send_request:
        # Setup mock to return a valid response
        mock_send_request.return_value = {
            "data": {
                "markdown": mock_parsed_document.markdown,
                "chunks": [chunk.model_dump() for chunk in mock_parsed_document.chunks],
            }
        }

        # Call the function under test
        result = _parse_image(img_path)

        # Check that _send_parsing_request was called with the right arguments
        mock_send_request.assert_called_once_with(
            str(img_path),
            include_marginalia=True,
            include_metadata_in_markdown=True,
            extraction_model=None,
            extraction_schema=None,
            config=None,
        )

        # Check that the result is a ParsedDocument with the expected values
        assert isinstance(result, ParsedDocument)
        assert result.markdown == mock_parsed_document.markdown
        assert result.doc_type == "image"
        assert result.start_page_idx == 0
        assert result.end_page_idx == 0


def test_parse_image_with_error(temp_dir):
    # Create a test image file
    img_path = temp_dir / "test.jpg"
    with open(img_path, "wb") as f:
        f.write(b"JFIF")

    # Mock _send_parsing_request function to raise an exception
    error_msg = "Test error"
    with patch(
        "agentic_doc.parse._send_parsing_request", side_effect=Exception(error_msg)
    ):
        # Call the function under test
        result = _parse_image(img_path)

        # Check that the result contains no chunks but has an error in the errors field
        assert isinstance(result, ParsedDocument)
        assert result.doc_type == "image"
        assert result.start_page_idx == 0
        assert result.end_page_idx == 0
        assert len(result.chunks) == 0
        assert len(result.errors) == 1
        assert result.errors[0].page_num == 0
        assert result.errors[0].error == error_msg
        assert result.errors[0].error_code == -1


def test_merge_part_results_empty_list():
    # Call the function with an empty list
    result = _merge_part_results([])

    # Check that it returns an empty ParsedDocument
    assert isinstance(result, ParsedDocument)
    assert result.markdown == ""
    assert result.chunks == []
    assert result.start_page_idx == 0
    assert result.end_page_idx == 0
    assert result.doc_type == "pdf"


def test_merge_part_results_single_item(mock_parsed_document):
    # Call the function with a single item
    result = _merge_part_results([mock_parsed_document])

    # Check that it returns the item as is
    assert result == mock_parsed_document


def test_merge_part_results_multiple_items(mock_multi_page_parsed_document):
    # Create two parsed documents to merge
    doc1 = ParsedDocument(
        markdown="# Document 1",
        chunks=[
            Chunk(
                text="Document 1",
                chunk_type=ChunkType.text,
                chunk_id="1",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            )
        ],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="pdf",
    )

    doc2 = ParsedDocument(
        markdown="# Document 2",
        chunks=[
            Chunk(
                text="Document 2",
                chunk_type=ChunkType.text,
                chunk_id="2",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            )
        ],
        start_page_idx=1,
        end_page_idx=1,
        doc_type="pdf",
    )

    # Call the function
    result = _merge_part_results([doc1, doc2])

    # Check the merged result
    assert result.markdown == "# Document 1\n\n# Document 2"
    assert len(result.chunks) == 2
    assert result.start_page_idx == 0
    assert result.end_page_idx == 1

    # Check that the page numbers were updated in the second document's chunks
    assert result.chunks[1].grounding[0].page == 1


def test_merge_next_part():
    # Create two ParsedDocuments to merge
    current_doc = ParsedDocument(
        markdown="# Current Doc",
        chunks=[
            Chunk(
                text="Current Doc",
                chunk_type=ChunkType.text,
                chunk_id="1",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            )
        ],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="pdf",
    )

    next_doc = ParsedDocument(
        markdown="# Next Doc",
        chunks=[
            Chunk(
                text="Next Doc",
                chunk_type=ChunkType.text,
                chunk_id="2",
                grounding=[
                    ChunkGrounding(
                        page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                    )
                ],
            )
        ],
        start_page_idx=1,
        end_page_idx=1,
        doc_type="pdf",
    )

    # Call the function
    _merge_next_part(current_doc, next_doc)

    # Check that the current_doc was updated
    assert current_doc.markdown == "# Current Doc\n\n# Next Doc"
    assert len(current_doc.chunks) == 2
    assert current_doc.end_page_idx == 1

    # Check that the page number was updated for the next doc's chunk
    assert current_doc.chunks[1].grounding[0].page == 1


def test_parse_doc_in_parallel(mock_parsed_document):
    # Create Document objects for testing
    doc_parts = [
        Document(file_path="/path/to/doc1.pdf", start_page_idx=0, end_page_idx=1),
        Document(file_path="/path/to/doc2.pdf", start_page_idx=2, end_page_idx=3),
    ]

    # Mock _parse_doc_parts
    with patch("agentic_doc.parse._parse_doc_parts", return_value=mock_parsed_document):
        # Call the function
        results = _parse_doc_in_parallel(doc_parts, doc_name="test.pdf")

        # Check the results
        assert len(results) == 2
        assert results[0] == mock_parsed_document
        assert results[1] == mock_parsed_document


def test_parse_doc_parts_success(mock_parsed_document):
    # Create a Document object for testing
    doc = Document(file_path="/path/to/doc.pdf", start_page_idx=0, end_page_idx=1)

    # Mock _send_parsing_request
    with patch("agentic_doc.parse._send_parsing_request") as mock_send_request:
        # Setup mock to return a valid response
        mock_send_request.return_value = {
            "data": {
                "markdown": mock_parsed_document.markdown,
                "chunks": [chunk.model_dump() for chunk in mock_parsed_document.chunks],
            }
        }

        # Call the function
        result = _parse_doc_parts(doc)

        # Check that _send_parsing_request was called with the right arguments
        mock_send_request.assert_called_once_with(
            str(doc.file_path),
            include_marginalia=True,
            include_metadata_in_markdown=True,
            extraction_model=None,
            extraction_schema=None,
            config=None,
        )

        # Check the result
        assert isinstance(result, ParsedDocument)
        assert result.markdown == mock_parsed_document.markdown
        assert result.start_page_idx == 0
        assert result.end_page_idx == 1
        assert result.doc_type == "pdf"


def test_parse_doc_parts_error():
    # Create a Document object for testing
    doc = Document(file_path="/path/to/doc.pdf", start_page_idx=0, end_page_idx=1)

    # Mock _send_parsing_request to raise an exception
    error_msg = "Test error"
    with patch(
        "agentic_doc.parse._send_parsing_request", side_effect=Exception(error_msg)
    ):
        # Call the function
        result = _parse_doc_parts(doc)

        # Check that the result contains no chunks but has errors for each page
        assert isinstance(result, ParsedDocument)
        assert result.doc_type == "pdf"
        assert result.start_page_idx == 0
        assert result.end_page_idx == 1
        assert len(result.chunks) == 0  # No chunks on error
        assert len(result.errors) == 2  # One error per page

        # Check the first error
        assert result.errors[0].page_num == 0
        assert result.errors[0].error == error_msg
        assert result.errors[0].error_code == -1

        # Check the second error
        assert result.errors[1].page_num == 1
        assert result.errors[1].error == error_msg
        assert result.errors[1].error_code == -1


def test_send_parsing_request_success():
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"markdown": "Test", "chunks": []}}

    # Mock httpx.post to return the mock response
    with (
        patch("agentic_doc.parse.httpx.post", return_value=mock_response),
        patch("agentic_doc.parse.open", MagicMock()),
        patch("agentic_doc.parse.Path") as mock_path,
    ):
        # Setup mock to make the suffix check work
        mock_path_instance = MagicMock()
        mock_path_instance.suffix.lower.return_value = ".pdf"
        mock_path.return_value = mock_path_instance

        # Call the function
        result = _send_parsing_request("test.pdf")

        # Check that the result matches the mock response
        assert result == {"data": {"markdown": "Test", "chunks": []}}


def test_parse_and_save_document_with_grounding_save_dir(
    temp_dir, mock_parsed_document
):
    # Test that grounding images are saved when grounding_save_dir is provided
    test_file = temp_dir / "test.pdf"
    with open(test_file, "wb") as f:
        f.write(b"%PDF-1.7\n")

    grounding_dir = temp_dir / "groundings"

    # Mock the required functions
    with (
        patch("agentic_doc.parse._parse_pdf", return_value=mock_parsed_document),
        patch("agentic_doc.parse.save_groundings_as_images") as mock_save_groundings,
    ):
        result = parse_and_save_document(test_file, grounding_save_dir=grounding_dir)
        # Check that save_groundings_as_images was called
        args, kwargs = mock_save_groundings.call_args
        assert args[0] == test_file
        assert args[1] == mock_parsed_document.chunks
        assert str(args[2]).startswith(str(grounding_dir))
        assert kwargs.get("inplace") is True


def test_parse_pdf_with_empty_result(temp_dir):
    # Test parsing a PDF that returns no chunks
    pdf_path = temp_dir / "empty.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    with (
        patch("agentic_doc.parse.split_pdf") as mock_split,
        patch("agentic_doc.parse._parse_doc_in_parallel") as mock_parse_parts,
    ):
        # Mock an empty result
        empty_doc = ParsedDocument(
            markdown="", chunks=[], start_page_idx=0, end_page_idx=0, doc_type="pdf"
        )

        mock_split.return_value = [
            Document(
                file_path=temp_dir / "empty_1.pdf", start_page_idx=0, end_page_idx=0
            )
        ]
        mock_parse_parts.return_value = [empty_doc]

        result = _parse_pdf(pdf_path)

        assert isinstance(result, ParsedDocument)
        assert len(result.chunks) == 0
        assert result.markdown == ""


def test_merge_part_results_with_errors(mock_parsed_document):
    # Test merging results that contain errors
    from agentic_doc.common import PageError

    doc_with_errors = ParsedDocument(
        markdown="# Document with errors",
        chunks=[],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="pdf",
        errors=[PageError(page_num=0, error="Test error", error_code=-1)],
    )

    result = _merge_part_results([mock_parsed_document, doc_with_errors])

    # Should merge both documents and preserve errors
    assert isinstance(result, ParsedDocument)
    assert len(result.errors) == 1
    assert result.errors[0].error == "Test error"


def test_parse_documents_with_mixed_file_types(temp_dir):
    # Test parsing a mix of file types
    pdf_path = temp_dir / "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    img_path = temp_dir / "test.jpg"
    with open(img_path, "wb") as f:
        f.write(b"JFIF")

    # Mock the parsing functions
    mock_pdf_doc = ParsedDocument(
        markdown="# PDF Document",
        chunks=[],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="pdf",
    )

    mock_img_doc = ParsedDocument(
        markdown="# Image Document",
        chunks=[],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="image",
    )

    with (
        patch("agentic_doc.parse._parse_pdf", return_value=mock_pdf_doc),
        patch("agentic_doc.parse._parse_image", return_value=mock_img_doc),
    ):
        results = parse_documents([str(pdf_path), str(img_path)])

        assert len(results) == 2
        assert results[0].doc_type == "pdf"
        assert results[1].doc_type == "image"


def test_send_parsing_request_with_different_file_types(temp_dir):
    # Test that _send_parsing_request handles different file extensions correctly

    # Test with PDF
    pdf_path = temp_dir / "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"markdown": "PDF Test", "chunks": []}}

    with (
        patch("agentic_doc.parse.httpx.post", return_value=mock_response),
        patch("agentic_doc.parse.open", MagicMock()),
    ):
        result = _send_parsing_request(str(pdf_path))
        assert result["data"]["markdown"] == "PDF Test"

    # Test with image
    img_path = temp_dir / "test.png"
    with open(img_path, "wb") as f:
        f.write(b"PNG")

    mock_response.json.return_value = {"data": {"markdown": "Image Test", "chunks": []}}

    with (
        patch("agentic_doc.parse.httpx.post", return_value=mock_response),
        patch("agentic_doc.parse.open", MagicMock()),
    ):
        result = _send_parsing_request(str(img_path))
        assert result["data"]["markdown"] == "Image Test"


def test_document_string_representation():
    # Test the string representation of Document objects
    doc = Document(
        file_path=Path("/path/to/test_document.pdf"), start_page_idx=5, end_page_idx=10
    )

    expected_str = "File name: test_document.pdf\tPage: [5:10]"
    assert str(doc) == expected_str


def test_parse_pdf_handles_single_page_document(temp_dir):
    # Test parsing a single-page PDF
    pdf_path = temp_dir / "single_page.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    single_page_doc = ParsedDocument(
        markdown="# Single Page",
        chunks=[],
        start_page_idx=0,
        end_page_idx=0,
        doc_type="pdf",
    )

    with (
        patch("agentic_doc.parse.split_pdf") as mock_split,
        patch("agentic_doc.parse._parse_doc_in_parallel") as mock_parse_parts,
    ):
        mock_split.return_value = [
            Document(
                file_path=temp_dir / "single_1.pdf", start_page_idx=0, end_page_idx=0
            )
        ]
        mock_parse_parts.return_value = [single_page_doc]

        result = _parse_pdf(pdf_path)

        assert result.start_page_idx == 0
        assert result.end_page_idx == 0
        assert result.doc_type == "pdf"


class TestParseFunctionConsolidated:
    """Test the consolidated parse function."""

    def test_parse_single_document(self, temp_dir, mock_parsed_document):
        """Test parsing a single document."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        with patch("agentic_doc.parse._parse_pdf", return_value=mock_parsed_document):
            result = parse(test_file)

            assert all(isinstance(res, ParsedDocument) for res in result)
            assert result == [mock_parsed_document]

    def test_parse_single_document_with_save_dir(self, temp_dir, mock_parsed_document):
        """Test parsing a single document with save directory."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        result_dir = temp_dir / "results"

        with patch("agentic_doc.parse._parse_pdf", return_value=mock_parsed_document):
            result = parse(test_file, result_save_dir=result_dir)

            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], ParsedDocument)

    def test_parse_multiple_documents(self, temp_dir, mock_parsed_document):
        """Test parsing multiple documents."""
        test_files = [temp_dir / "test1.pdf", temp_dir / "test2.pdf"]
        for f in test_files:
            with open(f, "wb") as file:
                file.write(b"%PDF-1.7\n")

        with patch(
            "agentic_doc.parse.parse_documents",
            return_value=[mock_parsed_document, mock_parsed_document],
        ) as mock_parse:
            result = parse([str(f) for f in test_files])

            assert isinstance(result, list)
            assert len(result) == 2
            mock_parse.assert_called_once()

    def test_parse_with_grounding_save_dir(self, temp_dir, mock_parsed_document):
        """Test parsing with grounding save directory."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        grounding_dir = temp_dir / "groundings"

        with (
            patch("agentic_doc.parse._parse_pdf", return_value=mock_parsed_document),
            patch(
                "agentic_doc.parse.save_groundings_as_images"
            ) as mock_save_groundings,
        ):
            result = parse(test_file, grounding_save_dir=grounding_dir)

            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], ParsedDocument)
            # Verify that save_groundings_as_images was called
            mock_save_groundings.assert_called_once()

    def test_parse_with_local_connector_config(self, temp_dir, mock_parsed_document):
        """Test parsing with local connector configuration."""
        # Create test files
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        config = LocalConnectorConfig()

        with (
            patch("agentic_doc.parse.create_connector") as mock_create,
            patch(
                "agentic_doc.parse._parse_document_list",
                return_value=[mock_parsed_document],
            ) as mock_parse_list,
        ):
            # Mock connector
            mock_connector = MagicMock()
            mock_connector.list_files.return_value = [str(test_file)]
            mock_connector.download_file.return_value = test_file
            mock_create.return_value = mock_connector

            result = parse(config, connector_path=str(temp_dir))

            assert isinstance(result, list)
            mock_create.assert_called_once_with(config)
            mock_connector.list_files.assert_called_once_with(str(temp_dir), None)

    def test_parse_with_local_connector_instance(self, temp_dir, mock_parsed_document):
        """Test parsing with local connector instance."""
        # Create test files
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        config = LocalConnectorConfig()
        connector = LocalConnector(config)

        with (
            patch.object(connector, "list_files", return_value=[str(test_file)]),
            patch.object(connector, "download_file", return_value=test_file),
            patch(
                "agentic_doc.parse._parse_document_list",
                return_value=[mock_parsed_document],
            ) as mock_parse_list,
        ):
            result = parse(connector, connector_path=str(temp_dir))

            assert isinstance(result, list)
            connector.list_files.assert_called_once_with(str(temp_dir), None)

    def test_parse_with_connector_no_files_found(self, temp_dir):
        """Test parsing with connector when no files are found."""
        config = LocalConnectorConfig()

        with patch("agentic_doc.parse.create_connector") as mock_create:
            # Mock connector that returns no files
            mock_connector = MagicMock()
            mock_connector.list_files.return_value = []
            mock_create.return_value = mock_connector

            result = parse(config, connector_path=str(temp_dir))

            assert result == []

    def test_parse_with_connector_download_failures(
        self, temp_dir, mock_parsed_document
    ):
        """Test parsing with connector when some downloads fail."""
        config = LocalConnectorConfig()

        with (
            patch("agentic_doc.parse.create_connector") as mock_create,
            patch(
                "agentic_doc.parse._parse_document_list",
                return_value=[mock_parsed_document],
            ) as mock_parse_list,
        ):
            # Mock connector
            mock_connector = MagicMock()
            mock_connector.list_files.return_value = ["file1.pdf", "file2.pdf"]
            # First download succeeds, second fails
            mock_connector.download_file.side_effect = [
                Path("file1.pdf"),
                Exception("Download failed"),
            ]
            mock_create.return_value = mock_connector

            result = parse(config)

            # Should continue with successful downloads
            assert isinstance(result, list)
            assert mock_connector.download_file.call_count == 2
            mock_parse_list.assert_called_once()

    def test_parse_with_connector_all_downloads_fail(self, temp_dir):
        """Test parsing with connector when all downloads fail."""
        config = LocalConnectorConfig()

        with patch("agentic_doc.parse.create_connector") as mock_create:
            # Mock connector
            mock_connector = MagicMock()
            mock_connector.list_files.return_value = ["file1.pdf", "file2.pdf"]
            mock_connector.download_file.side_effect = Exception("Download failed")
            mock_create.return_value = mock_connector

            result = parse(config)

            assert result == []

    def test_parse_unsupported_type(self):
        """Test parsing with unsupported document type."""
        with pytest.raises(ValueError, match="Unsupported documents type"):
            parse(123)  # Invalid type

    def test_parse_with_marginalia_and_metadata_flags(
        self, temp_dir, mock_parsed_document
    ):
        """Test parsing with marginalia and metadata flags."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        with patch(
            "agentic_doc.parse.parse_and_save_document",
            return_value=mock_parsed_document,
        ) as mock_parse:
            result = parse(
                test_file, include_marginalia=False, include_metadata_in_markdown=False
            )

            mock_parse.assert_called_once_with(
                test_file,
                include_marginalia=False,
                include_metadata_in_markdown=False,
                grounding_save_dir=None,
                result_save_dir=None,
                extraction_model=None,
                extraction_schema=None,
                config=None,
            )

    def test_parse_with_bytes(self, mock_parsed_document):
        """Test parsing with bytes."""
        with patch(
            "agentic_doc.parse.parse_and_save_document",
            return_value=mock_parsed_document,
        ) as mock_parse:
            result = parse(
                b"%PDF-1.7\n",
                include_marginalia=False,
                include_metadata_in_markdown=False,
            )

            mock_parse.assert_called_once_with(
                ANY,
                include_marginalia=False,
                include_metadata_in_markdown=False,
                grounding_save_dir=None,
                result_save_dir=None,
                extraction_model=None,
                extraction_schema=None,
                config=None,
            )

    def test_parse_list_with_save_dir(self, temp_dir, mock_parsed_document):
        """Test parsing list of documents with save directory."""
        test_files = [temp_dir / "test1.pdf", temp_dir / "test2.pdf"]
        test_save_files = [temp_dir / "result1.json", temp_dir / "result2.json"]
        for f in test_files:
            with open(f, "wb") as file:
                file.write(b"%PDF-1.7\n")

        for f in test_save_files:
            with open(f, "w") as file:
                file.write(
                    '{"markdown": "", "chunks": [], "start_page_idx": 0, "end_page_idx": 0, "doc_type": "pdf"}'
                )

        result_dir = temp_dir / "results"

        with patch(
            "agentic_doc.parse.parse_and_save_documents",
            return_value=[Path(test_save_files[0]), Path(test_save_files[1])],
        ) as mock_parse:
            result = parse([str(f) for f in test_files], result_save_dir=result_dir)

            assert isinstance(result, list)
            assert len(result) == 2
            mock_parse.assert_called_once()

    def test_parse_url_string(self, mock_parsed_document):
        """Test parsing a URL string."""
        url = "https://example.com/document.pdf"

        with patch(
            "agentic_doc.parse.parse_and_save_document",
            return_value=mock_parsed_document,
        ) as mock_parse:
            result = parse(url)

            assert all(isinstance(res, ParsedDocument) for res in result)
            mock_parse.assert_called_once_with(
                url,
                include_marginalia=True,
                include_metadata_in_markdown=True,
                grounding_save_dir=None,
                result_save_dir=None,
                extraction_model=None,
                extraction_schema=None,
                config=None,
            )

    def test_parse_with_extraction_model(self, temp_dir, mock_parsed_document):
        """Test parsing with an extraction model."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        class EmployeeFields(BaseModel):
            employee_name: str = Field(description="the full name of the employee")
            gross_pay: float = Field(description="the gross pay of the employee")

        with patch(
            "agentic_doc.parse.parse_and_save_document",
            return_value=mock_parsed_document,
        ) as mock_parse:
            result = parse(test_file, extraction_model=EmployeeFields)
            assert all(isinstance(res, ParsedDocument) for res in result)
            mock_parse.assert_called_once_with(
                test_file,
                include_marginalia=True,
                include_metadata_in_markdown=True,
                grounding_save_dir=None,
                result_save_dir=None,
                extraction_model=EmployeeFields,
                extraction_schema=None,
                config=None,
            )

    def test_extraction_metadata_with_simple_model(self, sample_image_path):
        class PersonInfo(BaseModel):
            name: str = Field(description="Person's name")
            age: int = Field(description="Person's age")

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Test Document\nName: John Doe\nAge: 30",
                    "chunks": [
                        {
                            "text": "Name: John Doe",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {"name": "John Doe", "age": 30},
                    "extraction_metadata": {
                        "name": {"chunk_references": ["high"]},
                        "age": {"chunk_references": ["medium"]},
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_model=PersonInfo)

            # Verify extraction is correctly typed
            assert isinstance(result[0].extraction, PersonInfo)
            assert result[0].extraction.name == "John Doe"
            assert result[0].extraction.age == 30

            # Verify extraction_metadata is correctly typed
            metadata = result[0].extraction_metadata
            assert metadata is not None

            # Check that metadata fields are dict[str, list[str]]
            assert isinstance(metadata.name, MetadataType)
            assert isinstance(metadata.age, MetadataType)

            # Check specific metadata values
            assert metadata.name.chunk_references == ["high"]
            assert metadata.age.chunk_references == ["medium"]

    def test_extraction_metadata_with_nested_models(self, sample_image_path):
        """Test extraction_metadata functionality with nested models."""

        class Address(BaseModel):
            street: str = Field(description="Street address")
            city: str = Field(description="City")

        class Person(BaseModel):
            name: str = Field(description="Person's name")
            address: Address = Field(description="Person's address")

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Person Info\nName: Jane Smith\nAddress: 123 Main St, Springfield",
                    "chunks": [
                        {
                            "text": "Name: Jane Smith",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {
                        "name": "Jane Smith",
                        "address": {"street": "123 Main St", "city": "Springfield"},
                    },
                    "extraction_metadata": {
                        "name": {"chunk_references": ["high"]},
                        "address": {
                            "street": {"chunk_references": ["medium"]},
                            "city": {"chunk_references": ["high"]},
                        },
                    },
                },
                "errors": [],
            }
            result = parse(sample_image_path, extraction_model=Person)

            assert isinstance(result[0].extraction, Person)
            assert result[0].extraction.name == "Jane Smith"
            assert isinstance(result[0].extraction.address, Address)
            assert result[0].extraction.address.street == "123 Main St"
            assert result[0].extraction.address.city == "Springfield"

            metadata = result[0].extraction_metadata
            assert metadata is not None

            assert isinstance(metadata.name, MetadataType)
            assert metadata.name.chunk_references == ["high"]

            assert hasattr(metadata, "address")
            assert hasattr(metadata.address, "street")
            assert hasattr(metadata.address, "city")

            assert isinstance(metadata.address.street, MetadataType)
            assert isinstance(metadata.address.city, MetadataType)
            assert metadata.address.street.chunk_references == ["medium"]
            assert metadata.address.city.chunk_references == ["high"]

    def test_extraction_metadata_with_optional_fields(self, sample_image_path):
        """Test extraction_metadata functionality with optional fields."""

        class PersonWithOptional(BaseModel):
            name: str = Field(description="Person's name")
            phone: Optional[str] = Field(default=None, description="Phone number")
            email: Optional[str] = Field(default=None, description="Email address")

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Contact Info\nName: Bob Johnson\nEmail: bob@example.com",
                    "chunks": [
                        {
                            "text": "Name: Bob Johnson",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {
                        "name": "Bob Johnson",
                        "phone": None,
                        "email": "bob@example.com",
                    },
                    "extraction_metadata": {
                        "name": {"chunk_references": ["high"]},
                        "phone": None,
                        "email": {"chunk_references": ["medium"]},
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_model=PersonWithOptional)

            assert isinstance(result[0].extraction, PersonWithOptional)
            assert result[0].extraction.name == "Bob Johnson"
            assert result[0].extraction.phone is None
            assert result[0].extraction.email == "bob@example.com"

            metadata = result[0].extraction_metadata
            assert metadata is not None

            assert isinstance(metadata.name, MetadataType)
            assert metadata.name.chunk_references == ["high"]

            assert metadata.phone is None  # Optional field with no data should be None
            assert isinstance(metadata.email, MetadataType)
            assert metadata.email.chunk_references == ["medium"]

    def test_extraction_metadata_with_list_fields(self, sample_image_path):
        """Test extraction_metadata functionality with list fields."""

        class Skill(BaseModel):
            name: str = Field(description="Skill name")
            level: str = Field(description="Skill level")

        class PersonWithSkills(BaseModel):
            name: str = Field(description="Person's name")
            skills: List[Skill] = Field(description="List of skills")

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Resume\nName: Alice Brown\nSkills: Python (Expert), Java (Intermediate)",
                    "chunks": [
                        {
                            "text": "Name: Alice Brown",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {
                        "name": "Alice Brown",
                        "skills": [
                            {"name": "Python", "level": "Expert"},
                            {"name": "Java", "level": "Intermediate"},
                        ],
                    },
                    "extraction_metadata": {
                        "name": {"chunk_references": ["high"]},
                        "skills": [
                            {
                                "name": {"chunk_references": ["high"]},
                                "level": {"chunk_references": ["high"]},
                            },
                            {
                                "name": {"chunk_references": ["high"]},
                                "level": {"chunk_references": ["medium"]},
                            },
                        ],
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_model=PersonWithSkills)

            assert isinstance(result[0].extraction, PersonWithSkills)
            assert result[0].extraction.name == "Alice Brown"
            assert len(result[0].extraction.skills) == 2
            assert result[0].extraction.skills[0].name == "Python"
            assert result[0].extraction.skills[0].level == "Expert"

            metadata = result[0].extraction_metadata
            assert metadata is not None

            assert isinstance(metadata.name, MetadataType)
            assert metadata.name.chunk_references == ["high"]

            assert isinstance(metadata.skills, list)
            assert len(metadata.skills) == 2

            first_skill_meta = metadata.skills[0]
            assert isinstance(first_skill_meta.name, MetadataType)
            assert isinstance(first_skill_meta.level, MetadataType)
            assert first_skill_meta.name.chunk_references == ["high"]
            assert first_skill_meta.level.chunk_references == ["high"]

            second_skill_meta = metadata.skills[1]
            assert isinstance(second_skill_meta.name, MetadataType)
            assert isinstance(second_skill_meta.level, MetadataType)
            assert second_skill_meta.name.chunk_references == ["high"]
            assert second_skill_meta.level.chunk_references == ["medium"]

    def test_extraction_metadata_error(self, sample_image_path):
        """Test extraction_metadata error."""

        class Skill(BaseModel):
            name: str = Field(description="Skill name")
            level: str = Field(description="Skill level")

        class PersonWithSkills(BaseModel):
            name: str = Field(description="Person's name")
            skills: List[Skill] = Field(description="List of skills")

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Resume\nName: Alice Brown\nSkills: Python (Expert), Java (Intermediate)",
                    "chunks": [
                        {
                            "text": "Name: Alice Brown",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {
                        "name": "Alice Brown",
                        "skills": [
                            {"name": "Python", "level": "Expert"},
                            {"name": "Java", "level": "Intermediate"},
                        ],
                    },
                    "extraction_metadata": {
                        "name": "Alice Brown",
                        "skills": [
                            {
                                "name": {"chunk_references": ["high"]},
                                "level": {"chunk_references": ["high"]},
                            },
                            {
                                "name": {"chunk_references": ["high"]},
                                "level": {"chunk_references": ["medium"]},
                            },
                        ],
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_model=PersonWithSkills)
            assert result[0].extraction is None
            assert result[0].extraction_metadata is None
            assert "validation error" in result[0].errors[0].error.lower()

    def test_parse_with_extraction_schema(self, temp_dir, mock_parsed_document):
        """Test parsing with an extraction schema."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        extraction_schema = {
            "type": "object",
            "properties": {
                "employee_name": {
                    "type": "string",
                    "description": "the full name of the employee",
                },
                "gross_pay": {
                    "type": "number",
                    "description": "the gross pay of the employee",
                },
            },
            "required": ["employee_name", "gross_pay"],
        }

        with patch(
            "agentic_doc.parse.parse_and_save_document",
            return_value=mock_parsed_document,
        ) as mock_parse:
            result = parse(test_file, extraction_schema=extraction_schema)
            assert all(isinstance(res, ParsedDocument) for res in result)
            mock_parse.assert_called_once_with(
                test_file,
                include_marginalia=True,
                include_metadata_in_markdown=True,
                grounding_save_dir=None,
                result_save_dir=None,
                extraction_model=None,
                extraction_schema=extraction_schema,
                config=None,
            )

    def test_parse_with_extraction_schema_validation(self, sample_image_path):
        """Test that extraction_schema validates the response correctly."""
        extraction_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name"},
                "age": {"type": "integer", "description": "Person's age"},
            },
            "required": ["name", "age"],
        }

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Test Document\nName: John Doe\nAge: 30",
                    "chunks": [
                        {
                            "text": "Name: John Doe",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {"name": "John Doe", "age": 30},
                    "extraction_metadata": {
                        "name": {"chunk_references": ["high"]},
                        "age": {"chunk_references": ["medium"]},
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_schema=extraction_schema)

            # Verify extraction is a dict (not a Pydantic model)
            assert isinstance(result[0].extraction, dict)
            assert result[0].extraction["name"] == "John Doe"
            assert result[0].extraction["age"] == 30
            assert isinstance(result[0].extraction_metadata, dict)

    def test_parse_with_extraction_schema_validation_error(self, sample_image_path):
        """Test that extraction_schema validation errors are handled correctly."""
        extraction_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name"},
                "age": {"type": "integer", "description": "Person's age"},
            },
            "required": ["name", "age"],
        }

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            # Return data that doesn't match the schema (age is string instead of integer)
            mock_request.return_value = {
                "data": {
                    "markdown": "# Test Document\nName: John Doe\nAge: thirty",
                    "chunks": [
                        {
                            "text": "Name: John Doe",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {
                        "name": "John Doe",
                        "age": "thirty",
                    },  # Invalid: age should be integer
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_schema=extraction_schema)

            assert result[0].extraction is None
            assert len(result[0].errors) > 0

    def test_parse_with_extraction_schema_api_validation_error(self, sample_image_path):
        """Test that extraction_schema api validation errors are forwarded correctly."""
        extraction_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name"},
                "age": {"type": "integer", "description": "Person's age"},
            },
            "required": ["name"],
        }
        extraction_error_msg = "Failed to extract the fields from the input schema. Error: Invalid schema - All object keys must be required at root. Expected required=['name', 'age'], got required=['name']"

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            # Return data that doesn't match the schema (age is string instead of integer)
            mock_request.return_value = {
                "data": {
                    "markdown": "# Test Document\nName: John Doe\nAge: 30",
                    "chunks": [
                        {
                            "text": "Name: John Doe",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": None,  # No fields extracted because of schema validation error
                },
                "errors": [],
                "extraction_error": extraction_error_msg,
            }

            result = parse(sample_image_path, extraction_schema=extraction_schema)

            assert result[0].extraction is None
            assert result[0].extraction_error == extraction_error_msg

    def test_parse_with_extraction_schema_complex(self, sample_image_path):
        """Test extraction_schema with complex nested schema."""
        extraction_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Person's name"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string", "description": "Street address"},
                        "city": {"type": "string", "description": "City"},
                    },
                    "required": ["street", "city"],
                },
                "skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Skill name"},
                            "level": {"type": "string", "description": "Skill level"},
                        },
                        "required": ["name", "level"],
                    },
                },
            },
            "required": ["name", "address", "skills"],
        }

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Resume\nName: Alice Brown\nAddress: 123 Main St, Springfield\nSkills: Python (Expert), Java (Intermediate)",
                    "chunks": [
                        {
                            "text": "Name: Alice Brown",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {
                        "name": "Alice Brown",
                        "address": {"street": "123 Main St", "city": "Springfield"},
                        "skills": [
                            {"name": "Python", "level": "Expert"},
                            {"name": "Java", "level": "Intermediate"},
                        ],
                    },
                    "extraction_metadata": {
                        "name": {"chunk_references": ["high"]},
                        "address": {
                            "street": {"chunk_references": ["medium"]},
                            "city": {"chunk_references": ["high"]},
                        },
                        "skills": [
                            {
                                "name": {"chunk_references": ["high"]},
                                "level": {"chunk_references": ["high"]},
                            },
                            {
                                "name": {"chunk_references": ["high"]},
                                "level": {"chunk_references": ["medium"]},
                            },
                        ],
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_schema=extraction_schema)

            # Verify extraction is a dict with complex nested structure
            assert isinstance(result[0].extraction, dict)
            assert result[0].extraction["name"] == "Alice Brown"
            assert isinstance(result[0].extraction["address"], dict)
            assert result[0].extraction["address"]["street"] == "123 Main St"
            assert result[0].extraction["address"]["city"] == "Springfield"
            assert isinstance(result[0].extraction["skills"], list)
            assert len(result[0].extraction["skills"]) == 2
            assert result[0].extraction["skills"][0]["name"] == "Python"
            assert result[0].extraction["skills"][0]["level"] == "Expert"
            assert isinstance(result[0].extraction_metadata, dict)

    def test_parse_with_both_extraction_model_and_schema_error(self, temp_dir):
        """Test that providing both extraction_model and extraction_schema raises an error."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        class EmployeeFields(BaseModel):
            employee_name: str = Field(description="the full name of the employee")
            gross_pay: float = Field(description="the gross pay of the employee")

        extraction_schema = {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string"},
                "gross_pay": {"type": "number"},
            },
        }

        with pytest.raises(
            ValueError,
            match="extraction_model and extraction_schema cannot be used together",
        ):
            parse(
                test_file,
                extraction_model=EmployeeFields,
                extraction_schema=extraction_schema,
            )

    def test_parse_with_neither_extraction_model_nor_schema(
        self, temp_dir, mock_parsed_document
    ):
        """Test parsing without any extraction model or schema."""
        test_file = temp_dir / "test.pdf"
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.7\n")

        with patch(
            "agentic_doc.parse.parse_and_save_document",
            return_value=mock_parsed_document,
        ) as mock_parse:
            result = parse(test_file)
            assert all(isinstance(res, ParsedDocument) for res in result)
            mock_parse.assert_called_once_with(
                test_file,
                include_marginalia=True,
                include_metadata_in_markdown=True,
                grounding_save_dir=None,
                result_save_dir=None,
                extraction_model=None,
                extraction_schema=None,
                config=None,
            )

    def test_parse_additional_extraction_metadata(
        self, sample_image_path
    ):
        """Test parsing with additional extraction metadata returned from the API"""
        class PersonInfo(BaseModel):
            name: str = Field(description="Person's name")
            age: int = Field(description="Person's age")

        with patch("agentic_doc.parse._send_parsing_request") as mock_request:
            mock_request.return_value = {
                "data": {
                    "markdown": "# Test Document\nName: John Doe\nAge: 30",
                    "chunks": [
                        {
                            "text": "Name: John Doe",
                            "grounding": [
                                {
                                    "page": 0,
                                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                }
                            ],
                            "chunk_type": "text",
                            "chunk_id": "1",
                        }
                    ],
                    "extracted_schema": {"name": "John Doe", "age": 30},
                    "extraction_metadata": {
                        "name": {"chunk_references": ["id1"], "confidence": 0.6, "bounding_box": [0.1, 0.4, 0.03, 0.25]},
                        "age": {"chunk_references": ["id2"], "confidence": 0.2, "bounding_box": [0.01, 0.09, 0.23, 1.0]},
                    },
                },
                "errors": [],
            }

            result = parse(sample_image_path, extraction_model=PersonInfo)

            # Verify extraction is correctly typed
            assert isinstance(result[0].extraction, PersonInfo)
            assert result[0].extraction.name == "John Doe"
            assert result[0].extraction.age == 30

            # Verify extraction_metadata is correctly typed
            metadata = result[0].extraction_metadata
            assert metadata is not None

            # Check that metadata fields are dict[str, list[str]]
            assert isinstance(metadata.name, MetadataType)
            assert isinstance(metadata.age, MetadataType)

            # Check specific metadata values
            assert metadata.name.chunk_references == ["id1"]
            assert metadata.age.chunk_references == ["id2"]


    def test_parse_with_config_integration(self, sample_image_path, sample_pdf_path, monkeypatch):
        import unittest.mock
        from unittest.mock import MagicMock
        
        monkeypatch.setenv("VISION_AGENT_API_KEY", "env_test_key")
        monkeypatch.setenv("SPLIT_SIZE", "5")
        monkeypatch.setenv("EXTRACTION_SPLIT_SIZE", "15")
        
        mock_response_data = {
            "data": {
                "markdown": "# Test Document\n\nThis is a test document.",
                "chunks": [
                    {
                        "text": "Test Document",
                        "chunk_type": "text",
                        "chunk_id": "test_chunk_1",
                        "grounding": [
                            {
                                "page": 0,
                                "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                                "image_path": None
                            }
                        ]
                    }
                ]
            },
            "errors": [],
            "extraction_error": None
        }
        
        captured_requests = []
        
        def mock_post(*args, **kwargs):
            captured_requests.append({
                "url": args[0] if args else kwargs.get("url"),
                "data": kwargs.get("data", {}),
                "headers": kwargs.get("headers", {}),
                "files": kwargs.get("files", {})
            })
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            return mock_response
        
        with unittest.mock.patch("httpx.post", side_effect=mock_post), \
            unittest.mock.patch("agentic_doc.parse.check_endpoint_and_api_key"):
            config_true_values = ParseConfig(
                api_key="config_test_key",
                include_marginalia=True,
                include_metadata_in_markdown=True,
                split_size=8,
                extraction_split_size=20
            )
            
            result = parse(sample_image_path, config=config_true_values)
            
            assert len(result) == 1
            assert result[0].markdown == "# Test Document\n\nThis is a test document."
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["data"]["include_marginalia"] is True
            assert request["data"]["include_metadata_in_markdown"] is True
            assert request["headers"]["Authorization"] == "Basic config_test_key"
            
            captured_requests.clear()
            
            partial_config = ParseConfig(
                include_marginalia=True,
                api_key="partial_config_key"
            )
            
            result = parse(sample_image_path, config=partial_config)
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["data"]["include_marginalia"] is True
            assert request["data"]["include_metadata_in_markdown"] is True
            assert request["headers"]["Authorization"] == "Basic partial_config_key"
            
            captured_requests.clear()
            
            result = parse(sample_image_path, include_marginalia=False, include_metadata_in_markdown=False)
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["data"]["include_marginalia"] is False
            assert request["data"]["include_metadata_in_markdown"] is False
            assert request["headers"]["Authorization"] == "Basic env_test_key"
            
            captured_requests.clear()
            
            config_with_settings_override = ParseConfig(
                api_key="final_config_key",
                include_marginalia=True
            )
            
            result = parse(
                sample_image_path, 
                config=config_with_settings_override,
                include_marginalia=False,
                include_metadata_in_markdown=False
            )
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["data"]["include_marginalia"] is True
            assert request["data"]["include_metadata_in_markdown"] is False
            assert request["headers"]["Authorization"] == "Basic final_config_key"
            
            captured_requests.clear()
            
        with unittest.mock.patch("httpx.post", side_effect=mock_post), \
            unittest.mock.patch("agentic_doc.parse.check_endpoint_and_api_key"):
            config_with_api_key_precedence = ParseConfig(
                api_key="precedence_test_key"
            )
            
            result = parse(sample_image_path, config=config_with_api_key_precedence)
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["headers"]["Authorization"] == "Basic precedence_test_key"
            
            captured_requests.clear()
            
            result = parse(sample_image_path)
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["headers"]["Authorization"] == "Basic env_test_key"
            
            captured_requests.clear()
            
        with unittest.mock.patch("httpx.post", side_effect=mock_post), \
            unittest.mock.patch("agentic_doc.parse.check_endpoint_and_api_key"):
            with unittest.mock.patch("agentic_doc.parse.split_pdf") as mock_split_pdf:
                mock_split_pdf.return_value = [
                    type('Document', (), {
                        'file_path': sample_pdf_path,
                        'start_page_idx': 0,
                        'end_page_idx': 0
                    })()
                ]
                
                config_with_split_size = ParseConfig(
                    api_key="split_size_test_key",
                    split_size=25
                )
                
                result = parse(sample_pdf_path, config=config_with_split_size)
                
                assert len(result) == 1
                mock_split_pdf.assert_called_once()
                split_size_arg = mock_split_pdf.call_args[0][2]
                assert split_size_arg == 25
                
                captured_requests.clear()
                mock_split_pdf.reset_mock()
                
                result = parse(sample_pdf_path)
                
                assert len(result) == 1
                
                captured_requests.clear()
                
        with unittest.mock.patch("httpx.post", side_effect=mock_post), \
            unittest.mock.patch("agentic_doc.parse.check_endpoint_and_api_key"):
            with unittest.mock.patch("agentic_doc.parse.split_pdf") as mock_split_pdf:
                mock_split_pdf.return_value = [
                    type('Document', (), {
                        'file_path': sample_pdf_path,
                        'start_page_idx': 0,
                        'end_page_idx': 0
                    })()
                ]
                
                class TestExtractionModel:
                    @staticmethod
                    def model_json_schema():
                        return {"type": "object", "properties": {"test_field": {"type": "string"}}}
                    @staticmethod
                    def model_validate(data):
                        return type('ExtractionResult', (), {"test_field": "test_value"})()
                
                config_with_extraction_split_size = ParseConfig(
                    api_key="extraction_split_size_test_key",
                    extraction_split_size=30
                )
                
                result = parse(sample_pdf_path, extraction_model=TestExtractionModel, config=config_with_extraction_split_size)
                
                assert len(result) == 1
                mock_split_pdf.assert_called_once()
                extraction_split_size_arg = mock_split_pdf.call_args[0][2]
                assert extraction_split_size_arg == 30
                
                captured_requests.clear()
                mock_split_pdf.reset_mock()
                
                result = parse(sample_pdf_path, extraction_model=TestExtractionModel)
                
                assert len(result) == 1
                mock_split_pdf.assert_called_once()
                extraction_split_size_arg = mock_split_pdf.call_args[0][2]
                assert extraction_split_size_arg == 15
                
                captured_requests.clear()
                
        with unittest.mock.patch("httpx.post", side_effect=mock_post), \
            unittest.mock.patch("agentic_doc.parse.check_endpoint_and_api_key"):
            settings_config = ParseConfig(
                api_key="settings_test_key",
                include_marginalia=None,
                include_metadata_in_markdown=None
            )
            
            result = parse(sample_image_path, config=settings_config, include_marginalia=True, include_metadata_in_markdown=False)
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["data"]["include_marginalia"] is True
            assert request["data"]["include_metadata_in_markdown"] is False
            assert request["headers"]["Authorization"] == "Basic settings_test_key"
            
            captured_requests.clear()
            
            none_config = ParseConfig(
                api_key="none_test_key",
                include_marginalia=None,
                include_metadata_in_markdown=None
            )
            
            result = parse(sample_image_path, config=none_config)
            
            assert len(result) == 1
            assert len(captured_requests) == 1
            
            request = captured_requests[0]
            assert request["data"]["include_marginalia"] is True
            assert request["data"]["include_metadata_in_markdown"] is True
            assert request["headers"]["Authorization"] == "Basic none_test_key"



================================================
FILE: tests/unit/test_utils.py
================================================
import base64
import json
import os
import re
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import httpx
import numpy as np
import pymupdf
import pytest
import requests
from PIL import Image
from pydantic_core import Url
from requests.exceptions import ConnectionError as RequestsConnectionError
from tenacity import RetryCallState

from agentic_doc.common import (
    Chunk,
    ChunkGrounding,
    ChunkGroundingBox,
    ChunkType,
    Document,
    ParsedDocument,
)
from agentic_doc.config import VisualizationConfig, settings
from agentic_doc.utils import (
    _crop_groundings,
    _crop_image,
    _place_mark,
    _read_img_rgb,
    check_endpoint_and_api_key,
    download_file,
    get_file_type,
    is_valid_httpurl,
    log_retry_failure,
    page_to_image,
    save_groundings_as_images,
    split_pdf,
    viz_chunks,
    viz_parsed_document,
    get_chunk_from_reference,
)


@pytest.mark.parametrize(
    "api_key_str, mock_response_status, side_effect, expected_exception, expected_msg",
    [
        # No API key
        ("", None, None, ValueError, "API key is not set"),
        # Endpoint down
        (
            base64.b64encode(b"user:pass").decode(),
            None,
            RequestsConnectionError("mocked connection error"),
            ValueError,
            "endpoint URL",
        ),
        # 404 Not Found
        (
            base64.b64encode(b"user:pass").decode(),
            404,
            None,
            ValueError,
            "API key is not valid for this endpoint",
        ),
        # 401 Unauthorized
        (
            base64.b64encode(b"user:pass").decode(),
            401,
            None,
            ValueError,
            "API key is invalid",
        ),
    ],
)
def test_check_endpoint_and_api_key_failures(
    api_key_str, mock_response_status, side_effect, expected_exception, expected_msg
):
    if side_effect is not None:
        mock_requests_get = MagicMock(side_effect=side_effect)
    else:
        mock_resp = MagicMock()
        mock_resp.status_code = mock_response_status
        mock_requests_get = MagicMock(return_value=mock_resp)

    with patch("agentic_doc.utils.requests.head", mock_requests_get):
        with pytest.raises(expected_exception) as exc_info:
            check_endpoint_and_api_key("https://example123.com", api_key=api_key_str)

        assert expected_msg in str(exc_info.value)


def test_check_endpoint_and_api_key_success():
    valid_api_key = base64.b64encode(b"user:pass").decode()

    mock_resp = MagicMock()
    mock_resp.json.return_value = {}

    with patch("agentic_doc.utils.requests.get", return_value=mock_resp):
        check_endpoint_and_api_key("https://example.com", valid_api_key)


def test_download_file_with_url(results_dir):
    url = "https://pdfobject.com/pdf/sample.pdf"
    output_file_path = Path(results_dir) / "sample.pdf"
    download_file(url, str(output_file_path))
    assert output_file_path.exists()
    assert output_file_path.name == "sample.pdf"
    assert output_file_path.stat().st_size > 0


def test_download_file_failure(monkeypatch):
    # Mock httpx.stream to simulate a failed download
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    # Create a context manager mock
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_response

    # Mock stream to return our context manager
    mock_stream = MagicMock(return_value=mock_context)
    monkeypatch.setattr(httpx, "stream", mock_stream)

    with pytest.raises(Exception) as exc_info:
        download_file("https://example.com/nonexistent.pdf", "output.pdf")

    # Just check that the error message contains "Download failed"
    assert "Download failed" in str(exc_info.value)


# Convert a standard PDF page to an RGB image with actual dimensions at default DPI
def test_convert_pdf_page_to_rgb_image_with_actual_dimensions(complex_pdf):
    with pymupdf.open(complex_pdf) as pdf_doc:
        result = page_to_image(pdf_doc, 0)
        assert isinstance(result, np.ndarray)
        assert result.shape[2] == 3  # RGB channels
        assert result.dtype == np.uint8


# Handle PDF with RGBA content by dropping alpha channel
def test_handle_rgba_content_by_dropping_alpha_channel(monkeypatch):
    # Create a PDF document
    with pymupdf.open() as pdf_doc:
        pdf_doc.new_page(width=100, height=100)
        # Create a mock pixmap with RGBA data (4 channels)
        rgba_data = np.zeros((100, 100, 4), dtype=np.uint8)
        rgba_data[..., 3] = 255  # Set alpha channel to 255

        # Create a mock get_pixmap method that returns a pixmap with RGBA data
        class MockPixmap:
            def __init__(self):
                self.samples = rgba_data.tobytes()
                self.h = 100
                self.w = 100

        def mock_get_pixmap(*args, **kwargs):
            return MockPixmap()

        monkeypatch.setattr(pymupdf.Page, "get_pixmap", mock_get_pixmap)

        # Call the function under test
        result = page_to_image(pdf_doc, 0)

        # Assert the result has only 3 channels (RGB, no alpha)
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)


def test_is_valid_httpurl():
    # Valid URLs
    assert is_valid_httpurl("http://example.com")
    assert is_valid_httpurl("https://example.com")
    assert is_valid_httpurl("https://example.com/path/to/file.pdf")

    # Invalid URLs
    assert not is_valid_httpurl("ftp://example.com")
    assert not is_valid_httpurl("file:///path/to/file.pdf")
    assert not is_valid_httpurl("/path/to/file.pdf")
    assert not is_valid_httpurl("example.com")
    assert not is_valid_httpurl("not a url")


def test_get_file_type_pdf(temp_dir):
    # Create a PDF file with proper header
    pdf_path = temp_dir / "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    assert get_file_type(pdf_path) == "pdf"


def test_get_file_type_image(temp_dir):
    # Create a fake image file
    img_path = temp_dir / "test.jpg"
    with open(img_path, "wb") as f:
        f.write(b"JFIF")  # Some non-PDF content

    assert get_file_type(img_path) == "image"


def test_get_file_type_fallback_to_extension(temp_dir):
    # File that can't be opened
    nonexistent_path = temp_dir / "nonexistent.pdf"
    assert get_file_type(nonexistent_path) == "pdf"

    nonexistent_image = temp_dir / "nonexistent.jpg"
    assert get_file_type(nonexistent_image) == "image"


def test_split_pdf(multi_page_pdf, temp_dir):
    # Test splitting a multi-page PDF
    output_dir = temp_dir / "split_output"
    result = split_pdf(multi_page_pdf, output_dir, split_size=2)

    # For a 5-page PDF with split_size=2, we should get 3 parts
    assert len(result) == 3

    # Check that each Document object has the correct page ranges
    assert result[0].start_page_idx == 0
    assert result[0].end_page_idx == 1

    assert result[1].start_page_idx == 2
    assert result[1].end_page_idx == 3

    assert result[2].start_page_idx == 4
    assert result[2].end_page_idx == 4

    # Check that the files were actually created
    for doc in result:
        assert Path(doc.file_path).exists()


def test_split_pdf_with_invalid_split_size(multi_page_pdf, temp_dir):
    output_dir = temp_dir / "split_output"

    # Test with invalid split_size values
    with pytest.raises(AssertionError):
        split_pdf(multi_page_pdf, output_dir, split_size=0)


def test_log_retry_failure_inline_block(monkeypatch, capsys):
    # Setup a mock retry state
    retry_state = MagicMock()
    retry_state.attempt_number = 3
    outcome = MagicMock()
    outcome.failed = True
    outcome.exception.return_value = Exception("Test error")
    retry_state.outcome = outcome

    # Set the retry logging style to inline_block
    settings.retry_logging_style = "inline_block"

    # Call the function
    log_retry_failure(retry_state)

    # Check that the progress block was printed
    captured = capsys.readouterr()
    assert "███" in captured.out


def test_log_retry_failure_none(monkeypatch, capsys, caplog):
    # Setup a mock retry state
    retry_state = MagicMock()
    retry_state.attempt_number = 3
    outcome = MagicMock()
    outcome.failed = True
    outcome.exception.return_value = Exception("Test error")
    retry_state.outcome = outcome

    # Set the retry logging style to none
    settings.retry_logging_style = "none"

    # Call the function
    log_retry_failure(retry_state)

    # Check that nothing was printed or logged
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "attempt" not in caplog.text


def test_log_retry_failure_invalid_style(monkeypatch):
    # Setup a mock retry state
    retry_state = MagicMock()
    retry_state.attempt_number = 3
    outcome = MagicMock()
    outcome.failed = True
    outcome.exception.return_value = Exception("Test error")
    retry_state.outcome = outcome

    # Set an invalid retry logging style
    settings.retry_logging_style = "invalid"
    
    # Call the function and check that it raises a ValueError
    with pytest.raises(ValueError) as exc_info:
        log_retry_failure(retry_state)

    assert "Invalid retry logging style" in str(exc_info.value)


def test_viz_parsed_document_image(temp_dir, mock_parsed_document):
    # Create a test image
    img_path = temp_dir / "test_image.png"
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(img_path)

    # Test visualization without saving
    with patch("agentic_doc.utils.get_file_type", return_value="image"):
        images = viz_parsed_document(img_path, mock_parsed_document)

        # Check that we got an image back
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)
        assert images[0].width == 200
        assert images[0].height == 200

    # Test visualization with saving
    output_dir = temp_dir / "viz_output"
    with patch("agentic_doc.utils.get_file_type", return_value="image"):
        images = viz_parsed_document(
            img_path, mock_parsed_document, output_dir=output_dir
        )

        # Check that the image was saved
        assert (output_dir / f"{img_path.stem}_viz_page_0.png").exists()


def test_viz_parsed_document_pdf(temp_dir, mock_multi_page_parsed_document):
    # Mock pymupdf.open and page_to_image to avoid needing a real PDF
    mock_page_image = np.zeros((200, 200, 3), dtype=np.uint8)

    with patch("agentic_doc.utils.pymupdf.open"), patch(
        "agentic_doc.utils.page_to_image", return_value=mock_page_image
    ), patch("agentic_doc.utils.get_file_type", return_value="pdf"):

        pdf_path = temp_dir / "test.pdf"
        output_dir = temp_dir / "viz_output"

        # Test visualization with saving
        images = viz_parsed_document(
            pdf_path, mock_multi_page_parsed_document, output_dir=output_dir
        )

        # Check that we got the right number of images back
        assert len(images) == 3  # 3 pages in mock_multi_page_parsed_document

        # Check that the images were saved
        for i in range(3):
            assert (output_dir / f"{pdf_path.stem}_viz_page_{i}.png").exists()


def test_viz_chunks():
    # Create a test image
    img = np.zeros((200, 200, 3), dtype=np.uint8)

    # Create some test chunks
    chunks = [
        Chunk(
            text="Test Title",
            chunk_type=ChunkType.text,
            chunk_id="1",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                )
            ],
        ),
        Chunk(
            text="Test Text",
            chunk_type=ChunkType.text,
            chunk_id="2",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                )
            ],
        ),
    ]

    # Test with default visualization config
    result = viz_chunks(img, chunks)
    assert isinstance(result, np.ndarray)
    assert result.shape == (200, 200, 3)

    # Test with custom visualization config
    viz_config = VisualizationConfig(thickness=2, font_scale=0.7)
    result = viz_chunks(img, chunks, viz_config)
    assert isinstance(result, np.ndarray)
    assert result.shape == (200, 200, 3)


def test_crop_image():
    # Create a test image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Fill with different colors to verify the crop
    img[0:50, 0:50] = [255, 0, 0]  # Top-left quadrant: red
    img[0:50, 50:100] = [0, 255, 0]  # Top-right quadrant: green
    img[50:100, 0:50] = [0, 0, 255]  # Bottom-left quadrant: blue
    img[50:100, 50:100] = [255, 255, 0]  # Bottom-right quadrant: yellow

    # Test crop with normalized coordinates
    bbox = ChunkGroundingBox(l=0.25, t=0.25, r=0.75, b=0.75)
    crop = _crop_image(img, bbox)

    # The crop should be a 50x50 region from the center of the image
    assert crop.shape == (50, 50, 3)

    # Test with coordinates at the boundaries
    bbox = ChunkGroundingBox(l=0.0, t=0.0, r=1.0, b=1.0)
    crop = _crop_image(img, bbox)
    assert crop.shape == (100, 100, 3)


def test_crop_groundings(temp_dir):
    # Create a test image
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    # Create a directory to save the crops
    crop_save_dir = temp_dir / "crops"

    # Create test chunks
    chunks = [
        Chunk(
            text="Test Document",
            chunk_type=ChunkType.text,
            chunk_id="11111",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                )
            ],
        ),
        Chunk(
            text="This is a test document.",
            chunk_type=ChunkType.text,
            chunk_id="22222",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                )
            ],
        ),
    ]

    # Mock cv2.imencode to make it return a valid result
    mock_buffer = MagicMock()
    mock_buffer.tobytes.return_value = b"mock_png_data"

    with patch("cv2.imencode", return_value=(True, mock_buffer)), patch(
        "pathlib.Path.write_bytes"
    ) as mock_write:

        # Test without inplace modification
        result = _crop_groundings(img, chunks, crop_save_dir, inplace=False)

        # Check that the result contains the chunk_id as keys
        assert "11111" in result
        assert "22222" in result

        # Check that write_bytes was called for each chunk
        assert mock_write.call_count >= 2

        # Verify the grounding image_path is still None (since inplace=False)
        assert chunks[0].grounding[0].image_path is None

        # Reset the mock for the next test
        mock_write.reset_mock()

        # Test with inplace modification
        result = _crop_groundings(img, chunks, crop_save_dir, inplace=True)

        # Check that write_bytes was called for each chunk
        assert mock_write.call_count >= 2

        # Check that the image_path was set in the chunks when inplace=True
        assert chunks[0].grounding[0].image_path is not None
        assert chunks[1].grounding[0].image_path is not None


def test_save_groundings_as_images_image(temp_dir):
    # Create a test image file
    img_path = temp_dir / "test.jpg"
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(img_path)

    # Create a directory to save the groundings
    save_dir = temp_dir / "groundings"

    # Create custom chunks with known types
    chunks = [
        Chunk(
            text="Test Document",
            chunk_type=ChunkType.text,
            chunk_id="11111",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                )
            ],
        ),
        Chunk(
            text="This is a test document.",
            chunk_type=ChunkType.text,
            chunk_id="22222",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                )
            ],
        ),
    ]

    # Mock the required functions to avoid filesystem operations
    mock_buffer = MagicMock()
    mock_buffer.tobytes.return_value = b"mock_png_data"

    with patch("agentic_doc.utils.get_file_type", return_value="image"), patch(
        "agentic_doc.utils.cv2.imread",
        return_value=np.zeros((100, 100, 3), dtype=np.uint8),
    ), patch("cv2.imencode", return_value=(True, mock_buffer)), patch(
        "pathlib.Path.write_bytes"
    ) as mock_write, patch(
        "pathlib.Path.mkdir", return_value=None
    ):

        result = save_groundings_as_images(img_path, chunks, save_dir)

        # Check that the result contains the chunk_id as keys
        assert "11111" in result
        assert "22222" in result

        # Check that write_bytes was called (twice, once for each chunk)
        assert mock_write.call_count == 2


def test_save_groundings_as_images_pdf(temp_dir):
    # Create a dummy PDF file
    pdf_path = temp_dir / "test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n")

    # Create a directory to save the groundings
    save_dir = temp_dir / "groundings"

    # Create custom chunks with different page indices
    chunks = [
        Chunk(
            text="Title",
            chunk_type=ChunkType.text,
            chunk_id="11111",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                )
            ],
        ),
        Chunk(
            text="Page content",
            chunk_type=ChunkType.text,
            chunk_id="22222",
            grounding=[
                ChunkGrounding(
                    page=0, box=ChunkGroundingBox(l=0.1, t=0.3, r=0.9, b=0.4)
                )
            ],
        ),
        Chunk(
            text="Header",
            chunk_type=ChunkType.text,
            chunk_id="33333",
            grounding=[
                ChunkGrounding(
                    page=1, box=ChunkGroundingBox(l=0.1, t=0.1, r=0.9, b=0.2)
                )
            ],
        ),
    ]

    # Mock the required functions to avoid filesystem operations
    mock_buffer = MagicMock()
    mock_buffer.tobytes.return_value = b"mock_png_data"

    with patch("agentic_doc.utils.get_file_type", return_value="pdf"), patch(
        "agentic_doc.utils.pymupdf.open"
    ) as mock_pymupdf_open, patch(
        "agentic_doc.utils.page_to_image",
        return_value=np.zeros((100, 100, 3), dtype=np.uint8),
    ), patch(
        "cv2.imencode", return_value=(True, mock_buffer)
    ), patch(
        "pathlib.Path.write_bytes"
    ) as mock_write, patch(
        "pathlib.Path.mkdir", return_value=None
    ):

        # Mock the context manager returned by pymupdf.open
        mock_pdf_doc = MagicMock()
        mock_pymupdf_open.return_value.__enter__.return_value = mock_pdf_doc

        # Call the function
        result = save_groundings_as_images(pdf_path, chunks, save_dir)

        # Check that the result contains the chunk_ids
        assert "11111" in result
        assert "22222" in result
        assert "33333" in result

        # Check that write_bytes was called for each chunk
        assert mock_write.call_count == 3


def test_read_img_rgb():
    # Create a mock for cv2.imread and cv2.cvtColor
    with patch(
        "agentic_doc.utils.cv2.imread",
        return_value=np.zeros((100, 100, 3), dtype=np.uint8),
    ), patch(
        "agentic_doc.utils.cv2.cvtColor",
        return_value=np.zeros((100, 100, 3), dtype=np.uint8),
    ):

        # Test with a regular RGB image
        result = _read_img_rgb("test.jpg")
        assert result.shape == (100, 100, 3)

    # Test with a grayscale image
    with patch(
        "agentic_doc.utils.cv2.imread",
        return_value=np.zeros((100, 100, 1), dtype=np.uint8),
    ), patch("agentic_doc.utils.cv2.cvtColor") as mock_cvtColor:

        # Set return value directly instead of using side_effect
        mock_cvtColor.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        result = _read_img_rgb("test.jpg")
        assert result.shape == (100, 100, 3)
        # Check that cvtColor was called at least once
        assert mock_cvtColor.call_count >= 1

    # Test with an RGBA image
    with patch(
        "agentic_doc.utils.cv2.imread",
        return_value=np.zeros((100, 100, 4), dtype=np.uint8),
    ), patch(
        "agentic_doc.utils.cv2.cvtColor",
        return_value=np.zeros((100, 100, 4), dtype=np.uint8),
    ):

        result = _read_img_rgb("test.png")
        assert result.shape == (100, 100, 3)  # Should drop the alpha channel


def test_split_pdf_edge_cases(temp_dir):
    # Test edge cases for PDF splitting
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate

    # Create a 1-page PDF
    single_page_pdf = temp_dir / "single_page.pdf"
    doc = SimpleDocTemplate(str(single_page_pdf), pagesize=letter)
    styles = getSampleStyleSheet()
    doc.build([Paragraph("Single page content", styles["Normal"])])

    # Test with split_size=1 on a 1-page PDF
    output_dir = temp_dir / "split_single"
    result = split_pdf(single_page_pdf, output_dir, split_size=1)

    assert len(result) == 1
    assert result[0].start_page_idx == 0
    assert result[0].end_page_idx == 0


def test_download_file_with_custom_filename(results_dir):
    # Test downloading to a specific filename
    url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    custom_filename = Path(results_dir) / "custom_name.pdf"

    download_file(url, str(custom_filename))

    assert custom_filename.exists()
    assert custom_filename.name == "custom_name.pdf"
    assert custom_filename.stat().st_size > 0


def test_get_file_type_with_various_extensions(temp_dir):
    # Test file type detection with different extensions

    # PDF files
    for ext in [".pdf", ".PDF"]:
        pdf_file = temp_dir / f"test{ext}"
        with open(pdf_file, "wb") as f:
            f.write(b"%PDF-1.7\n")
        assert get_file_type(pdf_file) == "pdf"

    # Image files
    for ext in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".JPG", ".PNG"]:
        img_file = temp_dir / f"test{ext}"
        with open(img_file, "wb") as f:
            f.write(b"fake image data")
        assert get_file_type(img_file) == "image"


def test_is_valid_httpurl_edge_cases():
    # Test edge cases for URL validation

    # Valid URLs with different protocols
    assert is_valid_httpurl("http://example.com")
    assert is_valid_httpurl("https://example.com")
    assert is_valid_httpurl("https://sub.domain.example.com/path/file.pdf")
    assert is_valid_httpurl("http://localhost:8080/test")

    # Invalid URLs (scheme-based validation)
    assert not is_valid_httpurl("")
    assert not is_valid_httpurl("   ")
    assert not is_valid_httpurl("ftp://example.com")
    assert not is_valid_httpurl("ftps://example.com")
    assert not is_valid_httpurl("file:///local/path")
    assert not is_valid_httpurl("mailto:test@example.com")
    assert not is_valid_httpurl("just-a-string")

    # Note: The function only validates scheme, so "http://" and "https://" are considered valid
    assert is_valid_httpurl("http://")
    assert is_valid_httpurl("https://")


def test_page_to_image_different_dpi_settings(complex_pdf, monkeypatch):
    # Test page conversion with different DPI settings

    # Test with high DPI
    with pymupdf.open(complex_pdf) as pdf_doc:
        result_high_dpi = page_to_image(pdf_doc, 0, 300)
        assert isinstance(result_high_dpi, np.ndarray)
        assert result_high_dpi.shape[2] == 3

    # Test with low DPI
    with pymupdf.open(complex_pdf) as pdf_doc:
        result_low_dpi = page_to_image(pdf_doc, 0, 72)
        assert isinstance(result_low_dpi, np.ndarray)
        assert result_low_dpi.shape[2] == 3

    # High DPI should produce larger images
    assert (result_high_dpi.shape[0] * result_high_dpi.shape[1]) > (
        result_low_dpi.shape[0] * result_low_dpi.shape[1]
    )


def test_viz_chunks_with_different_chunk_types():
    # Test visualization with all available chunk types
    img = np.zeros((200, 200, 3), dtype=np.uint8)

    chunks = []
    y_positions = [0.1, 0.3, 0.5, 0.7]

    for i, chunk_type in enumerate(ChunkType):
        if i >= len(y_positions):
            break

        chunk = Chunk(
            text=f"Test {chunk_type.value}",
            chunk_type=chunk_type,
            chunk_id=f"chunk_{i}",
            grounding=[
                ChunkGrounding(
                    page=0,
                    box=ChunkGroundingBox(
                        l=0.1, t=y_positions[i], r=0.9, b=y_positions[i] + 0.1
                    ),
                )
            ],
        )
        chunks.append(chunk)

    # Test visualization
    result = viz_chunks(img, chunks)
    assert isinstance(result, np.ndarray)
    assert result.shape == (200, 200, 3)


def test_crop_image_boundary_conditions():
    # Test cropping with boundary conditions
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White image

    # Test cropping the entire image
    bbox_full = ChunkGroundingBox(l=0.0, t=0.0, r=1.0, b=1.0)
    crop_full = _crop_image(img, bbox_full)
    assert crop_full.shape == (100, 100, 3)

    # Test cropping a very small area
    bbox_small = ChunkGroundingBox(l=0.49, t=0.49, r=0.51, b=0.51)
    crop_small = _crop_image(img, bbox_small)
    assert crop_small.shape[0] >= 1 and crop_small.shape[1] >= 1
    assert crop_small.shape[2] == 3


def test_crop_image_coordinate_clamping():
    # Test coordinate clamping for out-of-bounds coordinates
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White image

    # Test with negative coordinates - should be clamped to 0
    bbox_negative = ChunkGroundingBox(l=-0.1, t=-0.2, r=0.5, b=0.5)
    crop_negative = _crop_image(img, bbox_negative)
    assert isinstance(crop_negative, np.ndarray)
    assert crop_negative.shape[2] == 3
    assert crop_negative.shape[0] > 0 and crop_negative.shape[1] > 0

    # Test with coordinates > 1 - should be clamped to 1
    bbox_over_one = ChunkGroundingBox(l=0.5, t=0.5, r=1.2, b=1.3)
    crop_over_one = _crop_image(img, bbox_over_one)
    assert isinstance(crop_over_one, np.ndarray)
    assert crop_over_one.shape[2] == 3
    assert crop_over_one.shape[0] > 0 and crop_over_one.shape[1] > 0

    # Test with mixed invalid coordinates
    bbox_mixed = ChunkGroundingBox(l=-0.5, t=0.2, r=1.5, b=0.8)
    crop_mixed = _crop_image(img, bbox_mixed)
    assert isinstance(crop_mixed, np.ndarray)
    assert crop_mixed.shape[2] == 3
    assert crop_mixed.shape[0] > 0 and crop_mixed.shape[1] > 0

    # Test with all coordinates out of bounds (should still work)
    bbox_all_invalid = ChunkGroundingBox(l=-1.0, t=-1.0, r=2.0, b=2.0)
    crop_all_invalid = _crop_image(img, bbox_all_invalid)
    assert isinstance(crop_all_invalid, np.ndarray)
    assert crop_all_invalid.shape[2] == 3
    # Should crop the entire image when clamped
    assert crop_all_invalid.shape == (100, 100, 3)

    # Test with extreme values that result in valid crops after clamping
    bbox_extreme = ChunkGroundingBox(l=-999.0, t=-500.0, r=0.5, b=1000.0)
    crop_extreme = _crop_image(img, bbox_extreme)
    assert isinstance(crop_extreme, np.ndarray)
    assert crop_extreme.shape[2] == 3
    assert crop_extreme.shape[0] > 0 and crop_extreme.shape[1] > 0

    # Test edge case where clamping results in zero-size crop (top == bottom)
    bbox_zero_height = ChunkGroundingBox(
        l=0.2, t=500.0, r=0.8, b=600.0
    )  # Both t and b clamp to 1.0
    crop_zero_height = _crop_image(img, bbox_zero_height)
    assert isinstance(crop_zero_height, np.ndarray)
    assert crop_zero_height.shape[2] == 3
    # May have zero height when top == bottom after clamping
    assert crop_zero_height.shape[0] >= 0 and crop_zero_height.shape[1] > 0

    # Test edge case where clamping results in zero-size crop (left == right)
    bbox_zero_width = ChunkGroundingBox(
        l=500.0, t=0.2, r=600.0, b=0.8
    )  # Both l and r clamp to 1.0
    crop_zero_width = _crop_image(img, bbox_zero_width)
    assert isinstance(crop_zero_width, np.ndarray)
    assert crop_zero_width.shape[2] == 3
    # May have zero width when left == right after clamping
    assert crop_zero_width.shape[0] > 0 and crop_zero_width.shape[1] >= 0


def test_save_groundings_as_images_with_empty_chunks(temp_dir):
    # Test saving groundings when there are no chunks
    img_path = temp_dir / "test.jpg"
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(img_path)

    save_dir = temp_dir / "groundings"
    chunks = []  # Empty list

    with patch("agentic_doc.utils.get_file_type", return_value="image"):
        result = save_groundings_as_images(img_path, chunks, save_dir)

        # Should return empty dict for empty chunks
        assert result == {}


def test_viz_parsed_document_with_no_chunks(temp_dir):
    # Test visualization with a document that has no chunks
    img_path = temp_dir / "test_empty.png"
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(img_path)

    # Create a document with no chunks
    empty_doc = ParsedDocument(
        markdown="", chunks=[], start_page_idx=0, end_page_idx=0, doc_type="image"
    )

    with patch("agentic_doc.utils.get_file_type", return_value="image"):
        images = viz_parsed_document(img_path, empty_doc)

        # Should still return an image even with no chunks
        assert len(images) == 1
        assert isinstance(images[0], Image.Image)


def test_log_retry_failure_with_different_attempt_numbers(monkeypatch):
    # Test retry logging with different attempt numbers

    # Mock retry state for different attempt numbers
    for attempt_num in [1, 5, 10, 50]:
        retry_state = MagicMock()
        retry_state.attempt_number = attempt_num
        outcome = MagicMock()
        outcome.failed = True
        outcome.exception.return_value = Exception(f"Error on attempt {attempt_num}")
        retry_state.outcome = outcome
        retry_state.fn = MagicMock()
        retry_state.fn.__name__ = "test_function"

        # Set retry logging style
        settings.retry_logging_style = "log_msg"

        # Should not raise an exception regardless of attempt number
        log_retry_failure(retry_state)


def test_get_chunk_from_reference():
    chunks = [
        {
            "text": "Name: Bob Johnson",
            "grounding": [
                {
                    "page": 0,
                    "box": {"l": 0.1, "t": 0.1, "r": 0.9, "b": 0.2},
                }
            ],
            "chunk_type": "text",
            "chunk_id": "1",
        },
        {
            "text": "Name: Alice Smith",
            "grounding": [
                {
                    "page": 1,
                    "box": {"l": 0.2, "t": 0.2, "r": 0.8, "b": 0.3},
                }
            ],
            "chunk_type": "text",
            "chunk_id": "2",
        },
    ]

    result = get_chunk_from_reference("1", chunks)
    assert result["text"] == "Name: Bob Johnson"
    assert get_chunk_from_reference("999", chunks) == None



================================================
FILE: .github/workflows/ci-integ.yml
================================================
name: CI - Integration Tests

on:
  push:
    branches: [main]
  pull_request_target:
    branches: [main]
    types: [opened, synchronize, reopened, labeled]

env:
  PYTHONUTF8: 1

jobs:
  comment_on_fork_pr:
    name: Comment on fork PR
    if: github.event_name == 'pull_request_target' && github.event.pull_request.head.repo.full_name != github.repository && !contains(github.event.pull_request.labels.*.name, 'safe to test')
    runs-on: ubuntu-latest
    steps:
      - name: Comment on fork PR
        uses: thollander/actions-comment-pull-request@v3
        with:
          message: |
            👋 Thanks for your contribution! This PR is from a fork and requires manual review before integration tests can run.

            A maintainer will review your code and add the `safe to test` label if the changes are safe to test with our infrastructure.


  authorize:
    name: Authorize
    runs-on: ubuntu-latest
    outputs:
      decision: ${{ steps.decision.outputs.approved }}
    steps:
      - name: Check github event name
        run: |
          echo "Event name: ${{ github.event_name }}"
      - name: Check authorization
        id: decision
        run: |
          # For push events (only happens on main branch)
          if [ "${{ github.event_name }}" == "push" ]; then
            echo "approved=true" >> $GITHUB_OUTPUT
            echo "✅ Push to main branch - automatically approved" >> $GITHUB_STEP_SUMMARY
          
          # For pull_request_target events
          elif [ "${{ github.event_name }}" == "pull_request_target" ]; then
            # Check if it's from a fork
            if [ "${{ github.event.pull_request.head.repo.full_name }}" != "${{ github.repository }}" ]; then
              # External fork - check for 'safe to test' label
              if [[ "${{ contains(github.event.pull_request.labels.*.name, 'safe to test') }}" == "true" ]]; then
                echo "approved=true" >> $GITHUB_OUTPUT
                echo "✅ External fork PR approved with 'safe to test' label" >> $GITHUB_STEP_SUMMARY
              else
                echo "approved=false" >> $GITHUB_OUTPUT
                echo "⚠️ This PR is from a fork and needs the 'safe to test' label to run integration tests" >> $GITHUB_STEP_SUMMARY
                echo "A maintainer must review the code and add the 'safe to test' label if the changes are safe to test." >> $GITHUB_STEP_SUMMARY
              fi
            else
              # Internal PR - automatically approved
              echo "approved=true" >> $GITHUB_OUTPUT
              echo "✅ Internal PR - automatically approved" >> $GITHUB_STEP_SUMMARY
            fi
          else
            echo "approved=false" >> $GITHUB_OUTPUT
          fi

  integ_test:
    name: Integration Test
    needs: authorize
    if: needs.authorize.outputs.decision == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      checks: write
      pull-requests: write
    env:
      RUNTIME_TAG: ci_job
    steps:
      - name: Checkout PR branch
        uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          fetch-depth: 0
          
      - name: Merge PR for testing
        if: github.event_name == 'pull_request_target'
        run: |
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git config --global user.name "github-actions[bot]"
          git fetch origin ${{ github.event.pull_request.base.ref }}:base-branch
          git checkout base-branch
          git merge ${{ github.event.pull_request.head.sha }} --no-edit --allow-unrelated-histories

      - uses: actions/setup-python@v4
        with:
          python-version: 3.12
      
      - name: Install Python Poetry
        uses: abatilo/actions-poetry@v2.1.0
        with:
          poetry-version: 1.4.2
      
      - name: Configure poetry
        shell: bash
        run: poetry config virtualenvs.in-project true
      
      - name: Print Python environment information
        run: |
          poetry env info
          poetry --version
          poetry run pip -V
      
      - name: Install dependencies
        run: |
          poetry install --all-extras
      
      - name: Integration Test with pytest
        env:
          VISION_AGENT_API_KEY: ${{ secrets.VISION_AGENT_API_KEY }}
        run: |
          poetry run pytest -n auto -s -vvv tests/integ
          
      - name: Comment PR
        if: github.event_name == 'pull_request_target' && failure()
        uses: thollander/actions-comment-pull-request@v3
        with:
          message: |
            ❌ Integration tests failed. Please check the logs.



================================================
FILE: .github/workflows/ci-unit.yml
================================================
name: CI - Unit Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

env:
  PYTHONUTF8: 1

jobs:
  unit_test:
    name: Test
    strategy:
      matrix:
        python-version: [3.9, 3.13]
        os: [ubuntu-22.04, windows-2022, macos-14]
    runs-on: ${{ matrix.os }}
    env:
      RUNTIME_TAG: ci_job
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Python Poetry
        uses: abatilo/actions-poetry@v2.1.0
        with:
          poetry-version: 1.4.2
      
      - name: Configure poetry
        shell: bash
        run: poetry config virtualenvs.in-project true
      
      - name: Print Python environment information
        run: |
          poetry env info
          poetry --version
          poetry run pip -V
      
      - name: Install dependencies
        run: |
          poetry install --all-extras
      
      - name: Linting
        run: |
          poetry run flake8 . --exclude .venv,examples,tests --count --show-source --statistics
      
      - name: Check Format
        run: |
          poetry run black --check --diff --color agentic_doc/
      
      - name: Type Checking
        run: |
          poetry run mypy agentic_doc
      
      - name: Test with pytest
        run: |
          poetry run pytest -s -vvv tests/unit



================================================
FILE: .github/workflows/release.yml
================================================
name: Release Branch CI/CD

on:
  release:
    types: [created]

env:
  VISION_AGENT_API_KEY: "PLACEHOLDER"
  PYTHONUTF8: 1

jobs:
  unit_test:
    name: Test
    strategy:
      matrix:
        python-version: [3.9, 3.13]
        os: [ubuntu-22.04, windows-2022, macos-14]
    runs-on: ${{ matrix.os }}
    env:
      RUNTIME_TAG: ci_job
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install Python Poetry
        uses: abatilo/actions-poetry@v2.1.0
        with:
          poetry-version: 1.4.2
      - name: Configure poetry
        shell: bash
        run: poetry config virtualenvs.in-project true
      - name: Print Python environment information
        run: |
          poetry env info
          poetry --version
          poetry run pip -V
      - name: Install dependencies
        run: |
          poetry install --all-extras
      - name: Linting
        run: |
          poetry run flake8 . --exclude .venv,examples,tests --count --show-source --statistics
      - name: Check Format
        run: |
          poetry run black --check --diff --color agentic_doc/
      - name: Type Checking
        run: |
          poetry run mypy agentic_doc
      - name: Test with pytest
        run: |
          poetry run pytest -s -vvv tests/unit

  integ_test:
    name: Integ Test
    runs-on: ubuntu-latest
    env:
      RUNTIME_TAG: ci_job
      VISION_AGENT_API_KEY: ${{ secrets.VISION_AGENT_API_KEY }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: 3.12
      - name: Install Python Poetry
        uses: abatilo/actions-poetry@v2.1.0
        with:
          poetry-version: 1.4.2
      - name: Configure poetry
        shell: bash
        run: poetry config virtualenvs.in-project true
      - name: Print Python environment information
        run: |
          poetry env info
          poetry --version
          poetry run pip -V
      - name: Install dependencies
        run: |
          poetry install --all-extras
      - name: Integ Test with pytest
        run: |
          poetry run pytest -n auto -s -vvv tests/integ

  release:
    name: Release to PyPI
    needs: [unit_test, integ_test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: 3.10.11
      - name: Install Python Poetry
        uses: abatilo/actions-poetry@v2.1.0
        with:
          poetry-version: 1.4.2
      - name: Configure poetry
        shell: bash
        run: poetry config virtualenvs.in-project true
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.GH_TOKEN }}
      - name: setup git config
        run: |
          git config user.name "Landing AI Bot"
          git config user.email "dev@landing.ai"

      - name: Publish to PyPI
        run: |
          TAG=${{ github.ref_name }}
          poetry version ${TAG#v}
          poetry config pypi-token.pypi ${{ secrets.PYPI_TOKEN }}
          poetry publish --build -vvv

      - name: Checkout main code to bump version
        uses: actions/checkout@v3
        with:
          ref: main
          token: ${{ secrets.GH_TOKEN }}

      - name: Bump up version on main
        run: |
          TAG=${{ github.ref_name }}
          poetry version ${TAG#v}
          new_version=`poetry version`
          git add pyproject.toml
          git commit -m "[skip ci] chore(release): ${new_version}" && git push -f || true