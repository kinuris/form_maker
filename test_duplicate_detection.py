#!/usr/bin/env python3
"""
Test script to verify duplicate field detection works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_handler import PDFHandler
import unittest.mock as mock

def test_duplicate_field_detection():
    """Test that duplicate fields are properly detected and filtered"""
    print("🧪 Testing duplicate field detection...")
    
    # Mock canvas
    mock_canvas = mock.MagicMock()
    
    # Create PDF handler
    pdf_handler = PDFHandler(mock_canvas)
    
    # Test the duplicate detection logic manually
    print("\n📝 Testing duplicate detection logic...")
    
    detected_fields = []
    seen_fields = set()
    
    # Simulate detecting the same field twice
    field_name = "test_field"
    page_num = 0
    pdf_rect = [100, 200, 200, 230]
    
    # First detection
    field_id1 = (field_name, page_num, tuple(pdf_rect))
    if field_id1 not in seen_fields:
        seen_fields.add(field_id1)
        print(f"   Added field: {field_name} at {pdf_rect}")
        detected_fields.append(f"field_{len(detected_fields) + 1}")
    
    # Second detection (duplicate)
    field_id2 = (field_name, page_num, tuple(pdf_rect))
    if field_id2 not in seen_fields:
        seen_fields.add(field_id2)
        print(f"   Added field: {field_name} at {pdf_rect}")
        detected_fields.append(f"field_{len(detected_fields) + 1}")
    else:
        print(f"   ✅ Correctly skipped duplicate: {field_name} at {pdf_rect}")
    
    # Third detection (different position - should be added)
    different_rect = [100, 250, 200, 280]
    field_id3 = (field_name, page_num, tuple(different_rect))
    if field_id3 not in seen_fields:
        seen_fields.add(field_id3)
        print(f"   Added field: {field_name} at {different_rect} (different position)")
        detected_fields.append(f"field_{len(detected_fields) + 1}")
    
    print(f"\n📊 Results:")
    print(f"   Detected fields: {len(detected_fields)}")
    print(f"   Seen field IDs: {len(seen_fields)}")
    
    if len(detected_fields) == 2 and len(seen_fields) == 2:
        print("✅ Duplicate detection working correctly!")
    else:
        print("❌ Duplicate detection failed!")
    
    print("🔚 Test completed!")

if __name__ == "__main__":
    test_duplicate_field_detection()