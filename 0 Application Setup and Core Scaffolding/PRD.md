## 🧠 Overview

Create an Agentic human extraction form that acts as an internal business tool. Users upload PDFs for agentic extraction using the landing.ai SDK in Python, with a dual display for human-in-the-loop review and a chat interface for document interaction.

## 💡 Problem Statement

Users need an efficient way to extract and review data from PDFs, ensuring accuracy and context retention. Current solutions lack seamless integration for human review and interaction, leading to inefficiencies and potential errors in data handling. The agent's understanding of how to use the SDK is critical to ensure accurate and reliable data extraction.

## 🎯 Goals

- Successfully process and display 100 PDFs within the first month.
- Achieve a 90% user satisfaction rate with the extraction and review process.
- Ensure the AI agent accurately references the original PDF in 95% of interactions.

## 👥 Target Users

- ****Persona****: Internal business analysts and data processors.
- ****Pain point****: Manual data extraction from PDFs is time-consuming and error-prone.
- ****Behavior****: Currently use basic PDF readers and manual data entry methods.

## 🧭 UX Flows and Interfaces

1. ****PDF Upload****: Users can upload PDFs via drag-and-drop or file picker.
2. ****Processing****: The document is processed using the landing.ai SDK, with a fallback to the API if needed.
3. ****Review View****: Dual display with the original PDF on the left and extracted Markdown on the right.
4. ****Approval Workflow****: Users can approve, reject, or escalate documents, with navigation through a sidebar.
5. ****Chat Interface****: Users interact with the AI agent to ask questions about the document, with answers highlighted in the original PDF.

## 🎨 UI Style Guide

- Style is utility-focused with a dense layout and dark mode by default.
- Emphasis on functionality and clarity, with minimal decorative elements.
- Primary actions use solid buttons; secondary actions use inline links.
- Fast transitions and inline feedback for a seamless user experience.

## 📋 Feature Overview and Scope

- ****PDF Upload**** – Users can upload PDFs via drag-and-drop or file picker, with a maximum file size of 50 MB.
- ****Agentic Extraction**** – Utilizes the landing.ai SDK to extract data, focusing on clean Markdown presentation, with a fallback to the API if needed.
- ****Review View**** – Displays the original PDF and extracted Markdown side by side for comparison.
- ****Approval Workflow**** – Includes approve, reject, and escalate options with a sidebar for navigation.
- ****Chat with PDF**** – AI agent answers questions by referencing the original PDF, highlighting answer locations.

### ❌ Out of Scope

- Editable Markdown in the review view.
- Advanced customization of the AI agent's responses.

## 📊 Analytics and Instrumentation

#### Core Metrics

- Number of PDFs processed per user.
- Percentage of documents approved or rejected.
- Frequency of AI agent interactions per document.

## 🛡️ Security, Privacy, and Compliance

- PDFs and extracted data are stored persistently in a secure database.
- Data is encrypted at rest and in transit.
- No third-party data sharing; GDPR compliance ensured with user data deletion upon request.