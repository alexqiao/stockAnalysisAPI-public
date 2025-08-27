#!/usr/bin/env python3
"""
Test script to verify the authentication fix
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_login():
    """Test login functionality"""
    print("Testing login...")
    login_data = {
        "username": "ccppaap",
        "password": "ccppaap123"
    }
    
    try:
        # Create a session to handle redirects and cookies
        session = requests.Session()
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        print(f"Login response status: {response.status_code}")
        
        # Check if login was successful by looking for access_token cookie in session
        cookies = session.cookies
        if 'access_token' in cookies:
            print("✓ Login successful")
            print(f"Access token cookie found")
            return session
        else:
            print("✗ Login failed - no access token cookie")
            print("Available cookies:", list(cookies.keys()))
            return None
            
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None

def test_stock_analysis(session, symbol="GOOGL"):
    """Test stock analysis with authentication"""
    print(f"\nTesting stock analysis for {symbol}...")
    
    try:
        # Use the session object which already has the cookies
        response = session.get(f"{BASE_URL}/api/analyze/{symbol}")
        print(f"Analysis response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Stock analysis successful")
            data = response.json()
            print(f"Analysis result: {data.get('analysis', {}).get('recommendation', 'N/A')}")
            return True
        else:
            print("✗ Stock analysis failed")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Stock analysis error: {e}")
        return False

def test_add_stock(session, symbol="TEST"):
    """Test adding a stock with authentication"""
    print(f"\nTesting adding stock {symbol}...")
    
    try:
        # Use the session object which already has the cookies
        data = {
            "stock_symbol": symbol
        }
        
        response = session.post(f"{BASE_URL}/api/subscribe", json=data)
        print(f"Add stock response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Add stock successful")
            return True
        elif response.status_code == 400 and "already subscribed" in response.text.lower():
            print("✓ Stock already subscribed (expected)")
            return True
        else:
            print("✗ Add stock failed")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Add stock error: {e}")
        return False

if __name__ == "__main__":
    print("Testing authentication fix for stock API...")
    print("=" * 50)
    
    # Test login
    session = test_login()
    
    if session:
        # Test stock analysis
        analysis_success = test_stock_analysis(session)
        
        # Test adding stock
        add_success = test_add_stock(session, "TEST")
        
        print("\n" + "=" * 50)
        if analysis_success and add_success:
            print("✓ All authentication tests passed!")
        else:
            print("✗ Some tests failed")
    else:
        print("✗ Login test failed - cannot proceed with other tests")
