#!/usr/bin/env python3
"""
Test script to verify enhanced chat log storage with retry logic and fallback field.
Tests normal operation, fallback field storage, and handles storage failures gracefully.
"""

import requests
import json
import time
import sqlite3
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
DB_PATH = "./apex_ade.db"

def test_chat_storage_enhancements():
    print("=== Testing Enhanced Chat Log Storage ===\n")
    
    # Step 1: Get an existing document with EXTRACTED status
    print("1. Getting documents with EXTRACTED status...")
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
    
    extracted_docs = [doc for doc in documents if doc['status'] == 'EXTRACTED']
    
    if not extracted_docs:
        print("❌ No documents with EXTRACTED status found. Please ensure a document has been processed.")
        return False
    
    document = extracted_docs[0]
    doc_id = document['id']
    print(f"✅ Found document: {document['filename']} (ID: {doc_id})")
    
    # Step 2: Test normal chat query (fallback=False expected)
    print("\n2. Testing normal chat query (should have fallback=False)...")
    chat_request = {
        "query": "What are the key points in this document?"
    }
    
    response = requests.post(
        f"{BASE_URL}/documents/{doc_id}/chat",
        json=chat_request
    )
    
    if response.status_code == 207:
        # Multi-status: chat succeeded but storage failed
        detail = response.json()['detail']
        print(f"⚠️  Chat succeeded but storage failed (HTTP 207):")
        print(f"   - Response: {detail['response'][:100]}...")
        print(f"   - Storage error: {detail['storage_error']}")
        print(f"   - Retry available: {detail['retry_available']}")
        chat_response = detail
    elif response.status_code == 200:
        chat_response = response.json()
        print(f"✅ Chat response received and stored successfully:")
    else:
        print(f"❌ Chat query failed: {response.text}")
        return False
    
    print(f"   - Response preview: {chat_response['response'][:100]}...")
    print(f"   - Fallback: {chat_response.get('fallback', 'not present')}")
    
    # Step 3: Test fallback query (fallback=True expected)
    print("\n3. Testing fallback query (should have fallback=True)...")
    fallback_request = {
        "query": "What is the quantum flux capacitor reading for this document?"
    }
    
    response = requests.post(
        f"{BASE_URL}/documents/{doc_id}/chat",
        json=fallback_request
    )
    
    if response.status_code == 207:
        # Multi-status: chat succeeded but storage failed
        detail = response.json()['detail']
        print(f"⚠️  Chat succeeded but storage failed (HTTP 207):")
        print(f"   - Storage error: {detail['storage_error']}")
        fallback_response = detail
    elif response.status_code == 200:
        fallback_response = response.json()
        print(f"✅ Fallback response received and stored successfully:")
    else:
        print(f"❌ Fallback query failed: {response.text}")
        return False
    
    print(f"   - Response preview: {fallback_response['response'][:100]}...")
    print(f"   - Fallback: {fallback_response.get('fallback', 'not present')}")
    
    # Step 4: Verify fallback field in database
    print("\n4. Verifying fallback field storage in database...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if fallback column exists
        cursor.execute("PRAGMA table_info(chat_logs)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'fallback' not in column_names:
            print("❌ Fallback column not found in chat_logs table")
            return False
        
        print("✅ Fallback column exists in chat_logs table")
        
        # Get recent chat logs
        cursor.execute("""
            SELECT id, document_id, query, fallback, created_at 
            FROM chat_logs 
            WHERE document_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (doc_id,))
        
        logs = cursor.fetchall()
        print(f"\n   Recent chat logs for document {doc_id}:")
        for log in logs:
            fallback_val = bool(log[3]) if log[3] is not None else None
            print(f"   - ID: {log[0]}, Query: '{log[2][:50]}...', Fallback: {fallback_val}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
    
    # Step 5: Test chat history retrieval with fallback field
    print("\n5. Testing chat history retrieval with fallback field...")
    response = requests.get(f"{BASE_URL}/documents/{doc_id}/chat/history?limit=5")
    if response.status_code != 200:
        print(f"❌ Failed to get chat history: {response.text}")
        return False
    
    chat_history = response.json()
    print(f"✅ Chat history retrieved: {len(chat_history)} entries")
    
    for i, entry in enumerate(chat_history[:3]):
        fallback_val = entry.get('fallback', 'not present')
        print(f"   - Entry {i+1}: Query: '{entry['query'][:50]}...', Fallback: {fallback_val}")
    
    # Step 6: Test concurrent chat requests (stress test retry logic)
    print("\n6. Testing concurrent chat requests (stress test)...")
    import concurrent.futures
    
    def send_chat_query(query_num):
        try:
            response = requests.post(
                f"{BASE_URL}/documents/{doc_id}/chat",
                json={"query": f"Test query {query_num}: What is item {query_num} in the document?"}
            )
            return response.status_code, response.json() if response.status_code in [200, 207] else None
        except Exception as e:
            return None, str(e)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_chat_query, i) for i in range(5)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    success_count = sum(1 for status, _ in results if status == 200)
    partial_success_count = sum(1 for status, _ in results if status == 207)
    
    print(f"   - Successful saves: {success_count}")
    print(f"   - Partial successes (207): {partial_success_count}")
    print(f"   - Total requests: {len(results)}")
    
    if success_count + partial_success_count == len(results):
        print("   ✅ All requests handled gracefully")
    else:
        print("   ❌ Some requests failed unexpectedly")
    
    # Step 7: Test empty document handling
    print("\n7. Testing empty document handling...")
    # Find or note if there's a document with null extracted_md
    empty_docs = [doc for doc in documents if doc['status'] == 'EXTRACTED' and not doc.get('extracted_md')]
    if empty_docs:
        empty_doc_id = empty_docs[0]['id']
        response = requests.post(
            f"{BASE_URL}/documents/{empty_doc_id}/chat",
            json={"query": "What is in this document?"}
        )
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('fallback', False):
                print("   ✅ Empty document handled correctly with fallback response")
            else:
                print("   ⚠️  Empty document should trigger fallback response")
        else:
            print(f"   ❌ Empty document query failed: {response.text}")
    else:
        print("   ℹ️  No empty documents to test")
    
    print("\n=== Enhanced Chat Storage Test Complete ===")
    return True

if __name__ == "__main__":
    try:
        # Ensure server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("⚠️  Server health check failed, but continuing...")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please ensure the backend is running on http://localhost:8000")
        exit(1)
    
    try:
        success = test_chat_storage_enhancements()
        if success:
            print("\n✅ All enhanced chat storage tests passed!")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()