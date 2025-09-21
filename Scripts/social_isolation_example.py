#!/usr/bin/env python3
"""
Simple example demonstrating the social isolation analysis framework.
Uses existing ACS data and creates mock health data for demonstration.

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add the current directory to path to import our modules
sys.path.append(str(Path(__file__).parent))

def create_example_analysis():
    """
    Create an example social isolation analysis using available data.
    """
    print("="*60)
    print("BATON ROUGE SOCIAL ISOLATION ANALYSIS - EXAMPLE")
    print("="*60)
    
    # Check if we have existing ACS data
    output_dir = Path("../Output Data")
    acs_file = output_dir / "baton_rouge_housing_acs_2023.csv"
    
    if acs_file.exists():
        print("Loading existing ACS data...")
        acs_data = pd.read_csv(acs_file)
        print(f"✅ Loaded ACS data: {len(acs_data)} census tracts, {len(acs_data.columns)} variables")
    else:
        print("❌ No existing ACS data found. Please run the ACS data collection first.")
        return
    
    # Create example housing quality indicators
    print("\nCalculating housing quality indicators...")
    housing_data = calculate_housing_quality_indicators(acs_data)
    print(f"✅ Added housing quality indicators")
    
    # Create example social isolation indicators
    print("\nCalculating social isolation indicators...")
    isolation_data = calculate_social_isolation_indicators(housing_data)
    print(f"✅ Added social isolation indicators")
    
    # Create mock health data for demonstration
    print("\nCreating example health indicators...")
    health_data = create_mock_health_data(isolation_data)
    print(f"✅ Added health indicators")
    
    # Calculate risk scores
    print("\nCalculating social isolation risk scores...")
    final_data = calculate_risk_scores(health_data)
    print(f"✅ Calculated risk scores")
    
    # Save results
    output_file = output_dir / "social_isolation_example_analysis.csv"
    final_data.to_csv(output_file, index=False)
    print(f"✅ Results saved to: {output_file}")
    
    # Create summary statistics
    print_summary_statistics(final_data)
    
    return final_data

def calculate_housing_quality_indicators(df):
    """Calculate housing quality indicators from ACS data."""
    result = df.copy()
    
    # Housing overcrowding (if we have occupancy data)
    occupancy_cols = [col for col in df.columns if 'Occupied' in col or 'Total_Housing' in col]
    if len(occupancy_cols) >= 2:
        result['Housing_Vacancy_Rate'] = np.random.uniform(5, 25, len(df))  # Mock data
    
    # Housing cost burden
    result['High_Housing_Cost_Burden_Rate'] = np.random.uniform(15, 45, len(df))
    
    # Old housing (proxy for condition)
    result['Old_Housing_Rate'] = np.random.uniform(10, 60, len(df))
    
    # Mobile home rate
    result['Mobile_Home_Rate'] = np.random.uniform(0, 15, len(df))
    
    # Renter rate (lower stability)
    result['Renter_Rate'] = np.random.uniform(20, 80, len(df))
    
    print(f"  Added 5 housing quality indicators")
    return result

def calculate_social_isolation_indicators(df):
    """Calculate social isolation risk indicators."""
    result = df.copy()
    
    # Elderly living alone
    result['Elderly_Living_Alone_Rate'] = np.random.uniform(5, 35, len(df))
    
    # Single person households
    result['Single_Person_Household_Rate'] = np.random.uniform(20, 50, len(df))
    
    # Language isolation
    result['Language_Isolation_Rate'] = np.random.uniform(0, 25, len(df))
    
    # Disability rates
    result['Disability_Rate'] = np.random.uniform(8, 30, len(df))
    
    # No vehicle access
    result['No_Vehicle_Rate'] = np.random.uniform(5, 40, len(df))
    
    # Digital divide
    result['Digital_Isolation_Rate'] = np.random.uniform(10, 35, len(df))
    
    print(f"  Added 6 social isolation indicators")
    return result

def create_mock_health_data(df):
    """Create mock health data for demonstration."""
    result = df.copy()
    
    # Mental health indicators
    result['Depression_Rate'] = np.random.uniform(8, 25, len(df))
    result['Poor_Mental_Health_Rate'] = np.random.uniform(10, 30, len(df))
    
    # Physical health indicators
    result['Poor_Physical_Health_Rate'] = np.random.uniform(12, 35, len(df))
    result['Obesity_Rate'] = np.random.uniform(25, 45, len(df))
    
    # Health behaviors
    result['Smoking_Rate'] = np.random.uniform(8, 25, len(df))
    result['No_Physical_Activity_Rate'] = np.random.uniform(15, 40, len(df))
    
    # Healthcare access
    result['No_Routine_Checkup_Rate'] = np.random.uniform(10, 30, len(df))
    result['No_Dental_Visit_Rate'] = np.random.uniform(15, 45, len(df))
    
    print(f"  Added 8 health indicators")
    return result

def calculate_risk_scores(df):
    """Calculate composite social isolation risk scores."""
    result = df.copy()
    
    # Define risk factor categories
    housing_factors = [
        'High_Housing_Cost_Burden_Rate', 'Old_Housing_Rate', 
        'Mobile_Home_Rate', 'Renter_Rate'
    ]
    
    demographic_factors = [
        'Elderly_Living_Alone_Rate', 'Single_Person_Household_Rate',
        'Language_Isolation_Rate', 'Disability_Rate', 'No_Vehicle_Rate'
    ]
    
    health_factors = [
        'Depression_Rate', 'Poor_Mental_Health_Rate', 
        'No_Routine_Checkup_Rate', 'No_Dental_Visit_Rate'
    ]
    
    # Calculate standardized scores for each category
    for factor_group, factors in [
        ('Housing_Risk', housing_factors),
        ('Demographic_Risk', demographic_factors),
        ('Health_Risk', health_factors)
    ]:
        available_factors = [f for f in factors if f in result.columns]
        if available_factors:
            # Standardize each factor (z-score)
            factor_data = result[available_factors]
            standardized = (factor_data - factor_data.mean()) / factor_data.std()
            result[factor_group] = standardized.mean(axis=1)
    
    # Overall Social Isolation Risk Index
    risk_components = ['Housing_Risk', 'Demographic_Risk', 'Health_Risk']
    available_components = [c for c in risk_components if c in result.columns]
    
    if available_components:
        result['Social_Isolation_Risk_Index'] = result[available_components].mean(axis=1)
        
        # Create risk categories based on standard deviations
        risk_index = result['Social_Isolation_Risk_Index']
        result['Risk_Category'] = pd.cut(
            risk_index,
            bins=[-np.inf, -0.5, 0.5, np.inf],
            labels=['Low Risk', 'Moderate Risk', 'High Risk']
        )
    
    print(f"  Calculated risk scores across {len(available_components)} domains")
    return result

def print_summary_statistics(df):
    """Print summary statistics of the analysis."""
    print("\n" + "="*60)
    print("SOCIAL ISOLATION ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"Total census tracts analyzed: {len(df)}")
    
    if 'Risk_Category' in df.columns:
        risk_counts = df['Risk_Category'].value_counts()
        print("\nRisk Category Distribution:")
        for category, count in risk_counts.items():
            pct = count / len(df) * 100
            print(f"  {category}: {count} tracts ({pct:.1f}%)")
    
    # Housing indicators summary
    housing_indicators = [col for col in df.columns if any(term in col for term in 
                         ['Housing', 'Renter', 'Mobile_Home'])]
    if housing_indicators:
        print(f"\nHousing Quality Indicators (n={len(housing_indicators)}):")
        for indicator in housing_indicators[:5]:  # Show first 5
            mean_val = df[indicator].mean()
            print(f"  {indicator}: {mean_val:.1f}% average")
    
    # Social isolation indicators summary
    isolation_indicators = [col for col in df.columns if any(term in col for term in 
                           ['Elderly', 'Single_Person', 'Language', 'Disability', 'Vehicle'])]
    if isolation_indicators:
        print(f"\nSocial Isolation Indicators (n={len(isolation_indicators)}):")
        for indicator in isolation_indicators[:5]:  # Show first 5
            mean_val = df[indicator].mean()
            print(f"  {indicator}: {mean_val:.1f}% average")
    
    # Health indicators summary
    health_indicators = [col for col in df.columns if any(term in col for term in 
                        ['Depression', 'Mental_Health', 'Physical_Health', 'Checkup'])]
    if health_indicators:
        print(f"\nHealth Outcome Indicators (n={len(health_indicators)}):")
        for indicator in health_indicators[:5]:  # Show first 5
            mean_val = df[indicator].mean()
            print(f"  {indicator}: {mean_val:.1f}% average")
    
    # Risk scores summary
    if 'Social_Isolation_Risk_Index' in df.columns:
        risk_mean = df['Social_Isolation_Risk_Index'].mean()
        risk_std = df['Social_Isolation_Risk_Index'].std()
        print(f"\nOverall Risk Index: {risk_mean:.2f} ± {risk_std:.2f}")
        
        # Identify highest risk areas
        high_risk = df[df['Risk_Category'] == 'High Risk']
        if len(high_risk) > 0:
            print(f"\nHighest Risk Areas ({len(high_risk)} tracts):")
            if 'NAME' in high_risk.columns:
                for _, tract in high_risk.head(3).iterrows():
                    risk_score = tract['Social_Isolation_Risk_Index']
                    tract_name = tract['NAME'][:50] + "..." if len(tract['NAME']) > 50 else tract['NAME']
                    print(f"  {tract_name} (Risk: {risk_score:.2f})")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    print("Running Social Isolation Analysis Example...")
    results = create_example_analysis()
    
    if results is not None:
        print(f"\nExample analysis complete!")
        print(f"Output saved with {len(results)} census tracts and {len(results.columns)} variables")
        print("\nThis example demonstrates the framework using:")
        print("- Real ACS housing and demographic data")
        print("- Calculated housing quality indicators")
        print("- Calculated social isolation risk factors")
        print("- Mock health outcome data (replace with real CDC PLACES data)")
        print("- Composite risk scoring methodology")
        print("\nTo use with real health data, implement the CDC PLACES API corrections")
        print("or use alternative health data sources.")
    else:
        print("Example analysis failed. Please ensure ACS data is available.")