# Baton Rouge Data Collection and Spatial Analysis - Python Version

This Python script converts the original R script to collect and analyze data from the Baton Rouge Open Data Portal, including blight, building permits, and crime data with spatial analysis.

## Features

- **Modular Design**: Organized into a class-based structure with separate methods for each major operation
- **API Data Collection**: Automated data collection from BR Open Data Portal with pagination and error handling
- **Spatial Analysis**: Integration with Census tracts and ZIP codes using geopandas and pygris
- **Summary Statistics**: Comprehensive summaries by geography and data type
- **Flexible Output**: CSV exports and optional spatial data exports

## Installation

1. Make sure you have Python 3.8+ installed
2. Set up the Python environment (if you're in VS Code, it should be configured automatically)
3. Install required dependencies:

```bash
pip install -r requirements.txt
```

**Note**: If you're using the virtual environment created in this project, use the full path:
```bash
/path/to/your/project/.venv/bin/python -m pip install -r requirements.txt
```

## Usage

### As a Script
Run the script directly from the command line:

```bash
python baton_rouge_data_pulls.py --output-dir ./output --max-rows 50000
```

### As a Module
Import and use the class in your own code:

```python
from baton_rouge_data_pulls import BatonRougeDataCollector

# Initialize collector
collector = BatonRougeDataCollector(max_rows=10000)

# Collect all data
datasets = collector.collect_all_datasets()

# Process and analyze
cleaned_datasets = collector.filter_and_clean_data(datasets)
# ... continue with spatial analysis
```

### Key Methods

- `collect_api_data()`: Generic API data collection with pagination
- `collect_all_datasets()`: Collect from all configured endpoints
- `filter_and_clean_data()`: Data cleaning and filtering
- `load_spatial_reference_data()`: Load Census tracts and ZIP codes
- `perform_spatial_joins()`: Spatial analysis and geographic assignment
- `create_summary_tables()`: Generate summary statistics
- `save_results()`: Export results to CSV files

## Output Files

The script generates several CSV files:

- `tract_totals.csv`: Summary by Census tract
- `zip_totals.csv`: Summary by ZIP code  
- `tract_type_summary_[dataset].csv`: Detailed breakdowns by tract and type
- Additional summary files as available

## Configuration

Key parameters can be adjusted:

- `max_rows`: Maximum rows to collect per dataset (default: 50,000)
- `batch_limit`: API batch size (default: 1,000)
- `api_endpoints`: Dictionary of API URLs (can be modified for different datasets)

## Dependencies

- **pandas**: Data manipulation and analysis
- **geopandas**: Spatial data handling
- **requests**: HTTP requests for API calls
- **pygris**: Census geography data
- **shapely**: Geometric operations

## Differences from R Version

- Uses `pygris` instead of `tigris` for Census data
- `geopandas` replaces `sf` for spatial operations
- `requests` replaces `httr` for API calls
- Object-oriented design for better modularity
- Enhanced error handling and logging

## Troubleshooting

### Common Issues

**ValueError: 'index_right' cannot be a column name in the frames being joined**
- This error occurs during spatial joins when index columns from previous joins conflict
- **Fixed**: The script now automatically cleans up index columns between spatial join operations
- If you encounter this with custom modifications, ensure you drop columns starting with 'index_' between joins

**ModuleNotFoundError for geopandas or other packages**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- If using a virtual environment, make sure it's activated before installing packages

**API Request Failures**
- The script includes automatic rate limiting (0.5 second delays)
- If you encounter persistent API errors, try reducing `max_rows` or `batch_limit`

## Notes

- The script automatically handles rate limiting (0.5 second delays between requests)
- Spatial operations use WGS84 (EPSG:4326) coordinate system
- Large datasets are processed in batches to manage memory usage
- Census data is cached by pygris for faster subsequent runs
- Index columns from spatial joins are automatically cleaned up to prevent conflicts