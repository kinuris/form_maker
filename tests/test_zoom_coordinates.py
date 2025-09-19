#!/usr/bin/env python3
"""
Test script to validate zoom and coordinate functionality
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import AppConstants

def test_coordinate_conversion():
    """Test coordinate conversion at different zoom levels"""
    print("Testing coordinate conversion at different zoom levels:")
    print("-" * 60)
    
    # Test canvas coordinates
    canvas_x, canvas_y = 150, 200
    canvas_width, canvas_height = 100, 50
    
    # Test different zoom levels
    zoom_levels = [0.5, 1.0, 1.5, 2.0]
    
    for zoom in zoom_levels:
        # Convert canvas to PDF coordinates (simulate the new method)
        pdf_x = (canvas_x - AppConstants.CANVAS_OFFSET) / zoom
        pdf_y = (canvas_y - AppConstants.CANVAS_OFFSET) / zoom
        pdf_width = canvas_width / zoom
        pdf_height = canvas_height / zoom
        
        # Convert back to canvas coordinates
        back_canvas_x = pdf_x * zoom + AppConstants.CANVAS_OFFSET
        back_canvas_y = pdf_y * zoom + AppConstants.CANVAS_OFFSET
        back_canvas_width = pdf_width * zoom
        back_canvas_height = pdf_height * zoom
        
        print(f"Zoom {zoom*100:4.0f}%:")
        print(f"  Canvas: ({canvas_x}, {canvas_y}) {canvas_width}x{canvas_height}")
        print(f"  PDF:    ({pdf_x:.1f}, {pdf_y:.1f}) {pdf_width:.1f}x{pdf_height:.1f}")
        print(f"  Back:   ({back_canvas_x:.1f}, {back_canvas_y:.1f}) {back_canvas_width:.1f}x{back_canvas_height:.1f}")
        
        # Check if conversion is accurate
        x_accurate = abs(back_canvas_x - canvas_x) < 0.1
        y_accurate = abs(back_canvas_y - canvas_y) < 0.1
        w_accurate = abs(back_canvas_width - canvas_width) < 0.1
        h_accurate = abs(back_canvas_height - canvas_height) < 0.1
        
        accuracy = "✅ ACCURATE" if all([x_accurate, y_accurate, w_accurate, h_accurate]) else "❌ INACCURATE"
        print(f"  Result: {accuracy}")
        print()

def test_zoom_constants():
    """Test that zoom constants are properly defined"""
    print("Testing zoom constants:")
    print("-" * 30)
    
    constants_to_check = [
        ('MIN_ZOOM', AppConstants.MIN_ZOOM),
        ('MAX_ZOOM', AppConstants.MAX_ZOOM),
        ('DEFAULT_ZOOM', AppConstants.DEFAULT_ZOOM),
        ('ZOOM_STEP', AppConstants.ZOOM_STEP),
        ('ZOOM_WHEEL_FACTOR', AppConstants.ZOOM_WHEEL_FACTOR),
        ('PDF_DPI', AppConstants.PDF_DPI),
        ('CANVAS_OFFSET', AppConstants.CANVAS_OFFSET)
    ]
    
    for name, value in constants_to_check:
        print(f"  {name}: {value}")
    
    print(f"\nZoom range: {AppConstants.MIN_ZOOM*100:.0f}% to {AppConstants.MAX_ZOOM*100:.0f}%")
    print(f"Default zoom: {AppConstants.DEFAULT_ZOOM*100:.0f}%")
    print()

if __name__ == "__main__":
    print("PDF Form Maker - Zoom and Coordinate Test")
    print("=" * 50)
    print()
    
    test_zoom_constants()
    test_coordinate_conversion()
    
    print("Test completed! ✅")