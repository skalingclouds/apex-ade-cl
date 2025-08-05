#!/usr/bin/env python3
"""
Simple test script to verify Landing.AI SDK is working correctly.
Run this before starting the server to ensure the integration works.
"""

import os
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional

# Set the API key
os.environ['VISION_AGENT_API_KEY'] = 'MmhtN2t2enA1bHM1aWRhdnU5emVsOmljRlc4ZzdPd2J1bDgyUGZOeEZ1UWRldVVyY1ozODJz'

def test_landing_ai_parse():
    """Test basic parse functionality"""
    print("Testing Landing.AI parse...")
    
    try:
        from agentic_doc.parse import parse
        print("✓ Landing.AI SDK imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Landing.AI SDK: {e}")
        print("\nTo install: pip install agentic-doc")
        return False
    
    # Find a test PDF
    test_files = [
        "./test.pdf",
        "./uploads/20250805_134013_2-page-sample copy.pdf",
        "../uploads/20250805_134013_2-page-sample copy.pdf"
    ]
    
    test_file = None
    for file_path in test_files:
        if Path(file_path).exists():
            test_file = file_path
            break
    
    if not test_file:
        print("✗ No test PDF found. Please ensure test.pdf exists in the backend directory.")
        return False
    
    print(f"✓ Using test file: {test_file}")
    
    # Test 1: Basic parse without extraction
    print("\nTest 1: Basic parse (markdown only)...")
    try:
        result = parse(
            documents=[test_file],
            include_marginalia=True,
            include_metadata_in_markdown=True
        )
        
        if result and len(result) > 0:
            parsed_doc = result[0]
            has_markdown = hasattr(parsed_doc, 'markdown')
            markdown_len = len(getattr(parsed_doc, 'markdown', ''))
            
            print(f"✓ Parse successful")
            print(f"  - Has markdown: {has_markdown}")
            print(f"  - Markdown length: {markdown_len} characters")
            print(f"  - Document type: {getattr(parsed_doc, 'doc_type', 'unknown')}")
            
            if has_markdown and markdown_len > 0:
                print(f"  - First 200 chars of markdown: {parsed_doc.markdown[:200]}...")
        else:
            print("✗ Parse returned no results")
            return False
            
    except Exception as e:
        print(f"✗ Parse failed: {e}")
        return False
    
    # Test 2: Parse with extraction model
    print("\nTest 2: Parse with extraction model...")
    
    class SimpleExtraction(BaseModel):
        title: Optional[str] = Field(None, description="Document title or heading")
        date: Optional[str] = Field(None, description="Any date found in the document")
        content: Optional[str] = Field(None, description="Main content or summary")
    
    try:
        result_with_extraction = parse(
            documents=[test_file],
            extraction_model=SimpleExtraction
        )
        
        if result_with_extraction and len(result_with_extraction) > 0:
            parsed_doc = result_with_extraction[0]
            has_extraction = hasattr(parsed_doc, 'extraction')
            
            print(f"✓ Parse with extraction successful")
            print(f"  - Has extraction: {has_extraction}")
            
            if has_extraction and parsed_doc.extraction:
                extracted_data = parsed_doc.extraction.model_dump()
                print(f"  - Extracted fields: {list(extracted_data.keys())}")
                for key, value in extracted_data.items():
                    if value:
                        preview = str(value)[:100] if value else "None"
                        print(f"    • {key}: {preview}...")
            
            # Check for extraction metadata
            if hasattr(parsed_doc, 'extraction_metadata'):
                print(f"  - Has extraction metadata: True")
        else:
            print("✗ Extraction returned no results")
            return False
            
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        print(f"  Error details: {str(e)}")
        return False
    
    print("\n✓ All tests passed! Landing.AI integration is working correctly.")
    return True

if __name__ == "__main__":
    success = test_landing_ai_parse()
    sys.exit(0 if success else 1)