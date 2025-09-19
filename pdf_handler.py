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
from models import FormField, FieldType, AppConstants, ZoomState
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
        self.zoom_state = ZoomState()  # Add zoom state management
        self.page_images = {}  # Cache for rendered page images
    
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
            
            # Clear page image cache and reset zoom
            self.page_images.clear()
            self.zoom_state.reset_zoom()
            
            print(f"PDF loaded: {self.total_pages} pages")
            return True
            
        except Exception as e:
            print(f"Failed to load PDF: {e}")
            return False
    
    def display_page(self, page_num: int = None) -> bool:
        """
        Display a PDF page on the canvas with zoom support
        
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
            
            # Calculate scale considering zoom
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not yet properly sized, use default
                canvas_width = 800
                canvas_height = 600
            
            if self.zoom_state.fit_to_window:
                # Auto-fit to window
                base_scale = calculate_display_scale(
                    (canvas_width, canvas_height),
                    (page_rect.width, page_rect.height)
                )
                self.zoom_state.zoom_level = base_scale  # Update zoom state to match auto-fit
                self.pdf_scale = base_scale
            else:
                # Use current zoom level
                self.pdf_scale = self.zoom_state.zoom_level
            
            print(f"Display scaling: canvas={canvas_width}x{canvas_height}, "
                  f"PDF={page_rect.width}x{page_rect.height}, scale={self.pdf_scale:.3f}, "
                  f"zoom={self.zoom_state.get_zoom_percentage()}")
            
            # Create cache key including zoom level
            cache_key = f"{self.current_page}_{self.pdf_scale:.3f}"
            
            # Check if we have this image cached
            if cache_key not in self.page_images:
                # Create coordinate transformer
                self.coord_transformer = CoordinateTransformer(
                    self.pdf_scale, 
                    AppConstants.CANVAS_OFFSET
                )
                
                # Render page to pixmap at higher resolution for better quality
                matrix = fitz.Matrix(self.pdf_scale * AppConstants.PDF_DPI / 72, 
                                   self.pdf_scale * AppConstants.PDF_DPI / 72)
                pixmap = page.get_pixmap(matrix=matrix)
                
                # Convert to PIL Image then to PhotoImage
                img_data = pixmap.tobytes("ppm")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # Resize if needed for display
                display_width = int(page_rect.width * self.pdf_scale)
                display_height = int(page_rect.height * self.pdf_scale)
                if pil_image.size != (display_width, display_height):
                    pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                
                canvas_image = ImageTk.PhotoImage(pil_image)
                self.page_images[cache_key] = canvas_image
            else:
                canvas_image = self.page_images[cache_key]
            
            self.canvas_image = canvas_image
            
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
            scroll_width = int(page_rect.width * self.pdf_scale) + AppConstants.CANVAS_OFFSET * 2
            scroll_height = int(page_rect.height * self.pdf_scale) + AppConstants.CANVAS_OFFSET * 2
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
                
                # Fields now store PDF coordinates directly, so use them as-is
                pdf_rect = field.rect.copy()
                
                # Clamp to page boundaries
                pdf_rect[0] = max(0, min(pdf_rect[0], original_page_rect.width))
                pdf_rect[1] = max(0, min(pdf_rect[1], original_page_rect.height))
                pdf_rect[2] = max(pdf_rect[0] + 10, min(pdf_rect[2], original_page_rect.width))
                pdf_rect[3] = max(pdf_rect[1] + 10, min(pdf_rect[3], original_page_rect.height))
                
                print(f"Field '{field.name}': PDF coordinates {pdf_rect} (scale={self.pdf_scale:.3f})")
                
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
            
        elif field.type == FieldType.DATETIME:
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_value = field.value or ""
            widget.text_font = "helv"
            widget.text_fontsize = 11
            widget.fill_color = (1, 1, 1)
            widget.border_color = (0.5, 0.5, 0.5)
            widget.border_width = 1
            # Add some JavaScript for date validation if needed
            if hasattr(field, 'date_format') and field.date_format:
                # Store the format as part of the field name for reference
                widget.field_name = f"{field.name}_{field.date_format.replace('/', '_').replace('-', '_')}"
            
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
        self.page_images.clear()  # Clear image cache
        self.zoom_state.reset_zoom()  # Reset zoom state
        
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
    
    # Zoom control methods
    def zoom_in(self, center_x=None, center_y=None) -> bool:
        """
        Zoom in by one step
        
        Args:
            center_x: X coordinate to zoom around (optional)
            center_y: Y coordinate to zoom around (optional)
            
        Returns:
            True if zoom changed, False if at maximum zoom
        """
        old_zoom = self.zoom_state.zoom_level
        self.zoom_state.zoom_in(center_x, center_y)
        
        if self.zoom_state.zoom_level != old_zoom:
            self.display_page()  # Refresh display with new zoom
            return True
        return False
    
    def zoom_out(self, center_x=None, center_y=None) -> bool:
        """
        Zoom out by one step
        
        Args:
            center_x: X coordinate to zoom around (optional)
            center_y: Y coordinate to zoom around (optional)
            
        Returns:
            True if zoom changed, False if at minimum zoom
        """
        old_zoom = self.zoom_state.zoom_level
        self.zoom_state.zoom_out(center_x, center_y)
        
        if self.zoom_state.zoom_level != old_zoom:
            self.display_page()  # Refresh display with new zoom
            return True
        return False
    
    def set_zoom(self, zoom_level: float, center_x=None, center_y=None) -> bool:
        """
        Set specific zoom level
        
        Args:
            zoom_level: New zoom level
            center_x: X coordinate to zoom around (optional)
            center_y: Y coordinate to zoom around (optional)
            
        Returns:
            True if zoom changed, False otherwise
        """
        old_zoom = self.zoom_state.zoom_level
        self.zoom_state.set_zoom(zoom_level, center_x, center_y)
        
        if self.zoom_state.zoom_level != old_zoom:
            self.display_page()  # Refresh display with new zoom
            return True
        return False
    
    def fit_to_window(self) -> bool:
        """
        Reset zoom to fit the window
        
        Returns:
            True if zoom changed, False otherwise
        """
        old_fit = self.zoom_state.fit_to_window
        self.zoom_state.reset_zoom()
        
        if not old_fit or self.zoom_state.zoom_level != self.pdf_scale:
            self.display_page()  # Refresh display with auto-fit
            return True
        return False
    
    def get_zoom_percentage(self) -> str:
        """Get current zoom level as percentage string"""
        return self.zoom_state.get_zoom_percentage()
    
    def handle_mouse_wheel_zoom(self, event) -> bool:
        """
        Handle mouse wheel zoom
        
        Args:
            event: Mouse wheel event
            
        Returns:
            True if zoom changed, False otherwise
        """
        # Get mouse position for zoom center
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Calculate zoom change
        zoom_factor = AppConstants.ZOOM_WHEEL_FACTOR
        if event.delta > 0:  # Zoom in
            new_zoom = self.zoom_state.zoom_level + zoom_factor
        else:  # Zoom out
            new_zoom = self.zoom_state.zoom_level - zoom_factor
        
        return self.set_zoom(new_zoom, canvas_x, canvas_y)