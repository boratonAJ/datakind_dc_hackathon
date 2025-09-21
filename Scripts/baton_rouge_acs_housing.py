"""
Baton Rouge Housing ACS Data Collection and Spatial Analysis
Python version of the R script for pulling Census ACS data and performing spatial analysis

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import os
import time
import warnings
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union
import requests
from census import Census
try:
    import cenpy
    CENPY_AVAILABLE = True
except ImportError:
    CENPY_AVAILABLE = False
    print("Warning: cenpy not available. Some features may be limited.")
from shapely.geometry import Point
from shapely.ops import unary_union
import json

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class BatonRougeACSCollector:
    """Main class for collecting and processing Census ACS data for Baton Rouge."""
    
    def __init__(self, api_key: Optional[str] = None, year: int = 2023):
        """
        Initialize the ACS data collector.
        
        Args:
            api_key: Census API key (if not provided, will try environment variable)
            year: Census data year
        """
        self.year = year
        self.state_fips = "22"  # Louisiana
        self.county_fips = "033"  # East Baton Rouge Parish
        
        # Set up Census API
        if api_key is None:
            api_key = os.getenv('CENSUS_API_KEY')
        
        if api_key:
            self.census = Census(api_key)
            self.api_key = api_key
        else:
            print("Warning: No Census API key provided. Some functions may not work.")
            self.census = None
            self.api_key = None
        
        # Define CRS for spatial analysis
        self.louisiana_crs = 3452  # NAD83 / Louisiana South (feet)
        self.wgs84_crs = 4326      # WGS84
        
        # Initialize data containers
        self.raw_data = {}
        self.processed_data = {}
        
    def test_api_connection(self) -> bool:
        """Test Census API connectivity."""
        if not self.census:
            print("No Census API connection available")
            return False
            
        try:
            print("Testing Census API connectivity...")
            test_data = self.census.acs5.get('B01003_001E', geo={'for': 'state:*'}, year=self.year)
            print("API connection successful!")
            return True
        except Exception as e:
            print(f"Warning: API connection issue. Error: {e}")
            print("You may need to check your API key or try again later.")
            return False
    
    def get_variable_labels(self) -> pd.DataFrame:
        """Load ACS variable labels for reference."""
        if not CENPY_AVAILABLE:
            print("cenpy not available for variable labels")
            return pd.DataFrame()
        
        try:
            import cenpy
            variables = cenpy.remote.APIConnection("ACSDT5Y" + str(self.year))
            var_df = variables.variables
            return var_df
        except Exception as e:
            print(f"Could not load variable labels: {e}")
            return pd.DataFrame()
    
    def collect_acs_tables(self, tables: List[str], table_type: str = "dataset") -> pd.DataFrame:
        """
        Collect data from multiple ACS tables with error handling.
        
        Args:
            tables: List of ACS table codes
            table_type: Type description for logging
            
        Returns:
            Combined DataFrame with all table data
        """
        if not self.census:
            print("No Census API connection available")
            return pd.DataFrame()
        
        print(f"Fetching {table_type} data...")
        all_data = []
        
        for table in tables:
            print(f"Pulling table: {table}")
            try:
                time.sleep(1)  # Rate limiting
                
                # Get all variables for this table
                if table.startswith('S'):
                    # Subject tables - need special handling
                    data = self._collect_subject_table(table)
                elif table.startswith('DP'):
                    # Data profile tables
                    data = self._collect_data_profile_table(table)
                else:
                    # Detailed tables
                    data = self._collect_detailed_table(table)
                
                if not data.empty:
                    all_data.append(data)
                    
            except Exception as e:
                print(f"Warning: Could not fetch table {table} - Error: {e}")
                continue
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            print(f"Completed {table_type} collection: {len(combined_data)} rows")
            return combined_data
        else:
            print(f"No {table_type} data collected")
            return pd.DataFrame()
    
    def _collect_detailed_table(self, table: str) -> pd.DataFrame:
        """Collect data from a detailed table (B-series)."""
        try:
            if not CENPY_AVAILABLE:
                # Fallback to basic census library approach
                return self._collect_table_basic(table)
            
            # Get all variables for this table using cenpy
            con = cenpy.remote.APIConnection("ACSDT5Y" + str(self.year))
            variables = con.variables
            
            # Filter variables for this table
            table_vars = [var for var in variables.index if var.startswith(table + '_')]
            
            if not table_vars:
                print(f"No variables found for table {table}")
                return pd.DataFrame()
            
            # Limit to first 50 variables to avoid API limits
            table_vars = table_vars[:50]
            
            # Collect data
            data = self.census.acs5.get(
                table_vars,
                geo={'for': 'tract:*', 'in': f'state:{self.state_fips} county:{self.county_fips}'},
                year=self.year
            )
            
            df = pd.DataFrame(data)
            
            # Reshape to long format
            id_cols = ['state', 'county', 'tract']
            value_cols = [col for col in df.columns if col not in id_cols]
            
            df_long = pd.melt(df, id_vars=id_cols, value_vars=value_cols, 
                            var_name='variable', value_name='estimate')
            
            # Create GEOID
            df_long['GEOID'] = (df_long['state'] + df_long['county'] + df_long['tract'])
            df_long['NAME'] = 'Census Tract ' + df_long['tract'] + ', East Baton Rouge Parish, Louisiana'
            
            return df_long[['GEOID', 'NAME', 'variable', 'estimate']]
            
        except Exception as e:
            print(f"Error collecting detailed table {table}: {e}")
            return pd.DataFrame()
    
    def _collect_table_basic(self, table: str) -> pd.DataFrame:
        """Basic table collection using only census library."""
        try:
            # Use a predefined set of common variables for each table
            common_vars = self._get_common_variables(table)
            
            if not common_vars:
                print(f"No predefined variables for table {table}")
                return pd.DataFrame()
            
            # Collect data
            data = self.census.acs5.get(
                common_vars,
                geo={'for': 'tract:*', 'in': f'state:{self.state_fips} county:{self.county_fips}'},
                year=self.year
            )
            
            df = pd.DataFrame(data)
            
            # Reshape to long format
            id_cols = ['state', 'county', 'tract']
            value_cols = [col for col in df.columns if col not in id_cols]
            
            df_long = pd.melt(df, id_vars=id_cols, value_vars=value_cols, 
                            var_name='variable', value_name='estimate')
            
            # Create GEOID
            df_long['GEOID'] = (df_long['state'] + df_long['county'] + df_long['tract'])
            df_long['NAME'] = 'Census Tract ' + df_long['tract'] + ', East Baton Rouge Parish, Louisiana'
            
            return df_long[['GEOID', 'NAME', 'variable', 'estimate']]
            
        except Exception as e:
            print(f"Error collecting table {table}: {e}")
            return pd.DataFrame()
    
    def _get_common_variables(self, table: str) -> List[str]:
        """Get predefined common variables for tables."""
        common_table_vars = {
            'B25001': ['B25001_001'],  # Total housing units
            'B25002': ['B25002_001', 'B25002_002', 'B25002_003'],  # Occupancy status
            'B25003': ['B25003_001', 'B25003_002', 'B25003_003'],  # Tenure
            'B25077': ['B25077_001'],  # Median home value
            'B25064': ['B25064_001'],  # Median gross rent
            'B01003': ['B01003_001'],  # Total population
            'B02001': ['B02001_002', 'B02001_003', 'B02001_005'],  # Race
            'B03003': ['B03003_003'],  # Hispanic/Latino
            'B19013': ['B19013_001'],  # Median household income
            'B19001': ['B19001_002', 'B19001_003', 'B19001_004', 'B19001_005', 'B19001_006', 'B19001_007',
                      'B19001_008', 'B19001_009', 'B19001_010', 'B19001_011', 'B19001_012', 'B19001_013',
                      'B19001_014', 'B19001_015', 'B19001_016', 'B19001_017'],  # Income distribution
            'B17001': ['B17001_001', 'B17001_002', 'B17001_031'],  # Poverty status
            'B11001': ['B11001_001', 'B11001_002', 'B11001_007', 'B11001_008'],  # Household type
            'B25024': ['B25024_002', 'B25024_003', 'B25024_004', 'B25024_005', 'B25024_006', 'B25024_007',
                      'B25024_008', 'B25024_009', 'B25024_010'],  # Units in structure
            'B25034': ['B25034_002', 'B25034_003', 'B25034_004', 'B25034_005', 'B25034_006', 'B25034_007',
                      'B25034_008', 'B25034_009', 'B25034_010', 'B25034_011'],  # Year built
            'B25041': ['B25041_002', 'B25041_003', 'B25041_004', 'B25041_005', 'B25041_006', 'B25041_007']  # Bedrooms
        }
        
        return common_table_vars.get(table, [])
    
    def _collect_subject_table(self, table: str) -> pd.DataFrame:
        """Collect data from a subject table (S-series)."""
        if not CENPY_AVAILABLE:
            print(f"cenpy not available - skipping subject table {table}")
            return pd.DataFrame()
        
        try:
            # Subject tables need different handling
            con = cenpy.remote.APIConnection("ACSSDT5Y" + str(self.year))
            variables = con.variables
            
            # Filter variables for this table
            table_vars = [var for var in variables.index if var.startswith(table + '_')]
            
            if not table_vars:
                print(f"No variables found for subject table {table}")
                return pd.DataFrame()
            
            # Limit variables
            table_vars = table_vars[:50]
            
            # Use cenpy for subject tables
            data_df = con.query(
                cols=table_vars,
                geo_unit='tract',
                geo_filter={'state': self.state_fips, 'county': self.county_fips},
                year=self.year
            )
            
            if data_df.empty:
                return pd.DataFrame()
            
            # Reshape to long format
            id_cols = ['state', 'county', 'tract', 'GEOID', 'NAME']
            available_id_cols = [col for col in id_cols if col in data_df.columns]
            value_cols = [col for col in data_df.columns if col not in available_id_cols]
            
            df_long = pd.melt(data_df, id_vars=available_id_cols, value_vars=value_cols,
                            var_name='variable', value_name='estimate')
            
            # Ensure GEOID exists
            if 'GEOID' not in df_long.columns:
                if all(col in df_long.columns for col in ['state', 'county', 'tract']):
                    df_long['GEOID'] = (df_long['state'] + df_long['county'] + df_long['tract'])
            
            if 'NAME' not in df_long.columns:
                if 'tract' in df_long.columns:
                    df_long['NAME'] = 'Census Tract ' + df_long['tract'] + ', East Baton Rouge Parish, Louisiana'
            
            return df_long[['GEOID', 'NAME', 'variable', 'estimate']]
            
        except Exception as e:
            print(f"Error collecting subject table {table}: {e}")
            return pd.DataFrame()
    
    def _collect_data_profile_table(self, table: str) -> pd.DataFrame:
        """Collect data from a data profile table (DP-series)."""
        if not CENPY_AVAILABLE:
            print(f"cenpy not available - skipping data profile table {table}")
            return pd.DataFrame()
        
        try:
            # Data profile tables
            con = cenpy.remote.APIConnection("ACSDP5Y" + str(self.year))
            variables = con.variables
            
            # Filter variables for this table
            table_vars = [var for var in variables.index if var.startswith(table + '_')]
            
            if not table_vars:
                print(f"No variables found for data profile table {table}")
                return pd.DataFrame()
            
            # Limit variables
            table_vars = table_vars[:50]
            
            data_df = con.query(
                cols=table_vars,
                geo_unit='tract',
                geo_filter={'state': self.state_fips, 'county': self.county_fips},
                year=self.year
            )
            
            if data_df.empty:
                return pd.DataFrame()
            
            # Reshape to long format
            id_cols = ['state', 'county', 'tract', 'GEOID', 'NAME']
            available_id_cols = [col for col in id_cols if col in data_df.columns]
            value_cols = [col for col in data_df.columns if col not in available_id_cols]
            
            df_long = pd.melt(data_df, id_vars=available_id_cols, value_vars=value_cols,
                            var_name='variable', value_name='estimate')
            
            # Ensure GEOID exists
            if 'GEOID' not in df_long.columns:
                if all(col in df_long.columns for col in ['state', 'county', 'tract']):
                    df_long['GEOID'] = (df_long['state'] + df_long['county'] + df_long['tract'])
            
            if 'NAME' not in df_long.columns:
                if 'tract' in df_long.columns:
                    df_long['NAME'] = 'Census Tract ' + df_long['tract'] + ', East Baton Rouge Parish, Louisiana'
            
            return df_long[['GEOID', 'NAME', 'variable', 'estimate']]
            
        except Exception as e:
            print(f"Error collecting data profile table {table}: {e}")
            return pd.DataFrame()
    
    def collect_all_acs_data(self) -> Dict[str, pd.DataFrame]:
        """Collect all ACS data categories."""
        # Define table categories
        housing_tables = [
            "DP04", "B25001", "B25002", "B25003", "B25077", "B25064",
            "B25024", "B25034", "B25041", "B25040", "B25053", "B25070",
            "S2503", "S2504"
        ]
        
        demographic_tables = [
            "B01003", "B02001", "B03003"
        ]
        
        income_tables = [
            "B19013", "B19001", "B19101", "B17001", "B17017", "B25119", "DP03"
        ]
        
        household_tables = [
            "B11001", "B11005", "B11013", "B09001", "B09002", "B25115", "B08301"
        ]
        
        # Collect all data
        datasets = {}
        datasets['housing'] = self.collect_acs_tables(housing_tables, "housing")
        datasets['demographic'] = self.collect_acs_tables(demographic_tables, "demographic")
        datasets['income'] = self.collect_acs_tables(income_tables, "income")
        datasets['household'] = self.collect_acs_tables(household_tables, "household")
        
        # Store raw data
        self.raw_data = datasets
        
        return datasets
    
    def create_variable_mapping(self) -> Dict[str, str]:
        """Create mapping from ACS variables to friendly names."""
        mapping = {
            # Population and Demographics
            "B01003_001": "Total_Population",
            "B02001_002": "White_Alone",
            "B02001_003": "Black_Alone",
            "B02001_005": "Asian_Alone",
            "B03003_003": "Hispanic_Latino",
            
            # Income Variables
            "B19013_001": "Median_Household_Income",
            "B19001_002": "Income_Under_10K",
            "B19001_003": "Income_10K_15K",
            "B19001_004": "Income_15K_20K",
            "B19001_005": "Income_20K_25K",
            "B19001_006": "Income_25K_30K",
            "B19001_007": "Income_30K_35K",
            "B19001_008": "Income_35K_40K",
            "B19001_009": "Income_40K_45K",
            "B19001_010": "Income_45K_50K",
            "B19001_011": "Income_50K_60K",
            "B19001_012": "Income_60K_75K",
            "B19001_013": "Income_75K_100K",
            "B19001_014": "Income_100K_125K",
            "B19001_015": "Income_125K_150K",
            "B19001_016": "Income_150K_200K",
            "B19001_017": "Income_200K_Plus",
            
            # Family Income Distribution
            "B19101_001": "Total_Families",
            "B19101_017": "Family_Income_200K_Plus",
            
            # Poverty Status
            "B17001_001": "Total_Pop_Poverty_Status",
            "B17001_002": "Below_Poverty_Level",
            "B17001_003": "Below_Poverty_Male_Total",
            "B17001_004": "Below_Poverty_Male_Under_5",
            "B17001_005": "Below_Poverty_Male_5",
            "B17001_006": "Below_Poverty_Male_6_11",
            "B17001_007": "Below_Poverty_Male_12_14",
            "B17001_008": "Below_Poverty_Male_15",
            "B17001_009": "Below_Poverty_Male_16_17",
            "B17001_017": "Below_Poverty_Female_Total",
            "B17001_018": "Below_Poverty_Female_Under_5",
            "B17001_019": "Below_Poverty_Female_5",
            "B17001_020": "Below_Poverty_Female_6_11",
            "B17001_021": "Below_Poverty_Female_12_14",
            "B17001_022": "Below_Poverty_Female_15",
            "B17001_023": "Below_Poverty_Female_16_17",
            "B17001_031": "Above_Poverty_Level",
            
            # Poverty by Household Type
            "B17017_001": "Total_Households_Poverty_Status",
            "B17017_002": "Below_Poverty_Households",
            "B17017_010": "Above_Poverty_Households",
            
            # Income by Tenure
            "B25119_001": "Median_Household_Income_All_Tenure",
            "B25119_002": "Median_Income_Owner_Occupied",
            "B25119_003": "Median_Income_Renter_Occupied",
            
            # Household Composition
            "B11001_001": "Total_Households",
            "B11001_002": "Family_Households",
            "B11001_003": "Family_Married_Couple",
            "B11001_004": "Family_Male_No_Wife",
            "B11001_005": "Family_Female_No_Husband",
            "B11001_007": "Nonfamily_Households",
            "B11001_008": "Nonfamily_Living_Alone",
            "B11001_009": "Nonfamily_Not_Alone",
            
            # Households with Children
            "B11005_001": "Total_Households_Children_Status",
            "B11005_002": "Households_With_Children_Under_18",
            "B11005_011": "Households_No_Children_Under_18",
            
            # Children by Family Type
            "B09002_001": "Total_Own_Children_Under_18",
            "B09002_002": "Children_In_Married_Couple_Families",
            "B09002_009": "Children_In_Single_Father_Families",
            "B09002_015": "Children_In_Single_Mother_Families",
            
            # Population Under 18 by Age
            "B09001_001": "Total_Pop_Under_18",
            "B09001_002": "Pop_Under_3",
            "B09001_003": "Pop_3_4",
            "B09001_004": "Pop_5",
            "B09001_005": "Pop_6_11",
            "B09001_006": "Pop_12_14",
            "B09001_007": "Pop_15_17",
            
            # Household Size by Tenure
            "B25115_001": "Total_Occupied_Units_Size",
            "B25115_002": "Owner_1_Person",
            "B25115_003": "Owner_2_Person",
            "B25115_004": "Owner_3_Person",
            "B25115_005": "Owner_4_Person",
            "B25115_006": "Owner_5_Person",
            "B25115_007": "Owner_6_Person",
            "B25115_008": "Owner_7_Plus_Person",
            "B25115_010": "Renter_1_Person",
            "B25115_011": "Renter_2_Person",
            "B25115_012": "Renter_3_Person",
            "B25115_013": "Renter_4_Person",
            "B25115_014": "Renter_5_Person",
            "B25115_015": "Renter_6_Person",
            "B25115_016": "Renter_7_Plus_Person",
            
            # Basic Housing Units and Occupancy
            "B25001_001": "Total_Housing_Units",
            "B25002_001": "Total_Housing_Units_Check",
            "B25002_002": "Occupied_Units",
            "B25002_003": "Vacant_Units",
            
            # Tenure
            "B25003_001": "Total_Occupied_Units",
            "B25003_002": "Owner_Occupied",
            "B25003_003": "Renter_Occupied",
            
            # Housing Values and Costs
            "B25077_001": "Median_Home_Value",
            "B25064_001": "Median_Gross_Rent",
            
            # Structure Type (Units in Structure)
            "B25024_002": "Single_Family_Detached",
            "B25024_003": "Single_Family_Attached",
            "B25024_004": "Units_2",
            "B25024_005": "Units_3_4",
            "B25024_006": "Units_5_9",
            "B25024_007": "Units_10_19",
            "B25024_008": "Units_20_49",
            "B25024_009": "Units_50_Plus",
            "B25024_010": "Mobile_Home",
            "B25024_011": "Other_Housing_Type",
            
            # Year Built
            "B25034_002": "Built_2020_Later",
            "B25034_003": "Built_2010_2019",
            "B25034_004": "Built_2000_2009",
            "B25034_005": "Built_1990_1999",
            "B25034_006": "Built_1980_1989",
            "B25034_007": "Built_1970_1979",
            "B25034_008": "Built_1960_1969",
            "B25034_009": "Built_1950_1959",
            "B25034_010": "Built_1940_1949",
            "B25034_011": "Built_1939_Earlier",
            
            # Bedrooms
            "B25041_002": "No_Bedroom",
            "B25041_003": "One_Bedroom",
            "B25041_004": "Two_Bedrooms",
            "B25041_005": "Three_Bedrooms",
            "B25041_006": "Four_Bedrooms",
            "B25041_007": "Five_Plus_Bedrooms",
            
            # Owner Costs
            "B25053_002": "Owner_Costs_Under_300",
            "B25053_003": "Owner_Costs_300_599",
            "B25053_004": "Owner_Costs_600_999",
            "B25053_005": "Owner_Costs_1000_1499",
            "B25053_006": "Owner_Costs_1500_1999",
            "B25053_007": "Owner_Costs_2000_2999",
            "B25053_008": "Owner_Costs_3000_Plus",
            
            # Rent Burden
            "B25070_007": "Rent_Burden_30_34_Pct",
            "B25070_008": "Rent_Burden_35_39_Pct",
            "B25070_009": "Rent_Burden_40_49_Pct",
            "B25070_010": "Rent_Burden_50_Plus_Pct",
            
            # S2503 Financial Characteristics
            "S2503_C01_001": "S2503_Total_Occupied_Units",
            "S2503_C01_013": "S2503_Median_Household_Income",
            "S2503_C01_014": "S2503_Housing_Costs_Under_300",
            "S2503_C01_015": "S2503_Housing_Costs_300_499",
            "S2503_C01_016": "S2503_Housing_Costs_500_799",
            "S2503_C01_017": "S2503_Housing_Costs_800_999",
            "S2503_C01_018": "S2503_Housing_Costs_1000_1499",
            "S2503_C01_019": "S2503_Housing_Costs_1500_1999",
            "S2503_C01_020": "S2503_Housing_Costs_2000_2499",
            "S2503_C01_021": "S2503_Housing_Costs_2500_2999",
            "S2503_C01_022": "S2503_Housing_Costs_3000_Plus",
            "S2503_C01_024": "S2503_Median_Housing_Costs",
            "S2503_C01_028": "S2503_Cost_Burden_30_Plus_Under_20K",
            "S2503_C01_032": "S2503_Cost_Burden_30_Plus_20K_35K",
            "S2503_C01_036": "S2503_Cost_Burden_30_Plus_35K_50K",
            "S2503_C01_040": "S2503_Cost_Burden_30_Plus_50K_75K",
            "S2503_C01_044": "S2503_Cost_Burden_30_Plus_75K_Plus",
            "S2503_C03_001": "S2503_Total_Owner_Occupied",
            "S2503_C03_024": "S2503_Median_Owner_Costs",
            "S2503_C04_001": "S2503_Total_Renter_Occupied",
            "S2503_C04_024": "S2503_Median_Renter_Costs"
        }
        
        return mapping
    
    def transform_to_wide_format(self, combined_data: pd.DataFrame) -> pd.DataFrame:
        """Transform long format data to wide format with friendly names."""
        if combined_data.empty:
            return pd.DataFrame()
        
        # Get variable mapping
        base_mapping = self.create_variable_mapping()
        
        # Create mapping with 'E' suffix to match Census API returns
        variable_mapping = {}
        for var_code, friendly_name in base_mapping.items():
            # Add both with and without E suffix for compatibility
            variable_mapping[var_code] = friendly_name
            variable_mapping[var_code + 'E'] = friendly_name
        
        # Apply mapping
        combined_data['friendly_name'] = combined_data['variable'].map(variable_mapping)
        
        # Filter to only mapped variables
        mapped_data = combined_data[combined_data['friendly_name'].notna()].copy()
        
        if mapped_data.empty:
            print("Warning: No variables matched the mapping")
            return pd.DataFrame()
        
        # Convert estimates to numeric
        mapped_data['estimate'] = pd.to_numeric(mapped_data['estimate'], errors='coerce')
        
        # Pivot to wide format
        wide_data = mapped_data.pivot_table(
            index=['GEOID', 'NAME'],
            columns='friendly_name',
            values='estimate',
            aggfunc='first'
        ).reset_index()
        
        # Fill missing values with 0
        wide_data = wide_data.fillna(0)
        
        return wide_data
    
    def calculate_derived_indicators(self, wide_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate summary statistics and percentages."""
        df = wide_data.copy()
        
        # Helper function to safely divide
        def safe_divide(numerator, denominator, default=0):
            return np.where((denominator > 0) & (numerator.notna()) & (denominator.notna()), 
                          numerator / denominator * 100, default)
        
        # Population percentages
        if all(col in df.columns for col in ['White_Alone', 'Black_Alone', 'Asian_Alone', 'Hispanic_Latino', 'Total_Population']):
            df['Percent_White'] = safe_divide(df['White_Alone'], df['Total_Population'])
            df['Percent_Black'] = safe_divide(df['Black_Alone'], df['Total_Population'])
            df['Percent_Asian'] = safe_divide(df['Asian_Alone'], df['Total_Population'])
            df['Percent_Hispanic'] = safe_divide(df['Hispanic_Latino'], df['Total_Population'])
        
        # Income analysis
        income_cols = ['Income_Under_10K', 'Income_10K_15K', 'Income_15K_20K', 'Income_20K_25K', 'Income_25K_30K', 'Income_30K_35K']
        if all(col in df.columns for col in income_cols):
            df['Low_Income_Under_35K'] = df[income_cols].sum(axis=1)
        
        middle_income_cols = ['Income_35K_40K', 'Income_40K_45K', 'Income_45K_50K', 'Income_50K_60K', 'Income_60K_75K', 'Income_75K_100K']
        if all(col in df.columns for col in middle_income_cols):
            df['Middle_Income_35K_100K'] = df[middle_income_cols].sum(axis=1)
        
        high_income_cols = ['Income_100K_125K', 'Income_125K_150K', 'Income_150K_200K', 'Income_200K_Plus']
        if all(col in df.columns for col in high_income_cols):
            df['High_Income_100K_Plus'] = df[high_income_cols].sum(axis=1)
        
        if all(col in df.columns for col in ['Low_Income_Under_35K', 'High_Income_100K_Plus', 'Total_Households']):
            df['Percent_Low_Income_Under_35K'] = safe_divide(df['Low_Income_Under_35K'], df['Total_Households'])
            df['Percent_High_Income_100K_Plus'] = safe_divide(df['High_Income_100K_Plus'], df['Total_Households'])
        
        # Poverty analysis
        if all(col in df.columns for col in ['Below_Poverty_Level', 'Total_Pop_Poverty_Status']):
            df['Percent_Below_Poverty'] = safe_divide(df['Below_Poverty_Level'], df['Total_Pop_Poverty_Status'])
        
        if all(col in df.columns for col in ['Below_Poverty_Households', 'Total_Households_Poverty_Status']):
            df['Percent_Households_Below_Poverty'] = safe_divide(df['Below_Poverty_Households'], df['Total_Households_Poverty_Status'])
        
        # Children in poverty
        child_poverty_cols = ['Below_Poverty_Male_Under_5', 'Below_Poverty_Male_6_11', 'Below_Poverty_Male_12_14', 
                             'Below_Poverty_Male_15', 'Below_Poverty_Male_16_17', 'Below_Poverty_Female_Under_5',
                             'Below_Poverty_Female_6_11', 'Below_Poverty_Female_12_14', 'Below_Poverty_Female_15', 'Below_Poverty_Female_16_17']
        if all(col in df.columns for col in child_poverty_cols):
            df['Children_Below_Poverty'] = df[child_poverty_cols].sum(axis=1)
            if 'Total_Pop_Under_18' in df.columns:
                df['Percent_Children_Below_Poverty'] = safe_divide(df['Children_Below_Poverty'], df['Total_Pop_Under_18'])
        
        # Household composition analysis
        if all(col in df.columns for col in ['Family_Households', 'Total_Households']):
            df['Percent_Family_Households'] = safe_divide(df['Family_Households'], df['Total_Households'])
        
        if all(col in df.columns for col in ['Nonfamily_Living_Alone', 'Total_Households']):
            df['Percent_Single_Person_Households'] = safe_divide(df['Nonfamily_Living_Alone'], df['Total_Households'])
        
        if all(col in df.columns for col in ['Households_With_Children_Under_18', 'Total_Households_Children_Status']):
            df['Percent_Households_With_Children'] = safe_divide(df['Households_With_Children_Under_18'], df['Total_Households_Children_Status'])
        
        # Children by family structure
        if all(col in df.columns for col in ['Children_In_Married_Couple_Families', 'Total_Own_Children_Under_18']):
            df['Percent_Children_Married_Couple'] = safe_divide(df['Children_In_Married_Couple_Families'], df['Total_Own_Children_Under_18'])
        
        if all(col in df.columns for col in ['Children_In_Single_Mother_Families', 'Children_In_Single_Father_Families', 'Total_Own_Children_Under_18']):
            df['Percent_Children_Single_Parent'] = safe_divide(
                df['Children_In_Single_Mother_Families'] + df['Children_In_Single_Father_Families'], 
                df['Total_Own_Children_Under_18']
            )
        
        # Housing unit percentages
        if all(col in df.columns for col in ['Occupied_Units', 'Vacant_Units', 'Total_Housing_Units']):
            df['Percent_Occupied'] = safe_divide(df['Occupied_Units'], df['Total_Housing_Units'])
            df['Percent_Vacant'] = safe_divide(df['Vacant_Units'], df['Total_Housing_Units'])
        
        # Tenure percentages
        if all(col in df.columns for col in ['Owner_Occupied', 'Renter_Occupied', 'Total_Occupied_Units']):
            df['Percent_Owner_Occupied'] = safe_divide(df['Owner_Occupied'], df['Total_Occupied_Units'])
            df['Percent_Renter_Occupied'] = safe_divide(df['Renter_Occupied'], df['Total_Occupied_Units'])
        
        # Structure type percentages
        if all(col in df.columns for col in ['Single_Family_Detached', 'Single_Family_Attached', 'Total_Housing_Units']):
            df['Percent_Single_Family'] = safe_divide(
                df['Single_Family_Detached'] + df['Single_Family_Attached'], 
                df['Total_Housing_Units']
            )
        
        multi_family_cols = ['Units_2', 'Units_3_4', 'Units_5_9', 'Units_10_19', 'Units_20_49', 'Units_50_Plus']
        if all(col in df.columns for col in multi_family_cols + ['Total_Housing_Units']):
            df['Multi_Family_All_Units'] = df[multi_family_cols].sum(axis=1)
            df['Percent_Multi_Family_All'] = safe_divide(df['Multi_Family_All_Units'], df['Total_Housing_Units'])
        
        # Age of housing percentages
        new_housing_cols = ['Built_2020_Later', 'Built_2010_2019', 'Built_2000_2009']
        if all(col in df.columns for col in new_housing_cols + ['Total_Housing_Units']):
            df['Percent_Built_2000_Plus'] = safe_divide(df[new_housing_cols].sum(axis=1), df['Total_Housing_Units'])
        
        old_housing_cols = ['Built_1970_1979', 'Built_1960_1969', 'Built_1950_1959', 'Built_1940_1949', 'Built_1939_Earlier']
        if all(col in df.columns for col in old_housing_cols + ['Total_Housing_Units']):
            df['Percent_Built_Pre_1980'] = safe_divide(df[old_housing_cols].sum(axis=1), df['Total_Housing_Units'])
        
        # Bedroom distribution percentages
        bedroom_cols = ['Two_Bedrooms', 'Three_Bedrooms', 'Four_Bedrooms', 'Five_Plus_Bedrooms']
        if all(col in df.columns for col in bedroom_cols + ['Total_Housing_Units']):
            df['Two_Plus_Bedroom_Units'] = df[bedroom_cols].sum(axis=1)
            df['Percent_Two_Plus_Bedrooms'] = safe_divide(df['Two_Plus_Bedroom_Units'], df['Total_Housing_Units'])
        
        # Cost burden indicators
        rent_burden_cols = ['Rent_Burden_30_34_Pct', 'Rent_Burden_35_39_Pct', 'Rent_Burden_40_49_Pct', 'Rent_Burden_50_Plus_Pct']
        if all(col in df.columns for col in rent_burden_cols + ['Renter_Occupied']):
            df['High_Rent_Burden_30_Plus_Units'] = df[rent_burden_cols].sum(axis=1)
            df['High_Rent_Burden_50_Plus_Units'] = df['Rent_Burden_50_Plus_Pct']
            df['Percent_High_Rent_Burden_30_Plus'] = safe_divide(df['High_Rent_Burden_30_Plus_Units'], df['Renter_Occupied'])
            df['Percent_High_Rent_Burden_50_Plus'] = safe_divide(df['High_Rent_Burden_50_Plus_Units'], df['Renter_Occupied'])
        
        # Replace infinite values and NaN with 0
        df = df.replace([np.inf, -np.inf, np.nan], 0)
        
        return df
    
    def get_tract_geometries(self) -> gpd.GeoDataFrame:
        """Get tract geometries using cenpy or pygris."""
        try:
            print("Fetching tract geometries...")
            
            if CENPY_AVAILABLE:
                # Use cenpy to get geometries
                con = cenpy.remote.APIConnection("ACSDT5Y" + str(self.year))
                tract_shapes = con.query(
                    cols=['B01003_001'],  # Total population for basic data
                    geo_unit='tract',
                    geo_filter={'state': self.state_fips, 'county': self.county_fips},
                    return_geometry=True,
                    year=self.year
                )
            else:
                # Fallback to pygris
                print("Using pygris for tract geometries...")
                from pygris import tracts
                tract_shapes = tracts(state=self.state_fips, county=self.county_fips, year=self.year)
            
            if not tract_shapes.empty:
                # Ensure CRS is set
                if tract_shapes.crs is None:
                    tract_shapes = tract_shapes.set_crs(self.wgs84_crs)
                
                # Transform to WGS84
                tract_shapes = tract_shapes.to_crs(self.wgs84_crs)
                
                return tract_shapes[['GEOID', 'geometry']]
            else:
                print("No tract geometries found")
                return gpd.GeoDataFrame()
                
        except Exception as e:
            print(f"Error fetching tract geometries: {e}")
            return gpd.GeoDataFrame()
    
    def calculate_spatial_metrics(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Calculate spatial metrics like density."""
        if gdf.empty:
            return gdf
        
        try:
            # Transform to projected CRS for area calculations
            gdf_projected = gdf.to_crs(self.louisiana_crs)
            
            # Calculate tract areas
            gdf_projected['tract_area_sqft'] = gdf_projected.geometry.area
            gdf_projected['tract_area_sqmi'] = gdf_projected['tract_area_sqft'] / 27878400  # Convert to sq miles
            
            # Calculate density measures
            if 'Total_Housing_Units' in gdf_projected.columns:
                gdf_projected['housing_units_per_sqmi'] = gdf_projected['Total_Housing_Units'] / gdf_projected['tract_area_sqmi']
            
            if 'Occupied_Units' in gdf_projected.columns:
                gdf_projected['occupied_units_per_sqmi'] = gdf_projected['Occupied_Units'] / gdf_projected['tract_area_sqmi']
            
            if 'Total_Population' in gdf_projected.columns:
                gdf_projected['population_per_sqmi'] = gdf_projected['Total_Population'] / gdf_projected['tract_area_sqmi']
            
            # Add density categories
            if 'housing_units_per_sqmi' in gdf_projected.columns:
                gdf_projected['density_category'] = pd.cut(
                    gdf_projected['housing_units_per_sqmi'],
                    bins=[0, 500, 2000, 5000, 10000, float('inf')],
                    labels=['Very Low Density', 'Low Density', 'Medium Density', 'High Density', 'Very High Density'],
                    include_lowest=True
                )
            
            # Transform back to WGS84
            result = gdf_projected.to_crs(self.wgs84_crs)
            
            return result
            
        except Exception as e:
            print(f"Error calculating spatial metrics: {e}")
            return gdf
    
    def save_results(self, data: Union[pd.DataFrame, gpd.GeoDataFrame], 
                    output_dir: str = ".", 
                    filename_base: str = "housing_data") -> None:
        """Save results to CSV and GeoJSON files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        try:
            # Save CSV (without geometry)
            if isinstance(data, gpd.GeoDataFrame):
                csv_data = data.drop(columns='geometry')
            else:
                csv_data = data
            
            csv_filename = output_path / f"{filename_base}.csv"
            csv_data.to_csv(csv_filename, index=False)
            print(f"Saved CSV: {csv_filename}")
            
            # Save GeoJSON (if GeoDataFrame)
            if isinstance(data, gpd.GeoDataFrame) and not data.empty:
                geojson_filename = output_path / f"{filename_base}_with_geometry.geojson"
                data.to_file(geojson_filename, driver='GeoJSON')
                print(f"Saved GeoJSON: {geojson_filename}")
                
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def print_summary_stats(self, data: Union[pd.DataFrame, gpd.GeoDataFrame]) -> None:
        """Print summary statistics."""
        print("\n" + "="*60)
        print("BATON ROUGE ACS DATA SUMMARY")
        print("="*60)
        
        if data.empty:
            print("No data to summarize")
            return
        
        print(f"Data shape: {data.shape[0]} rows, {data.shape[1]} columns")
        
        # Population summary
        if 'Total_Population' in data.columns:
            total_pop = data['Total_Population'].sum()
            print(f"Total population: {total_pop:,}")
        
        # Housing summary
        if 'Total_Housing_Units' in data.columns:
            total_units = data['Total_Housing_Units'].sum()
            print(f"Total housing units: {total_units:,}")
        
        if 'Occupied_Units' in data.columns:
            occupied_units = data['Occupied_Units'].sum()
            occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0
            print(f"Occupied units: {occupied_units:,} ({occupancy_rate:.1f}%)")
        
        # Income summary
        if 'Median_Household_Income' in data.columns:
            median_income = data['Median_Household_Income'].median()
            print(f"Median household income (tract median): ${median_income:,.0f}")
        
        # Tenure summary
        if all(col in data.columns for col in ['Owner_Occupied', 'Renter_Occupied']):
            owner_pct = (data['Owner_Occupied'].sum() / (data['Owner_Occupied'].sum() + data['Renter_Occupied'].sum()) * 100)
            print(f"Owner occupancy rate: {owner_pct:.1f}%")
        
        # Density summary (if available)
        if 'housing_units_per_sqmi' in data.columns:
            avg_density = data['housing_units_per_sqmi'].mean()
            max_density = data['housing_units_per_sqmi'].max()
            print(f"Average housing density: {avg_density:.1f} units/sq mi")
            print(f"Maximum housing density: {max_density:.1f} units/sq mi")
        
        print("\nData collection and processing complete!")


def main(api_key: Optional[str] = None, 
         output_dir: str = ".", 
         year: int = 2023,
         include_spatial: bool = True) -> None:
    """
    Main function to run the complete ACS data collection and processing pipeline.
    
    Args:
        api_key: Census API key
        output_dir: Directory to save output files
        year: Census data year
        include_spatial: Whether to include spatial analysis
    """
    # Initialize collector
    collector = BatonRougeACSCollector(api_key=api_key, year=year)
    
    # Test API connection
    if not collector.test_api_connection():
        print("Cannot proceed without valid API connection")
        return
    
    # Step 1: Collect all ACS data
    print("Collecting ACS data...")
    datasets = collector.collect_all_acs_data()
    
    # Check if we have any data
    if not any(not df.empty for df in datasets.values()):
        print("No data collected. Exiting.")
        return
    
    # Step 2: Combine all datasets
    print("Combining datasets...")
    all_data = pd.concat([df for df in datasets.values() if not df.empty], ignore_index=True)
    
    # Step 3: Transform to wide format
    print("Transforming to wide format...")
    wide_data = collector.transform_to_wide_format(all_data)
    
    if wide_data.empty:
        print("No data after transformation. Check variable mappings.")
        return
    
    # Step 4: Calculate derived indicators
    print("Calculating derived indicators...")
    processed_data = collector.calculate_derived_indicators(wide_data)
    
    # Step 5: Add spatial data if requested
    if include_spatial:
        print("Adding spatial data...")
        tract_geometries = collector.get_tract_geometries()
        
        if not tract_geometries.empty:
            # Merge with geometries
            spatial_data = tract_geometries.merge(processed_data, on='GEOID', how='left')
            
            # Calculate spatial metrics
            final_data = collector.calculate_spatial_metrics(spatial_data)
        else:
            print("Could not load tract geometries, proceeding without spatial data")
            final_data = processed_data
    else:
        final_data = processed_data
    
    # Step 6: Save results
    print("Saving results...")
    collector.save_results(final_data, output_dir, "baton_rouge_housing_acs_2023")
    
    # Step 7: Print summary
    collector.print_summary_stats(final_data)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Baton Rouge ACS Housing Data Collection and Analysis")
    parser.add_argument("--api-key", help="Census API key (or set CENSUS_API_KEY environment variable)")
    parser.add_argument("--output-dir", default=".", help="Output directory for results")
    parser.add_argument("--year", type=int, default=2023, help="Census data year")
    parser.add_argument("--no-spatial", action="store_true", help="Skip spatial analysis")
    
    args = parser.parse_args()
    
    main(
        api_key=args.api_key,
        output_dir=args.output_dir,
        year=args.year,
        include_spatial=not args.no_spatial
    )