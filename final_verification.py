#!/usr/bin/env python3
"""
Final verification that the authentication fix is working
"""
import requests
import time

BASE_URL = "http://localhost:8001"

def test_web_interface():
    """Test the web interface functionality"""
    print("Testing web interface authentication...")
    
    # Create session for cookie persistence
    session = requests.Session()
    
    # Test login
    login_data = {
        "username": "ccppaap",
        "password": "ccppaap123"
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    print(f"Login status: {response.status_code}")
    
    if response.status_code != 200 and response.status_code != 303:
        print("✗ Login failed")
        return False
    
    # Test dashboard access
    response = session.get(f"{BASE_URL}/dashboard")
    print(f"Dashboard status: {response.status_code}")
    
    if response.status_code != 200:
        print("✗ Dashboard access failed")
        return False
    
    print("✓ Web interface authentication working")
    return True

def test_api_endpoints():
    """Test API endpoints with session cookies"""
    print("\nTesting API endpoints with session authentication...")
    
    # Create session for cookie persistence
    session = requests.Session()
    
    # Login first
    login_data = {
        "username": "ccppaap",
        "password": "ccppaap123"
    }
    session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    # Test stock analysis
    response = session.get(f"{BASE_URL}/api/analyze/GOOGL")
    print(f"Stock analysis status: {response.status_code}")
    
    if response.status_code != 200:
        print("✗ Stock analysis failed")
        return False
    
    # Test stock subscription
    data = {"stock_symbol": "TEST"}
    response = session.post(f"{BASE_URL}/api/subscribe", json=data)
    print(f"Stock subscription status: {response.status_code}")
    
    if response.status_code != 200 and response.status_code != 400:
        print("✗ Stock subscription failed")
        return False
    
    print("✓ API endpoints working with session authentication")
    return True

if __name__ == "__main__":
    print("Final verification of authentication fix")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    web_success = test_web_interface()
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if web_success and api_success:
        print("✅ ALL TESTS PASSED - Authentication fix is working!")
        print("\nThe following issues have been resolved:")
        print("1. ✅ Clicking stocks no longer shows '请先登录' error")
        print("2. ✅ Adding stocks no longer shows '请先登录' error")
        print("3. ✅ Both web interface and API endpoints work with session cookies")
    else:
        print("❌ Some tests failed")
