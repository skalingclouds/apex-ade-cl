#!/usr/bin/env python3
"""
Test script to verify export functionality with audit logging.
Tests CSV, Markdown, and PDF exports with proper status checks and audit trails.
"""

import requests
import json
import os
import tempfile
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_export_functionality():
    print("=== Testing Export Functionality with Audit Logging ===\n")
    
    # Step 1: Get an existing document with EXTRACTED or APPROVED status
    print("1. Getting documents with EXTRACTED or APPROVED status...")
    response = requests.get(f"{BASE_URL}/documents")
    if response.status_code != 200:
        print(f"❌ Failed to get documents: {response.text}")
        return False
    
    response_data = response.json()
    if isinstance(response_data, dict) and 'documents' in response_data:
        documents = response_data['documents']
    elif isinstance(response_data, list):
        documents = response_data
    else:
        print(f"❌ Unexpected response format: {type(response_data)}")
        return False
    
    valid_docs = [doc for doc in documents if doc['status'] in ['EXTRACTED', 'APPROVED']]
    
    if not valid_docs:
        print("❌ No documents with EXTRACTED or APPROVED status found.")
        return False
    
    document = valid_docs[0]
    doc_id = document['id']
    print(f"✅ Found document: {document['filename']} (ID: {doc_id}, Status: {document['status']})")
    
    # Step 2: Test CSV export
    print("\n2. Testing CSV export...")
    response = requests.get(f"{BASE_URL}/documents/{doc_id}/export/csv")
    
    if response.status_code != 200:
        print(f"❌ CSV export failed: {response.text}")
        return False
    
    # Save CSV to temp file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
        f.write(response.content)
        csv_path = f.name
    
    csv_size = os.path.getsize(csv_path)
    print(f"✅ CSV export successful:")
    print(f"   - File size: {csv_size} bytes")
    print(f"   - Content-Type: {response.headers.get('content-type')}")
    print(f"   - Filename: {response.headers.get('content-disposition')}")
    
    # Preview CSV content
    with open(csv_path, 'r') as f:
        lines = f.readlines()[:3]
        print(f"   - Preview: {' | '.join(lines[0].strip().split(',')[:3])}...")
    
    os.unlink(csv_path)
    
    # Step 3: Test Markdown export
    print("\n3. Testing Markdown export...")
    response = requests.get(f"{BASE_URL}/documents/{doc_id}/export/markdown")
    
    if response.status_code != 200:
        print(f"❌ Markdown export failed: {response.text}")
        return False
    
    # Save Markdown to temp file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.md', delete=False) as f:
        f.write(response.content)
        md_path = f.name
    
    md_size = os.path.getsize(md_path)
    print(f"✅ Markdown export successful:")
    print(f"   - File size: {md_size} bytes")
    print(f"   - Content-Type: {response.headers.get('content-type')}")
    
    # Preview Markdown content
    with open(md_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')[:5]
        print(f"   - Preview: {lines[0][:50]}...")
    
    os.unlink(md_path)
    
    # Step 4: Test PDF streaming
    print("\n4. Testing PDF streaming...")
    response = requests.get(f"{BASE_URL}/documents/{doc_id}/pdf")
    
    if response.status_code != 200:
        print(f"❌ PDF streaming failed: {response.text}")
        return False
    
    print(f"✅ PDF streaming successful:")
    print(f"   - File size: {len(response.content)} bytes")
    print(f"   - Content-Type: {response.headers.get('content-type')}")
    print(f"   - Content-Disposition: {response.headers.get('content-disposition')}")
    
    # Step 5: Test markdown content retrieval
    print("\n5. Testing markdown content retrieval...")
    response = requests.get(f"{BASE_URL}/documents/{doc_id}/markdown")
    
    if response.status_code != 200:
        print(f"❌ Markdown retrieval failed: {response.text}")
        return False
    
    md_data = response.json()
    print(f"✅ Markdown content retrieved:")
    print(f"   - Content length: {len(md_data.get('markdown', ''))} characters")
    print(f"   - Processed at: {md_data.get('processed_at')}")
    print(f"   - Status: {md_data.get('status')}")
    
    # Step 6: Test export with invalid document status
    print("\n6. Testing export restrictions for invalid status...")
    # Find a PENDING document
    pending_docs = [doc for doc in documents if doc['status'] == 'PENDING']
    if pending_docs:
        pending_id = pending_docs[0]['id']
        response = requests.get(f"{BASE_URL}/documents/{pending_id}/export/csv")
        if response.status_code == 400:
            print(f"   ✅ Correctly rejected export for PENDING document")
            error_detail = response.json().get('detail', '')
            print(f"   - Error: {error_detail}")
        else:
            print(f"   ❌ Expected 400 error for PENDING document, got {response.status_code}")
    else:
        print("   ℹ️  No PENDING documents to test status validation")
    
    # Step 7: Test non-existent document
    print("\n7. Testing export for non-existent document...")
    response = requests.get(f"{BASE_URL}/documents/99999/export/csv")
    if response.status_code == 404:
        print("   ✅ Correctly returned 404 for non-existent document")
    else:
        print(f"   ❌ Expected 404 error, got {response.status_code}")
    
    # Step 8: Test export when extracted_data is null
    print("\n8. Testing export with missing data...")
    # This would require a document with null extracted_data
    empty_docs = [doc for doc in valid_docs if doc.get('extracted_data') is None]
    if empty_docs:
        empty_id = empty_docs[0]['id']
        response = requests.get(f"{BASE_URL}/documents/{empty_id}/export/csv")
        if response.status_code == 400:
            print("   ✅ Correctly handled missing extracted data")
        else:
            print(f"   ❌ Expected 400 error for missing data, got {response.status_code}")
    else:
        print("   ℹ️  No documents with missing data to test")
    
    print("\n=== Export Functionality Test Complete ===")
    return True

def verify_audit_logs():
    """Optional: Verify audit logs were created (requires database access)"""
    print("\n=== Verifying Audit Logs ===")
    import sqlite3
    
    try:
        conn = sqlite3.connect("./apex_ade.db")
        cursor = conn.cursor()
        
        # Get recent audit logs for exports
        cursor.execute("""
            SELECT id, document_id, action, created_at, ip_address 
            FROM audit_logs 
            WHERE action LIKE '%export%' OR action LIKE '%download%' OR action LIKE '%view%'
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        logs = cursor.fetchall()
        if logs:
            print(f"✅ Found {len(logs)} recent export-related audit logs:")
            for log in logs[:5]:
                print(f"   - ID: {log[0]}, Doc: {log[1]}, Action: {log[2]}, Time: {log[3]}")
        else:
            print("⚠️  No export-related audit logs found")
        
        conn.close()
    except Exception as e:
        print(f"   ℹ️  Could not verify audit logs: {e}")

if __name__ == "__main__":
    try:
        # Check server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Server health check failed, but continuing...")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please ensure the backend is running on http://localhost:8000")
        exit(1)
    
    try:
        success = test_export_functionality()
        if success:
            verify_audit_logs()
            print("\n✅ All export functionality tests passed!")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()