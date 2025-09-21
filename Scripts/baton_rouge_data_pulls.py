"""
Baton Rouge Multi-Dataset Collection and Spatial Analysis
Python version of the R script for pulling blight, building permit, and crime data from BR Open Data Portal

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import pandas as pd
import requests
import geopandas as gpd
import time
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Tuple
import warnings
from shapely.geometry import Point
from shapely.ops import unary_union
import census
from pygris import tracts, zctas

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class BatonRougeDataCollector:
    """Main class for collecting and processing Baton Rouge municipal data."""
    
    def __init__(self, max_rows: int = 50000, batch_limit: int = 1000):
        """
        Initialize the data collector.
        
        Args:
            max_rows: Maximum number of rows to collect per dataset
            batch_limit: Number of rows to fetch per API batch
        """
        self.max_rows = max_rows
        self.batch_limit = batch_limit
        
        # API endpoints
        self.api_endpoints = {
            'blight': "https://data.brla.gov/resource/7ixm-mnvx.csv",
            'permits': "https://data.brla.gov/resource/7fq7-8j7r.csv",
            'crime': "https://data.brla.gov/resource/6zc2-imdr.csv"
        }
        
        # Louisiana FIPS: 22, East Baton Rouge Parish FIPS: 033
        self.state_fips = "22"
        self.county_fips = "033"
    
    def collect_api_data(self, base_url: str, dataset_name: str = "dataset") -> pd.DataFrame:
        """
        Generic function to collect data from API with pagination.
        
        Args:
            base_url: Base URL for the API endpoint
            dataset_name: Name of the dataset for logging
            
        Returns:
            DataFrame containing collected data
        """
        print(f"Collecting {dataset_name} data from API...")
        
        # Initialize variables
        offset = 0
        limit = self.batch_limit
        all_data = []
        more_data = True
        total_rows = 0
        
        # Download data in batches
        while more_data and total_rows < self.max_rows:
            # Calculate batch size for this iteration
            batch_size = min(limit, self.max_rows - total_rows)
            if batch_size <= 0:
                break
            
            # Construct URL with pagination
            url = f"{base_url}?$limit={batch_size}&$offset={offset}"
            
            try:
                # Make API request
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Read CSV data
                from io import StringIO
                data = pd.read_csv(StringIO(response.text))
                
                # Append to main dataset
                if len(data) > 0:
                    all_data.append(data)
                    total_rows += len(data)
                    offset += batch_size
                    
                    # Check if we've reached end of dataset
                    if len(data) < batch_size:
                        more_data = False
                else:
                    more_data = False
                    
            except requests.RequestException as e:
                print(f"Error downloading {dataset_name} data: {e}")
                break
            
            # Rate limiting
            time.sleep(0.5)
            
            # Progress update
            if total_rows % 5000 == 0:
                print(f"Downloaded {total_rows} {dataset_name} rows")
        
        # Combine all data
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
        else:
            result = pd.DataFrame()
        
        print(f"Completed {dataset_name} collection: {len(result)} rows")
        return result
    
    def collect_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Collect data from all API endpoints.
        
        Returns:
            Dictionary containing all collected datasets
        """
        datasets = {}
        
        for name, url in self.api_endpoints.items():
            datasets[name] = self.collect_api_data(url, name)
        
        return datasets
    
    def filter_and_clean_data(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Filter and clean the collected datasets.
        
        Args:
            datasets: Dictionary of raw datasets
            
        Returns:
            Dictionary of cleaned datasets
        """
        cleaned_datasets = {}
        
        # Filter and clean blight data
        if 'blight' in datasets and not datasets['blight'].empty:
            blight = datasets['blight']
            if 'parenttype' in blight.columns:
                blight_filtered = blight[blight['parenttype'] == "BLIGHTED PROPERTIES"]
            else:
                blight_filtered = blight
            
            # Filter for valid coordinates
            if 'longitude' in blight_filtered.columns and 'latitude' in blight_filtered.columns:
                blight_clean = blight_filtered.dropna(subset=['longitude', 'latitude'])
                blight_clean = blight_clean.copy()
                blight_clean['dataset_type'] = 'blight'
                cleaned_datasets['blight'] = blight_clean
        
        # Clean permits data (assuming it has coordinate columns)
        if 'permits' in datasets and not datasets['permits'].empty:
            permits = datasets['permits']
            if 'longitude' in permits.columns and 'latitude' in permits.columns:
                permits_clean = permits.dropna(subset=['longitude', 'latitude'])
                permits_clean = permits_clean.copy()
                permits_clean['dataset_type'] = 'permits'
                cleaned_datasets['permits'] = permits_clean
        
        # Clean crime data
        if 'crime' in datasets and not datasets['crime'].empty:
            crime = datasets['crime']
            if 'longitude' in crime.columns and 'latitude' in crime.columns:
                crime_clean = crime.dropna(subset=['longitude', 'latitude'])
                crime_clean = crime_clean.copy()
                crime_clean['dataset_type'] = 'crime'
                cleaned_datasets['crime'] = crime_clean
        
        return cleaned_datasets
    
    def load_spatial_reference_data(self) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
        """
        Load spatial reference data (census tracts and ZIP codes).
        
        Returns:
            Tuple of (census_tracts, zip_codes) GeoDataFrames
        """
        print("\nDownloading spatial reference data...")
        
        try:
            # Download census tract data for East Baton Rouge Parish
            census_tracts = tracts(state=self.state_fips, county=self.county_fips, 
                                 cb=True, year=2020)
            
            # Download ZIP code data for Louisiana
            zip_codes = zctas(state=self.state_fips, year=2010)
            
            # Ensure both are in WGS84 (EPSG:4326)
            census_tracts = census_tracts.to_crs(4326)
            zip_codes = zip_codes.to_crs(4326)
            
            return census_tracts, zip_codes
            
        except Exception as e:
            print(f"Error loading spatial reference data: {e}")
            return None, None
    
    def create_spatial_dataframes(self, cleaned_datasets: Dict[str, pd.DataFrame]) -> Dict[str, gpd.GeoDataFrame]:
        """
        Convert cleaned datasets to spatial format.
        
        Args:
            cleaned_datasets: Dictionary of cleaned pandas DataFrames
            
        Returns:
            Dictionary of GeoDataFrames
        """
        spatial_datasets = {}
        
        for name, df in cleaned_datasets.items():
            if 'longitude' in df.columns and 'latitude' in df.columns:
                # Create geometry from coordinates
                geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
                gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=4326)
                spatial_datasets[name] = gdf
        
        return spatial_datasets
    
    def perform_spatial_joins(self, spatial_datasets: Dict[str, gpd.GeoDataFrame], 
                            census_tracts: gpd.GeoDataFrame, 
                            zip_codes: gpd.GeoDataFrame) -> Dict[str, gpd.GeoDataFrame]:
        """
        Perform spatial joins with census tracts and ZIP codes.
        
        Args:
            spatial_datasets: Dictionary of spatial datasets
            census_tracts: Census tracts GeoDataFrame
            zip_codes: ZIP codes GeoDataFrame
            
        Returns:
            Dictionary of spatially joined datasets
        """
        print("Performing spatial joins...")
        
        # Create study area buffer to filter ZIP codes
        all_points = []
        for gdf in spatial_datasets.values():
            all_points.extend(gdf.geometry.tolist())
        
        if all_points:
            study_area = unary_union(all_points)
            study_area_buffer = study_area.buffer(0.1)  # ~11km buffer
            zip_codes_br = zip_codes[zip_codes.intersects(study_area_buffer)]
        else:
            zip_codes_br = zip_codes
        
        joined_datasets = {}
        
        for name, gdf in spatial_datasets.items():
            # Join with census tracts
            gdf_with_tracts = gpd.sjoin(gdf, census_tracts, how='left', predicate='within')
            
            # Clean up index columns from first join to avoid conflicts
            columns_to_drop = [col for col in gdf_with_tracts.columns if col.startswith('index_')]
            if columns_to_drop:
                gdf_with_tracts = gdf_with_tracts.drop(columns=columns_to_drop)
            
            # Join with ZIP codes
            gdf_joined = gpd.sjoin(gdf_with_tracts, zip_codes_br, how='left', predicate='within')
            
            # Clean up index columns from second join
            columns_to_drop = [col for col in gdf_joined.columns if col.startswith('index_')]
            if columns_to_drop:
                gdf_joined = gdf_joined.drop(columns=columns_to_drop)
            
            # Clean up column names and add standard identifiers
            if 'GEOID' in gdf_joined.columns:
                gdf_joined['tract_id'] = gdf_joined['GEOID']
            if 'NAMELSAD' in gdf_joined.columns:
                gdf_joined['tract_name'] = gdf_joined['NAMELSAD']
            if 'ZCTA5CE10' in gdf_joined.columns:
                gdf_joined['zip_code'] = gdf_joined['ZCTA5CE10']
            
            joined_datasets[name] = gdf_joined
        
        return joined_datasets
    
    def create_summary_tables(self, joined_datasets: Dict[str, gpd.GeoDataFrame], 
                            census_tracts: gpd.GeoDataFrame, 
                            zip_codes: gpd.GeoDataFrame) -> Dict[str, pd.DataFrame]:
        """
        Create summary tables by tract and ZIP code.
        
        Args:
            joined_datasets: Dictionary of spatially joined datasets
            census_tracts: Census tracts GeoDataFrame
            zip_codes: ZIP codes GeoDataFrame
            
        Returns:
            Dictionary of summary tables
        """
        print("Creating summary tables...")
        
        summaries = {}
        
        # Create tract-level summaries for each dataset
        tract_summaries = {}
        for name, gdf in joined_datasets.items():
            if 'tract_id' in gdf.columns:
                summary = (gdf.drop(columns='geometry')
                          .groupby(['tract_id', 'tract_name'])
                          .size()
                          .reset_index(name=f'{name}_count'))
                tract_summaries[name] = summary
        
        # Create ZIP-level summaries for each dataset
        zip_summaries = {}
        for name, gdf in joined_datasets.items():
            if 'zip_code' in gdf.columns:
                summary = (gdf.drop(columns='geometry')
                          .dropna(subset=['zip_code'])
                          .groupby('zip_code')
                          .size()
                          .reset_index(name=f'{name}_count'))
                zip_summaries[name] = summary
        
        # Combine tract summaries
        if tract_summaries:
            tract_base = census_tracts[['GEOID', 'NAMELSAD']].copy()
            tract_base.columns = ['tract_id', 'tract_name']
            tract_base = tract_base.drop(columns='geometry') if 'geometry' in tract_base.columns else tract_base
            
            tract_totals = tract_base.copy()
            total_incidents = 0
            
            for name, summary in tract_summaries.items():
                tract_totals = tract_totals.merge(summary, on=['tract_id', 'tract_name'], how='left')
                tract_totals[f'{name}_count'] = tract_totals[f'{name}_count'].fillna(0)
                total_incidents += tract_totals[f'{name}_count']
            
            tract_totals['total_incidents'] = total_incidents
            tract_totals = tract_totals.sort_values('total_incidents', ascending=False)
            summaries['tract_totals'] = tract_totals
        
        # Combine ZIP summaries
        if zip_summaries:
            # Get ZIP codes that intersect with study area
            all_zips = set()
            for summary in zip_summaries.values():
                all_zips.update(summary['zip_code'].tolist())
            
            zip_base = pd.DataFrame({'zip_code': list(all_zips)})
            zip_totals = zip_base.copy()
            total_incidents = 0
            
            for name, summary in zip_summaries.items():
                zip_totals = zip_totals.merge(summary, on='zip_code', how='left')
                zip_totals[f'{name}_count'] = zip_totals[f'{name}_count'].fillna(0)
                total_incidents += zip_totals[f'{name}_count']
            
            zip_totals['total_incidents'] = total_incidents
            zip_totals = zip_totals.sort_values('total_incidents', ascending=False)
            summaries['zip_totals'] = zip_totals
        
        # Create detailed breakdowns by type
        for name, gdf in joined_datasets.items():
            if 'tract_id' in gdf.columns:
                # Try to find a type column
                type_col = None
                for col in ['typename', 'permit_type', 'type', 'category']:
                    if col in gdf.columns:
                        type_col = col
                        break
                
                if type_col:
                    type_summary = (gdf.drop(columns='geometry')
                                  .groupby(['tract_id', 'tract_name', type_col])
                                  .size()
                                  .reset_index(name='count'))
                    type_summary['dataset'] = name
                    summaries[f'tract_type_summary_{name}'] = type_summary
        
        return summaries
    
    def save_results(self, summaries: Dict[str, pd.DataFrame], 
                    joined_datasets: Dict[str, gpd.GeoDataFrame], 
                    output_dir: str = ".") -> None:
        """
        Save all results to CSV files.
        
        Args:
            summaries: Dictionary of summary tables
            joined_datasets: Dictionary of spatially joined datasets
            output_dir: Directory to save files
        """
        print("Saving results...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save summary tables
        for name, df in summaries.items():
            filename = output_path / f"{name}.csv"
            df.to_csv(filename, index=False)
        
        # Optionally save full datasets (can be large)
        # for name, gdf in joined_datasets.items():
        #     filename = output_path / f"{name}_with_spatial_joins.csv"
        #     gdf.drop(columns='geometry').to_csv(filename, index=False)
    
    def print_summary_stats(self, summaries: Dict[str, pd.DataFrame], 
                          joined_datasets: Dict[str, gpd.GeoDataFrame]) -> None:
        """
        Print summary statistics.
        
        Args:
            summaries: Dictionary of summary tables
            joined_datasets: Dictionary of spatially joined datasets
        """
        print("\n=== PROCESSING COMPLETE ===")
        
        for name, gdf in joined_datasets.items():
            print(f"Total {name} incidents processed: {len(gdf)}")
        
        if 'tract_totals' in summaries:
            unique_tracts = summaries['tract_totals']['tract_id'].nunique()
            print(f"Unique census tracts with data: {unique_tracts}")
        
        if 'zip_totals' in summaries:
            unique_zips = summaries['zip_totals']['zip_code'].nunique()
            print(f"Unique ZIP codes with data: {unique_zips}")
        
        if 'tract_totals' in summaries:
            print("\nTop 5 census tracts by combined incident count:")
            print(summaries['tract_totals'].head())
        
        if 'zip_totals' in summaries:
            print("\nTop 5 ZIP codes by combined incident count:")
            print(summaries['zip_totals'].head())
        
        print("\nFiles saved:")
        for name in summaries.keys():
            print(f"- {name}.csv")
        
        print("\nReady for ACS integration and additional analysis!")


def main(output_dir: str = ".", max_rows: int = 50000) -> None:
    """
    Main function to run the complete data collection and processing pipeline.
    
    Args:
        output_dir: Directory to save output files
        max_rows: Maximum number of rows to collect per dataset
    """
    # Initialize collector
    collector = BatonRougeDataCollector(max_rows=max_rows)
    
    # Step 1: Collect data from APIs
    datasets = collector.collect_all_datasets()
    
    # Step 2: Filter and clean data
    cleaned_datasets = collector.filter_and_clean_data(datasets)
    
    if not cleaned_datasets:
        print("No valid datasets collected. Exiting.")
        return
    
    # Step 3: Load spatial reference data
    census_tracts, zip_codes = collector.load_spatial_reference_data()
    
    if census_tracts is None or zip_codes is None:
        print("Failed to load spatial reference data. Exiting.")
        return
    
    # Step 4: Create spatial dataframes
    spatial_datasets = collector.create_spatial_dataframes(cleaned_datasets)
    
    # Step 5: Perform spatial joins
    joined_datasets = collector.perform_spatial_joins(spatial_datasets, census_tracts, zip_codes)
    
    # Step 6: Create summary tables
    summaries = collector.create_summary_tables(joined_datasets, census_tracts, zip_codes)
    
    # Step 7: Save results
    collector.save_results(summaries, joined_datasets, output_dir)
    
    # Step 8: Print summary statistics
    collector.print_summary_stats(summaries, joined_datasets)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Baton Rouge Data Collection and Spatial Analysis")
    parser.add_argument("--output-dir", default=".", help="Output directory for results")
    parser.add_argument("--max-rows", type=int, default=50000, help="Maximum rows per dataset")
    
    args = parser.parse_args()
    
    main(output_dir=args.output_dir, max_rows=args.max_rows)