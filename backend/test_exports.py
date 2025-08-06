#!/usr/bin/env python3
"""
Test script to verify all export formats are working correctly
"""
import os
import requests
import json
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def test_exports(document_id: int = 8):
    """Test all export formats for a document"""
    
    print(f"\n📋 Testing exports for document ID: {document_id}")
    print("=" * 60)
    
    # 1. Test getting markdown (with preprocessing)
    print("\n1. Testing markdown retrieval...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/markdown")
        if response.status_code == 200:
            data = response.json()
            markdown = data['markdown']
            print(f"   ✅ Markdown retrieved: {len(markdown)} characters")
            print(f"   - Status: {data['status']}")
            print(f"   - Processed at: {data['processed_at']}")
            
            # Check if HTML comments are removed
            if '<!--' not in markdown:
                print("   ✅ HTML comments successfully removed")
            else:
                print("   ⚠️ HTML comments still present")
                
            # Check if ID markers are removed
            if '{#' not in markdown:
                print("   ✅ ID markers successfully removed")
            else:
                print("   ⚠️ ID markers still present")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Test CSV export
    print("\n2. Testing CSV export...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/export/csv")
        if response.status_code == 200:
            csv_content = response.text
            print(f"   ✅ CSV exported: {len(csv_content)} bytes")
            
            # Check first few lines
            lines = csv_content.split('\n')[:5]
            print("   Sample content:")
            for line in lines:
                if line.strip():
                    print(f"      {line[:80]}...")
                    
            # Check if markdown syntax is removed
            if '**' not in csv_content and '##' not in csv_content and '|' not in csv_content:
                print("   ✅ Markdown syntax successfully removed from CSV")
            else:
                print("   ⚠️ Some markdown syntax may still be present")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test plain text export
    print("\n3. Testing plain text export...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/export/text")
        if response.status_code == 200:
            text_content = response.text
            print(f"   ✅ Text exported: {len(text_content)} bytes")
            
            # Check first few lines
            lines = text_content.split('\n')[:10]
            print("   Sample content:")
            for line in lines:
                if line.strip():
                    print(f"      {line[:80]}...")
                    
            # Check if markdown syntax is removed
            if '**' not in text_content and '##' not in text_content and '|' not in text_content:
                print("   ✅ All markdown syntax successfully removed")
            else:
                print("   ⚠️ Some markdown syntax may still be present")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Test markdown export (formatted)
    print("\n4. Testing markdown export (formatted)...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/export/markdown")
        if response.status_code == 200:
            md_content = response.text
            print(f"   ✅ Markdown exported: {len(md_content)} bytes")
            
            # Check first few lines
            lines = md_content.split('\n')[:10]
            print("   Sample content:")
            for line in lines:
                if line.strip():
                    print(f"      {line[:80]}...")
                    
            # Check if tables are properly formatted
            if '|' in md_content:
                print("   ✅ Tables present and formatted")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Export testing complete!")
    print("\nNext steps:")
    print("1. Check the frontend at http://localhost:3000")
    print("2. Navigate to document review page")
    print("3. Verify markdown is properly rendered with tables")
    print("4. Test each export button")
    print("5. Verify exported files are properly formatted for non-technical users")

if __name__ == "__main__":
    # You can change the document ID here if needed
    test_exports(document_id=8)