#!/usr/bin/env python3
"""
Debug script to find the exact location of extra placeholders in VALUES clause
"""
import re

# The VALUES clause from the INSERT statement
values_clause = """
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
"""

def analyze_placeholders(values_clause):
    """Analyze the VALUES clause to find placeholder patterns"""
    # Split by lines and clean up
    lines = [line.strip() for line in values_clause.strip().split('\n') if line.strip()]
    
    print("=== VALUES CLAUSE ANALYSIS ===")
    print()
    
    total_placeholders = 0
    line_number = 1
    
    for line in lines:
        # Count %s in this line
        placeholders_in_line = line.count('%s')
        total_placeholders += placeholders_in_line
        
        print(f"Line {line_number}: {placeholders_in_line} placeholders")
        print(f"  Content: {line}")
        print()
        
        line_number += 1
    
    print(f"Total placeholders: {total_placeholders}")
    
    # Now let's count them manually by splitting
    all_placeholders = values_clause.replace('\n', '').replace(' ', '')
    placeholder_list = all_placeholders.split(',')
    
    print(f"\n=== MANUAL COUNT ===")
    print(f"Split by comma: {len(placeholder_list)} items")
    
    # Show each placeholder with its position
    for i, placeholder in enumerate(placeholder_list):
        if placeholder.strip():
            print(f"{i+1:2d}. {placeholder.strip()}")
    
    return total_placeholders

# Analyze the placeholders
analyze_placeholders(values_clause)
