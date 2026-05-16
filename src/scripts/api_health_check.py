#!/usr/bin/env python
"""Health check script - single ping to API health endpoint"""
import os
import sys
import requests

API_URL = os.getenv("API_URL", "")

def check_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ {response.json()}")
            return True
        else:
            print(f"❌ Status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ {e}")
        return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)