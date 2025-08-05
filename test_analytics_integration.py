#!/usr/bin/env python3
"""
Test Analytics Integration
This script verifies that the Analytics page is properly integrated and accessible
"""

import requests
import time
import subprocess
from datetime import datetime

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000/api/v1"

def check_frontend_running():
    """Check if the frontend server is running"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        return response.status_code < 500
    except:
        return False

def check_backend_running():
    """Check if the backend server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return True
    except:
        return False

def test_analytics_route():
    """Test that the Analytics route is accessible"""
    print("\n🔍 Testing Analytics Route...")
    
    # Test analytics page loads
    try:
        response = requests.get(f"{BASE_URL}/analytics", timeout=10, allow_redirects=True)
        if response.status_code == 200:
            print("✓ Analytics page is accessible")
            # Check if the page contains expected content
            if "Analytics Dashboard" in response.text:
                print("✓ Analytics page contains expected content")
            else:
                print("⚠️  Analytics page loaded but content might be missing")
            return True
        else:
            print(f"✗ Analytics page returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to access analytics page: {str(e)}")
        return False

def test_analytics_api_endpoints():
    """Test all analytics API endpoints"""
    print("\n🔍 Testing Analytics API Endpoints...")
    
    endpoints = [
        ("GET", "/analytics/metrics", "Overall metrics"),
        ("GET", "/analytics/metrics/timeseries?period=day", "Time series data"),
        ("GET", "/analytics/metrics/top-users?limit=5", "Top users"),
        ("GET", "/analytics/metrics/performance", "Performance metrics"),
        ("GET", "/analytics/events/recent?limit=10", "Recent events")
    ]
    
    all_passed = True
    
    for method, endpoint, description in endpoints:
        try:
            response = requests.request(method, f"{API_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✓ {description}: OK")
                # Print sample data for verification
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    first_key = list(data.keys())[0]
                    print(f"  Sample field: {first_key} = {data[first_key]}")
            else:
                print(f"✗ {description}: Status {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"✗ {description}: Failed - {str(e)}")
            all_passed = False
    
    return all_passed

def test_navigation_link():
    """Test that the Analytics link appears in navigation"""
    print("\n🔍 Testing Navigation Link...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
        if response.status_code == 200:
            if "Analytics" in response.text and "BarChart3" in response.text:
                print("✓ Analytics navigation link is present")
                return True
            else:
                print("✗ Analytics navigation link not found in page")
                return False
        else:
            print(f"✗ Failed to load dashboard: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to test navigation: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Analytics Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if servers are running
    if not check_frontend_running():
        print("\n❌ Frontend server is not running!")
        print("Please start it with: cd frontend && npm run dev")
        return
    
    if not check_backend_running():
        print("\n❌ Backend server is not running!")
        print("Please start it with: cd backend && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &")
        return
    
    print("\n✓ Both servers are running")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_analytics_route():
        tests_passed += 1
    
    if test_navigation_link():
        tests_passed += 1
    
    if test_analytics_api_endpoints():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Test Summary: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Analytics integration is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("\n📊 To view the Analytics dashboard:")
    print("   1. Open your browser to http://localhost:3000")
    print("   2. Click on 'Analytics' in the navigation menu")
    print("   3. You should see real-time metrics and charts")
    
    print("\n⚠️  Note: The Analytics dashboard is intended for admin users.")
    print("   Consider adding authentication/authorization in production.")

if __name__ == "__main__":
    main()