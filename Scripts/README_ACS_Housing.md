# Baton Rouge ACS Housing Data Collection - Python Version

This Python script converts the original R script to collect and analyze Census American Community Survey (ACS) data for housing, demographics, income, and household characteristics in Baton Rouge (East Baton Rouge Parish), Louisiana.

## Features

- **Comprehensive ACS Data Collection**: Housing, demographic, income, and household data from Census Bureau
- **Modular Design**: Object-oriented approach with separate methods for data collection, processing, and analysis
- **Variable Mapping**: Automatic transformation of ACS variable codes to friendly names
- **Spatial Analysis**: Integration with Census tract geometries and spatial metrics calculation
- **Derived Indicators**: Comprehensive calculation of percentages, ratios, and summary statistics
- **Flexible Output**: CSV and GeoJSON exports with configurable parameters

## Data Categories

### Housing Data
- Housing units, occupancy, and tenure (owner vs renter)
- Housing values, rent, and cost burden
- Structure types and age of housing
- Bedroom distribution and household size

### Demographics
- Population by race and ethnicity
- Age distribution, especially children and families

### Income & Economics
- Household income distribution and medians
- Poverty status by age, gender, and household type
- Income by housing tenure

### Household Composition
- Family vs non-family households
- Households with children
- Single-person households
- Household size by tenure

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Get a Census API key:
   - Visit: <https://api.census.gov/data/key_signup.html>
   - Set as environment variable: `export CENSUS_API_KEY="your_actual_key_here"`
   - Or pass directly to the script

## Usage

### Command Line
```bash
# Basic usage with API key (replace with your actual key)
python baton_rouge_acs_housing.py --api-key e27fa55047fbf6a1719e8fe93b907ab8c3bd11e0

# Or use environment variable
export CENSUS_API_KEY="e27fa55047fbf6a1719e8fe93b907ab8c3bd11e0"
python baton_rouge_acs_housing.py --output-dir ./output

# Specify output directory and year
python baton_rouge_acs_housing.py --api-key YOUR_ACTUAL_KEY --output-dir ./output --year 2023

# Skip spatial analysis for faster processing
python baton_rouge_acs_housing.py --api-key YOUR_ACTUAL_KEY --no-spatial
```

### As a Module
```python
from baton_rouge_acs_housing import BatonRougeACSCollector

# Initialize collector
collector = BatonRougeACSCollector(api_key="your_key", year=2023)

# Test API connection
collector.test_api_connection()

# Collect all data
datasets = collector.collect_all_acs_data()

# Transform and process
all_data = pd.concat([df for df in datasets.values() if not df.empty])
wide_data = collector.transform_to_wide_format(all_data)
processed_data = collector.calculate_derived_indicators(wide_data)
```

## Key Methods

### Data Collection
- `collect_all_acs_data()`: Collect from all ACS table categories
- `collect_acs_tables()`: Generic method for collecting specific tables
- `test_api_connection()`: Verify Census API connectivity

### Data Processing
- `transform_to_wide_format()`: Convert long format to wide with friendly names
- `calculate_derived_indicators()`: Calculate percentages and derived metrics
- `create_variable_mapping()`: Map ACS codes to readable names

### Spatial Analysis
- `get_tract_geometries()`: Retrieve Census tract boundaries
- `calculate_spatial_metrics()`: Calculate density and area metrics

### Output
- `save_results()`: Export to CSV and GeoJSON formats
- `print_summary_stats()`: Display data summary

## Output Files

The script generates several output files:

- `baton_rouge_housing_acs_2023.csv`: Main dataset without geometry
- `baton_rouge_housing_acs_2023_with_geometry.geojson`: Spatial dataset with tract boundaries

## ACS Tables Included

### Housing Tables
- **B25001-B25003**: Housing units, occupancy, and tenure
- **B25024**: Units in structure (single-family vs multi-family)
- **B25034**: Year structure built
- **B25041**: Number of bedrooms
- **B25053**: Selected monthly owner costs
- **B25064**: Median gross rent
- **B25070**: Gross rent as percentage of household income
- **B25077**: Median value (owner-occupied units)
- **S2503**: Financial characteristics for occupied housing units
- **S2504**: Physical housing characteristics
- **DP04**: Selected housing characteristics (Data Profile)

### Demographic Tables
- **B01003**: Total population
- **B02001**: Race
- **B03003**: Hispanic or Latino origin

### Income Tables
- **B19001**: Household income in the past 12 months
- **B19013**: Median household income
- **B19101**: Family income distribution
- **B17001**: Poverty status in the past 12 months by sex by age
- **B17017**: Poverty status by household type
- **B25119**: Median household income by tenure
- **DP03**: Selected economic characteristics

### Household Tables
- **B09001**: Population under 18 years by age
- **B09002**: Own children under 18 years by family type
- **B11001**: Household type
- **B11005**: Households by presence of people under 18 years
- **B25115**: Tenure by household size

## Derived Indicators

The script calculates numerous derived indicators:

### Population & Demographics
- Racial/ethnic percentages
- Age distribution analysis

### Income & Poverty
- Income category groupings (low, middle, high income)
- Poverty rates by various demographics
- Children in poverty analysis

### Housing
- Occupancy and vacancy rates
- Owner vs renter percentages
- Housing structure type distributions
- Age of housing stock analysis
- Cost burden indicators
- Density metrics (units/sq mi, population/sq mi)

### Household Composition
- Family household percentages
- Single-person household rates
- Households with children
- Children by family structure (married couple vs single parent)

## Configuration

Key parameters that can be adjusted:

- `year`: Census data year (default: 2023)
- `state_fips`: State FIPS code (default: "22" for Louisiana)
- `county_fips`: County FIPS code (default: "033" for East Baton Rouge Parish)
- `include_spatial`: Whether to include spatial analysis (default: True)

## Dependencies

- **pandas**: Data manipulation and analysis
- **geopandas**: Spatial data handling
- **numpy**: Numerical computations
- **census**: Official Census Bureau API client
- **cenpy**: Alternative Census data interface with enhanced features
- **shapely**: Geometric operations
- **requests**: HTTP requests

## Error Handling

The script includes comprehensive error handling:

- API connection testing and validation
- Table-by-table error handling (continues if individual tables fail)
- Rate limiting to respect Census API limits
- Graceful handling of missing variables or geometry data

## Performance Notes

- Uses rate limiting (1-second delays) to respect Census API limits
- Processes tables in batches to manage memory usage
- Limits variables per table to avoid API timeouts
- Spatial operations use appropriate projections for accurate calculations

## Differences from R Version

- Uses `census` and `cenpy` libraries instead of `tidycensus`
- Object-oriented design for better modularity
- Enhanced error handling and logging
- Simplified spatial operations using geopandas
- More flexible output options

## Troubleshooting

### API Key Issues
- Ensure your Census API key is valid and active
- Set as environment variable or pass directly to script
- Check API limits if you encounter rate limiting errors

### Missing Data
- Some tables may not be available for all years
- Subject tables (S-series) and Data Profile tables (DP-series) may have different availability
- Script continues processing even if some tables fail

### Geometry Issues
- Spatial analysis requires additional processing time
- Use `--no-spatial` flag for faster processing if geometry isn't needed
- Ensure geopandas and spatial dependencies are properly installed

## Notes

- Processing time varies based on number of tables and whether spatial analysis is included
- Census tract geometries are automatically downloaded and cached
- All coordinate systems are standardized to WGS84 for output
- Derived indicators are calculated with safe division to handle zero denominators