#!/bin/bash

# Baton Rouge Social Isolation Framework - Visualization Viewer
# Quick access script to open all generated visualizations
#
# Author: Olabode Oluwaseun Ajayi
# Created: September 2025
# Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
# Contact: github.com/DataKind-DC

echo "🎯 BATON ROUGE SOCIAL ISOLATION FRAMEWORK"
echo "   VISUALIZATION DASHBOARD VIEWER"
echo "================================================"
echo ""

# Set base directory
BASE_DIR="/Users/boratonaj/Documents/Personal_Project/Baton-Rouge-Housing-and-Health/Scripts/framework_analysis_output"

echo "📊 Available Visualizations:"
echo ""

# Function to open visualization
open_viz() {
    local file_path="$1"
    local description="$2"
    
    if [ -f "$file_path" ]; then
        echo "✅ $description"
        echo "   📁 $file_path"
        read -p "   🚀 Open this visualization? (y/n): " choice
        if [[ $choice == [Yy]* ]]; then
            open "$file_path"
            echo "   🌐 Opened in browser!"
        fi
        echo ""
    else
        echo "❌ $description - File not found"
        echo ""
    fi
}

# Master Dashboard
echo "🏆 MASTER DASHBOARD:"
open_viz "$BASE_DIR/INTEGRATED_DASHBOARD.html" "Complete Framework Overview"

# Analysis Visualizations
echo "📊 ANALYSIS VISUALIZATIONS:"
open_viz "$BASE_DIR/analysis/housing_quality_visualization.html" "Housing Quality Analysis Dashboard"
open_viz "$BASE_DIR/analysis/social_isolation_visualization.html" "Social Isolation Analysis Dashboard"
open_viz "$BASE_DIR/analysis/vulnerability_index_visualization.html" "Vulnerability Index Dashboard"
open_viz "$BASE_DIR/analysis/geographic_clustering_visualization.html" "Geographic Clustering Analysis"

# Spatial Visualizations
echo "🗺️ SPATIAL VISUALIZATIONS:"
open_viz "$BASE_DIR/spatial/geographic_coverage_map.html" "Interactive Geographic Coverage Map"
open_viz "$BASE_DIR/spatial/tract_council_visualization.html" "Census Tract - Council District Crosswalk"

# Report Visualizations
echo "📋 REPORT VISUALIZATIONS:"
open_viz "$BASE_DIR/reports/comprehensive_summary_dashboard.html" "Executive Summary Dashboard"
open_viz "$BASE_DIR/reports/policy_recommendations_dashboard.html" "Policy Recommendations Dashboard"
open_viz "$BASE_DIR/reports/data_quality_dashboard.html" "Data Quality Assessment Dashboard"

echo "🎉 All visualizations checked!"
echo "🌟 Framework analysis complete and ready for presentation!"
echo ""
echo "💡 Pro Tip: Start with the INTEGRATED_DASHBOARD.html for the complete overview,"
echo "   then explore individual dashboards for detailed analysis."