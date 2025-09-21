"""
Census API Test Script
Simple test to verify Census API connectivity

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import requests
api_key = 'e27fa55047fbf6a1719e8fe93b907ab8c3bd11e0'
test_url = f'https://api.census.gov/data/2022/acs/acs5?get=B01003_001E&for=state:22&key={api_key}'
print('Testing API URL:', test_url)
try:
    response = requests.get(test_url, timeout=10)
    print('Status Code:', response.status_code)
    print('Response:', response.text[:200] + '...' if len(response.text) > 200 else response.text)
except Exception as e:
    print('Error:', e)