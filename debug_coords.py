#!/usr/bin/env python3
"""
Simplified test to debug coordinate transformation issues
"""

import fitz
import tkinter as tk
from tkinter import filedialog, messagebox

def test_coordinate_mapping():
    """Test coordinate mapping between canvas and PDF"""
    
    # Open a test PDF
    try:
        doc = fitz.open("generated_form_mm.pdf")
        page = doc[0]
        page_rect = page.rect
        print(f"PDF page dimensions: {page_rect.width} x {page_rect.height} points")
        
        # Simulate canvas display scaling
        canvas_width = 800
        canvas_height = 600
        scale_x = (canvas_width - 50) / page_rect.width
        scale_y = (canvas_height - 50) / page_rect.height
        scale = min(scale_x, scale_y, 2.0)
        
        print(f"Canvas dimensions: {canvas_width} x {canvas_height}")
        print(f"Scale factor: {scale}")
        
        # Test a few coordinate mappings
        test_points = [
            (100, 100),  # Top-left area
            (300, 200),  # Center-left
            (500, 400),  # Center-right
        ]
        
        for canvas_x, canvas_y in test_points:
            print(f"\n--- Testing canvas point ({canvas_x}, {canvas_y}) ---")
            
            # Step 1: Remove image offset
            pdf_display_x = canvas_x - 25
            pdf_display_y = canvas_y - 25
            print(f"After removing offset: ({pdf_display_x}, {pdf_display_y})")
            
            # Step 2: Scale back to PDF size
            pdf_x = pdf_display_x / scale
            pdf_y = pdf_display_y / scale
            print(f"After scaling back: ({pdf_x}, {pdf_y})")
            
            # Step 3: Convert to PDF coordinate system (flip Y)
            final_x = pdf_x
            final_y = page_rect.height - pdf_y
            print(f"Final PDF coordinates: ({final_x}, {final_y})")
            
            # Verify it's within bounds
            if 0 <= final_x <= page_rect.width and 0 <= final_y <= page_rect.height:
                print("✓ Coordinates are within page bounds")
            else:
                print("✗ Coordinates are outside page bounds!")
        
        doc.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_coordinate_mapping()