#!/usr/bin/env python3
"""Test script to verify CSV export properly handles multi-value fields"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.enhanced_markdown_processor import LandingAIMarkdownProcessor
import json
import csv
from io import StringIO

def test_csv_export_with_arrays():
    """Test that array values are properly formatted in CSV export"""
    
    # Test data with multi-value fields (like apex_id)
    test_data = {
        "apex_id": [
            "25USOA21345", "25USOA47643", "25USOA27031", "25USOA16720", 
            "25USOA35162", "25USOA47492", "25USOA48074", "25USOA42723", 
            "25USOA20491", "25USOA14183", "25USOA17712", "25USOA12704", 
            "25USOA13352", "25USOA24381", "25USOA36028", "25USOA11669", 
            "25USOA03793", "25USOA40804", "25USOA16952", "25USOA12064", 
            "25USOA30165", "25USOA09215", "25USOA06796", "25USOA09205", 
            "25USOA43414", "25USOA24699", "25USOA11541", "25USOA07233", 
            "25USOA04468", "25USOA11286"
        ],
        "document_type": "invoice",
        "date": ["2024-01-15", "2024-01-16", "2024-01-17"],
        "single_value": "test_value"
    }
    
    # Convert to JSON string (simulating database storage)
    extracted_data_json = json.dumps(test_data)
    
    # Test CSV extraction
    csv_result = LandingAIMarkdownProcessor.extract_clean_csv_data(
        markdown="",  # Empty markdown for this test
        extracted_data=extracted_data_json
    )
    
    print("Generated CSV Output:")
    print("-" * 50)
    print(csv_result)
    print("-" * 50)
    
    # Parse the CSV to verify it's valid
    csv_reader = csv.reader(StringIO(csv_result))
    rows = list(csv_reader)
    
    if len(rows) >= 2:
        headers = rows[0]
        values = rows[1]
        
        print("\nParsed CSV:")
        for header, value in zip(headers, values):
            print(f"  {header}: {value[:100]}...")  # Truncate long values for display
        
        # Check that apex_id values are semicolon-separated, not Python list format
        apex_id_idx = headers.index('apex_id')
        apex_id_value = values[apex_id_idx]
        
        # Verify it doesn't contain Python list syntax
        assert not apex_id_value.startswith('['), "CSV should not contain Python list syntax"
        assert not apex_id_value.endswith(']'), "CSV should not contain Python list syntax"
        assert "'" not in apex_id_value, "CSV should not contain Python string quotes"
        
        # Verify it's semicolon-separated
        assert '; ' in apex_id_value, "Multi-value fields should be semicolon-separated"
        
        # Count the values
        apex_ids = apex_id_value.split('; ')
        print(f"\n✅ Success! Found {len(apex_ids)} apex_id values properly formatted")
        print(f"   First 3 values: {apex_ids[:3]}")
        
        # Check date field (also multi-value)
        date_idx = headers.index('date')
        date_value = values[date_idx]
        assert '; ' in date_value, "Date field should be semicolon-separated"
        dates = date_value.split('; ')
        print(f"✅ Found {len(dates)} date values: {dates}")
        
        # Check single value field
        single_idx = headers.index('single_value')
        single_value = values[single_idx]
        assert '; ' not in single_value, "Single value should not have semicolons"
        print(f"✅ Single value field correct: {single_value}")
        
        print("\n✅ All tests passed! CSV export properly handles multi-value fields.")
        
        # Test Excel compatibility
        print("\n📊 Excel Import Instructions:")
        print("1. The semicolon-separated values can be split in Excel using:")
        print("   - Data > Text to Columns > Delimited > Semicolon")
        print("2. Or use Power Query to expand the multi-value fields")
        
    else:
        print("❌ Error: CSV doesn't have expected rows")
        
    return csv_result

def test_list_of_dicts():
    """Test CSV export with list of dictionaries"""
    test_data = [
        {"id": "001", "values": ["A", "B", "C"], "name": "First"},
        {"id": "002", "values": ["D", "E"], "name": "Second"},
        {"id": "003", "values": ["F"], "name": "Third"}
    ]
    
    csv_result = LandingAIMarkdownProcessor.extract_clean_csv_data(
        markdown="",
        extracted_data=json.dumps(test_data)
    )
    
    print("\n\nList of Dicts CSV Output:")
    print("-" * 50)
    print(csv_result)
    print("-" * 50)
    
    # Verify the CSV
    csv_reader = csv.reader(StringIO(csv_result))
    rows = list(csv_reader)
    
    assert len(rows) == 4, "Should have header + 3 data rows"
    
    # Check that multi-value 'values' field is properly formatted
    for i, row in enumerate(rows[1:], 1):
        values_field = row[1]  # 'values' is second column
        assert not values_field.startswith('['), f"Row {i} should not have Python list syntax"
        print(f"✅ Row {i} values field: {values_field}")
    
    print("✅ List of dicts test passed!")

if __name__ == "__main__":
    print("Testing CSV Export with Multi-Value Fields")
    print("=" * 60)
    
    # Test single dict with array values
    test_csv_export_with_arrays()
    
    # Test list of dicts with array values
    test_list_of_dicts()
    
    print("\n" + "=" * 60)
    print("All CSV export tests completed successfully! 🎉")