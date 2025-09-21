# Baton Rouge Social Isolation & Loneliness Analysis Framework

This framework provides comprehensive tools for analyzing social isolation and loneliness factors in Baton Rouge, Louisiana, using data from multiple sources including the Census Bureau, CDC, municipal data, and environmental factors.

## Overview

Social isolation and loneliness are significant public health concerns that intersect with housing conditions, community characteristics, and various social determinants of health. This analysis framework helps identify areas and populations at highest risk for social isolation by combining:

- **Housing conditions** and quality indicators from Census ACS data
- **Health outcomes** from CDC PLACES and Louisiana Department of Health
- **Crime and safety** data from Baton Rouge Open Data Portal
- **Environmental factors** including air quality, noise, and green space access
- **Demographic risk factors** including age, disability, language barriers
- **Economic factors** including poverty, unemployment, and housing cost burden

## Files and Components

### Core Analysis Script
- **`social_isolation_analyzer.py`** - Main analysis framework that extends existing ACS and municipal data collectors

### Enhanced Data Collectors
- **`enhanced_data_collectors.py`** - Specialized collectors for health, crime, and environmental data

### Existing Infrastructure
- **`baton_rouge_acs_housing.py`** - Base ACS housing and demographic data collector
- **`baton_rouge_data_pulls.py`** - Municipal data collector (blight, permits, crime)

## Key Features

### 1. Housing Quality Indicators
Calculates derived variables that indicate housing-related isolation risk:
- Housing overcrowding rates
- Housing cost burden (>30% of income)
- Housing age and condition proxies
- Mobile home concentration
- Housing vacancy rates
- Renter vs. owner occupancy stability

### 2. Social Isolation Risk Factors
Identifies demographic characteristics associated with isolation:
- Elderly living alone rates
- Single-person household rates
- Language isolation (limited English proficiency)
- Disability rates
- Transportation limitations (no vehicle access)
- Digital divide indicators (no internet access)

### 3. Health Outcomes Integration
Collects health data from CDC PLACES including:
- Depression and mental health indicators
- Physical health limitations
- Preventive care access
- Chronic disease rates
- Health risk behaviors

### 4. Enhanced Crime and Safety Analysis
Analyzes crime patterns for both safety concerns and overpolicing:
- Crime rates by type (violent, property, quality-of-life)
- Temporal crime patterns (day/night, weekday/weekend)
- Arrest-to-crime ratios as overpolicing indicators
- Perceived safety factors

### 5. Environmental Factors
Collects environmental data affecting social isolation:
- Air quality indicators
- Traffic noise levels
- Green space access
- Walkability measures

### 6. Spatial Analysis
- Census tract level aggregation
- Crosswalk between census tracts and City Council districts
- Spatial relationships between housing, health, and environmental factors

## Installation and Setup

### Prerequisites
```bash
# Install required packages
pip install pandas geopandas requests census cenpy numpy pathlib
```

### API Keys Required

1. **Census API Key** (required for ACS data)
   - Get from: https://api.census.gov/data/key_signup.html
   - Set as environment variable: `export CENSUS_API_KEY="your_key_here"`

2. **AirNow API Key** (optional for air quality data)
   - Get from: https://docs.airnowapi.org/account/request/
   - Set as environment variable: `export AIRNOW_API_KEY="your_key_here"`
   
   **Purpose:** The AirNow API provides real-time and historical air quality data that connects to social isolation through multiple pathways:
   
   - **Health-Related Isolation**: Poor air quality forces vulnerable populations (elderly, asthmatic) to stay indoors, reducing social interactions
   - **Environmental Justice**: Communities with poor air quality often experience higher social isolation and economic disadvantage  
   - **Outdoor Activity Limitations**: High pollution days reduce park usage, community gatherings, and children's outdoor play
   
   **Data Collected:**
   - Current Air Quality Index (AQI) readings
   - Pollutant concentrations (PM2.5, PM10, ozone)
   - Air quality forecasts and health advisories
   - Historical air quality trends by geographic area
   
   **Integration:** Air quality data is aggregated to census tract level and integrated into environmental justice composite scores, correlated with health outcomes, and used to create environmental burden indicators.
   
   **Why Optional:** The core housing and demographic analysis works without air quality data, and alternative EPA data sources exist. Obtain this key if you want to study environmental health factors, environmental justice issues, or how air pollution affects community social patterns.

## Usage

### Basic Social Isolation Analysis
```bash
# Run comprehensive analysis
export CENSUS_API_KEY="your_census_api_key"
python social_isolation_analyzer.py --output-dir ./social_isolation_output --year 2022
```

### Health Data Collection Only
```bash
# Collect just CDC PLACES health data
python enhanced_data_collectors.py --health-only --output-dir ./health_data
```

### Specific Component Analysis
```python
from social_isolation_analyzer import SocialIsolationAnalyzer

# Initialize analyzer
analyzer = SocialIsolationAnalyzer(census_api_key="your_key", year=2022)

# Run specific components
acs_data = analyzer.acs_collector.run_data_collection()
housing_indicators = analyzer.calculate_housing_quality_indicators(acs_data)
isolation_indicators = analyzer.calculate_social_isolation_indicators(housing_indicators)
health_data = analyzer.collect_health_outcomes_data()
```

## Output Files

The analysis generates several output files:

### Primary Outputs
- **`social_isolation_analysis.csv`** - Complete analysis with all indicators and risk scores
- **`cdc_places_health_data.csv`** - Raw health outcomes data from CDC PLACES
- **`tract_health_indicators.csv`** - Health indicators summarized by census tract
- **`tract_council_district_crosswalk.csv`** - Spatial crosswalk file

### Analysis Components
- Housing quality indicators (overcrowding, cost burden, age, etc.)
- Social isolation risk factors (elderly alone, language barriers, etc.)
- Health outcomes (depression, chronic disease, preventive care)
- Environmental factors (air quality, noise, green space)
- Composite risk scores and categories

## Data Sources

### Primary Sources
1. **U.S. Census Bureau American Community Survey (ACS)**
   - Housing characteristics
   - Demographic data
   - Economic indicators
   - Transportation access

2. **CDC PLACES (Population Level Analysis and Community Estimations)**
   - Health outcomes by census tract
   - Preventive care indicators
   - Chronic disease prevalence
   - Mental health indicators

3. **Baton Rouge Open Data Portal**
   - Crime incidents
   - Building permits
   - Blight data

### Secondary Sources (Framework Ready)
4. **Louisiana Department of Health**
   - Hospital discharge data
   - Mental health facilities
   - Public health surveillance

5. **EPA Environmental Data**
   - Air quality monitoring
   - Environmental justice indicators

6. **Louisiana DOTD**
   - Traffic count data (noise proxy)

7. **OpenStreetMap**
   - Highway/road data
   - Land use information

## Analysis Framework

### Risk Score Calculation
The framework calculates composite risk scores across multiple domains:

1. **Housing Risk Index**
   - Cost burden, overcrowding, housing age, vacancy rates

2. **Demographic Risk Index**
   - Age factors, disability, language barriers, transportation

3. **Economic Risk Index**
   - Poverty, unemployment, digital access

4. **Overall Social Isolation Risk Index**
   - Standardized combination of all risk domains
   - Categorized as Low, Moderate, or High Risk

### Statistical Methods
- Z-score standardization for indicator comparison
- Composite index creation using domain averages
- Risk categorization using percentile thresholds
- Spatial aggregation to census tract level

## Addressing the Research Questions

### 1. Housing Conditions and Health Outcomes
The framework relates housing quality indicators to health outcomes through:
- **Housing Quality Metrics**: Cost burden, overcrowding, age, stability
- **Health Outcome Metrics**: Depression, chronic disease, preventive care access
- **Modeling Approach**: Correlation analysis and regression modeling capability

### 2. Crime and Safety Analysis
Addresses both safety concerns and overpolicing through:
- **Safety Indicators**: Crime rates, temporal patterns, crime types
- **Overpolicing Indicators**: Arrest-to-crime ratios, enforcement patterns
- **Community Impact**: Relationship to social isolation and community trust

### 3. Environmental Justice
Examines environmental factors affecting vulnerable populations:
- **Pollution Exposure**: Air quality, noise, industrial proximity
- **Access to Amenities**: Green space, walkability, transportation
- **Cumulative Impact**: Multiple environmental stressors

### 4. Poverty and Socioeconomic Analysis
Comprehensive socioeconomic analysis including:
- **Income and Poverty**: Multiple poverty measures, income distribution
- **Employment**: Unemployment, job accessibility, work transportation
- **Housing Affordability**: Cost burden across income levels
- **Digital Divide**: Internet access, technology barriers

## Council District Analysis

The framework includes spatial crosswalk capabilities to relate census tract data to Baton Rouge City Council Districts, enabling:
- District-level aggregation of social isolation indicators
- Comparison across council districts
- Policy-relevant geographic analysis
- Resource allocation planning

## Limitations and Future Enhancements

### Current Limitations
- Some data sources require manual implementation of specific APIs
- Environmental data collection needs API keys and additional setup
- Temporal analysis limited by data availability
- Some health data may have privacy restrictions

### Planned Enhancements
- Machine learning models for risk prediction
- Temporal trend analysis
- Intervention impact assessment
- Interactive visualization dashboard
- Real-time data updates

## Contributing

To extend this framework:
1. Add new data sources by extending the collector classes
2. Implement additional risk indicators in the analyzer methods
3. Add new modeling approaches in the risk calculation functions
4. Enhance spatial analysis capabilities

## Support and Documentation

For questions or issues:
1. Check existing data source documentation
2. Verify API keys and data access
3. Review error logs for specific data collection issues
4. Consider data availability and temporal limitations

## Example Analysis Workflow

```python
# Complete analysis workflow example
from social_isolation_analyzer import SocialIsolationAnalyzer

# 1. Initialize
analyzer = SocialIsolationAnalyzer(year=2022)

# 2. Run comprehensive analysis
results = analyzer.run_comprehensive_analysis(output_dir="./analysis_output")

# 3. Access specific components
housing_data = results.get('housing_quality')
health_data = results.get('health_outcomes')
final_analysis = results.get('final_analysis')

# 4. Custom analysis
if final_analysis is not None:
    high_risk_tracts = final_analysis[final_analysis['Risk_Category'] == 'High Risk']
    print(f"Found {len(high_risk_tracts)} high-risk census tracts")
```

This framework provides a comprehensive foundation for analyzing social isolation and loneliness factors in Baton Rouge, with the flexibility to extend and customize for specific research questions and policy needs.