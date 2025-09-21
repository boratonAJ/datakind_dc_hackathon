# Enhanced Data Collectors for Social Isolation Analysis

## Overview

The `enhanced_data_collectors.py` script provides specialized data collection tools that complement the main social isolation analysis framework. These collectors focus on health outcomes, crime patterns, environmental factors, and spatial analysis that contribute to understanding social isolation and loneliness in Baton Rouge.

## Purpose and Scope

This script serves as a **modular data collection toolkit** that can be used independently or integrated with the main social isolation analyzer. It addresses specific research needs for:

- **Health outcomes research** using CDC and state health data
- **Environmental justice analysis** incorporating air quality and pollution data
- **Crime and safety research** with both safety and overpolicing indicators
- **Spatial analysis** with council district mapping and geographic aggregation

## Core Components

### 1. HealthOutcomesCollector
Specialized collector for health data from multiple authoritative sources.

**Primary Data Source:**
- **CDC PLACES** (Population Level Analysis and Community Estimations)
- **Louisiana Department of Health** (framework ready)
- **Hospital and mental health facility data** (framework ready)

**Health Indicators Collected:**
- Depression and mental health indicators
- Physical health limitations (poor physical/mental health days)
- Preventive care access (checkups, dental visits, screenings)
- Chronic disease prevalence (diabetes, hypertension, heart disease)
- Health risk behaviors (smoking, drinking, physical inactivity)
- Obesity and sleep health indicators

### 2. EnhancedCrimeAnalyzer
Advanced crime analysis focusing on social isolation factors.

**Analysis Capabilities:**
- Crime categorization (violent, property, quality-of-life, traffic)
- Temporal pattern analysis (day/night, weekday/weekend)
- Arrest-to-crime ratio calculations (overpolicing indicators)
- Spatial aggregation to census tracts
- Safety perception indicators

**Crime Categories:**
- **Violent**: Homicide, robbery, assault, battery
- **Property**: Burglary, theft, auto theft, vandalism  
- **Quality of Life**: Drug offenses, disturbances, noise violations
- **Traffic**: DUI, traffic violations, accidents

### 3. EnvironmentalDataCollector
Comprehensive environmental factors affecting social isolation.

**Data Sources:**
- **EPA AirNow API** - Real-time air quality data
- **EPA Air Quality System (AQS)** - Historical air quality
- **Louisiana DOTD** - Traffic volume data (noise proxy)
- **OpenStreetMap** - Highway/road data for noise modeling
- **USGS National Land Cover Database** - Green space analysis
- **Walk Score data** - Walkability indicators

**Environmental Indicators:**
- Air Quality Index (AQI) and pollutant concentrations
- Traffic noise levels and highway proximity
- Green space access and park availability
- Walkability and transportation access

### 4. CouncilDistrictMapper
Spatial analysis tools for policy-relevant geographic aggregation.

**Capabilities:**
- Census tract to City Council District crosswalk creation
- Spatial join operations between geographic boundaries
- Area-weighted aggregation for overlapping boundaries
- Geographic relationship mapping

## Installation and Setup

### Prerequisites
```bash
# Core dependencies
pip install pandas geopandas requests numpy pathlib

# Optional for enhanced spatial analysis
pip install shapely pygris cenpy

# For faster string matching (removes warnings)
pip install python-Levenshtein
```

### API Keys Configuration

#### Required for Full Functionality
```bash
# For air quality data (optional)
export AIRNOW_API_KEY="your_airnow_api_key"

# Get AirNow API key from:
# https://docs.airnowapi.org/account/request/
```

#### No API Keys Required For
- CDC PLACES health data (public API)
- Council district crosswalk creation
- Basic environmental data framework

## Usage Guide

### Command Line Interface

#### Basic Syntax
```bash
python enhanced_data_collectors.py [OPTIONS]
```

#### Available Options
- `--output-dir DIR` - Output directory (default: ./output)
- `--health-only` - Collect only health data from CDC PLACES
- `--crime-only` - Analyze only crime data (requires existing data)
- `--env-only` - Collect only environmental data

### Usage Examples

#### 1. Collect Health Data Only
```bash
# Basic health data collection
python enhanced_data_collectors.py --health-only --output-dir ./health_output

# What this does:
# - Connects to CDC PLACES API
# - Collects 20+ health indicators for East Baton Rouge Parish
# - Aggregates data to census tract level
# - Creates both raw and processed health datasets
```

**Output Files:**
- `cdc_places_health_data.csv` - Raw health data from CDC PLACES
- `tract_health_indicators.csv` - Processed tract-level health summary

#### 2. Environmental Data Collection
```bash
# Requires AirNow API key for full functionality
export AIRNOW_API_KEY="your_key_here"
python enhanced_data_collectors.py --env-only --output-dir ./environmental_output

# What this collects:
# - Real-time air quality data (AQI, pollutants)
# - Traffic volume data for noise modeling
# - Green space and walkability indicators
```

#### 3. Comprehensive Data Collection
```bash
# Collect all available data types
python enhanced_data_collectors.py --output-dir ./complete_output

# This runs:
# - Health outcomes collection
# - Council district crosswalk creation
# - Environmental data collection (if APIs available)
```

#### 4. Crime Analysis (Framework)
```bash
# Analyze existing crime data
python enhanced_data_collectors.py --crime-only --output-dir ./crime_analysis

# Note: Requires existing crime data to be available
# Framework ready for Baton Rouge Open Data Portal integration
```

### Python API Usage

#### Direct Class Usage
```python
from enhanced_data_collectors import (
    HealthOutcomesCollector, 
    EnvironmentalDataCollector,
    CouncilDistrictMapper,
    EnhancedCrimeAnalyzer
)

# Health data collection
health_collector = HealthOutcomesCollector()
health_data = health_collector.collect_cdc_places_data("./output")
tract_summary = health_collector._create_tract_health_summary(health_data)

# Environmental data collection
env_collector = EnvironmentalDataCollector()
air_quality = env_collector.collect_air_quality_data()
traffic_noise = env_collector.collect_traffic_noise_data()

# Spatial analysis
mapper = CouncilDistrictMapper()
crosswalk = mapper.create_tract_council_crosswalk("./output")
```

#### Integration with Main Analysis
```python
# Use with social isolation analyzer
from social_isolation_analyzer import SocialIsolationAnalyzer
from enhanced_data_collectors import HealthOutcomesCollector

# Initialize both
analyzer = SocialIsolationAnalyzer(year=2022)
health_collector = HealthOutcomesCollector()

# Collect specialized health data
health_data = health_collector.collect_cdc_places_data("./output")

# Integrate with main analysis
# (Manual integration or use analyzer's built-in health collection)
```

## Data Sources and APIs

### CDC PLACES API
**Endpoint:** `https://chronicdata.cdc.gov/resource/cwsq-ngmh.json`

**Data Available:**
- Census tract level health indicators
- 27+ health measures including mental health, chronic diseases, preventive care
- Updated annually with latest survey data
- No API key required (public access)

**Geographic Coverage:** All U.S. census tracts with sufficient population

### EPA AirNow API
**Purpose:** Real-time and forecasted air quality data

**Data Provided:**
- Air Quality Index (AQI) values
- Pollutant-specific concentrations (PM2.5, PM10, Ozone, etc.)
- Air quality forecasts and health advisories
- Geographic data by ZIP code, county, and monitoring station

**API Limits:** 500 calls per hour (free tier)

### Louisiana Department of Health (Framework Ready)
**Potential Data Sources:**
- Hospital discharge data
- Mental health facility locations
- Public health surveillance data
- Health facility accessibility data

**Implementation Status:** Framework prepared, needs specific API endpoints

### Baton Rouge Open Data Portal (Crime Data)
**Data Available:**
- Crime incident reports with location and time
- Arrest data with demographic information
- Building permits and code violations
- Blight and property condition data

**Integration Status:** Framework ready for existing municipal data collector

## Output File Formats

### Health Data Outputs

#### `cdc_places_health_data.csv`
**Structure:**
```
locationname, measure_id, measure_description, data_value, GEOID, year
"Census Tract 1.01, East Baton Rouge Parish, Louisiana", "DEPRESSION", "Depression among adults aged >=18 years", "18.5", "22033000101", "2021"
```

**Key Fields:**
- `GEOID` - Census tract identifier
- `measure_id` - Health indicator code (DEPRESSION, MHLTH, etc.)
- `data_value` - Percentage value for the indicator
- `measure_description` - Full description of health measure

#### `tract_health_indicators.csv`
**Structure:** Wide format with one row per census tract
```
GEOID, tract_name, Depression_Rate, Poor_Mental_Health_Rate, Obesity_Rate, ...
"22033000101", "Census Tract 1.01...", 18.5, 12.3, 31.2, ...
```

### Environmental Data Outputs

#### Air Quality Data
- Current AQI readings by location
- Pollutant-specific measurements
- Time-series data for trend analysis
- Geographic aggregation to census tract level

#### Traffic and Noise Data
- Traffic volume counts by road segment
- Estimated noise levels based on traffic and road type
- Distance calculations to major highways
- Noise exposure indicators by census tract

### Spatial Analysis Outputs

#### `tract_council_district_crosswalk.csv`
**Structure:**
```
GEOID, district_id, district_name, intersection_area
"22033000101", 1, "District 1", 0.95
```

**Usage:** Enables aggregation of census tract data to council district level for policy analysis

## Health Indicators Reference

### Mental Health Indicators
- **DEPRESSION** - Depression among adults aged >=18 years
- **MHLTH** - Mental health not good for >=14 days among adults aged >=18 years

### Physical Health Indicators  
- **PHLTH** - Physical health not good for >=14 days among adults aged >=18 years
- **OBESITY** - Obesity among adults aged >=18 years

### Health Behaviors
- **CSMOKING** - Current smoking among adults aged >=18 years
- **BINGE** - Binge drinking among adults aged >=18 years
- **LPA** - No leisure-time physical activity among adults aged >=18 years
- **SLEEP** - Sleeping less than 7 hours among adults aged >=18 years

### Preventive Care
- **CHECKUP** - Visits to doctor for routine checkup within the past year
- **DENTAL** - Visits to dentist or dental clinic within the past year
- **MAMMOUSE** - Mammography use among women aged 50-74 years
- **CERVICAL** - Cervical cancer screening among women aged 21-65 years

### Chronic Diseases
- **DIABETES** - Diabetes among adults aged >=18 years
- **BPHIGH** - High blood pressure among adults aged >=18 years
- **HIGHCHOL** - High cholesterol among adults aged >=18 years
- **CHD** - Coronary heart disease among adults aged >=18 years
- **STROKE** - Stroke among adults aged >=18 years
- **COPD** - Chronic obstructive pulmonary disease among adults aged >=18 years

## Error Handling and Troubleshooting

### Common Issues and Solutions

#### 1. CDC PLACES API Errors
**Problem:** HTTP 400 errors when collecting health data
**Solutions:**
- Check geographic parameters (state, county names)
- Verify measure IDs are correct for the data year
- Review API query structure and parameters

#### 2. Missing API Keys
**Problem:** Environmental data collection fails
**Solutions:**
- Verify AirNow API key is set: `echo $AIRNOW_API_KEY`
- Check API key validity with test requests
- Use framework without environmental data if APIs unavailable

#### 3. Spatial Data Issues
**Problem:** Council district crosswalk creation fails
**Solutions:**
- Verify geographic boundary data availability
- Check coordinate reference systems match
- Use alternative geographic aggregation methods

#### 4. Output Directory Issues
**Problem:** Permission denied or file creation errors
**Solutions:**
- Ensure output directory exists and is writable
- Use absolute paths when possible
- Check disk space availability

### Debug Mode Usage
```python
# Enable detailed logging for troubleshooting
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual collectors
from enhanced_data_collectors import HealthOutcomesCollector
collector = HealthOutcomesCollector()
# Check API connectivity before full collection
```

## Performance Considerations

### API Rate Limits
- **CDC PLACES:** No explicit rate limits, but be respectful
- **AirNow:** 500 calls per hour (free tier)
- **EPA AQS:** Various limits depending on data type

### Data Volume
- **Health Data:** ~100-200 records per measure per parish
- **Environmental Data:** Varies by monitoring station density
- **Processing Time:** 2-10 minutes for complete health data collection

### Memory Usage
- **Health Data:** Low memory footprint
- **Spatial Analysis:** Higher memory for geographic operations
- **Large Datasets:** Consider chunked processing for very large areas

## Integration with Main Framework

### Automatic Integration
The enhanced data collectors are designed to work seamlessly with the main social isolation analyzer:

```python
# Main analyzer automatically uses enhanced collectors
from social_isolation_analyzer import SocialIsolationAnalyzer

analyzer = SocialIsolationAnalyzer(year=2022)
results = analyzer.run_comprehensive_analysis()

# Health data is collected using HealthOutcomesCollector
# Environmental data uses EnvironmentalDataCollector
# Spatial analysis uses CouncilDistrictMapper
```

### Manual Integration
For custom analysis workflows:

```python
# Collect data using enhanced collectors
health_data = HealthOutcomesCollector().collect_cdc_places_data("./output")
env_data = EnvironmentalDataCollector().collect_air_quality_data()

# Merge with existing analysis
# Custom integration logic here
```

## Development and Extension

### Adding New Data Sources
1. **Create new collector class** following existing patterns
2. **Implement data collection methods** with error handling
3. **Add geographic aggregation** to census tract level
4. **Include in main() function** with command-line options

### Example Extension
```python
class NewDataCollector:
    def __init__(self):
        self.api_endpoint = "https://api.example.com/data"
    
    def collect_data(self) -> pd.DataFrame:
        # Implement data collection logic
        pass
    
    def aggregate_to_tracts(self, data: pd.DataFrame) -> pd.DataFrame:
        # Implement geographic aggregation
        pass
```

### Contributing Guidelines
1. **Follow existing code patterns** and error handling
2. **Include comprehensive documentation** and examples
3. **Add unit tests** for new data collection methods
4. **Update command-line interface** for new options
5. **Update this README** with new capabilities

## Limitations and Future Development

### Current Limitations
- **Geographic Scope:** Focused on East Baton Rouge Parish
- **Data Availability:** Some sources require specific API access
- **Real-time Data:** Limited to sources with public APIs
- **Spatial Resolution:** Constrained by data source geographic detail

### Planned Enhancements
- **Additional Health Sources:** State and local health departments
- **Enhanced Environmental Data:** Satellite imagery, noise measurements
- **Real-time Crime Data:** Direct integration with police data systems
- **Machine Learning Integration:** Predictive modeling capabilities
- **Interactive Visualization:** Dashboard and mapping interfaces

### Research Applications
This enhanced data collection framework supports research in:
- **Public health and social determinants**
- **Environmental justice and health equity**
- **Urban planning and community development**
- **Crime prevention and community safety**
- **Social isolation intervention planning**

## Support and Documentation

### Getting Help
1. **Check this README** for comprehensive usage information
2. **Review error messages** for specific troubleshooting guidance
3. **Test individual components** before running complete analysis
4. **Verify API access** and data availability for your research area

### Additional Resources
- **CDC PLACES Documentation:** https://www.cdc.gov/places/
- **EPA AirNow API Guide:** https://docs.airnowapi.org/
- **Geopandas Documentation:** https://geopandas.org/
- **Census API Documentation:** https://www.census.gov/developers/

This enhanced data collection framework provides a robust foundation for comprehensive social isolation research, with the flexibility to extend and customize for specific research questions and geographic areas.