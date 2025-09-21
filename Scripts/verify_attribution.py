#!/usr/bin/env python3
"""
Attribution Verification Script
Checks that all script files have proper author attribution

Author: Olabode Oluwaseun Ajayi
Created: September 2025
Repository: DataKind-DC/Baton-Rouge-Housing-and-Health
Contact: github.com/DataKind-DC
"""

import os
import glob

def check_attribution():
    """Check all script files for proper attribution"""
    
    script_dir = "/Users/boratonaj/Documents/Personal_Project/Baton-Rouge-Housing-and-Health/Scripts"
    
    # File patterns to check
    patterns = {
        'Python': '*.py',
        'R': '*.R', 
        'Shell': '*.sh'
    }
    
    results = {}
    
    for file_type, pattern in patterns.items():
        results[file_type] = {'attributed': [], 'missing': []}
        
        files = glob.glob(os.path.join(script_dir, pattern))
        
        for file_path in files:
            filename = os.path.basename(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'Author: Olabode Oluwaseun Ajayi' in content:
                    results[file_type]['attributed'].append(filename)
                else:
                    results[file_type]['missing'].append(filename)
                    
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    # Display results
    print("🎯 ATTRIBUTION VERIFICATION REPORT")
    print("=" * 50)
    
    total_attributed = 0
    total_files = 0
    
    for file_type, data in results.items():
        attributed = len(data['attributed'])
        missing = len(data['missing'])
        total = attributed + missing
        
        total_attributed += attributed
        total_files += total
        
        print(f"\n📝 {file_type.upper()} FILES:")
        print(f"   ✅ Attributed: {attributed}/{total}")
        print(f"   ❌ Missing: {missing}/{total}")
        
        if data['attributed']:
            print(f"   ✅ Files with attribution:")
            for filename in sorted(data['attributed']):
                print(f"      • {filename}")
        
        if data['missing']:
            print(f"   ❌ Files missing attribution:")
            for filename in sorted(data['missing']):
                print(f"      • {filename}")
    
    print(f"\n🏆 OVERALL ATTRIBUTION STATUS:")
    print(f"   Total Files: {total_files}")
    print(f"   Attributed: {total_attributed}")
    print(f"   Coverage: {total_attributed/total_files*100:.1f}%")
    
    if total_attributed == total_files:
        print("   🎉 ALL FILES PROPERLY ATTRIBUTED!")
    else:
        print(f"   ⚠️  {total_files - total_attributed} files need attribution")
    
    return results

if __name__ == "__main__":
    check_attribution()