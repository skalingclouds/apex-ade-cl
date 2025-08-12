---
url: "https://docs.landing.ai/ade/ade-connectors"
title: "Parse Documents from Amazon S3, Google Drive, and More - LandingAI"
---

[LandingAI home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-color-RGB_scale.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/landingaitest/logo/LandingAI-logo-primary-white_scale.png)](https://docs.landing.ai/)

Search...

Ctrl KAsk AI

Search...

Navigation

Parsing

Parse Documents from Amazon S3, Google Drive, and More

[Guides](https://docs.landing.ai/ade/ade-overview) [API](https://docs.landing.ai/api-reference/tools/agentic-document-extraction) [Changelog](https://docs.landing.ai/ade/ade-changelog)

On this page

- [Parse Documents from Google Drive](https://docs.landing.ai/ade/ade-connectors#parse-documents-from-google-drive)
- [Sample Script: Google Drive](https://docs.landing.ai/ade/ade-connectors#sample-script%3A-google-drive)
- [Parse Documents from Amazon S3](https://docs.landing.ai/ade/ade-connectors#parse-documents-from-amazon-s3)
- [Parse Documents from a Local Directory with a Connector](https://docs.landing.ai/ade/ade-connectors#parse-documents-from-a-local-directory-with-a-connector)
- [Parse Documents from a URL with a Connector](https://docs.landing.ai/ade/ade-connectors#parse-documents-from-a-url-with-a-connector)

If you need to parse documents stored in places like Google Drive, Amazon S3, URLs, or local folders, you can use the `connectors` module to access and authenticate to those locations.A **connector** is a Python class, along with configuration settings, that enables the [`parse`](https://docs.landing.ai/ade/ade-parse-docs) function to access and retrieve documents from a specific source, such as a cloud storage bucket or local directory.You can pass a connector to the `parse` function to fetch and parse all documents from that source, without manually listing each file.You can use a connector to access all documents in an Amazon S3 bucket or Google Drive. Also, instead of specifying every file path in a local folder, you can use a connector to parse the entire directory in one call.

The `connectors` module is available in the [agentic-doc library](https://github.com/landing-ai/agentic-doc) v0.2.3 and later.

## [​](https://docs.landing.ai/ade/ade-connectors\#parse-documents-from-google-drive)  Parse Documents from Google Drive

Before parsing documents from Google Drive, we recommend running through this tutorial first to help you set up your Google credentials: [Google Drive API Python Quickstart](https://developers.google.com/workspace/drive/api/quickstart/python).The tutorial guides you through:

1. Creating a Google Cloud project
2. Enabling the Google Drive API
3. Setting up OAuth 2.0 credentials

### [​](https://docs.landing.ai/ade/ade-connectors\#sample-script%3A-google-drive)  Sample Script: Google Drive

After completing the [tutorial](https://developers.google.com/workspace/drive/api/quickstart/python), run the following script to parse documents from Google Drive.

Copy

Ask AI

```
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

## [​](https://docs.landing.ai/ade/ade-connectors\#parse-documents-from-amazon-s3)  Parse Documents from Amazon S3

Run the following script to parse documents from an Amazon S3 bucket.

Copy

Ask AI

```
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

## [​](https://docs.landing.ai/ade/ade-connectors\#parse-documents-from-a-local-directory-with-a-connector)  Parse Documents from a Local Directory with a Connector

Run the following script to parse documents in a local dirctory. The function only parses documents directly in the local directory; it does not parse documents in nested directories.

Copy

Ask AI

```
from agentic_doc.parse import parse
from agentic_doc.connectors import LocalConnectorConfig

config = LocalConnectorConfig()

# Parse all supported documents in a directory
results = parse(config, connector_path="/path/to/documents")

# Parse with pattern filtering
results = parse(config, connector_path="/path/to/documents", connector_pattern="*.pdf")

```

## [​](https://docs.landing.ai/ade/ade-connectors\#parse-documents-from-a-url-with-a-connector)  Parse Documents from a URL with a Connector

Run the following script to parse documents at a specified URL.

Copy

Ask AI

```
from agentic_doc.parse import parse
from agentic_doc.connectors import URLConnectorConfig

config = URLConnectorConfig(
    headers={"Authorization": "Bearer your-token"},  # Optional
    timeout=60  # Optional
)
# Parse document from URL
results = parse(config, connector_path="https://example.com/document.pdf")

```

Was this page helpful?

YesNo

[Parsing Basics](https://docs.landing.ai/ade/ade-parse-docs) [Chunk Types](https://docs.landing.ai/ade/ade-chunk-types)

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