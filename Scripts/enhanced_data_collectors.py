#!/usr/bin/env python3
"""
Enhanced Data Collectors for Social Isolation Analysis

This script provides specialized data collectors for the various data sources
identified in the social isolation analysis requirements.

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import os
import pandas as pd
import geopandas as gpd
import requests
import numpy as np
from typing import Dict, List, Optional, Tuple
import time
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')


class HealthOutcomesCollector:
    """
    Specialized collector for health outcomes data from multiple sources.
    """
    
    def __init__(self):
        self.state_code = '22'
        self.parish_code = '033'  # East Baton Rouge
        
    def collect_cdc_places_data(self, output_dir: str = "./output") -> pd.DataFrame:
        """
        Collect comprehensive health data from CDC PLACES (Population Level Analysis 
        and Community Estimations) - the successor to 500 Cities.
        
        Focuses on indicators related to social isolation and mental health.
        """
        print("Collecting CDC PLACES health data...")
        
        # CDC PLACES API endpoint
        base_url = "https://chronicdata.cdc.gov/resource/cwsq-ngmh.json"
        
        # Health measures particularly relevant to social isolation
        health_measures = {
            'DEPRESSION': 'Depression among adults aged >=18 years',
            'MHLTH': 'Mental health not good for >=14 days among adults aged >=18 years',
            'PHLTH': 'Physical health not good for >=14 days among adults aged >=18 years',
            'CSMOKING': 'Current smoking among adults aged >=18 years',
            'BINGE': 'Binge drinking among adults aged >=18 years',
            'LPA': 'No leisure-time physical activity among adults aged >=18 years',
            'OBESITY': 'Obesity among adults aged >=18 years',
            'SLEEP': 'Sleeping less than 7 hours among adults aged >=18 years',
            'CHECKUP': 'Visits to doctor for routine checkup within the past year',
            'DENTAL': 'Visits to dentist or dental clinic within the past year',
            'MAMMOUSE': 'Mammography use among women aged 50-74 years',
            'CERVICAL': 'Cervical cancer screening among women aged 21-65 years',
            'COLON_SCREEN': 'Fecal occult blood test, sigmoidoscopy, or colonoscopy',
            'HIGHCHOL': 'High cholesterol among adults aged >=18 years',
            'BPHIGH': 'High blood pressure among adults aged >=18 years',
            'DIABETES': 'Diabetes among adults aged >=18 years',
            'KIDNEY': 'Chronic kidney disease among adults aged >=18 years',
            'CHD': 'Coronary heart disease among adults aged >=18 years',
            'STROKE': 'Stroke among adults aged >=18 years',
            'COPD': 'Chronic obstructive pulmonary disease among adults aged >=18 years'
        }
        
        all_health_data = []
        
        for measure_id, description in health_measures.items():
            try:
                print(f"  Collecting {measure_id}: {description}")
                
                # Query parameters for East Baton Rouge Parish tracts
                params = {
                    '$where': f"stateabbr='LA' AND countyname='East Baton Rouge Parish' AND measureid='{measure_id}' AND datavalueunit='%'",
                    '$limit': 5000,
                    '$order': 'locationname'
                }
                
                response = requests.get(base_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        df = pd.DataFrame(data)
                        df['measure_id'] = measure_id
                        df['measure_description'] = description
                        all_health_data.append(df)
                        print(f"    ✅ Collected {len(df)} records")
                    else:
                        print(f"    ⚠️  No data found for {measure_id}")
                else:
                    print(f"    ❌ API error {response.status_code} for {measure_id}")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ Error collecting {measure_id}: {e}")
                continue
        
        if all_health_data:
            combined_data = pd.concat(all_health_data, ignore_index=True)
            
            # Clean and standardize the data
            combined_data = self._clean_places_data(combined_data)
            
            # Save raw data
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            output_file = output_path / "cdc_places_health_data.csv"
            combined_data.to_csv(output_file, index=False)
            print(f"✅ CDC PLACES data saved: {output_file}")
            
            # Create tract-level summary
            tract_summary = self._create_tract_health_summary(combined_data)
            summary_file = output_path / "tract_health_indicators.csv"
            tract_summary.to_csv(summary_file, index=False)
            print(f"✅ Tract health summary saved: {summary_file}")
            
            return combined_data
        else:
            print("❌ No CDC PLACES data collected")
            return pd.DataFrame()
    
    def _clean_places_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize CDC PLACES data."""
        if df.empty:
            return df
        
        # Extract tract GEOID from locationname
        if 'locationname' in df.columns:
            # Format: "Census Tract 1.01, East Baton Rouge Parish, Louisiana"
            df['tract_name'] = df['locationname']
            
            # Extract tract number and convert to GEOID
            tract_numbers = df['locationname'].str.extract(r'Census Tract ([\d.]+)')
            if not tract_numbers.empty:
                # Convert tract number to 6-digit format for GEOID
                df['tract_number'] = tract_numbers[0].astype(float)
                df['GEOID'] = '22033' + (df['tract_number'] * 100).astype(int).astype(str).str.zfill(6)
        
        # Clean data values
        if 'data_value' in df.columns:
            df['data_value'] = pd.to_numeric(df['data_value'], errors='coerce')
        
        # Add year information
        if 'year' not in df.columns and 'datavalueyear' in df.columns:
            df['year'] = df['datavalueyear']
        
        return df
    
    def _create_tract_health_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a wide-format summary of health indicators by tract."""
        if df.empty or 'GEOID' not in df.columns:
            return pd.DataFrame()
        
        # Pivot to wide format
        pivot_data = df.pivot_table(
            index=['GEOID', 'tract_name'],
            columns='measure_id',
            values='data_value',
            aggfunc='first'
        ).reset_index()
        
        # Add meaningful column names
        health_measures = {
            'DEPRESSION': 'Depression_Rate',
            'MHLTH': 'Poor_Mental_Health_Rate',
            'PHLTH': 'Poor_Physical_Health_Rate',
            'CSMOKING': 'Smoking_Rate',
            'BINGE': 'Binge_Drinking_Rate',
            'LPA': 'No_Physical_Activity_Rate',
            'OBESITY': 'Obesity_Rate',
            'SLEEP': 'Poor_Sleep_Rate',
            'CHECKUP': 'Routine_Checkup_Rate',
            'DENTAL': 'Dental_Visit_Rate',
            'HIGHCHOL': 'High_Cholesterol_Rate',
            'BPHIGH': 'High_Blood_Pressure_Rate',
            'DIABETES': 'Diabetes_Rate',
            'CHD': 'Heart_Disease_Rate',
            'STROKE': 'Stroke_Rate',
            'COPD': 'COPD_Rate'
        }
        
        # Rename columns to friendly names
        for old_name, new_name in health_measures.items():
            if old_name in pivot_data.columns:
                pivot_data = pivot_data.rename(columns={old_name: new_name})
        
        return pivot_data
    
    def collect_louisiana_health_data(self) -> pd.DataFrame:
        """
        Collect health data from Louisiana Department of Health sources.
        
        This would include:
        - Hospital discharge data
        - Mental health facility locations
        - Public health surveillance data
        """
        print("Collecting Louisiana Department of Health data...")
        
        # Placeholder for Louisiana-specific data sources
        # Would need to identify specific APIs or data portals
        
        # Example: Mental health facilities (if available)
        facilities_data = self._collect_mental_health_facilities()
        
        # Example: Hospital data (if available)
        hospital_data = self._collect_hospital_data()
        
        # Combine all Louisiana sources
        la_data_sources = [facilities_data, hospital_data]
        valid_sources = [df for df in la_data_sources if not df.empty]
        
        if valid_sources:
            return pd.concat(valid_sources, ignore_index=True)
        else:
            print("⚠️  No Louisiana health data sources available")
            return pd.DataFrame()
    
    def _collect_mental_health_facilities(self) -> pd.DataFrame:
        """Collect mental health facility locations."""
        # This would need specific data source
        print("  Mental health facilities collection not yet implemented")
        return pd.DataFrame()
    
    def _collect_hospital_data(self) -> pd.DataFrame:
        """Collect hospital and healthcare facility data."""
        # This could use CMS Hospital Compare or Louisiana hospital data
        print("  Hospital data collection not yet implemented")
        return pd.DataFrame()


class EnhancedCrimeAnalyzer:
    """
    Enhanced crime analysis focusing on safety and overpolicing indicators.
    """
    
    def __init__(self, municipal_collector):
        self.municipal_collector = municipal_collector
    
    def analyze_crime_patterns(self, crime_data: pd.DataFrame, 
                             tract_boundaries: gpd.GeoDataFrame = None) -> pd.DataFrame:
        """
        Analyze crime patterns for social isolation factors.
        
        Creates indicators for:
        - Crime rates by type
        - Temporal crime patterns
        - Arrest to crime ratios (overpolicing indicator)
        - Perceived safety indicators
        """
        if crime_data.empty:
            return pd.DataFrame()
        
        print("Analyzing enhanced crime patterns...")
        
        # Crime type categorization
        crime_analysis = self._categorize_crimes(crime_data)
        
        # Temporal analysis
        crime_analysis = self._analyze_temporal_patterns(crime_analysis)
        
        # Spatial aggregation to census tracts
        if tract_boundaries is not None:
            tract_crime_stats = self._aggregate_to_tracts(crime_analysis, tract_boundaries)
        else:
            tract_crime_stats = self._aggregate_to_geographic_areas(crime_analysis)
        
        return tract_crime_stats
    
    def _categorize_crimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize crimes into relevant types for social isolation analysis."""
        # This would depend on the actual crime data structure
        # Categories relevant to social isolation:
        crime_categories = {
            'violent': ['HOMICIDE', 'ROBBERY', 'ASSAULT', 'BATTERY'],
            'property': ['BURGLARY', 'THEFT', 'AUTO_THEFT', 'VANDALISM'],
            'quality_of_life': ['DRUG', 'DISTURBANCE', 'NOISE', 'VAGRANCY'],
            'traffic': ['DUI', 'TRAFFIC', 'ACCIDENT']
        }
        
        # Add crime category column
        df['crime_category'] = 'other'
        # Implementation would depend on actual crime data fields
        
        return df
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze when crimes occur (day/night, weekday/weekend)."""
        # Add temporal indicators
        if 'datetime' in df.columns:
            df['hour'] = pd.to_datetime(df['datetime']).dt.hour
            df['is_night'] = (df['hour'] < 6) | (df['hour'] >= 22)
            df['is_weekend'] = pd.to_datetime(df['datetime']).dt.weekday >= 5
        
        return df
    
    def _aggregate_to_tracts(self, crime_df: pd.DataFrame, 
                            tract_boundaries: gpd.GeoDataFrame) -> pd.DataFrame:
        """Aggregate crime statistics to census tract level."""
        # Spatial join and aggregation
        # This would require actual spatial operations
        
        # Placeholder implementation
        tract_stats = pd.DataFrame({
            'GEOID': ['22033000100'],
            'Total_Crimes': [0],
            'Violent_Crime_Rate': [0.0],
            'Property_Crime_Rate': [0.0],
            'Night_Crime_Rate': [0.0]
        })
        
        return tract_stats
    
    def _aggregate_to_geographic_areas(self, crime_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate crime data when tract boundaries aren't available."""
        # Use ZIP codes or other geographic identifiers
        print("  Geographic aggregation not yet implemented")
        return pd.DataFrame()


class EnvironmentalDataCollector:
    """
    Collector for environmental factors affecting social isolation.
    """
    
    def __init__(self):
        self.state_code = '22'
        self.parish_code = '033'
        self.council_mapper = CouncilDistrictMapper()
    
    def collect_air_quality_data(self) -> pd.DataFrame:
        """
        Collect air quality data from EPA AirNow API and other sources.
        """
        print("Collecting air quality data...")
        
        # EPA AirNow API for current air quality
        airnow_data = self._collect_airnow_data()
        
        # EPA Air Quality System (AQS) for historical data
        aqs_data = self._collect_aqs_data()
        
        return pd.concat([airnow_data, aqs_data], ignore_index=True)
    
    def _collect_airnow_data(self) -> pd.DataFrame:
        """Collect current air quality from EPA AirNow."""
        # AirNow API requires API key
        api_key = os.getenv('AIRNOW_API_KEY')
        if not api_key:
            print("  No AirNow API key found")
            return pd.DataFrame()
        
        # Implementation would use AirNow API
        print("  AirNow data collection not yet implemented")
        return pd.DataFrame()
    
    def _collect_aqs_data(self) -> pd.DataFrame:
        """Collect historical air quality from EPA AQS."""
        print("  EPA AQS data collection not yet implemented")
        return pd.DataFrame()
    
    def collect_traffic_noise_data(self) -> pd.DataFrame:
        """
        Collect traffic volume data as proxy for noise pollution.
        """
        print("Collecting traffic and noise data...")
        
        # Louisiana DOTD traffic counts
        dotd_data = self._collect_dotd_traffic_data()
        
        # OpenStreetMap highway data for noise modeling
        osm_data = self._collect_osm_highway_data()
        
        return pd.concat([dotd_data, osm_data], ignore_index=True)
    
    def _collect_dotd_traffic_data(self) -> pd.DataFrame:
        """Collect traffic count data from Louisiana DOTD."""
        print("  DOTD traffic data collection not yet implemented")
        return pd.DataFrame()
    
    def _collect_osm_highway_data(self) -> pd.DataFrame:
        """Collect highway/road data from OpenStreetMap for noise modeling."""
        print("  OpenStreetMap highway data collection not yet implemented")
        return pd.DataFrame()
    
    def collect_green_space_data(self) -> pd.DataFrame:
        """
        Collect green space and walkability data.
        """
        print("Collecting green space and walkability data...")
        
        # USGS National Land Cover Database
        nlcd_data = self._collect_nlcd_data()
        
        # Walk Score data (if available)
        walk_score_data = self._collect_walk_score_data()
        
        return pd.concat([nlcd_data, walk_score_data], ignore_index=True)
    
    def _collect_nlcd_data(self) -> pd.DataFrame:
        """Collect land cover data from USGS NLCD."""
        print("  NLCD green space data collection not yet implemented")
        return pd.DataFrame()
    
    def _collect_walk_score_data(self) -> pd.DataFrame:
        """Collect walkability scores."""
        print("  Walk Score data collection not yet implemented")
        return pd.DataFrame()


class CouncilDistrictMapper:
    """
    Creates spatial crosswalk between census tracts and Baton Rouge City Council Districts.
    """
    
    def __init__(self):
        self.city_data_portal = "https://data.brla.gov"
    
    def create_tract_council_crosswalk(self, output_dir: str = "./output") -> pd.DataFrame:
        """
        Create crosswalk between census tracts and city council districts using real data when available.
        
        Attempts to use real boundary data and falls back gracefully to enhanced templates.
        """
        print("Creating tract-to-council district crosswalk...")
        
        # Try to download real boundary data
        council_districts = self._download_council_districts()
        census_tracts = self._download_census_tracts()
        
        # Check what data we have available
        has_council_data = not council_districts.empty
        has_tract_data = not census_tracts.empty
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if has_council_data and has_tract_data:
            print("✅ Real boundary data available for both council districts and census tracts")
            crosswalk = self._create_spatial_crosswalk(census_tracts, council_districts)
            
            if not crosswalk.empty:
                crosswalk_file = output_path / "tract_council_district_crosswalk.csv"
                crosswalk.to_csv(crosswalk_file, index=False)
                print(f"✅ Real crosswalk saved: {crosswalk_file}")
                return crosswalk
            else:
                print("⚠️  Spatial join failed, falling back to enhanced template")
                
        elif has_tract_data and not has_council_data:
            print("⚠️  Census tract data available but no council district boundaries")
            print("    Creating enhanced template with real tract GEOIDs...")
            crosswalk = self._create_enhanced_template_from_tracts(census_tracts)
            
            crosswalk_file = output_path / "tract_council_district_crosswalk_enhanced_template.csv"
            crosswalk.to_csv(crosswalk_file, index=False)
            print(f"✅ Enhanced template saved: {crosswalk_file}")
            print("📝 Note: Contains real tract GEOIDs but placeholder council assignments")
            return crosswalk
            
        else:
            print("⚠️  Real boundary data not available, creating basic template...")
            crosswalk = self._create_template_crosswalk()
            
            crosswalk_file = output_path / "tract_council_district_crosswalk_template.csv"
            crosswalk.to_csv(crosswalk_file, index=False)
            print(f"✅ Template crosswalk saved: {crosswalk_file}")
            print("📝 Note: This is a basic template. Replace with actual data.")
            return crosswalk
    
    def _create_enhanced_template_from_tracts(self, tracts_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Create enhanced template using real census tract data but placeholder council districts.
        
        Args:
            tracts_gdf: Real census tract boundaries from pygris
        """
        try:
            print("  Creating enhanced template with real tract GEOIDs...")
            
            # Extract tract information
            template_data = []
            for _, tract in tracts_gdf.iterrows():
                geoid = tract.get('GEOID', tract.get('geoid', ''))
                name = tract.get('NAME', tract.get('name', f"Census Tract {geoid[-6:]}"))
                
                template_data.append({
                    'GEOID': geoid,
                    'tract_name': f"Census Tract {name}, East Baton Rouge Parish, Louisiana",
                    'council_district_id': 'TBD',
                    'council_district_name': 'To Be Determined - Use Real Boundary Data',
                    'assignment_method': 'enhanced_template',
                    'notes': 'Real tract GEOID, placeholder council assignment - requires boundary overlay'
                })
            
            # Add instruction row
            template_data.append({
                'GEOID': 'INSTRUCTIONS',
                'tract_name': 'REPLACE WITH REAL COUNCIL DISTRICT BOUNDARIES', 
                'council_district_id': '1-12',
                'council_district_name': 'Baton Rouge has 12 council districts',
                'assignment_method': 'spatial_join',
                'notes': 'Download council boundaries from data.brla.gov or contact city clerk'
            })
            
            crosswalk_df = pd.DataFrame(template_data)
            print(f"  Created enhanced template with {len(tracts_gdf)} real tract entries")
            print("  📋 Enhanced template includes:")
            print("     - Real census tract GEOIDs from Census Bureau")
            print("     - Actual tract names and boundaries")
            print("     - Placeholder council district assignments")
            print("     - Instructions for completing with boundary data")
            
            return crosswalk_df
            
        except Exception as e:
            print(f"  ❌ Error creating enhanced template: {e}")
            return pd.DataFrame()
    
    def _create_spatial_crosswalk(self, tracts_gdf: gpd.GeoDataFrame, 
                                districts_gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Create crosswalk using spatial join of real boundary data.
        
        Args:
            tracts_gdf: Census tract boundaries
            districts_gdf: Council district boundaries
        """
        try:
            print("  Performing spatial join of tract and council district boundaries...")
            
            # Ensure both datasets are in same CRS
            if tracts_gdf.crs != districts_gdf.crs:
                districts_gdf = districts_gdf.to_crs(tracts_gdf.crs)
            
            # Spatial join - assign each tract to council district
            joined = gpd.sjoin(tracts_gdf, districts_gdf, how='left', predicate='intersects')
            
            # Create crosswalk dataframe
            crosswalk_data = []
            for _, row in joined.iterrows():
                crosswalk_data.append({
                    'GEOID': row.get('GEOID', ''),
                    'tract_name': row.get('NAME', ''),
                    'council_district_id': row.get('DISTRICT', row.get('COUNCIL_DIST', 'Unknown')),
                    'council_district_name': f"Council District {row.get('DISTRICT', 'Unknown')}",
                    'assignment_method': 'spatial_join',
                    'notes': 'Assigned via spatial intersection of tract and council boundaries'
                })
            
            crosswalk_df = pd.DataFrame(crosswalk_data)
            print(f"  ✅ Spatial crosswalk created with {len(crosswalk_df)} tract assignments")
            
            return crosswalk_df
            
        except Exception as e:
            print(f"  ❌ Error creating spatial crosswalk: {e}")
            return pd.DataFrame()
    
    def _create_template_crosswalk(self) -> pd.DataFrame:
        """
        Create a template crosswalk with East Baton Rouge census tracts.
        
        This provides a starting framework that can be populated with actual
        council district assignments when boundary data becomes available.
        """
        try:
            # East Baton Rouge Parish GEOID pattern: 22033XXXXXX
            # Create template with known tract patterns
            template_tracts = []
            
            # Generate representative tract GEOIDs for East Baton Rouge
            # Format: 22033 + 6-digit tract code
            sample_tracts = [
                ("22033000100", "Census Tract 1, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033000200", "Census Tract 2, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033000300", "Census Tract 3, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033000400", "Census Tract 4, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033000500", "Census Tract 5, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033009700", "Census Tract 97, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033009800", "Census Tract 98, East Baton Rouge Parish, Louisiana", "TBD"),
                ("22033009900", "Census Tract 99, East Baton Rouge Parish, Louisiana", "TBD"),
            ]
            
            # Create template with placeholder council districts
            crosswalk_data = []
            for geoid, name, district in sample_tracts:
                crosswalk_data.append({
                    'GEOID': geoid,
                    'tract_name': name,
                    'council_district_id': district,
                    'council_district_name': f"Council District {district}" if district != "TBD" else "To Be Determined",
                    'assignment_method': 'template',
                    'notes': 'Placeholder - requires actual boundary data for assignment'
                })
            
            # Add instructions row
            crosswalk_data.append({
                'GEOID': 'INSTRUCTIONS',
                'tract_name': 'REPLACE WITH ACTUAL TRACT DATA',
                'council_district_id': '1-12',
                'council_district_name': 'Baton Rouge has 12 council districts',
                'assignment_method': 'spatial_join',
                'notes': 'Use real boundary data from data.brla.gov or similar source'
            })
            
            template_df = pd.DataFrame(crosswalk_data)
            
            print(f"  Created template with {len(template_df)-1} sample tract entries")
            print("  📋 Template includes:")
            print("     - Sample tract GEOIDs following 22033XXXXXX pattern")
            print("     - Placeholder council district assignments")
            print("     - Instructions for completing with real data")
            
            return template_df
            
        except Exception as e:
            print(f"  Error creating template crosswalk: {e}")
            return pd.DataFrame()
    
    def _download_council_districts(self) -> gpd.GeoDataFrame:
        """Download Baton Rouge City Council district boundaries."""
        print("  Attempting to download council district boundaries...")
        
        # Try multiple data sources
        data_sources = [
            {
                'name': 'Baton Rouge Open Data Portal',
                'method': self._try_brla_council_data
            },
            {
                'name': 'Louisiana Secretary of State',
                'method': self._try_sos_council_data
            },
            {
                'name': 'Census Bureau Electoral Districts',
                'method': self._try_census_electoral_data
            }
        ]
        
        for source in data_sources:
            try:
                print(f"    📡 Trying {source['name']}...")
                gdf = source['method']()
                if not gdf.empty:
                    print(f"    ✅ Successfully downloaded from {source['name']}")
                    return gdf
                else:
                    print(f"    ⚠️  No data available from {source['name']}")
            except Exception as e:
                print(f"    ❌ Error with {source['name']}: {e}")
        
        print("    📍 All data sources failed, potential manual sources:")
        potential_sources = [
            "https://data.brla.gov - Search for 'council' or 'district'", 
            "https://my.brla.gov - Open Neighborhood BR mapping portal",
            "Contact City Clerk: clerk@brgov.com for official boundaries",
            "East Baton Rouge Parish GIS Department"
        ]
        for source in potential_sources:
            print(f"       - {source}")
        
        return gpd.GeoDataFrame()
    
    def _try_brla_council_data(self) -> gpd.GeoDataFrame:
        """Try to get council district data from Baton Rouge open data."""
        # This would need the actual API endpoint - for now return empty
        # Real implementation would use Socrata API or direct shapefile download
        return gpd.GeoDataFrame()
    
    def _try_sos_council_data(self) -> gpd.GeoDataFrame:
        """Try to get council district data from Louisiana Secretary of State."""
        # Louisiana SOS sometimes has municipal electoral districts
        return gpd.GeoDataFrame()
    
    def _try_census_electoral_data(self) -> gpd.GeoDataFrame:
        """Try to get council district data from Census Bureau."""
        try:
            import pygris
            # Try to get voting districts which sometimes include city council
            # This is a long shot but worth trying
            voting_districts = pygris.voting_districts(state="22", county="033", year=2020)
            if not voting_districts.empty:
                # Would need to filter for city council districts specifically
                print("      Found voting districts, but need to filter for city council")
            return gpd.GeoDataFrame()
        except:
            return gpd.GeoDataFrame()
    
    def _download_census_tracts(self) -> gpd.GeoDataFrame:
        """Download census tract boundaries for East Baton Rouge Parish."""
        print("  Downloading census tract boundaries from Census Bureau...")
        
        try:
            import pygris
            
            # Download census tracts for East Baton Rouge Parish (FIPS: 22033)
            # State 22 = Louisiana, County 033 = East Baton Rouge Parish
            tracts_gdf = pygris.tracts(
                state="22", 
                county="033", 
                year=2020,
                cb=True  # Use cartographic boundary files (smaller, simplified)
            )
            
            print(f"    ✅ Downloaded {len(tracts_gdf)} census tracts")
            print(f"    📍 Coverage: East Baton Rouge Parish, Louisiana")
            
            # Ensure we have the GEOID column and geometry
            if 'GEOID' not in tracts_gdf.columns:
                print("    ⚠️  No GEOID column found, checking alternatives...")
                geoid_cols = [col for col in tracts_gdf.columns if 'geoid' in col.lower()]
                if geoid_cols:
                    tracts_gdf = tracts_gdf.rename(columns={geoid_cols[0]: 'GEOID'})
                    print(f"    ✅ Using {geoid_cols[0]} as GEOID")
            
            return tracts_gdf
            
        except ImportError:
            print("    ❌ pygris not available - install with: pip install pygris")
            return gpd.GeoDataFrame()
        except Exception as e:
            print(f"    ❌ Error downloading census tracts: {e}")
            print("    📍 Fallback options:")
            print("       - Manual download from Census TIGER/Line")
            print("       - Use Census API with geometry=True")
            return gpd.GeoDataFrame()
    
    def _spatial_join_tracts_districts(self, tracts: gpd.GeoDataFrame, 
                                     districts: gpd.GeoDataFrame) -> pd.DataFrame:
        """Perform spatial join between tracts and council districts."""
        # Spatial overlay to determine which district each tract is in
        try:
            # Use geopandas overlay or sjoin
            crosswalk = gpd.sjoin(tracts, districts, how='left', predicate='intersects')
            
            # Calculate intersection areas for tracts that span multiple districts
            # Keep the district with the largest intersection area
            
            return crosswalk[['GEOID', 'district_id', 'district_name']].drop_duplicates()
        except Exception as e:
            print(f"  Error in spatial join: {e}")
            return pd.DataFrame()


def main():
    """Demonstrate the enhanced data collectors."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Data Collection for Social Isolation Analysis')
    parser.add_argument('--output-dir', default='./output', help='Output directory')
    parser.add_argument('--health-only', action='store_true', help='Collect only health data')
    parser.add_argument('--crime-only', action='store_true', help='Analyze only crime data')
    parser.add_argument('--env-only', action='store_true', help='Collect only environmental data')
    
    args = parser.parse_args()
    
    if args.health_only or not any([args.crime_only, args.env_only]):
        print("Collecting health outcomes data...")
        health_collector = HealthOutcomesCollector()
        health_data = health_collector.collect_cdc_places_data(args.output_dir)
        print(f"Health data collection complete: {len(health_data)} records")
    
    if args.crime_only:
        print("Crime analysis would require existing crime data...")
    
    if args.env_only:
        print("Collecting environmental data...")
        env_collector = EnvironmentalDataCollector()
        air_quality = env_collector.collect_air_quality_data()
        traffic_noise = env_collector.collect_traffic_noise_data()
        green_space = env_collector.collect_green_space_data()
        print("Environmental data collection complete")
    
    # Council district crosswalk
    print("Creating council district crosswalk...")
    council_mapper = CouncilDistrictMapper()
    crosswalk = council_mapper.create_tract_council_crosswalk(args.output_dir)
    print(f"Crosswalk creation complete: {len(crosswalk)} mappings")


if __name__ == "__main__":
    main()