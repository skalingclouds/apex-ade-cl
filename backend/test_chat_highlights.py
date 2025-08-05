#!/usr/bin/env python3
"""Test script for chat functionality with highlight metadata"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_chat_highlights():
    """Test chat processing with highlight metadata"""
    
    print("=== Testing Chat Functionality with Highlights ===\n")
    
    # Step 1: Upload a test document
    print("1. Uploading test document...")
    
    # Create a simple test PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n200\n%%EOF"
    
    files = {
        'file': ('test_chat_document.pdf', pdf_content, 'application/pdf')
    }
    
    response = requests.post(f"{BASE_URL}/documents/upload", files=files)
    
    if response.status_code != 200:
        print(f"✗ Upload failed: {response.text}")
        return
    
    document_id = response.json()['id']
    print(f"✓ Document uploaded successfully. ID: {document_id}")
    
    # Step 2: Set document to EXTRACTED status for testing
    print("\n2. Setting document status to EXTRACTED...")
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Add some sample extracted markdown content
    sample_extracted_md = """# Product Catalog
    
This document contains information about our product lineup.

## Product: Laptop Model X1

The Laptop Model X1 is our flagship device with the following features:
- Intel Core i7 processor
- 16GB RAM
- 512GB SSD storage
- 15.6 inch display
- Price: $1,299

## Product: Wireless Mouse Pro

The Wireless Mouse Pro offers:
- Ergonomic design
- Long battery life (up to 6 months)
- Precision tracking
- Price: $49.99

## Product: USB-C Hub

Our USB-C Hub includes:
- 4 USB-A ports
- 1 HDMI port
- SD card reader
- Price: $79.99

For more information, please contact our sales team."""
    
    with SessionLocal() as session:
        session.execute(text("""
            UPDATE documents 
            SET status = 'EXTRACTED', 
                extracted_md = :extracted_md,
                extracted_data = :extracted_data
            WHERE id = :id
        """), {
            "id": document_id,
            "extracted_md": sample_extracted_md,
            "extracted_data": json.dumps({"products": ["Laptop Model X1", "Wireless Mouse Pro", "USB-C Hub"]})
        })
        session.commit()
    
    print("✓ Document status updated to EXTRACTED with sample content")
    
    # Step 3: Test chat queries
    test_queries = [
        "What is the price of the laptop?",
        "Tell me about the wireless mouse",
        "What products are available?",
        "Does the USB hub have HDMI?",
        "What is the warranty period?"  # This should trigger fallback
    ]
    
    print("\n3. Testing chat queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: '{query}'")
        
        chat_request = {
            "query": query
        }
        
        response = requests.post(
            f"{BASE_URL}/documents/{document_id}/chat",
            json=chat_request
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Response received:")
            print(f"  - Response: {data['response'][:100]}...")
            print(f"  - Fallback: {data.get('fallback', False)}")
            
            if data.get('highlighted_areas'):
                print(f"  - Highlights: {len(data['highlighted_areas'])} areas")
                for j, highlight in enumerate(data['highlighted_areas'][:2]):  # Show first 2
                    print(f"    • Page {highlight['page']}: bbox {highlight['bbox']}")
            else:
                print("  - Highlights: None")
        else:
            print(f"✗ Chat query failed: {response.text}")
        
        print()
    
    # Step 4: Test chat history
    print("4. Testing chat history retrieval...")
    
    response = requests.get(f"{BASE_URL}/documents/{document_id}/chat/history")
    
    if response.status_code == 200:
        history = response.json()
        print(f"✓ Retrieved {len(history)} chat log entries")
        
        if history:
            print("\nRecent chat history:")
            for entry in history[:3]:  # Show first 3
                print(f"  - Query: '{entry['query']}'")
                print(f"    Response: {entry['response'][:60]}...")
                print(f"    Fallback: {entry.get('fallback', False)}")
    else:
        print(f"✗ Failed to retrieve chat history: {response.text}")
    
    # Step 5: Test error handling
    print("\n5. Testing error handling...")
    
    # Test with non-existent document
    response = requests.post(
        f"{BASE_URL}/documents/99999/chat",
        json={"query": "test"}
    )
    
    if response.status_code == 404:
        print("✓ Correctly handled non-existent document")
    else:
        print(f"✗ Unexpected response for non-existent document: {response.status_code}")
    
    # Test with non-extracted document
    with SessionLocal() as session:
        session.execute(text("UPDATE documents SET status = 'PENDING' WHERE id = :id"), {"id": document_id})
        session.commit()
    
    response = requests.post(
        f"{BASE_URL}/documents/{document_id}/chat",
        json={"query": "test"}
    )
    
    if response.status_code == 400:
        print("✓ Correctly rejected chat for non-extracted document")
    else:
        print(f"✗ Unexpected response for non-extracted document: {response.status_code}")
    
    # Cleanup
    print("\n6. Cleaning up...")
    response = requests.delete(f"{BASE_URL}/documents/{document_id}")
    if response.status_code == 204:
        print("✓ Test document deleted")
    
    print("\n=== Chat Functionality Test Complete ===")

if __name__ == "__main__":
    try:
        test_chat_highlights()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)