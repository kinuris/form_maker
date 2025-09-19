#!/usr/bin/env python3
"""
Test script to verify coordinate transformation logic
"""

def test_coordinate_transformation():
    """Test the coordinate transformation from canvas to PDF"""
    
    # Simulate the transformation logic from the PDF Form Maker
    
    # Example values (these would come from the actual application)
    pdf_scale = 0.8  # Example scale factor
    canvas_image_offset = 25  # PDF image offset on canvas
    original_page_height = 792  # Standard US Letter height in points
    original_page_width = 612   # Standard US Letter width in points
    
    # Test case: Field placed at canvas coordinates (150, 100) with size (100, 30)
    canvas_x1, canvas_y1 = 150, 100
    canvas_x2, canvas_y2 = 250, 130
    
    print("=== Coordinate Transformation Test ===")
    print(f"Canvas coordinates: ({canvas_x1}, {canvas_y1}, {canvas_x2}, {canvas_y2})")
    print(f"PDF scale factor: {pdf_scale}")
    print(f"Canvas offset: {canvas_image_offset}")
    print(f"Original page size: {original_page_width} x {original_page_height}")
    print()
    
    # Step 1: Adjust for image offset
    pdf_display_x1 = canvas_x1 - canvas_image_offset
    pdf_display_y1 = canvas_y1 - canvas_image_offset
    pdf_display_x2 = canvas_x2 - canvas_image_offset
    pdf_display_y2 = canvas_y2 - canvas_image_offset
    
    print(f"After offset adjustment: ({pdf_display_x1}, {pdf_display_y1}, {pdf_display_x2}, {pdf_display_y2})")
    
    # Step 2: Scale back to original PDF dimensions
    pdf_x1 = pdf_display_x1 / pdf_scale
    pdf_y1 = pdf_display_y1 / pdf_scale
    pdf_x2 = pdf_display_x2 / pdf_scale
    pdf_y2 = pdf_display_y2 / pdf_scale
    
    print(f"After scale adjustment: ({pdf_x1}, {pdf_y1}, {pdf_x2}, {pdf_y2})")
    
    # Step 3: Flip Y-axis (canvas: top-left origin, PDF: bottom-left origin)
    final_x1 = pdf_x1
    final_y1 = original_page_height - pdf_y2  # Bottom of field
    final_x2 = pdf_x2
    final_y2 = original_page_height - pdf_y1  # Top of field
    
    print(f"Final PDF coordinates: ({final_x1}, {final_y1}, {final_x2}, {final_y2})")
    
    # Verify the transformation makes sense
    field_width = final_x2 - final_x1
    field_height = final_y2 - final_y1
    
    print(f"Field dimensions in PDF: {field_width} x {field_height} points")
    
    # Convert to more familiar units (1 inch = 72 points)
    field_width_inches = field_width / 72
    field_height_inches = field_height / 72
    
    print(f"Field dimensions in inches: {field_width_inches:.2f} x {field_height_inches:.2f}")
    
    # The field should be positioned relative to bottom-left corner of PDF
    distance_from_left = final_x1 / 72
    distance_from_bottom = final_y1 / 72
    
    print(f"Position from bottom-left corner: {distance_from_left:.2f}\" from left, {distance_from_bottom:.2f}\" from bottom")

if __name__ == "__main__":
    test_coordinate_transformation()