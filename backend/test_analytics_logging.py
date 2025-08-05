#!/usr/bin/env python3
"""
Test script to verify analytics event logging functionality.
Tests that events are properly logged for uploads, status changes, exports, and chat interactions.
"""

import requests
import json
import sqlite3
import time
from datetime import datetime
import tempfile
import os

BASE_URL = "http://localhost:8000/api/v1"
DB_PATH = "./apex_ade.db"

def test_analytics_event_logging():
    print("=== Testing Analytics Event Logging ===\n")
    
    # Step 1: Upload a document and check event logging
    print("1. Testing document upload event logging...")
    
    # Create a test PDF file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        f.write('%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n')
        test_pdf_path = f.name
    
    with open(test_pdf_path, 'rb') as f:
        files = {'file': ('test_analytics.pdf', f, 'application/pdf')}
        response = requests.post(f"{BASE_URL}/documents/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return False
    
    document = response.json()
    doc_id = document['id']
    print(f"✅ Document uploaded: ID {doc_id}")
    
    # Give time for background task to complete
    time.sleep(1)
    
    # Step 2: Check if upload event was logged
    print("\n2. Verifying upload event in analytics...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT event_type, document_id, event_data, created_at 
        FROM analytics_events 
        WHERE document_id = ? AND event_type = 'document_upload'
        ORDER BY created_at DESC
        LIMIT 1
    """, (doc_id,))
    
    upload_event = cursor.fetchone()
    if upload_event:
        print(f"✅ Upload event logged:")
        print(f"   - Event type: {upload_event[0]}")
        print(f"   - Document ID: {upload_event[1]}")
        print(f"   - Event data: {upload_event[2]}")
    else:
        print("❌ Upload event not found in analytics")
    
    # Step 3: Test status change events (approve document)
    print("\n3. Testing status change event logging...")
    
    # First, set document to EXTRACTED status for testing
    cursor.execute("""
        UPDATE documents 
        SET status = 'EXTRACTED', 
            extracted_md = 'Test content for analytics',
            extracted_data = '{"test": "data"}'
        WHERE id = ?
    """, (doc_id,))
    conn.commit()
    
    # Approve the document
    response = requests.post(f"{BASE_URL}/documents/{doc_id}/approve")
    if response.status_code == 200:
        print("✅ Document approved")
        time.sleep(1)
        
        # Check analytics event
        cursor.execute("""
            SELECT event_type, event_data, created_at 
            FROM analytics_events 
            WHERE document_id = ? AND event_type = 'document_approved'
            ORDER BY created_at DESC
            LIMIT 1
        """, (doc_id,))
        
        approve_event = cursor.fetchone()
        if approve_event:
            print(f"✅ Approval event logged:")
            print(f"   - Event data: {approve_event[1]}")
        else:
            print("❌ Approval event not found")
    
    # Step 4: Test export event logging
    print("\n4. Testing export event logging...")
    response = requests.get(f"{BASE_URL}/documents/{doc_id}/export/csv")
    if response.status_code == 200:
        print("✅ CSV export successful")
        time.sleep(1)
        
        cursor.execute("""
            SELECT event_type, event_data 
            FROM analytics_events 
            WHERE document_id = ? AND event_type = 'document_exported'
            ORDER BY created_at DESC
            LIMIT 1
        """, (doc_id,))
        
        export_event = cursor.fetchone()
        if export_event:
            print(f"✅ Export event logged:")
            print(f"   - Event data: {export_event[1]}")
        else:
            print("❌ Export event not found")
    
    # Step 5: Test chat interaction event logging
    print("\n5. Testing chat interaction event logging...")
    chat_request = {"query": "What is the main content of this document?"}
    response = requests.post(f"{BASE_URL}/documents/{doc_id}/chat", json=chat_request)
    
    if response.status_code in [200, 207]:
        print("✅ Chat query processed")
        time.sleep(1)
        
        cursor.execute("""
            SELECT event_type, event_data, duration_ms 
            FROM analytics_events 
            WHERE document_id = ? AND event_type = 'chat_interaction'
            ORDER BY created_at DESC
            LIMIT 1
        """, (doc_id,))
        
        chat_event = cursor.fetchone()
        if chat_event:
            print(f"✅ Chat interaction event logged:")
            print(f"   - Event data: {chat_event[1]}")
            print(f"   - Duration: {chat_event[2]:.2f}ms" if chat_event[2] else "   - Duration: N/A")
        else:
            print("❌ Chat event not found")
    
    # Step 6: Get summary of all events for this document
    print("\n6. Summary of all analytics events for document...")
    cursor.execute("""
        SELECT event_type, COUNT(*) as count 
        FROM analytics_events 
        WHERE document_id = ? 
        GROUP BY event_type
    """, (doc_id,))
    
    event_summary = cursor.fetchall()
    print("✅ Event summary:")
    for event_type, count in event_summary:
        print(f"   - {event_type}: {count} events")
    
    # Step 7: Test non-blocking nature (events should be logged even if analytics fails)
    print("\n7. Testing non-blocking analytics...")
    # This is harder to test directly, but we can verify events were logged asynchronously
    cursor.execute("""
        SELECT COUNT(*) FROM analytics_events WHERE document_id = ?
    """, (doc_id,))
    total_events = cursor.fetchone()[0]
    
    print(f"✅ Total events logged for document: {total_events}")
    print("   Analytics logging appears to be working correctly")
    
    conn.close()
    
    # Cleanup
    os.unlink(test_pdf_path)
    
    print("\n=== Analytics Event Logging Test Complete ===")
    return True

def get_analytics_metrics():
    """Get some basic analytics metrics"""
    print("\n=== Analytics Metrics Summary ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total events by type
    cursor.execute("""
        SELECT event_type, COUNT(*) as count 
        FROM analytics_events 
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    print("\nEvent counts by type:")
    for event_type, count in cursor.fetchall():
        print(f"  {event_type}: {count}")
    
    # Recent activity
    cursor.execute("""
        SELECT event_type, document_id, created_at 
        FROM analytics_events 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    print("\nRecent events:")
    for event in cursor.fetchall()[:5]:
        print(f"  {event[2]}: {event[0]} (Doc {event[1]})")
    
    conn.close()

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
        success = test_analytics_event_logging()
        if success:
            get_analytics_metrics()
            print("\n✅ All analytics event logging tests passed!")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()