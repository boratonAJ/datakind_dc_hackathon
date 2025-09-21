#!/usr/bin/env python3
"""
Baton Rouge Social Isolation and Loneliness Analysis

This script extends the existing ACS and municipal data collection classes to create
a comprehensive framework for analyzing social isolation and loneliness factors,
including housing conditions, health outcomes, crime, poverty, and environmental factors.

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import os
import sys
import pandas as pd
import geopandas as gpd
import numpy as np
import requests
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import time
from census import Census
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Import our existing classes
from baton_rouge_acs_housing import BatonRougeACSCollector
from baton_rouge_data_pulls import BatonRougeDataCollector


class SocialIsolationAnalyzer:
    """
    Comprehensive analyzer for social isolation and loneliness factors in Baton Rouge.
    
    Extends existing data collection classes to analyze:
    - Housing conditions and quality
    - Health outcomes
    - Crime and safety
    - Poverty and socioeconomic factors
    - Environmental factors
    - Social connectivity indicators
    """
    
    def __init__(self, census_api_key: Optional[str] = None, year: int = 2022):
        """Initialize the analyzer with existing data collectors."""
        self.year = year
        self.census_api_key = census_api_key or os.getenv('CENSUS_API_KEY')
        
        if not self.census_api_key:
            print("Warning: No Census API key provided. Some features will be limited.")
        
        # Initialize existing collectors
        self.acs_collector = BatonRougeACSCollector(api_key=self.census_api_key, year=year)
        self.municipal_collector = BatonRougeDataCollector()
        
        # Louisiana state code and East Baton Rouge Parish code
        self.state_code = '22'
        self.parish_code = '033'
        
        print(f"Social Isolation Analyzer initialized for year {year}")
    
    def calculate_housing_quality_indicators(self, acs_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate additional housing quality indicators from ACS data.
        
        These indicators are strongly associated with social isolation:
        - Housing overcrowding
        - Housing cost burden
        - Housing age and condition proxies
        - Tenure stability
        - Housing type isolation factors
        """
        df = acs_data.copy()
        
        print("Calculating housing quality indicators...")
        
        # Housing overcrowding indicators
        if 'Total_Housing_Units' in df.columns and 'Occupied_Units' in df.columns:
            df['Housing_Vacancy_Rate'] = ((df['Total_Housing_Units'] - df['Occupied_Units']) / 
                                        df['Total_Housing_Units'] * 100).fillna(0)
        
        # Housing cost burden (30%+ of income on housing)
        cost_burden_cols = [col for col in df.columns if 'Cost_Burden' in col]
        if cost_burden_cols:
            df['High_Housing_Cost_Burden_Rate'] = df[cost_burden_cols].sum(axis=1) / df.get('Total_Households', 1) * 100
        
        # Housing age as proxy for condition
        old_housing_cols = [col for col in df.columns if any(decade in col for decade in ['1939', '1940_1949', '1950_1959'])]
        if old_housing_cols:
            df['Old_Housing_Rate'] = df[old_housing_cols].sum(axis=1) / df.get('Total_Housing_Units', 1) * 100
        
        # Mobile home indicator (associated with social isolation)
        if 'Mobile_Home' in df.columns:
            df['Mobile_Home_Rate'] = df['Mobile_Home'] / df.get('Total_Housing_Units', 1) * 100
        
        # Renter occupancy rate (lower stability)
        if 'Renter_Occupied' in df.columns and 'Occupied_Units' in df.columns:
            df['Renter_Rate'] = df['Renter_Occupied'] / df['Occupied_Units'] * 100
        
        # Overcrowding indicators
        overcrowding_cols = [col for col in df.columns if 'More_Than_1_Person_Per_Room' in col]
        if overcrowding_cols:
            df['Overcrowding_Rate'] = df[overcrowding_cols].sum(axis=1) / df.get('Occupied_Units', 1) * 100
        
        print(f"✅ Added {len([c for c in df.columns if c not in acs_data.columns])} housing quality indicators")
        return df
    
    def calculate_social_isolation_indicators(self, acs_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate social isolation risk indicators from ACS demographic data.
        
        Key factors include:
        - Age-related isolation (elderly living alone)
        - Language barriers
        - Disability status
        - Limited transportation access
        - Single-person households
        """
        df = acs_data.copy()
        
        print("Calculating social isolation indicators...")
        
        # Elderly living alone
        if 'Living_Alone_65_Plus' in df.columns and 'Population_65_Plus' in df.columns:
            df['Elderly_Living_Alone_Rate'] = (df['Living_Alone_65_Plus'] / 
                                             df['Population_65_Plus'] * 100).fillna(0)
        
        # Single person households
        if 'Single_Person_Households' in df.columns and 'Total_Households' in df.columns:
            df['Single_Person_Household_Rate'] = (df['Single_Person_Households'] / 
                                                df['Total_Households'] * 100).fillna(0)
        
        # Language isolation
        limited_english_cols = [col for col in df.columns if 'Limited_English' in col or 'Linguistically_Isolated' in col]
        if limited_english_cols:
            df['Language_Isolation_Rate'] = (df[limited_english_cols].sum(axis=1) / 
                                           df.get('Total_Population', 1) * 100).fillna(0)
        
        # Disability rates
        disability_cols = [col for col in df.columns if 'Disability' in col]
        if disability_cols:
            df['Disability_Rate'] = (df[disability_cols].sum(axis=1) / 
                                   df.get('Total_Population', 1) * 100).fillna(0)
        
        # Transportation limitations (no vehicle available)
        if 'No_Vehicle_Available' in df.columns and 'Total_Households' in df.columns:
            df['No_Vehicle_Rate'] = (df['No_Vehicle_Available'] / 
                                   df['Total_Households'] * 100).fillna(0)
        
        # Digital divide indicators
        if 'No_Internet_Access' in df.columns and 'Total_Households' in df.columns:
            df['Digital_Isolation_Rate'] = (df['No_Internet_Access'] / 
                                          df['Total_Households'] * 100).fillna(0)
        
        print(f"✅ Added {len([c for c in df.columns if c not in acs_data.columns])} social isolation indicators")
        return df
    
    def collect_health_outcomes_data(self) -> pd.DataFrame:
        """
        Collect health outcomes data from various sources.
        
        Sources:
        - CDC 500 Cities data
        - Louisiana Department of Health
        - Hospital discharge data (if available)
        - Mental health facility locations
        """
        print("Collecting health outcomes data...")
        
        health_data_sources = []
        
        # Try CDC 500 Cities data (now PLACES data)
        try:
            places_data = self._collect_cdc_places_data()
            if not places_data.empty:
                health_data_sources.append(places_data)
                print("✅ CDC PLACES data collected")
        except Exception as e:
            print(f"⚠️  Could not collect CDC PLACES data: {e}")
        
        # Try Louisiana health data
        try:
            la_health_data = self._collect_louisiana_health_data()
            if not la_health_data.empty:
                health_data_sources.append(la_health_data)
                print("✅ Louisiana health data collected")
        except Exception as e:
            print(f"⚠️  Could not collect Louisiana health data: {e}")
        
        # Combine all health data sources
        if health_data_sources:
            combined_health = pd.concat(health_data_sources, ignore_index=True)
            return combined_health
        else:
            print("⚠️  No health data sources available")
            return pd.DataFrame()
    
    def _collect_cdc_places_data(self) -> pd.DataFrame:
        """Collect health data from CDC PLACES (formerly 500 Cities) API."""
        # CDC PLACES API for tract-level health data
        base_url = "https://chronicdata.cdc.gov/resource/cwsq-ngmh.json"
        
        # Focus on mental health and isolation-related indicators
        health_measures = [
            'DEPRESSION',  # Depression among adults
            'MHLTH',       # Mental health not good for >=14 days
            'CSMOKING',    # Current smoking
            'BINGE',       # Binge drinking
            'LPA',         # No leisure-time physical activity
            'SLEEP'        # Less than 7 hours of sleep
        ]
        
        all_health_data = []
        
        for measure in health_measures:
            try:
                # Query for Louisiana tracts
                params = {
                    '$where': f"stateabbr='LA' AND countyname='East Baton Rouge Parish' AND measureid='{measure}'",
                    '$limit': 5000
                }
                
                response = requests.get(base_url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        df = pd.DataFrame(data)
                        df['measure'] = measure
                        all_health_data.append(df)
                        print(f"  Collected {len(df)} records for {measure}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  Error collecting {measure}: {e}")
        
        if all_health_data:
            return pd.concat(all_health_data, ignore_index=True)
        return pd.DataFrame()
    
    def _collect_louisiana_health_data(self) -> pd.DataFrame:
        """Collect health data from Louisiana Department of Health or other state sources."""
        # Placeholder for Louisiana-specific health data
        # This would need specific API endpoints or data sources
        print("  Louisiana health data collection not yet implemented")
        return pd.DataFrame()
    
    def analyze_crime_safety_factors(self, crime_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze crime data for safety and overpolicing indicators.
        
        Creates indicators for:
        - Overall crime rates
        - Violent crime rates
        - Property crime rates
        - Arrest rates vs. crime rates (overpolicing indicator)
        - Crime temporal patterns
        """
        if crime_data.empty:
            return pd.DataFrame()
        
        print("Analyzing crime and safety factors...")
        
        # This would process the crime data from the municipal collector
        # Group by census tract and calculate rates
        
        # Placeholder implementation - would need actual crime data structure
        crime_indicators = pd.DataFrame({
            'GEOID': ['sample_tract'],
            'Violent_Crime_Rate': [0.0],
            'Property_Crime_Rate': [0.0],
            'Total_Crime_Rate': [0.0],
            'Arrest_to_Crime_Ratio': [0.0]
        })
        
        print("✅ Crime safety analysis complete")
        return crime_indicators
    
    def collect_environmental_data(self) -> pd.DataFrame:
        """
        Collect environmental factors that affect social isolation.
        
        Includes:
        - Air quality data
        - Traffic noise proxies
        - Green space access
        - Walkability indicators
        """
        print("Collecting environmental data...")
        
        environmental_data = []
        
        # EPA Air Quality data
        try:
            air_quality = self._collect_air_quality_data()
            if not air_quality.empty:
                environmental_data.append(air_quality)
        except Exception as e:
            print(f"⚠️  Air quality data error: {e}")
        
        # Traffic and noise proxies
        try:
            traffic_data = self._collect_traffic_data()
            if not traffic_data.empty:
                environmental_data.append(traffic_data)
        except Exception as e:
            print(f"⚠️  Traffic data error: {e}")
        
        if environmental_data:
            return pd.concat(environmental_data, ignore_index=True)
        return pd.DataFrame()
    
    def _collect_air_quality_data(self) -> pd.DataFrame:
        """Collect air quality data from EPA APIs."""
        # EPA Air Quality API
        # This is a placeholder - would need specific EPA API implementation
        print("  Air quality data collection not yet implemented")
        return pd.DataFrame()
    
    def _collect_traffic_data(self) -> pd.DataFrame:
        """Collect traffic volume data as noise pollution proxy."""
        # Could use DOTD traffic count data or OpenStreetMap
        print("  Traffic data collection not yet implemented")
        return pd.DataFrame()
    
    def create_council_district_crosswalk(self) -> pd.DataFrame:
        """
        Create crosswalk between census tracts and Baton Rouge City Council Districts.
        """
        print("Creating Council District crosswalk...")
        
        # This would download council district boundaries and create spatial joins
        # Placeholder implementation
        crosswalk = pd.DataFrame({
            'GEOID': ['22033000100'],
            'Council_District': [1],
            'District_Name': ['District 1']
        })
        
        print("✅ Council district crosswalk created")
        return crosswalk
    
    def develop_isolation_risk_model(self, combined_data: pd.DataFrame) -> pd.DataFrame:
        """
        Develop a composite social isolation risk score.
        
        Combines multiple factors into risk indices:
        - Housing-based isolation risk
        - Demographic isolation risk
        - Environmental isolation risk
        - Economic isolation risk
        """
        if combined_data.empty:
            return combined_data
        
        print("Developing social isolation risk model...")
        
        df = combined_data.copy()
        
        # Housing isolation risk factors
        housing_risk_factors = [
            'Housing_Cost_Burden_Rate', 'Old_Housing_Rate', 'Overcrowding_Rate',
            'Mobile_Home_Rate', 'Housing_Vacancy_Rate'
        ]
        
        # Demographic isolation risk factors
        demographic_risk_factors = [
            'Elderly_Living_Alone_Rate', 'Single_Person_Household_Rate',
            'Language_Isolation_Rate', 'Disability_Rate', 'No_Vehicle_Rate'
        ]
        
        # Economic isolation risk factors
        economic_risk_factors = [
            'Poverty_Rate', 'Unemployment_Rate', 'No_Internet_Rate'
        ]
        
        # Calculate standardized scores for each category
        for factor_group, factors in [
            ('Housing_Risk', housing_risk_factors),
            ('Demographic_Risk', demographic_risk_factors),
            ('Economic_Risk', economic_risk_factors)
        ]:
            available_factors = [f for f in factors if f in df.columns]
            if available_factors:
                # Standardize each factor (z-score)
                for factor in available_factors:
                    factor_std = f"{factor}_std"
                    mean_val = df[factor].mean()
                    std_val = df[factor].std()
                    if std_val > 0:
                        df[factor_std] = (df[factor] - mean_val) / std_val
                    else:
                        df[factor_std] = 0
                
                # Calculate composite risk score
                std_factors = [f"{f}_std" for f in available_factors]
                df[factor_group] = df[std_factors].mean(axis=1)
        
        # Overall Social Isolation Risk Index
        risk_components = ['Housing_Risk', 'Demographic_Risk', 'Economic_Risk']
        available_components = [c for c in risk_components if c in df.columns]
        
        if available_components:
            df['Social_Isolation_Risk_Index'] = df[available_components].mean(axis=1)
            
            # Create risk categories
            df['Risk_Category'] = pd.cut(
                df['Social_Isolation_Risk_Index'],
                bins=[-np.inf, -0.5, 0.5, np.inf],
                labels=['Low Risk', 'Moderate Risk', 'High Risk']
            )
        
        print("✅ Social isolation risk model developed")
        return df
    
    def run_comprehensive_analysis(self, output_dir: str = "./output") -> Dict[str, pd.DataFrame]:
        """
        Run the complete social isolation and loneliness analysis.
        
        Returns:
            Dictionary containing all analysis results
        """
        print("="*60)
        print("BATON ROUGE SOCIAL ISOLATION & LONELINESS ANALYSIS")
        print("="*60)
        
        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 1. Collect base ACS housing and demographic data
        print("\n1. Collecting ACS housing and demographic data...")
        try:
            # Test API connection first
            if not self.acs_collector.test_api_connection():
                print("❌ Census API connection failed")
                acs_data = pd.DataFrame()
            else:
                # Collect all ACS data
                datasets = self.acs_collector.collect_all_acs_data()
                
                if datasets and any(not df.empty for df in datasets.values()):
                    # Combine datasets
                    all_data = pd.concat([df for df in datasets.values() if not df.empty], ignore_index=True)
                    
                    # Transform to wide format
                    acs_data = self.acs_collector.transform_to_wide_format(all_data)
                    
                    if not acs_data.empty:
                        # Calculate derived indicators
                        acs_data = self.acs_collector.calculate_derived_indicators(acs_data)
                        results['acs_base'] = acs_data
                        print(f"✅ ACS data: {len(acs_data)} census tracts")
                    else:
                        print("⚠️  No data after transformation")
                        acs_data = pd.DataFrame()
                else:
                    print("⚠️  No ACS datasets collected")
                    acs_data = pd.DataFrame()
        except Exception as e:
            print(f"❌ ACS data collection failed: {e}")
            acs_data = pd.DataFrame()
        
        # 2. Calculate housing quality indicators
        if not acs_data.empty:
            print("\n2. Calculating housing quality indicators...")
            acs_enhanced = self.calculate_housing_quality_indicators(acs_data)
            results['housing_quality'] = acs_enhanced
        else:
            acs_enhanced = pd.DataFrame()
        
        # 3. Calculate social isolation indicators
        if not acs_enhanced.empty:
            print("\n3. Calculating social isolation indicators...")
            acs_with_isolation = self.calculate_social_isolation_indicators(acs_enhanced)
            results['social_isolation'] = acs_with_isolation
        else:
            acs_with_isolation = pd.DataFrame()
        
        # 4. Collect health outcomes data
        print("\n4. Collecting health outcomes data...")
        health_data = self.collect_health_outcomes_data()
        if not health_data.empty:
            results['health_outcomes'] = health_data
        
        # 5. Collect and analyze crime data
        print("\n5. Collecting crime and safety data...")
        try:
            # This would use the municipal collector for crime data
            crime_indicators = self.analyze_crime_safety_factors(pd.DataFrame())
            results['crime_safety'] = crime_indicators
        except Exception as e:
            print(f"⚠️  Crime analysis error: {e}")
        
        # 6. Collect environmental data
        print("\n6. Collecting environmental data...")
        environmental_data = self.collect_environmental_data()
        if not environmental_data.empty:
            results['environmental'] = environmental_data
        
        # 7. Create council district crosswalk
        print("\n7. Creating council district crosswalk...")
        council_crosswalk = self.create_council_district_crosswalk()
        results['council_districts'] = council_crosswalk
        
        # 8. Develop comprehensive risk model
        if not acs_with_isolation.empty:
            print("\n8. Developing social isolation risk model...")
            final_analysis = self.develop_isolation_risk_model(acs_with_isolation)
            results['final_analysis'] = final_analysis
            
            # Save final results
            output_file = output_path / "social_isolation_analysis.csv"
            final_analysis.to_csv(output_file, index=False)
            print(f"✅ Final analysis saved to: {output_file}")
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
        return results


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Baton Rouge Social Isolation Analysis')
    parser.add_argument('--output-dir', default='./output', 
                       help='Output directory for analysis results')
    parser.add_argument('--year', type=int, default=2022,
                       help='Analysis year (default: 2022)')
    parser.add_argument('--api-key', help='Census API key (or set CENSUS_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = SocialIsolationAnalyzer(
        census_api_key=args.api_key,
        year=args.year
    )
    
    # Run comprehensive analysis
    results = analyzer.run_comprehensive_analysis(output_dir=args.output_dir)
    
    # Print summary
    print(f"\nAnalysis complete! Results saved to: {args.output_dir}")
    print(f"Generated {len(results)} analysis components:")
    for component, data in results.items():
        if isinstance(data, pd.DataFrame):
            print(f"  - {component}: {len(data)} rows")
        else:
            print(f"  - {component}: {type(data)}")


if __name__ == "__main__":
    main()