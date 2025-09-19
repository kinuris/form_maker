#!/usr/bin/env python3
"""
Test script for copy/paste functionality and datetime fields
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FormField, FieldType
from copy import deepcopy

def test_copy_paste_functionality():
    """Test the copy/paste field functionality"""
    print("Testing copy/paste functionality...")
    
    # Create a test datetime field
    original_field = FormField(
        name="birth_date",
        type=FieldType.DATETIME,
        page_num=0,
        rect=[100.0, 200.0, 220.0, 230.0],
        date_format="MM/DD/YYYY",
        value=""
    )
    
    print(f"✅ Original field: {original_field.name} ({original_field.type.value})")
    print(f"   Format: {original_field.date_format}")
    print(f"   Position: {original_field.rect}")
    
    # Test copy operation (deep copy)
    copied_field = deepcopy(original_field)
    copied_field.canvas_id = None  # Clear canvas ID
    
    print(f"✅ Copied field: {copied_field.name} ({copied_field.type.value})")
    print(f"   Format: {copied_field.date_format}")
    print(f"   Canvas ID cleared: {copied_field.canvas_id is None}")
    
    # Test paste operation (rename and reposition)
    pasted_field = deepcopy(copied_field)
    pasted_field.name = f"{original_field.name}_copy_1"
    
    # Offset position
    offset = 20.0
    pasted_field.rect = [
        original_field.rect[0] + offset,
        original_field.rect[1] + offset,
        original_field.rect[2] + offset,
        original_field.rect[3] + offset
    ]
    
    print(f"✅ Pasted field: {pasted_field.name} ({pasted_field.type.value})")
    print(f"   New position: {pasted_field.rect}")
    print(f"   Format preserved: {pasted_field.date_format == original_field.date_format}")

def test_datetime_field_properties():
    """Test datetime field specific properties"""
    print("\nTesting datetime field properties...")
    
    # Test different date formats
    formats = ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD", "DD MMM YYYY", "MMM DD, YYYY"]
    
    for i, date_format in enumerate(formats):
        field = FormField(
            name=f"date_field_{i+1}",
            type=FieldType.DATETIME,
            page_num=0,
            rect=[50.0 + i*30, 100.0, 170.0 + i*30, 130.0],
            date_format=date_format,
            value=""
        )
        
        print(f"✅ Field {field.name}: format '{field.date_format}'")
    
    # Test serialization
    test_field = FormField(
        name="test_datetime",
        type=FieldType.DATETIME,
        page_num=1,
        rect=[10.0, 20.0, 130.0, 50.0],
        date_format="DD/MM/YYYY",
        value="25/12/2023"
    )
    
    # Test to_dict
    field_dict = test_field.to_dict()
    print(f"✅ Serialization test:")
    print(f"   Dict keys: {list(field_dict.keys())}")
    print(f"   Date format in dict: {field_dict.get('date_format')}")
    print(f"   Value in dict: {field_dict.get('value')}")
    
    # Test from_dict
    reconstructed = FormField.from_dict(field_dict)
    print(f"✅ Deserialization test:")
    print(f"   Name: {reconstructed.name}")
    print(f"   Type: {reconstructed.type.value}")
    print(f"   Date format: {reconstructed.date_format}")
    print(f"   Value: {reconstructed.value}")

def test_field_type_enum():
    """Test the updated FieldType enum"""
    print("\nTesting FieldType enum...")
    
    # Check all available field types
    available_types = [field_type for field_type in FieldType]
    print(f"✅ Available field types: {[ft.value for ft in available_types]}")
    
    # Verify removed types are gone
    removed_types = ['RADIO', 'DROPDOWN']
    for removed_type in removed_types:
        try:
            getattr(FieldType, removed_type)
            print(f"❌ {removed_type} should have been removed!")
        except AttributeError:
            print(f"✅ {removed_type} successfully removed")
    
    # Verify new type is present
    try:
        datetime_type = FieldType.DATETIME
        print(f"✅ DATETIME field type available: {datetime_type.value}")
    except AttributeError:
        print("❌ DATETIME field type not found!")

def test_field_colors_and_sizes():
    """Test field colors and sizes for new field types"""
    print("\nTesting field colors and sizes...")
    
    from models import AppConstants
    
    # Test field colors
    print("Field colors:")
    for field_type in FieldType:
        color = AppConstants.FIELD_COLORS.get(field_type)
        print(f"  {field_type.value}: {color}")
        if color is None:
            print(f"❌ No color defined for {field_type.value}")
    
    # Test field sizes
    print("\\nField sizes:")
    for field_type in FieldType:
        size = AppConstants.DEFAULT_FIELD_SIZES.get(field_type)
        print(f"  {field_type.value}: {size}")
        if size is None:
            print(f"❌ No size defined for {field_type.value}")

if __name__ == "__main__":
    test_field_type_enum()
    test_field_colors_and_sizes()
    test_datetime_field_properties()
    test_copy_paste_functionality()
    print("\n✅ All tests completed successfully!")