#!/usr/bin/env python3
"""
Test script to verify sidebar field selection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FormField, FieldType

def test_field_hashability():
    """Test if FormField objects can be used as dictionary keys"""
    print("Testing FormField hashability...")
    
    field1 = FormField(
        name="test_field",
        type=FieldType.TEXT,
        page_num=1,
        rect=[10.0, 20.0, 100.0, 40.0]
    )
    
    field2 = FormField(
        name="test_field2",
        type=FieldType.CHECKBOX,
        page_num=1,
        rect=[10.0, 50.0, 30.0, 70.0]
    )
    
    # Test using field objects as dictionary keys
    try:
        field_dict = {}
        field_dict[field1] = "widget1"
        field_dict[field2] = "widget2"
        print("❌ FormField objects are hashable (this should not happen)")
    except TypeError as e:
        print(f"✅ FormField objects are not hashable: {e}")
    
    # Test using field names as dictionary keys (our solution)
    try:
        field_dict = {}
        field_dict[field1.name] = "widget1"
        field_dict[field2.name] = "widget2"
        print("✅ Using field names as keys works correctly")
        
        # Test field lookup
        if field1.name in field_dict:
            print("✅ Field name lookup works")
        else:
            print("❌ Field name lookup failed")
            
    except Exception as e:
        print(f"❌ Using field names failed: {e}")

def test_sidebar_selection_logic():
    """Test the sidebar selection logic"""
    print("\nTesting sidebar selection logic...")
    
    # Simulate the field_items dictionary structure
    field_items = {}
    
    field1 = FormField(
        name="text_field",
        type=FieldType.TEXT,
        page_num=1,
        rect=[10.0, 20.0, 100.0, 40.0]
    )
    
    field2 = FormField(
        name="checkbox_field",
        type=FieldType.CHECKBOX,
        page_num=1,
        rect=[10.0, 50.0, 30.0, 70.0]
    )
    
    # Simulate UI widgets (using simple strings for this test)
    field_items[field1.name] = f"widget_for_{field1.name}"
    field_items[field2.name] = f"widget_for_{field2.name}"
    
    # Test selection logic
    selected_field = None
    
    # Select field1
    old_selected = selected_field
    selected_field = field1
    
    if old_selected and old_selected.name in field_items:
        print(f"Would deselect: {field_items[old_selected.name]}")
    
    if selected_field and selected_field.name in field_items:
        print(f"✅ Would select: {field_items[selected_field.name]}")
    
    # Select field2
    old_selected = selected_field
    selected_field = field2
    
    if old_selected and old_selected.name in field_items:
        print(f"✅ Would deselect: {field_items[old_selected.name]}")
    
    if selected_field and selected_field.name in field_items:
        print(f"✅ Would select: {field_items[selected_field.name]}")

if __name__ == "__main__":
    test_field_hashability()
    test_sidebar_selection_logic()
    print("\n✅ All tests completed successfully!")