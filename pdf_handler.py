#!/usr/bin/env python3
"""
PDF Handler for PDF Form Maker

Handles PDF loading, display, and saving operations.
"""

import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io
import tkinter as tk
from typing import Optional, List, Tuple
from models import FormField, FieldType, AppConstants
from coordinate_utils import CoordinateTransformer, calculate_display_scale


class PDFHandler:
    """Handles PDF operations - loading, display, and saving"""
    
    def __init__(self, canvas: tk.Canvas):
        """
        Initialize the PDF handler
        
        Args:
            canvas: The tkinter Canvas widget for displaying PDF
        """
        self.canvas = canvas
        self.pdf_doc: Optional[fitz.Document] = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_scale = 1.0
        self.canvas_image = None
        self.coord_transformer: Optional[CoordinateTransformer] = None
    
    def load_pdf(self, file_path: str) -> bool:
        """
        Load a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Close existing document if any
            if self.pdf_doc:
                self.pdf_doc.close()
            
            # Open new document
            self.pdf_doc = fitz.open(file_path)
            self.total_pages = len(self.pdf_doc)
            self.current_page = 0
            
            print(f"PDF loaded: {self.total_pages} pages")
            return True
            
        except Exception as e:
            print(f"Failed to load PDF: {e}")
            return False
    
    def display_page(self, page_num: int = None) -> bool:
        """
        Display a PDF page on the canvas
        
        Args:
            page_num: Page number to display (uses current_page if None)
            
        Returns:
            True if displayed successfully, False otherwise
        """
        if not self.pdf_doc:
            return False
        
        if page_num is not None:
            self.current_page = page_num
        
        if self.current_page >= self.total_pages:
            return False
        
        try:
            # Get the page
            page = self.pdf_doc[self.current_page]
            page_rect = page.rect
            
            # Calculate scale to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not yet properly sized, use default
                canvas_width = 800
                canvas_height = 600
            
            self.pdf_scale = calculate_display_scale(
                (canvas_width, canvas_height),
                (page_rect.width, page_rect.height)
            )
            
            print(f"Display scaling: canvas={canvas_width}x{canvas_height}, "
                  f"PDF={page_rect.width}x{page_rect.height}, scale={self.pdf_scale:.3f}")
            
            # Create coordinate transformer
            self.coord_transformer = CoordinateTransformer(
                self.pdf_scale, 
                AppConstants.CANVAS_OFFSET
            )
            
            # Render page to pixmap
            matrix = fitz.Matrix(self.pdf_scale, self.pdf_scale)
            pixmap = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image then to PhotoImage
            img_data = pixmap.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            self.canvas_image = ImageTk.PhotoImage(pil_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(
                AppConstants.CANVAS_OFFSET, 
                AppConstants.CANVAS_OFFSET,
                anchor='nw',
                image=self.canvas_image,
                tags="pdf_page"
            )
            
            # Update canvas scroll region
            scroll_width = pixmap.width + AppConstants.CANVAS_OFFSET * 2
            scroll_height = pixmap.height + AppConstants.CANVAS_OFFSET * 2
            self.canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))
            
            return True
            
        except Exception as e:
            print(f"Failed to display page: {e}")
            return False
    
    def save_pdf_with_fields(self, file_path: str, fields: List[FormField]) -> bool:
        """
        Save the PDF with form fields
        
        Args:
            file_path: Path to save the PDF
            fields: List of form fields to add
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.pdf_doc or not self.coord_transformer:
            return False
        
        try:
            # Create a copy of the document for saving
            temp_doc = fitz.open()
            for page_num in range(len(self.pdf_doc)):
                temp_doc.insert_pdf(self.pdf_doc, from_page=page_num, to_page=page_num)
            
            # Add form fields to each page
            for field in fields:
                page = temp_doc[field.page_num]
                original_page_rect = page.rect
                
                # Convert canvas coordinates to PDF coordinates
                pdf_rect = self.coord_transformer.canvas_to_pdf(
                    field.rect, 
                    original_page_rect.height
                )
                
                # Clamp to page boundaries
                pdf_rect = self.coord_transformer.clamp_to_page(
                    pdf_rect,
                    original_page_rect.width,
                    original_page_rect.height
                )
                
                print(f"Field '{field.name}': canvas{field.rect} -> PDF{pdf_rect}")
                
                # Create the rectangle for PyMuPDF
                rect = fitz.Rect(*pdf_rect)
                
                # Add the appropriate widget based on field type
                self._add_widget_to_page(page, field, rect)
            
            # Save the document
            temp_doc.save(file_path, incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
            temp_doc.close()
            
            print(f"PDF saved successfully: {file_path}")
            return True
            
        except Exception as e:
            print(f"Failed to save PDF: {e}")
            return False
    
    def _add_widget_to_page(self, page: fitz.Page, field: FormField, rect: fitz.Rect):
        """
        Add a widget to a PDF page
        
        Args:
            page: PDF page to add widget to
            field: Form field data
            rect: Rectangle for the widget
        """
        widget = fitz.Widget()
        widget.field_name = field.name
        widget.rect = rect
        
        if field.type == FieldType.TEXT:
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_value = ""
            widget.text_font = "helv"
            widget.text_fontsize = 12
            widget.fill_color = (1, 1, 1)  # White background
            
        elif field.type == FieldType.CHECKBOX:
            widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
            widget.field_value = False
            widget.fill_color = (1, 1, 1)
            
        elif field.type == FieldType.RADIO:
            widget.field_type = fitz.PDF_WIDGET_TYPE_RADIOBUTTON
            widget.field_name = field.group or field.name
            widget.field_value = field.value or field.name
            widget.fill_color = (1, 1, 1)
            
        elif field.type == FieldType.DROPDOWN:
            widget.field_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
            widget.choice_values = field.options or ['Option 1', 'Option 2']
            widget.field_value = widget.choice_values[0] if widget.choice_values else ""
            widget.text_font = "helv"
            widget.text_fontsize = 11
            widget.fill_color = (1, 1, 1)
            
        elif field.type == FieldType.SIGNATURE:
            # For signature fields, create a text field with signature appearance
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_value = ""
            widget.text_font = "helv"
            widget.text_fontsize = 12
            widget.fill_color = (0.95, 0.95, 0.95)  # Light gray background
            widget.border_color = (0.5, 0.5, 0.5)
            widget.border_width = 2
        
        page.add_widget(widget)
    
    def get_page_rect(self, page_num: int = None) -> Optional[fitz.Rect]:
        """
        Get the rectangle of a PDF page
        
        Args:
            page_num: Page number (uses current_page if None)
            
        Returns:
            Page rectangle or None if not available
        """
        if not self.pdf_doc:
            return None
        
        if page_num is None:
            page_num = self.current_page
        
        if 0 <= page_num < self.total_pages:
            return self.pdf_doc[page_num].rect
        
        return None
    
    def close_pdf(self):
        """Close the current PDF document"""
        if self.pdf_doc:
            self.pdf_doc.close()
            self.pdf_doc = None
        
        self.current_page = 0
        self.total_pages = 0
        self.pdf_scale = 1.0
        self.canvas_image = None
        self.coord_transformer = None
        
        # Clear canvas
        self.canvas.delete("all")
    
    def can_go_to_page(self, page_num: int) -> bool:
        """Check if we can navigate to a specific page"""
        return self.pdf_doc is not None and 0 <= page_num < self.total_pages
    
    def next_page(self) -> bool:
        """Go to next page"""
        if self.can_go_to_page(self.current_page + 1):
            return self.display_page(self.current_page + 1)
        return False
    
    def previous_page(self) -> bool:
        """Go to previous page"""
        if self.can_go_to_page(self.current_page - 1):
            return self.display_page(self.current_page - 1)
        return False