"""
PowerPoint Visual Elements Generator
Creates exportable chart specifications and design templates for the Baton Rouge Social Isolation Framework presentation

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import json
from datetime import datetime

def create_chart_specifications():
    """Generate detailed chart specifications for PowerPoint creation"""
    
    chart_specs = {
        "data_integration_matrix": {
            "type": "table_with_progress_bars",
            "title": "Data Source Integration Matrix",
            "columns": ["Data Source", "Indicators", "Coverage", "Update Frequency", "Status"],
            "data": [
                ["🏠 Census ACS", "50+", "All Tracts", "Annual", "✅ 100%"],
                ["🏛️ Municipal", "25+", "Citywide", "Monthly", "✅ 100%"],
                ["🏥 CDC PLACES", "27", "All Tracts", "Annual", "✅ 100%"],
                ["🌍 Environmental", "15+", "Regional", "Quarterly", "✅ 100%"],
                ["🚔 Crime Data", "20+", "Citywide", "Daily", "✅ 100%"],
                ["🗺️ Spatial", "10+", "All Tracts", "Annual", "✅ 100%"],
                ["📊 Isolation", "12", "Calculated", "On-Demand", "✅ 100%"]
            ],
            "styling": {
                "colors": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"],
                "progress_bar_column": 4,
                "highlight_total": True
            }
        },
        
        "framework_architecture": {
            "type": "hierarchical_flowchart",
            "title": "Framework Architecture",
            "levels": [
                {
                    "level": 1,
                    "items": ["Unified Controller (BatonRougeSocialIsolationFramework)"]
                },
                {
                    "level": 2,
                    "items": ["Configuration Management", "Data Sources", "Analytics Engine"]
                },
                {
                    "level": 3,
                    "items": ["JSON Config", "API Keys", "Census ACS", "Municipal", "Health", "Environment", "Crime", "Risk Scores", "Spatial Analysis", "Trend Analysis", "Reports"]
                }
            ],
            "connections": [
                {"from": "Unified Controller", "to": ["Configuration Management", "Data Sources", "Analytics Engine"]},
                {"from": "Configuration Management", "to": ["JSON Config", "API Keys"]},
                {"from": "Data Sources", "to": ["Census ACS", "Municipal", "Health", "Environment", "Crime"]},
                {"from": "Analytics Engine", "to": ["Risk Scores", "Spatial Analysis", "Trend Analysis", "Reports"]}
            ]
        },
        
        "workflow_timeline": {
            "type": "gantt_chart",
            "title": "5-Phase Analysis Pipeline",
            "phases": [
                {"name": "Data Collection", "duration": 10, "components": ["ACS", "Municipal", "Health", "Environmental", "Crime"]},
                {"name": "Spatial Analysis", "duration": 5, "components": ["Boundaries", "Joins", "Densities"]},
                {"name": "Isolation Analysis", "duration": 8, "components": ["Housing Quality", "Risk Scoring", "Vulnerability", "Composite"]},
                {"name": "Results Generation", "duration": 3, "components": ["Summary", "Policy", "Quality"]},
                {"name": "Output Organization", "duration": 2, "components": ["Structure", "Master File", "Documentation"]}
            ],
            "total_time": "15-30 minutes",
            "styling": {
                "colors": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#8B5A3C"],
                "show_progress": True,
                "animate": True
            }
        },
        
        "impact_comparison": {
            "type": "before_after_comparison",
            "title": "Research Transformation Impact",
            "categories": [
                {
                    "metric": "Processing Time",
                    "before": "Weeks",
                    "after": "15-30 minutes",
                    "improvement": "90% reduction"
                },
                {
                    "metric": "Data Integration",
                    "before": "Manual scripts",
                    "after": "7 unified sources",
                    "improvement": "100% automation"
                },
                {
                    "metric": "Quality Control",
                    "before": "Variable",
                    "after": "Built-in validation",
                    "improvement": "Consistent quality"
                },
                {
                    "metric": "Geographic Coverage",
                    "before": "Partial",
                    "after": "All census tracts",
                    "improvement": "Complete coverage"
                },
                {
                    "metric": "Technical Expertise",
                    "before": "High requirement",
                    "after": "User-friendly",
                    "improvement": "Accessible to all"
                }
            ],
            "styling": {
                "before_color": "#C73E1D",
                "after_color": "#2E86AB",
                "improvement_highlight": "#F18F01"
            }
        },
        
        "capability_dashboard": {
            "type": "capability_matrix",
            "title": "Research Capabilities Dashboard",
            "dimensions": [
                {
                    "name": "Housing Quality",
                    "metrics": ["Structure", "Affordability", "Maintenance"],
                    "count": "15+ indicators",
                    "color": "#2E86AB"
                },
                {
                    "name": "Social Connectivity",
                    "metrics": ["Transport", "Digital", "Resources"],
                    "count": "12+ indicators",
                    "color": "#A23B72"
                },
                {
                    "name": "Health Vulnerability",
                    "metrics": ["Disease", "Healthcare", "Environment"],
                    "count": "18+ indicators",
                    "color": "#F18F01"
                },
                {
                    "name": "Economic Security",
                    "metrics": ["Employment", "Financial", "Mobility"],
                    "count": "10+ indicators",
                    "color": "#C73E1D"
                },
                {
                    "name": "Spatial Intelligence",
                    "metrics": ["Risk Maps", "Proximity", "Clusters"],
                    "count": "8+ indicators",
                    "color": "#8B5A3C"
                },
                {
                    "name": "Policy Outputs",
                    "metrics": ["Targeting", "Resources", "Evaluation"],
                    "count": "5+ outputs",
                    "color": "#6A994E"
                }
            ]
        },
        
        "scalability_roadmap": {
            "type": "timeline_roadmap",
            "title": "Scalability & Growth Roadmap",
            "milestones": [
                {
                    "year": "2025",
                    "title": "Baton Rouge Foundation",
                    "achievements": ["Complete Framework", "7 Data Sources", "Production Ready", "Quality Assurance"],
                    "status": "completed"
                },
                {
                    "year": "2026",
                    "title": "Regional Expansion",
                    "achievements": ["New Orleans", "Shreveport", "Lafayette", "Multi-City Analysis"],
                    "status": "planned"
                },
                {
                    "year": "2027",
                    "title": "Advanced Analytics",
                    "achievements": ["Machine Learning", "Real-Time Data", "Network Analysis", "Intervention Modeling"],
                    "status": "future"
                },
                {
                    "year": "2028+",
                    "title": "National Platform",
                    "achievements": ["Multi-State Network", "Federal Integration", "Academic Consortium", "Policy Partnership"],
                    "status": "vision"
                }
            ]
        }
    }
    
    return chart_specs

def create_design_templates():
    """Generate design template specifications"""
    
    design_templates = {
        "color_palette": {
            "primary": "#2E86AB",  # Professional Blue
            "secondary": "#A23B72",  # Accent Purple
            "tertiary": "#F18F01",  # Highlight Orange
            "quaternary": "#C73E1D",  # Alert Red
            "neutral": "#6C757D",  # Gray
            "success": "#6A994E",  # Green
            "background": "#FFFFFF",  # White
            "text_primary": "#212529",  # Dark Gray
            "text_secondary": "#6C757D"  # Medium Gray
        },
        
        "typography": {
            "title_font": "Segoe UI",
            "header_font": "Segoe UI Semibold",
            "body_font": "Calibri",
            "code_font": "Consolas",
            "title_size": 32,
            "header_size": 24,
            "subheader_size": 18,
            "body_size": 14,
            "caption_size": 12
        },
        
        "layout_grid": {
            "slide_width": 1920,
            "slide_height": 1080,
            "margin_top": 80,
            "margin_bottom": 80,
            "margin_left": 100,
            "margin_right": 100,
            "content_width": 1720,
            "content_height": 920,
            "title_area_height": 120,
            "footer_area_height": 60
        },
        
        "icon_library": {
            "housing": "🏠",
            "data": "📊",
            "analysis": "📈",
            "policy": "🏛️",
            "health": "🏥",
            "environment": "🌍",
            "crime": "🚔",
            "spatial": "🗺️",
            "success": "✅",
            "warning": "⚠️",
            "info": "ℹ️",
            "clock": "⏱️",
            "target": "🎯",
            "rocket": "🚀",
            "shield": "🛡️"
        },
        
        "slide_layouts": {
            "title_slide": {
                "background": "gradient_blue",
                "title_position": "center",
                "subtitle_position": "center_below",
                "logo_position": "bottom_right"
            },
            "content_slide": {
                "background": "white",
                "title_position": "top_left",
                "content_area": "main_center",
                "footer": "slide_number"
            },
            "two_column": {
                "background": "white",
                "title_position": "top_center",
                "left_column": "50%",
                "right_column": "50%",
                "gap": "40px"
            },
            "dashboard": {
                "background": "light_gray",
                "title_position": "top_center",
                "grid": "3x2",
                "card_style": "elevated"
            }
        }
    }
    
    return design_templates

def create_animation_specifications():
    """Generate animation and transition specifications"""
    
    animations = {
        "slide_transitions": {
            "default": "fade",
            "duration": 0.5,
            "special_slides": {
                "title": "zoom_in",
                "architecture": "slide_from_left",
                "workflow": "cascade",
                "impact": "split"
            }
        },
        
        "element_animations": {
            "bullet_points": {
                "type": "appear",
                "timing": "after_previous",
                "delay": 0.3
            },
            "charts": {
                "type": "grow",
                "timing": "with_previous",
                "duration": 1.0
            },
            "progress_bars": {
                "type": "wipe_left_to_right",
                "timing": "after_previous",
                "duration": 1.5
            },
            "workflow_arrows": {
                "type": "draw",
                "timing": "after_previous",
                "duration": 0.8
            }
        },
        
        "interactive_elements": {
            "hover_effects": {
                "charts": "highlight_segment",
                "buttons": "color_change",
                "icons": "scale_up"
            },
            "click_actions": {
                "drill_down": "reveal_details",
                "navigation": "jump_to_slide",
                "external_links": "open_browser"
            }
        }
    }
    
    return animations

def generate_powerpoint_assets():
    """Generate all PowerPoint assets and specifications"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate all specifications
    chart_specs = create_chart_specifications()
    design_templates = create_design_templates()
    animations = create_animation_specifications()
    
    # Combine into comprehensive package
    powerpoint_package = {
        "metadata": {
            "title": "Baton Rouge Social Isolation Framework - PowerPoint Assets",
            "created": timestamp,
            "version": "1.0",
            "total_slides": 12,
            "estimated_duration": "25-30 minutes"
        },
        "chart_specifications": chart_specs,
        "design_templates": design_templates,
        "animation_specifications": animations,
        "slide_specific_notes": {
            "slide_1": "Use map background of Baton Rouge with census tract outlines",
            "slide_3": "Create hierarchical flowchart with animated connections",
            "slide_4": "Implement sortable table with progress bars",
            "slide_5": "Use Gantt chart style timeline with phase indicators",
            "slide_6": "Design 6-panel capability dashboard with hover effects",
            "slide_8": "Create interactive directory tree visualization",
            "slide_9": "Use split-screen before/after comparison layout",
            "slide_11": "Timeline roadmap with milestone markers and status indicators",
            "slide_12": "Call-to-action layout with prominent next steps"
        }
    }
    
    return powerpoint_package

def main():
    """Generate PowerPoint visual assets and specifications"""
    
    print("🎨 Generating Enhanced PowerPoint Visual Assets...")
    print("=" * 60)
    
    # Generate comprehensive package
    package = generate_powerpoint_assets()
    
    # Save to JSON file for reference
    filename = f"PowerPoint_Visual_Assets_{package['metadata']['created']}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(package, f, indent=2, ensure_ascii=False)
    
    print("📊 CHART SPECIFICATIONS GENERATED:")
    print("  ✅ Data Integration Matrix")
    print("  ✅ Framework Architecture Flowchart") 
    print("  ✅ Workflow Timeline (Gantt style)")
    print("  ✅ Impact Comparison (Before/After)")
    print("  ✅ Capability Dashboard (6-panel)")
    print("  ✅ Scalability Roadmap (Timeline)")
    
    print("\n🎨 DESIGN TEMPLATES CREATED:")
    print("  ✅ Professional Color Palette")
    print("  ✅ Typography Specifications")
    print("  ✅ Layout Grid System")
    print("  ✅ Icon Library")
    print("  ✅ Slide Layout Templates")
    
    print("\n🎬 ANIMATION SPECIFICATIONS:")
    print("  ✅ Slide Transitions")
    print("  ✅ Element Animations")
    print("  ✅ Interactive Effects")
    
    print(f"\n📁 Assets saved to: {filename}")
    print("\n🚀 POWERPOINT CREATION INSTRUCTIONS:")
    print("=" * 60)
    print("1. Open PowerPoint and create new presentation")
    print("2. Apply design template using color palette and fonts")
    print("3. Create charts using specifications in JSON file")
    print("4. Add animations following timing specifications")
    print("5. Test interactive elements and transitions")
    print("\n🎯 Ready for professional presentation creation!")

if __name__ == "__main__":
    main()