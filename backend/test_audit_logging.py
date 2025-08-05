#!/usr/bin/env python3
"""Test script for audit logging functionality"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_audit_logging():
    """Test audit logging across different operations"""
    
    print("=== Testing Audit Logging Functionality ===\n")
    
    # Test 1: Upload document (should create audit log)
    print("1. Testing document upload audit logging...")
    
    # Create a simple test PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n200\n%%EOF"
    
    files = {
        'file': ('test_document.pdf', pdf_content, 'application/pdf')
    }
    
    headers = {
        'User-Agent': 'TestAuditLogger/1.0'
    }
    
    response = requests.post(f"{BASE_URL}/documents/upload", files=files, headers=headers)
    
    if response.status_code == 200:
        document_id = response.json()['id']
        print(f"✓ Document uploaded successfully. ID: {document_id}")
    else:
        print(f"✗ Upload failed: {response.text}")
        return
    
    # Test 2: Approve document (should create status change audit log)
    print("\n2. Testing document approval audit logging...")
    
    # First we need to set the document to EXTRACTED status for testing
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        session.execute(text("UPDATE documents SET status = 'EXTRACTED' WHERE id = :id"), {"id": document_id})
        session.commit()
    
    response = requests.post(f"{BASE_URL}/documents/{document_id}/approve", headers=headers)
    
    if response.status_code == 200:
        print(f"✓ Document approved successfully")
    else:
        print(f"✗ Approval failed: {response.text}")
    
    # Test 3: Check audit logs
    print("\n3. Checking audit logs in database...")
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, action, old_value, new_value, ip_address, user_agent, created_at
            FROM audit_logs 
            WHERE document_id = :doc_id
            ORDER BY created_at DESC
        """), {"doc_id": document_id})
        
        logs = result.fetchall()
        
        print(f"\nFound {len(logs)} audit log entries:")
        for log in logs:
            print(f"\n  ID: {log[0]}")
            print(f"  Action: {log[1]}")
            print(f"  Old Value: {log[2]}")
            print(f"  New Value: {log[3]}")
            print(f"  IP Address: {log[4]}")
            print(f"  User Agent: {log[5]}")
            print(f"  Created At: {log[6]}")
    
    # Test 4: Delete document (should create deletion audit log)
    print("\n4. Testing document deletion audit logging...")
    
    response = requests.delete(f"{BASE_URL}/documents/{document_id}", headers=headers)
    
    if response.status_code == 204:
        print(f"✓ Document deleted successfully")
    else:
        print(f"✗ Deletion failed: {response.text}")
    
    # Check deletion audit log
    print("\n5. Checking deletion audit log...")
    
    with engine.connect() as conn:
        # Check all audit logs to see the deletion log
        result = conn.execute(text("""
            SELECT id, document_id, action, old_value, details, created_at
            FROM audit_logs 
            WHERE action = 'deletion'
            ORDER BY created_at DESC
            LIMIT 1
        """))
        
        deletion_log = result.fetchone()
        
        if deletion_log:
            print(f"\n✓ Deletion audit log found:")
            print(f"  ID: {deletion_log[0]}")
            print(f"  Document ID: {deletion_log[1]}")
            print(f"  Action: {deletion_log[2]}")
            print(f"  Document Info: {deletion_log[3]}")
            print(f"  Details: {deletion_log[4]}")
            print(f"  Created At: {deletion_log[5]}")
        else:
            print("\n✗ No deletion audit log found")
    
    print("\n=== Audit Logging Test Complete ===")

if __name__ == "__main__":
    try:
        test_audit_logging()
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)