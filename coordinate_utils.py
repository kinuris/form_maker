#!/usr/bin/env python3
"""
Coordinate transformation utilities for PDF Form Maker

This module handles the conversion between different coordinate systems:
- Canvas coordinates (top-left origin, y increases downward)
- PDF coordinates (bottom-left origin, y increases upward)
"""

class CoordinateTransformer:
    """Handles coordinate transformations between canvas and PDF coordinate systems"""
    
    def __init__(self, pdf_scale, canvas_offset=25):
        """
        Initialize the coordinate transformer
        
        Args:
            pdf_scale (float): Scale factor used when displaying PDF on canvas
            canvas_offset (int): Pixel offset where PDF image is placed on canvas
        """
        self.pdf_scale = pdf_scale
        self.canvas_offset = canvas_offset
    
    def canvas_to_pdf(self, canvas_rect, page_height):
        """
        Convert canvas coordinates to PDF coordinates
        
        Args:
            canvas_rect (list): [x1, y1, x2, y2] in canvas coordinates
            page_height (float): Height of the PDF page in points
            
        Returns:
            list: [x1, y1, x2, y2] in PDF coordinates
        """
        canvas_x1, canvas_y1, canvas_x2, canvas_y2 = canvas_rect
        
        # Step 1: Remove the canvas offset (PDF image is placed at offset on canvas)
        relative_x1 = canvas_x1 - self.canvas_offset
        relative_y1 = canvas_y1 - self.canvas_offset
        relative_x2 = canvas_x2 - self.canvas_offset
        relative_y2 = canvas_y2 - self.canvas_offset
        
        # Step 2: Scale back from display coordinates to PDF coordinates
        pdf_x1 = relative_x1 / self.pdf_scale
        pdf_y1 = relative_y1 / self.pdf_scale
        pdf_x2 = relative_x2 / self.pdf_scale
        pdf_y2 = relative_y2 / self.pdf_scale
        
        # Step 3: Convert coordinate systems (direct mapping for now)
        final_x1 = pdf_x1
        final_y1 = pdf_y1
        final_x2 = pdf_x2
        final_y2 = pdf_y2
        
        # Ensure proper rectangle ordering
        if final_x1 > final_x2:
            final_x1, final_x2 = final_x2, final_x1
        if final_y1 > final_y2:
            final_y1, final_y2 = final_y2, final_y1
            
        return [final_x1, final_y1, final_x2, final_y2]
    
    def pdf_to_canvas(self, pdf_rect, page_height):
        """
        Convert PDF coordinates to canvas coordinates
        
        Args:
            pdf_rect (list): [x1, y1, x2, y2] in PDF coordinates
            page_height (float): Height of the PDF page in points
            
        Returns:
            list: [x1, y1, x2, y2] in canvas coordinates
        """
        pdf_x1, pdf_y1, pdf_x2, pdf_y2 = pdf_rect
        
        # Step 1: Convert coordinate systems (direct mapping for now)
        relative_x1 = pdf_x1
        relative_y1 = pdf_y1
        relative_x2 = pdf_x2
        relative_y2 = pdf_y2
        
        # Step 2: Scale to display coordinates
        display_x1 = relative_x1 * self.pdf_scale
        display_y1 = relative_y1 * self.pdf_scale
        display_x2 = relative_x2 * self.pdf_scale
        display_y2 = relative_y2 * self.pdf_scale
        
        # Step 3: Add canvas offset
        canvas_x1 = display_x1 + self.canvas_offset
        canvas_y1 = display_y1 + self.canvas_offset
        canvas_x2 = display_x2 + self.canvas_offset
        canvas_y2 = display_y2 + self.canvas_offset
        
        return [canvas_x1, canvas_y1, canvas_x2, canvas_y2]
    
    def clamp_to_page(self, pdf_rect, page_width, page_height, min_size=10):
        """
        Clamp PDF coordinates to page boundaries and ensure minimum size
        
        Args:
            pdf_rect (list): [x1, y1, x2, y2] in PDF coordinates
            page_width (float): Width of the PDF page
            page_height (float): Height of the PDF page
            min_size (float): Minimum width/height for the rectangle
            
        Returns:
            list: Clamped [x1, y1, x2, y2] coordinates
        """
        x1, y1, x2, y2 = pdf_rect
        
        # Clamp to page boundaries
        x1 = max(0, min(x1, page_width - min_size))
        y1 = max(0, min(y1, page_height - min_size))
        x2 = max(x1 + min_size, min(x2, page_width))
        y2 = max(y1 + min_size, min(y2, page_height))
        
        return [x1, y1, x2, y2]


def calculate_display_scale(canvas_size, page_size, max_scale=2.0, margin=50):
    """
    Calculate the scale factor for displaying a PDF page on canvas
    
    Args:
        canvas_size (tuple): (width, height) of the canvas
        page_size (tuple): (width, height) of the PDF page
        max_scale (float): Maximum allowed scale factor
        margin (int): Margin to leave around the PDF
        
    Returns:
        float: Scale factor to use for display
    """
    canvas_width, canvas_height = canvas_size
    page_width, page_height = page_size
    
    # Calculate scale factors for each dimension
    scale_x = (canvas_width - margin) / page_width
    scale_y = (canvas_height - margin) / page_height
    
    # Use the smaller scale factor to ensure the page fits
    scale = min(scale_x, scale_y, max_scale)
    
    return scale