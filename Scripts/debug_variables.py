#!/usr/bin/env python3
"""
Debug Census Variables
Test script to examine available census variables

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import os
from census import Census

# Test to see what variables we actually get
api_key = os.getenv('CENSUS_API_KEY', 'e27fa55047fbf6a1719e8fe93b907ab8c3bd11e0')
c = Census(api_key)

# Get a small sample and see the column names
try:
    data = c.acs5.get('B01003_001E', geo={'for': 'tract:*', 'in': 'state:22 county:033'}, year=2022)
    print("Sample data columns:", data[0].keys() if data else "No data")
    
    # Try with multiple variables
    data2 = c.acs5.get(['B01003_001E', 'B25001_001E'], geo={'for': 'tract:*', 'in': 'state:22 county:033'}, year=2022)
    print("Multi-variable columns:", data2[0].keys() if data2 else "No data")
    print("First row sample:", data2[0] if data2 else "No data")
    
except Exception as e:
    print(f"Error: {e}")