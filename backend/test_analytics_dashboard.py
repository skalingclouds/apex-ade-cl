#!/usr/bin/env python3
"""
Test script to verify analytics dashboard endpoints.
Tests metrics aggregation, time series data, and performance metrics.
"""

import requests
import json
from datetime import datetime
import pprint

BASE_URL = "http://localhost:8000/api/v1"

def test_analytics_dashboard():
    print("=== Testing Analytics Dashboard Endpoints ===\n")
    
    # Step 1: Test overall metrics endpoint
    print("1. Testing overall analytics metrics...")
    response = requests.get(f"{BASE_URL}/analytics/metrics")
    
    if response.status_code != 200:
        print(f"❌ Failed to get analytics metrics: {response.text}")
        return False
    
    metrics = response.json()
    print("✅ Analytics metrics retrieved:")
    print(f"   - Total documents: {metrics['total_documents']}")
    print(f"   - Status distribution: {metrics['status_distribution']}")
    print(f"   - Approval rate: {metrics['approval_rate']}%")
    print(f"   - Rejection rate: {metrics['rejection_rate']}%")
    print(f"   - Total chat interactions: {metrics['total_chat_interactions']}")
    print(f"   - Unique documents chatted: {metrics['unique_documents_chatted']}")
    print(f"   - Average chats per document: {metrics['average_chats_per_document']}")
    print(f"   - Total exports: {metrics['total_exports']}")
    print(f"   - Recent uploads (24h): {metrics['recent_uploads_24h']}")
    print(f"   - Recent chats (24h): {metrics['recent_chats_24h']}")
    
    # Step 2: Test time series data
    print("\n2. Testing time series metrics...")
    
    # Test uploads time series
    response = requests.get(f"{BASE_URL}/analytics/metrics/timeseries?metric=uploads&days=7")
    if response.status_code == 200:
        timeseries = response.json()
        print(f"✅ Upload time series (last 7 days): {len(timeseries)} data points")
        if timeseries:
            print(f"   Latest: {timeseries[-1]['date']} - {timeseries[-1]['value']} uploads")
    else:
        print(f"❌ Failed to get upload time series: {response.text}")
    
    # Test chats time series
    response = requests.get(f"{BASE_URL}/analytics/metrics/timeseries?metric=chats&days=7")
    if response.status_code == 200:
        timeseries = response.json()
        print(f"✅ Chat time series (last 7 days): {len(timeseries)} data points")
        if timeseries:
            print(f"   Latest: {timeseries[-1]['date']} - {timeseries[-1]['value']} chats")
    else:
        print(f"❌ Failed to get chat time series: {response.text}")
    
    # Step 3: Test top users endpoint
    print("\n3. Testing top users metrics...")
    response = requests.get(f"{BASE_URL}/analytics/metrics/top-users?limit=5")
    
    if response.status_code == 200:
        top_users = response.json()
        print(f"✅ Top users by uploads: {len(top_users)} users")
        for i, user in enumerate(top_users[:3]):
            print(f"   {i+1}. {user['user_identifier']}: {user['upload_count']} uploads")
    else:
        print(f"❌ Failed to get top users: {response.text}")
    
    # Step 4: Test performance metrics
    print("\n4. Testing performance metrics...")
    response = requests.get(f"{BASE_URL}/analytics/metrics/performance")
    
    if response.status_code == 200:
        perf_metrics = response.json()
        print("✅ Performance metrics retrieved:")
        print(f"   - Average chat response time: {perf_metrics['average_chat_response_time_ms']}ms")
        print(f"   - Document failure rate: {perf_metrics['document_failure_rate']}%")
        print(f"   - Chat fallback rate: {perf_metrics['chat_fallback_rate']}%")
        print(f"   - Total failed documents: {perf_metrics['total_failed_documents']}")
        print(f"   - Total fallback chats: {perf_metrics['total_fallback_chats']}")
    else:
        print(f"❌ Failed to get performance metrics: {response.text}")
    
    # Step 5: Test recent events endpoint
    print("\n5. Testing recent events endpoint...")
    response = requests.get(f"{BASE_URL}/analytics/events/recent?limit=5")
    
    if response.status_code == 200:
        recent_events = response.json()
        print(f"✅ Recent events: {len(recent_events)} events")
        for event in recent_events[:3]:
            print(f"   - {event['created_at']}: {event['event_type']} (Doc {event['document_id']})")
    else:
        print(f"❌ Failed to get recent events: {response.text}")
    
    # Step 6: Test specific event type filtering
    print("\n6. Testing event filtering...")
    response = requests.get(f"{BASE_URL}/analytics/events/recent?event_type=chat_interaction&limit=5")
    
    if response.status_code == 200:
        chat_events = response.json()
        print(f"✅ Recent chat events: {len(chat_events)} events")
        if chat_events:
            print(f"   Latest chat: {chat_events[0]['created_at']}")
            if chat_events[0]['event_data']:
                print(f"   Event data: {chat_events[0]['event_data']}")
    else:
        print(f"❌ Failed to get filtered events: {response.text}")
    
    print("\n=== Analytics Dashboard Test Complete ===")
    return True

def create_sample_data():
    """Create some sample data to make analytics more interesting"""
    print("\n=== Creating Sample Data for Analytics ===\n")
    
    # Upload a few test documents
    for i in range(3):
        with open('/tmp/test.pdf', 'wb') as f:
            f.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
        
        with open('/tmp/test.pdf', 'rb') as f:
            files = {'file': (f'analytics_test_{i}.pdf', f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
            if response.status_code == 200:
                doc = response.json()
                print(f"✅ Created test document {i+1}: ID {doc['id']}")
                
                # Simulate some actions on the document
                # Note: Some of these might fail if the document isn't in the right state
                requests.post(f"{BASE_URL}/documents/{doc['id']}/approve")
                requests.post(f"{BASE_URL}/documents/{doc['id']}/chat", 
                            json={"query": f"Test query {i}"})

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
        # Optionally create sample data
        # create_sample_data()
        
        success = test_analytics_dashboard()
        if success:
            print("\n✅ All analytics dashboard tests passed!")
            print("\n📊 Note: The analytics dashboard is designed for admin users.")
            print("   In production, these endpoints should be protected with authentication.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()