#!/usr/bin/env python3
"""
Baton Rouge Social Isolation & Loneliness Analysis Framework
Unified Main Controller for Comprehensive Analysis

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC

This is the main framework that integrates all existing components into a 
comprehensive social isolation and loneliness analysis system for Baton Rouge.

Components Integrated:
- Census ACS Housing & Demographics (BatonRougeACSCollector)
- Municipal Data (BatonRougeDataCollector) 
- Health Outcomes (HealthOutcomesCollector)
- Environmental Factors (EnvironmentalDataCollector)
- Crime & Safety Analysis (EnhancedCrimeAnalyzer)
- Spatial Analysis (CouncilDistrictMapper)
- Social Isolation Analysis (SocialIsolationAnalyzer)

Author: GitHub Copilot
Date: September 2025
"""

import os
import sys
import pandas as pd
import geopandas as gpd
import numpy as np
import json
import warnings
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import time
from datetime import datetime
import argparse
warnings.filterwarnings('ignore')

# Import all existing components with error handling
try:
    from baton_rouge_acs_housing import BatonRougeACSCollector
    ACS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ACS Housing module not available: {e}")
    ACS_AVAILABLE = False

try:
    from baton_rouge_data_pulls import BatonRougeDataCollector
    MUNICIPAL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Municipal data module not available: {e}")
    MUNICIPAL_AVAILABLE = False

try:
    from social_isolation_analyzer import SocialIsolationAnalyzer
    ISOLATION_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Social isolation analyzer not available: {e}")
    ISOLATION_ANALYZER_AVAILABLE = False

try:
    from enhanced_data_collectors import (
        HealthOutcomesCollector,
        EnvironmentalDataCollector,
        EnhancedCrimeAnalyzer,
        CouncilDistrictMapper
    )
    ENHANCED_COLLECTORS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Enhanced data collectors not available: {e}")
    ENHANCED_COLLECTORS_AVAILABLE = False


class BatonRougeSocialIsolationFramework:
    """
    Unified framework for comprehensive social isolation and loneliness analysis.
    
    This main controller class orchestrates all data collection, analysis, and
    reporting components to provide a complete picture of social isolation
    factors in Baton Rouge.
    """
    
    def __init__(self, 
                 census_api_key: Optional[str] = None,
                 airnow_api_key: Optional[str] = None,
                 year: int = 2023,
                 output_dir: str = "./social_isolation_analysis",
                 config_file: Optional[str] = None):
        """
        Initialize the comprehensive social isolation analysis framework.
        
        Args:
            census_api_key: Census Bureau API key
            airnow_api_key: AirNow API key for environmental data
            year: Analysis year
            output_dir: Base output directory for all results
            config_file: Optional JSON configuration file
        """
        print("=" * 70)
        print("🏠 BATON ROUGE SOCIAL ISOLATION & LONELINESS ANALYSIS FRAMEWORK")
        print("=" * 70)
        print(f"📊 Analysis Year: {year}")
        print(f"📁 Output Directory: {output_dir}")
        
        # Load configuration
        self.config = self._load_configuration(config_file)
        
        # Core parameters
        self.year = year
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # API keys
        self.census_api_key = census_api_key or os.getenv('CENSUS_API_KEY')
        self.airnow_api_key = airnow_api_key or os.getenv('AIRNOW_API_KEY')
        
        # Initialize all data collectors
        self._initialize_collectors()
        
        # Analysis state tracking
        self.collected_data = {}
        self.analysis_results = {}
        self.spatial_data = {}
        
        print("✅ Framework initialized successfully")
        
    def _load_configuration(self, config_file: Optional[str]) -> Dict:
        """Load configuration from JSON file or use defaults."""
        default_config = {
            "data_sources": {
                "census_acs": True,
                "municipal_data": True,
                "health_outcomes": True,
                "environmental_data": True,
                "crime_analysis": True,
                "spatial_crosswalks": True
            },
            "analysis_options": {
                "include_spatial": True,
                "calculate_risk_scores": True,
                "create_composite_indices": True,
                "generate_visualizations": False,
                "save_intermediate_results": True
            },
            "geographic_scope": {
                "state_fips": "22",
                "county_fips": "033",
                "parish_name": "East Baton Rouge Parish"
            },
            "output_formats": ["csv", "geojson"],
            "processing_options": {
                "max_rows_per_dataset": 50000,
                "spatial_analysis": True,
                "verbose_logging": True
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                default_config.update(user_config)
                print(f"📋 Loaded configuration from: {config_file}")
            except Exception as e:
                print(f"⚠️  Error loading config file: {e}, using defaults")
        
        return default_config
    
    def _initialize_collectors(self) -> None:
        """Initialize all data collection components."""
        print("\n🔧 Initializing data collectors...")
        
        try:
            # Core ACS data collector
            if ACS_AVAILABLE:
                self.acs_collector = BatonRougeACSCollector(
                    api_key=self.census_api_key, 
                    year=self.year
                )
                print("  ✅ Census ACS collector initialized")
            else:
                self.acs_collector = None
                print("  ⚠️  Census ACS collector not available")
            
            # Municipal data collector  
            if MUNICIPAL_AVAILABLE:
                self.municipal_collector = BatonRougeDataCollector(
                    max_rows=self.config["processing_options"]["max_rows_per_dataset"]
                )
                print("  ✅ Municipal data collector initialized")
            else:
                self.municipal_collector = None
                print("  ⚠️  Municipal data collector not available")
            
            # Social isolation analyzer (main analysis engine)
            if ISOLATION_ANALYZER_AVAILABLE:
                self.isolation_analyzer = SocialIsolationAnalyzer(
                    census_api_key=self.census_api_key,
                    year=self.year
                )
                print("  ✅ Social isolation analyzer initialized")
            else:
                self.isolation_analyzer = None
                print("  ⚠️  Social isolation analyzer not available")
            
            # Enhanced data collectors
            if ENHANCED_COLLECTORS_AVAILABLE:
                self.health_collector = HealthOutcomesCollector()
                print("  ✅ Health outcomes collector initialized")
                
                self.environmental_collector = EnvironmentalDataCollector()
                print("  ✅ Environmental data collector initialized")
                
                self.crime_analyzer = EnhancedCrimeAnalyzer(self.municipal_collector)
                print("  ✅ Crime analyzer initialized")
                
                self.spatial_mapper = CouncilDistrictMapper()
                print("  ✅ Spatial mapper initialized")
            else:
                self.health_collector = None
                self.environmental_collector = None
                self.crime_analyzer = None
                self.spatial_mapper = None
                print("  ⚠️  Enhanced data collectors not available")
            
        except Exception as e:
            print(f"❌ Error initializing collectors: {e}")
            raise
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Run the complete social isolation analysis workflow.
        
        Returns:
            Dictionary containing all analysis results and data
        """
        print("\n🚀 STARTING COMPREHENSIVE SOCIAL ISOLATION ANALYSIS")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            # Phase 1: Data Collection
            self._collect_all_data()
            
            # Phase 2: Spatial Analysis
            self._perform_spatial_analysis()
            
            # Phase 3: Social Isolation Analysis
            self._analyze_social_isolation()
            
            # Phase 4: Generate Results and Reports
            self._generate_final_results()
            
            # Phase 5: Save All Results
            self._save_comprehensive_results()
            
            elapsed_time = time.time() - start_time
            print(f"\n✅ ANALYSIS COMPLETE! Total time: {elapsed_time:.1f} seconds")
            
            return self._create_results_summary()
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {e}")
            raise
    
    def _collect_all_data(self) -> None:
        """Phase 1: Collect data from all sources."""
        print("\n📊 PHASE 1: DATA COLLECTION")
        print("-" * 50)
        
        # Census ACS Data
        if self.config["data_sources"]["census_acs"] and self.acs_collector:
            print("\n🏠 Collecting Census ACS housing and demographic data...")
            try:
                acs_datasets = self.acs_collector.collect_all_acs_data()
                combined_acs = self.acs_collector.combine_all_datasets(acs_datasets)
                self.collected_data['acs_data'] = combined_acs
                print(f"  ✅ ACS data: {len(combined_acs)} census tracts")
            except Exception as e:
                print(f"  ❌ ACS collection error: {e}")
                self.collected_data['acs_data'] = pd.DataFrame()
        elif self.config["data_sources"]["census_acs"]:
            print("\n⚠️  Census ACS collection requested but collector not available")
            self.collected_data['acs_data'] = pd.DataFrame()
        
        # Municipal Data
        if self.config["data_sources"]["municipal_data"] and self.municipal_collector:
            print("\n🏛️  Collecting municipal data (blight, permits, crime)...")
            try:
                municipal_datasets = self.municipal_collector.collect_all_datasets()
                cleaned_municipal = self.municipal_collector.filter_and_clean_data(municipal_datasets)
                self.collected_data['municipal_data'] = cleaned_municipal
                print(f"  ✅ Municipal data: {len(cleaned_municipal)} datasets")
            except Exception as e:
                print(f"  ❌ Municipal collection error: {e}")
                self.collected_data['municipal_data'] = {}
        elif self.config["data_sources"]["municipal_data"]:
            print("\n⚠️  Municipal data collection requested but collector not available")
            self.collected_data['municipal_data'] = {}
        
        # Health Outcomes Data
        if self.config["data_sources"]["health_outcomes"] and self.health_collector:
            print("\n🏥 Collecting health outcomes data...")
            try:
                health_data = self.health_collector.collect_cdc_places_data(
                    str(self.output_dir / "health")
                )
                self.collected_data['health_data'] = health_data
                print(f"  ✅ Health data: {len(health_data)} records")
            except Exception as e:
                print(f"  ❌ Health collection error: {e}")
                self.collected_data['health_data'] = pd.DataFrame()
        elif self.config["data_sources"]["health_outcomes"]:
            print("\n⚠️  Health outcomes collection requested but collector not available")
            self.collected_data['health_data'] = pd.DataFrame()
        
        # Environmental Data
        if self.config["data_sources"]["environmental_data"] and self.environmental_collector:
            print("\n🌍 Collecting environmental data...")
            try:
                air_quality = self.environmental_collector.collect_air_quality_data()
                noise_data = self.environmental_collector.collect_traffic_noise_data()
                green_space = self.environmental_collector.collect_green_space_data()
                
                self.collected_data['environmental_data'] = {
                    'air_quality': air_quality,
                    'noise': noise_data,
                    'green_space': green_space
                }
                total_env_records = sum(len(df) for df in self.collected_data['environmental_data'].values() if not df.empty)
                print(f"  ✅ Environmental data: {total_env_records} total records")
            except Exception as e:
                print(f"  ❌ Environmental collection error: {e}")
                self.collected_data['environmental_data'] = {}
        elif self.config["data_sources"]["environmental_data"]:
            print("\n⚠️  Environmental data collection requested but collector not available")
            self.collected_data['environmental_data'] = {}
        
        # Crime Analysis
        if self.config["data_sources"]["crime_analysis"] and self.crime_analyzer:
            print("\n🚔 Analyzing crime and safety data...")
            try:
                # Note: Crime analysis uses existing municipal data
                if 'municipal_data' in self.collected_data and 'Crime' in self.collected_data['municipal_data']:
                    crime_analysis = self.crime_analyzer.analyze_crime_patterns(
                        self.collected_data['municipal_data']['Crime']
                    )
                    self.collected_data['crime_analysis'] = crime_analysis
                    print(f"  ✅ Crime analysis: {len(crime_analysis)} tract-level records")
                else:
                    print("  ⚠️  No crime data available for analysis")
                    self.collected_data['crime_analysis'] = pd.DataFrame()
            except Exception as e:
                print(f"  ❌ Crime analysis error: {e}")
                self.collected_data['crime_analysis'] = pd.DataFrame()
        elif self.config["data_sources"]["crime_analysis"]:
            print("\n⚠️  Crime analysis requested but analyzer not available")
            self.collected_data['crime_analysis'] = pd.DataFrame()
    
    def _perform_spatial_analysis(self) -> None:
        """Phase 2: Perform spatial analysis and create geographic crosswalks."""
        print("\n🗺️  PHASE 2: SPATIAL ANALYSIS")
        print("-" * 50)
        
        if self.config["data_sources"]["spatial_crosswalks"] and self.spatial_mapper:
            print("\n📍 Creating spatial crosswalks...")
            try:
                # Create tract-to-council district crosswalk
                crosswalk = self.spatial_mapper.create_tract_council_crosswalk(
                    str(self.output_dir / "spatial")
                )
                self.spatial_data['tract_council_crosswalk'] = crosswalk
                print(f"  ✅ Tract-council crosswalk: {len(crosswalk)} mappings")
                
                # Get tract geometries if spatial analysis enabled
                if self.config["analysis_options"]["include_spatial"] and self.acs_collector:
                    if not self.collected_data.get('acs_data', pd.DataFrame()).empty:
                        tract_geometries = self.acs_collector.get_tract_geometries()
                        self.spatial_data['tract_geometries'] = tract_geometries
                        print(f"  ✅ Tract geometries: {len(tract_geometries)} boundaries")
                
            except Exception as e:
                print(f"  ❌ Spatial analysis error: {e}")
        elif self.config["data_sources"]["spatial_crosswalks"]:
            print("\n⚠️  Spatial crosswalks requested but spatial mapper not available")
    
    def _analyze_social_isolation(self) -> None:
        """Phase 3: Perform comprehensive social isolation analysis."""
        print("\n🔍 PHASE 3: SOCIAL ISOLATION ANALYSIS")
        print("-" * 50)
        
        acs_data = self.collected_data.get('acs_data', pd.DataFrame())
        
        if not acs_data.empty and self.isolation_analyzer:
            print("\n📊 Calculating social isolation indicators...")
            try:
                # Housing quality indicators
                housing_indicators = self.isolation_analyzer.calculate_housing_quality_indicators(acs_data)
                self.analysis_results['housing_indicators'] = housing_indicators
                print(f"  ✅ Housing indicators: {len(housing_indicators)} tracts")
                
                # Social isolation indicators
                isolation_indicators = self.isolation_analyzer.calculate_social_isolation_indicators(acs_data)
                self.analysis_results['isolation_indicators'] = isolation_indicators
                print(f"  ✅ Isolation indicators: {len(isolation_indicators)} tracts")
                
                # Calculate risk scores if enabled
                if self.config["analysis_options"]["calculate_risk_scores"]:
                    risk_scores = self.isolation_analyzer.calculate_risk_scores(isolation_indicators)
                    self.analysis_results['risk_scores'] = risk_scores
                    print(f"  ✅ Risk scores: {len(risk_scores)} tracts")
                
                # Create composite indices if enabled
                if self.config["analysis_options"]["create_composite_indices"]:
                    composite_data = pd.merge(
                        housing_indicators, 
                        isolation_indicators, 
                        on='GEOID', 
                        how='outer'
                    )
                    
                    # Add health data if available
                    health_data = self.collected_data.get('health_data', pd.DataFrame())
                    if not health_data.empty:
                        composite_data = pd.merge(
                            composite_data,
                            health_data,
                            left_on='GEOID',
                            right_on='LocationName',
                            how='left'
                        )
                    
                    self.analysis_results['composite_analysis'] = composite_data
                    print(f"  ✅ Composite analysis: {len(composite_data)} tracts")
                
            except Exception as e:
                print(f"  ❌ Social isolation analysis error: {e}")
        elif acs_data.empty:
            print("\n⚠️  No ACS data available for social isolation analysis")
        elif not self.isolation_analyzer:
            print("\n⚠️  Social isolation analysis requested but analyzer not available")
    
    def _generate_final_results(self) -> None:
        """Phase 4: Generate final analysis results and summaries."""
        print("\n📋 PHASE 4: GENERATING FINAL RESULTS")
        print("-" * 50)
        
        try:
            # Create comprehensive summary
            self._create_comprehensive_summary()
            
            # Generate policy recommendations
            self._generate_policy_recommendations()
            
            # Create data quality report
            self._create_data_quality_report()
            
        except Exception as e:
            print(f"  ❌ Results generation error: {e}")
    
    def _create_comprehensive_summary(self) -> None:
        """Create a comprehensive summary of all analyses."""
        print("\n📊 Creating comprehensive summary...")
        
        try:
            summary_stats = {
                'analysis_date': datetime.now().isoformat(),
                'analysis_year': self.year,
                'geographic_scope': self.config["geographic_scope"],
                'data_sources_used': {},
                'tract_coverage': {},
                'key_findings': {}
            }
            
            # Data source summary
            for source, data in self.collected_data.items():
                if isinstance(data, pd.DataFrame):
                    summary_stats['data_sources_used'][source] = {
                        'records': len(data),
                        'columns': len(data.columns) if not data.empty else 0
                    }
                elif isinstance(data, dict):
                    summary_stats['data_sources_used'][source] = {
                        'datasets': len(data),
                        'total_records': sum(len(df) for df in data.values() if isinstance(df, pd.DataFrame))
                    }
            
            # Analysis results summary
            for analysis, results in self.analysis_results.items():
                if isinstance(results, pd.DataFrame) and not results.empty:
                    summary_stats['tract_coverage'][analysis] = len(results)
            
            self.analysis_results['comprehensive_summary'] = summary_stats
            print("  ✅ Comprehensive summary created")
            
        except Exception as e:
            print(f"  ❌ Summary creation error: {e}")
    
    def _generate_policy_recommendations(self) -> None:
        """Generate policy recommendations based on analysis results."""
        print("\n🏛️  Generating policy recommendations...")
        
        try:
            recommendations = {
                'high_priority_areas': [],
                'intervention_strategies': [],
                'data_gaps': [],
                'next_steps': []
            }
            
            # Identify high-risk areas
            if 'risk_scores' in self.analysis_results:
                risk_data = self.analysis_results['risk_scores']
                if not risk_data.empty and 'composite_risk_score' in risk_data.columns:
                    high_risk_tracts = risk_data[
                        risk_data['composite_risk_score'] > risk_data['composite_risk_score'].quantile(0.75)
                    ]
                    recommendations['high_priority_areas'] = high_risk_tracts['GEOID'].tolist()
            
            # Data gaps analysis
            for source, data in self.collected_data.items():
                if isinstance(data, pd.DataFrame) and data.empty:
                    recommendations['data_gaps'].append(source)
                elif isinstance(data, dict) and not data:
                    recommendations['data_gaps'].append(source)
            
            # Standard recommendations
            recommendations['intervention_strategies'] = [
                "Improve housing quality in high-risk census tracts",
                "Expand public transportation in isolated areas", 
                "Increase community center and social service accessibility",
                "Address environmental health concerns",
                "Enhance neighborhood safety and lighting"
            ]
            
            recommendations['next_steps'] = [
                "Validate findings with community stakeholders",
                "Develop tract-specific intervention plans",
                "Establish baseline metrics for tracking progress",
                "Secure funding for priority interventions"
            ]
            
            self.analysis_results['policy_recommendations'] = recommendations
            print("  ✅ Policy recommendations generated")
            
        except Exception as e:
            print(f"  ❌ Policy recommendations error: {e}")
    
    def _create_data_quality_report(self) -> None:
        """Create a data quality and completeness report."""
        print("\n🔍 Creating data quality report...")
        
        try:
            quality_report = {
                'data_completeness': {},
                'missing_data_analysis': {},
                'data_source_reliability': {},
                'recommendations': []
            }
            
            # Analyze data completeness
            for source, data in self.collected_data.items():
                if isinstance(data, pd.DataFrame):
                    if not data.empty:
                        completeness = (1 - data.isnull().sum() / len(data)).to_dict()
                        quality_report['data_completeness'][source] = completeness
                    else:
                        quality_report['missing_data_analysis'][source] = "No data collected"
                elif isinstance(data, dict):
                    for subsource, subdata in data.items():
                        if isinstance(subdata, pd.DataFrame) and not subdata.empty:
                            completeness = (1 - subdata.isnull().sum() / len(subdata)).to_dict()
                            quality_report['data_completeness'][f"{source}_{subsource}"] = completeness
            
            # Add quality recommendations
            quality_report['recommendations'] = [
                "Validate API connections for failed data sources",
                "Implement data validation checks",
                "Establish regular data refresh schedules",
                "Create backup data sources for critical indicators"
            ]
            
            self.analysis_results['data_quality_report'] = quality_report
            print("  ✅ Data quality report created")
            
        except Exception as e:
            print(f"  ❌ Data quality report error: {e}")
    
    def _save_comprehensive_results(self) -> None:
        """Phase 5: Save all results to files."""
        print("\n💾 PHASE 5: SAVING RESULTS")
        print("-" * 50)
        
        try:
            # Create output subdirectories
            data_dir = self.output_dir / "data"
            analysis_dir = self.output_dir / "analysis"
            spatial_dir = self.output_dir / "spatial"
            reports_dir = self.output_dir / "reports"
            
            for directory in [data_dir, analysis_dir, spatial_dir, reports_dir]:
                directory.mkdir(exist_ok=True)
            
            # Save collected data
            print("\n💾 Saving collected data...")
            for source, data in self.collected_data.items():
                if isinstance(data, pd.DataFrame) and not data.empty:
                    filepath = data_dir / f"{source}.csv"
                    data.to_csv(filepath, index=False)
                    print(f"  ✅ Saved: {filepath}")
                elif isinstance(data, dict):
                    for subsource, subdata in data.items():
                        if isinstance(subdata, pd.DataFrame) and not subdata.empty:
                            filepath = data_dir / f"{source}_{subsource}.csv"
                            subdata.to_csv(filepath, index=False)
                            print(f"  ✅ Saved: {filepath}")
            
            # Save analysis results
            print("\n📊 Saving analysis results...")
            for analysis, results in self.analysis_results.items():
                if isinstance(results, pd.DataFrame) and not results.empty:
                    filepath = analysis_dir / f"{analysis}.csv"
                    results.to_csv(filepath, index=False)
                    print(f"  ✅ Saved: {filepath}")
                elif isinstance(results, dict):
                    filepath = reports_dir / f"{analysis}.json"
                    with open(filepath, 'w') as f:
                        json.dump(results, f, indent=2, default=str)
                    print(f"  ✅ Saved: {filepath}")
            
            # Save spatial data
            print("\n🗺️  Saving spatial data...")
            for spatial_name, spatial_data in self.spatial_data.items():
                if isinstance(spatial_data, (pd.DataFrame, gpd.GeoDataFrame)) and not spatial_data.empty:
                    # Save as CSV
                    csv_path = spatial_dir / f"{spatial_name}.csv"
                    spatial_data.to_csv(csv_path, index=False)
                    print(f"  ✅ Saved: {csv_path}")
                    
                    # Save as GeoJSON if it's a GeoDataFrame
                    if isinstance(spatial_data, gpd.GeoDataFrame):
                        geojson_path = spatial_dir / f"{spatial_name}.geojson"
                        spatial_data.to_file(geojson_path, driver='GeoJSON')
                        print(f"  ✅ Saved: {geojson_path}")
            
            # Create master results file
            master_results = self._create_results_summary()
            master_path = self.output_dir / "MASTER_ANALYSIS_RESULTS.json"
            with open(master_path, 'w') as f:
                json.dump(master_results, f, indent=2, default=str)
            print(f"\n🎯 Master results saved: {master_path}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def _create_results_summary(self) -> Dict[str, Any]:
        """Create a comprehensive summary of all results."""
        return {
            'framework_info': {
                'analysis_date': datetime.now().isoformat(),
                'analysis_year': self.year,
                'output_directory': str(self.output_dir),
                'configuration': self.config
            },
            'data_collection_summary': {
                source: {
                    'collected': not (data.empty if isinstance(data, pd.DataFrame) else not bool(data)),
                    'record_count': len(data) if isinstance(data, pd.DataFrame) else 
                                  sum(len(df) for df in data.values() if isinstance(df, pd.DataFrame)) if isinstance(data, dict) else 0
                }
                for source, data in self.collected_data.items()
            },
            'analysis_summary': {
                analysis: {
                    'completed': not (results.empty if isinstance(results, pd.DataFrame) else not bool(results)),
                    'record_count': len(results) if isinstance(results, pd.DataFrame) else 1 if results else 0
                }
                for analysis, results in self.analysis_results.items()
            },
            'spatial_analysis_summary': {
                spatial_name: {
                    'created': not spatial_data.empty if hasattr(spatial_data, 'empty') else bool(spatial_data),
                    'record_count': len(spatial_data) if hasattr(spatial_data, '__len__') else 0
                }
                for spatial_name, spatial_data in self.spatial_data.items()
            }
        }


def create_default_config(config_path: str) -> None:
    """Create a default configuration file."""
    default_config = {
        "data_sources": {
            "census_acs": True,
            "municipal_data": True,
            "health_outcomes": True,
            "environmental_data": True,
            "crime_analysis": True,
            "spatial_crosswalks": True
        },
        "analysis_options": {
            "include_spatial": True,
            "calculate_risk_scores": True,
            "create_composite_indices": True,
            "generate_visualizations": False,
            "save_intermediate_results": True
        },
        "geographic_scope": {
            "state_fips": "22",
            "county_fips": "033", 
            "parish_name": "East Baton Rouge Parish"
        },
        "output_formats": ["csv", "geojson"],
        "processing_options": {
            "max_rows_per_dataset": 50000,
            "spatial_analysis": True,
            "verbose_logging": True
        }
    }
    
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=2)
    print(f"✅ Default configuration created: {config_path}")


def main():
    """Main execution function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Baton Rouge Social Isolation & Loneliness Analysis Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete analysis with all data sources
  python baton_rouge_social_isolation_framework.py --output-dir ./analysis_2023

  # Run analysis with specific year and custom config
  python baton_rouge_social_isolation_framework.py --year 2022 --config config.json
  
  # Generate default configuration file
  python baton_rouge_social_isolation_framework.py --create-config config.json
        """
    )
    
    parser.add_argument('--output-dir', default='./social_isolation_analysis',
                       help='Output directory for analysis results')
    parser.add_argument('--year', type=int, default=2023,
                       help='Analysis year (default: 2023)')
    parser.add_argument('--census-api-key', 
                       help='Census API key (or set CENSUS_API_KEY env var)')
    parser.add_argument('--airnow-api-key',
                       help='AirNow API key (or set AIRNOW_API_KEY env var)')
    parser.add_argument('--config', 
                       help='Path to JSON configuration file')
    parser.add_argument('--create-config',
                       help='Create default configuration file and exit')
    
    args = parser.parse_args()
    
    # Create default config if requested
    if args.create_config:
        create_default_config(args.create_config)
        return
    
    try:
        # Initialize framework
        framework = BatonRougeSocialIsolationFramework(
            census_api_key=args.census_api_key,
            airnow_api_key=args.airnow_api_key,
            year=args.year,
            output_dir=args.output_dir,
            config_file=args.config
        )
        
        # Run comprehensive analysis
        results = framework.run_comprehensive_analysis()
        
        # Print final summary
        print("\n" + "=" * 70)
        print("🎉 ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📁 Results saved to: {args.output_dir}")
        print(f"📊 Data sources collected: {len([k for k, v in results['data_collection_summary'].items() if v['collected']])}")
        print(f"🔍 Analyses completed: {len([k for k, v in results['analysis_summary'].items() if v['completed']])}")
        print("\n📋 Key Output Files:")
        print(f"  - Master Results: {args.output_dir}/MASTER_ANALYSIS_RESULTS.json")
        print(f"  - Analysis Data: {args.output_dir}/analysis/")
        print(f"  - Collected Data: {args.output_dir}/data/")
        print(f"  - Spatial Data: {args.output_dir}/spatial/")
        print(f"  - Reports: {args.output_dir}/reports/")
        
    except Exception as e:
        print(f"\n❌ Framework execution error: {e}")
        raise


if __name__ == "__main__":
    main()