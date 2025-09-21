# Baton Rouge Social Isolation & Loneliness Analysis Framework

## 🏠 Overview

The **Baton Rouge Social Isolation Framework** is a comprehensive, unified system for analyzing social isolation and loneliness factors across East Baton Rouge Parish. This framework integrates all existing data collection and analysis components into a single, coordinated workflow.

## 🎯 Key Features

### Comprehensive Data Integration
- **Census ACS Data**: Housing, demographics, socioeconomic indicators
- **Municipal Data**: Blight, building permits, crime records
- **Health Outcomes**: CDC PLACES health indicators
- **Environmental Factors**: Air quality, noise, green space access
- **Crime & Safety**: Enhanced crime pattern analysis
- **Spatial Analysis**: Census tract and council district crosswalks

### Advanced Analytics
- **Risk Scoring**: Multi-dimensional risk assessment
- **Composite Indices**: Combined social isolation metrics
- **Spatial Analysis**: Geographic clustering and patterns
- **Policy Recommendations**: Data-driven intervention strategies

### Automated Workflow
- **End-to-End Processing**: Complete analysis pipeline
- **Configuration Management**: Flexible, JSON-based settings
- **Error Handling**: Graceful fallbacks and detailed logging
- **Output Management**: Organized, structured results

## 📋 Quick Start

### 1. Installation
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Install additional spatial dependencies if needed
pip install pygris
```

### 2. API Keys Setup
```bash
# Set environment variables for API access
export CENSUS_API_KEY="your_census_api_key_here"
export AIRNOW_API_KEY="your_airnow_api_key_here"  # Optional
```

### 3. Run Complete Analysis
```bash
# Run full analysis with default settings
python baton_rouge_social_isolation_framework.py --output-dir ./analysis_2023

# Run with custom configuration
python baton_rouge_social_isolation_framework.py --config framework_config.json --year 2023
```

### 4. Create Custom Configuration
```bash
# Generate default configuration file
python baton_rouge_social_isolation_framework.py --create-config my_config.json
```

## 🔧 Configuration Options

### Data Sources
```json
{
  "data_sources": {
    "census_acs": true,           // Census housing & demographics
    "municipal_data": true,       // Blight, permits, crime
    "health_outcomes": true,      // CDC PLACES health data
    "environmental_data": true,   // Air quality, noise, green space
    "crime_analysis": true,       // Enhanced crime patterns
    "spatial_crosswalks": true    // Geographic crosswalks
  }
}
```

### Analysis Options
```json
{
  "analysis_options": {
    "include_spatial": true,           // Include spatial analysis
    "calculate_risk_scores": true,     // Generate risk assessments
    "create_composite_indices": true,  // Create combined metrics
    "generate_visualizations": false,  // Create charts/maps
    "save_intermediate_results": true  // Save intermediate data
  }
}
```

## 📊 Output Structure

The framework creates a comprehensive output directory structure:

```
social_isolation_analysis/
├── MASTER_ANALYSIS_RESULTS.json          # Complete results summary
├── data/                                  # Raw collected data
│   ├── acs_data.csv                      # Census ACS data
│   ├── municipal_data_Crime.csv          # Crime records
│   ├── health_data.csv                   # Health outcomes
│   └── environmental_data_*.csv          # Environmental data
├── analysis/                             # Analysis results
│   ├── housing_indicators.csv           # Housing quality metrics
│   ├── isolation_indicators.csv         # Social isolation metrics
│   ├── risk_scores.csv                  # Risk assessments
│   └── composite_analysis.csv           # Combined analysis
├── spatial/                             # Geographic data
│   ├── tract_council_crosswalk.csv     # Spatial mappings
│   └── tract_geometries.geojson         # Tract boundaries
└── reports/                             # Analysis reports
    ├── comprehensive_summary.json       # Analysis summary
    ├── policy_recommendations.json      # Policy guidance
    └── data_quality_report.json        # Data quality assessment
```

## 🎯 Key Analysis Components

### 1. Housing Quality Indicators
- **Overcrowding**: People per room ratios
- **Housing Problems**: Structural issues, incomplete facilities
- **Cost Burden**: Rent/mortgage as % of income
- **Tenure Stability**: Rental vs. ownership patterns

### 2. Social Isolation Indicators
- **Age Isolation**: Elderly living alone
- **Transportation Access**: Vehicle availability
- **Economic Isolation**: Poverty, unemployment
- **Digital Divide**: Internet access disparities

### 3. Health Outcomes
- **Physical Health**: Chronic disease prevalence
- **Mental Health**: Depression, anxiety indicators
- **Healthcare Access**: Provider availability
- **Health Behaviors**: Smoking, exercise patterns

### 4. Environmental Factors
- **Air Quality**: Pollution exposure
- **Noise Pollution**: Traffic and industrial noise
- **Green Space**: Parks and natural area access
- **Environmental Justice**: Cumulative exposures

### 5. Crime & Safety
- **Crime Density**: Incidents per tract
- **Crime Types**: Violent vs. property crime
- **Safety Perceptions**: Neighborhood safety
- **Policing Patterns**: Enforcement concentration

## 🔍 Analysis Workflow

### Phase 1: Data Collection
1. **Census ACS Data**: Collect 150+ housing/demographic variables
2. **Municipal Data**: Download blight, permits, crime from BR Open Data
3. **Health Outcomes**: Fetch CDC PLACES health indicators
4. **Environmental Data**: Collect air quality, noise, green space data
5. **Crime Analysis**: Process and analyze crime patterns

### Phase 2: Spatial Analysis
1. **Tract Boundaries**: Download Census tract geometries
2. **Council Districts**: Create tract-to-district crosswalks
3. **Spatial Joins**: Assign data points to geographic areas
4. **Spatial Metrics**: Calculate density, distance measures

### Phase 3: Social Isolation Analysis
1. **Housing Indicators**: Calculate housing quality metrics
2. **Isolation Indicators**: Compute social isolation measures
3. **Risk Scoring**: Generate multi-dimensional risk scores
4. **Composite Indices**: Create combined vulnerability measures

### Phase 4: Results Generation
1. **Comprehensive Summary**: Create analysis overview
2. **Policy Recommendations**: Generate intervention strategies
3. **Data Quality Report**: Assess data completeness and reliability
4. **Spatial Products**: Create maps and geographic outputs

### Phase 5: Output Creation
1. **Structured Exports**: Save all data in organized format
2. **Master Results**: Create comprehensive results file
3. **Documentation**: Generate analysis documentation
4. **Quality Checks**: Validate outputs and flag issues

## 🚀 Advanced Usage

### Custom Data Sources
```python
from baton_rouge_social_isolation_framework import BatonRougeSocialIsolationFramework

# Initialize with custom settings
framework = BatonRougeSocialIsolationFramework(
    year=2022,
    output_dir="./custom_analysis",
    config_file="custom_config.json"
)

# Access individual collectors
acs_data = framework.acs_collector.collect_all_acs_data()
health_data = framework.health_collector.collect_cdc_places_data()

# Run specific analysis components
housing_indicators = framework.isolation_analyzer.calculate_housing_quality_indicators(acs_data)
```

### Modular Analysis
```python
# Run only specific components
framework = BatonRougeSocialIsolationFramework(config_file="minimal_config.json")

# Collect only ACS and health data
framework.config["data_sources"] = {
    "census_acs": True,
    "health_outcomes": True,
    "municipal_data": False,
    "environmental_data": False,
    "crime_analysis": False,
    "spatial_crosswalks": False
}

results = framework.run_comprehensive_analysis()
```

## 📚 Dependencies

### Core Requirements
- **pandas >= 1.5.0**: Data manipulation
- **geopandas >= 0.10.0**: Spatial data handling
- **requests >= 2.25.0**: API communication
- **numpy >= 1.21.0**: Numerical operations

### Specialized Libraries
- **census >= 0.8.19**: Census Bureau API access
- **pygris >= 0.1.5**: Census geography downloads
- **shapely >= 1.8.0**: Geometric operations
- **cenpy >= 1.0.1**: Enhanced Census data access

## 🔧 Troubleshooting

### API Connection Issues
- **Census API**: Ensure valid API key and rate limiting compliance
- **Municipal APIs**: Check BR Open Data Portal availability
- **Health APIs**: Verify CDC PLACES API accessibility

### Data Collection Problems
- **Missing Data**: Framework continues with available data sources
- **Spatial Issues**: Falls back to template crosswalks when boundaries unavailable
- **Memory Limits**: Adjust `max_rows_per_dataset` in configuration

### Analysis Errors
- **Tract Coverage**: Minimum 100 tracts recommended for reliable analysis
- **Data Quality**: Check data quality report for completeness issues
- **Coordinate Systems**: All spatial data standardized to WGS84

## 📈 Analysis Validation

### Data Quality Checks
- **Completeness**: % of non-null values per indicator
- **Coverage**: Number of census tracts with data
- **Consistency**: Cross-validation between data sources
- **Currency**: Data recency and update frequency

### Analysis Validation
- **Range Checks**: Validate indicator values within expected ranges
- **Correlation Analysis**: Check for expected relationships between variables
- **Spatial Validation**: Verify geographic assignments and boundaries
- **Trend Analysis**: Compare results across time periods

## 🎯 Policy Applications

### High-Priority Areas
- **Risk Mapping**: Identify census tracts with highest isolation risk
- **Resource Allocation**: Guide service placement and funding decisions
- **Intervention Targeting**: Focus programs on most vulnerable populations

### Intervention Strategies
- **Housing Improvements**: Target substandard housing conditions
- **Transportation Access**: Improve public transit in isolated areas
- **Health Services**: Expand healthcare access in underserved areas
- **Community Building**: Support social connectivity programs

### Monitoring & Evaluation
- **Baseline Metrics**: Establish pre-intervention measurements
- **Progress Tracking**: Monitor changes over time
- **Impact Assessment**: Evaluate intervention effectiveness
- **Adaptive Management**: Adjust strategies based on results

## 👥 Support & Contributing

### Getting Help
- **Documentation**: Comprehensive README files for each component
- **Configuration**: Use `--create-config` to generate template settings
- **Error Logs**: Check output for detailed error messages and guidance

### Development
- **Modular Design**: Easy to extend with new data sources or analyses
- **Error Handling**: Comprehensive exception handling and graceful fallbacks
- **Testing**: Built-in validation and quality checks
- **Documentation**: Extensive inline documentation and examples

## 📄 License & Citation

This framework is part of the Baton Rouge Housing and Health project. When using this framework in research or policy work, please cite the comprehensive nature of the analysis and data sources used.

---

**🏠 Baton Rouge Social Isolation & Loneliness Analysis Framework**  
*Comprehensive data-driven analysis for informed policy and intervention strategies*