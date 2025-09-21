#!/usr/bin/env python3
"""
Debug CDC PLACES API to fix the query parameters.

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import requests
import pandas as pd

# Test the CDC PLACES API with different query approaches
base_url = "https://chronicdata.cdc.gov/resource/cwsq-ngmh.json"

# First, let's see what data is available
print("Testing CDC PLACES API...")

# Simple query to see data structure
try:
    print("1. Testing basic query...")
    response = requests.get(f"{base_url}?$limit=5", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"Found {len(data)} records")
            print("Sample record keys:", list(data[0].keys()))
            print("Sample record:", data[0])
        else:
            print("No data returned")
    else:
        print(f"Error response: {response.text[:200]}")
    
    print("\n" + "="*50)
    
    # Test Louisiana-specific query
    print("2. Testing Louisiana query...")
    params = {
        '$where': "stateabbr='LA'",
        '$limit': 5
    }
    response = requests.get(base_url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"Found {len(data)} Louisiana records")
            print("Sample Louisiana record:", data[0])
        else:
            print("No Louisiana data found")
    
    print("\n" + "="*50)
    
    # Test East Baton Rouge specific query
    print("3. Testing East Baton Rouge query...")
    params = {
        '$where': "stateabbr='LA' AND countyname LIKE '%East Baton Rouge%'",
        '$limit': 10
    }
    response = requests.get(base_url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"Found {len(data)} East Baton Rouge records")
            # Check available measures
            measures = set(record.get('measureid', 'N/A') for record in data)
            print(f"Available measures: {sorted(measures)}")
            print("Sample record:", data[0])
        else:
            print("No East Baton Rouge data found")
    
    print("\n" + "="*50)
    
    # Test specific measure query
    print("4. Testing specific measure query...")
    params = {
        '$where': "stateabbr='LA' AND measureid='DEPRESSION'",
        '$limit': 5
    }
    response = requests.get(base_url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"Found {len(data)} DEPRESSION records")
            print("Sample depression record:", data[0])
        else:
            print("No DEPRESSION data found")
    
except Exception as e:
    print(f"Error: {e}")