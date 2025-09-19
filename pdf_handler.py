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
    
    def detect_existing_fields(self) -> List['FormField']:
        """
        Detect and extract existing form fields from the loaded PDF
        
        Returns:
            List of FormField objects representing existing fields in the PDF
        """
        if not self.pdf_doc:
            return []
        
        from models import FormField, FieldType
        detected_fields = []
        seen_fields = set()  # Track field names and positions to avoid duplicates
        
        try:
            # Iterate through all pages
            for page_num in range(len(self.pdf_doc)):
                page = self.pdf_doc[page_num]
                
                # Get all form widgets on this page
                widgets = page.widgets()
                
                for widget in widgets:
                    try:
                        # Extract widget properties
                        field_type = self._map_pdf_field_type(widget.field_type)
                        if field_type is None:
                            continue  # Skip unsupported field types
                        
                        # Enhanced detection for DATE and IMAGE fields
                        # Check if this is actually a DATE field based on field name pattern
                        field_name = widget.field_name or f"field_{len(detected_fields) + 1}"
                        if field_type == FieldType.TEXT and self._is_date_field(field_name):
                            field_type = FieldType.DATE
                        elif field_type == FieldType.TEXT and self._is_image_field(field_name):
                            field_type = FieldType.IMAGE
                        
                        # Get field rectangle in PDF coordinates
                        rect = widget.rect
                        pdf_rect = [rect.x0, rect.y0, rect.x1, rect.y1]
                        
                        # Create unique identifier for this field (name + position + page)
                        field_name = widget.field_name or f"field_{len(detected_fields) + 1}"
                        # Get field rectangle in PDF coordinates
                        rect = widget.rect
                        pdf_rect = [rect.x0, rect.y0, rect.x1, rect.y1]
                        
                        # Clean up field name (remove date type encoding if present)
                        clean_field_name = self._clean_field_name(field_name)
                        
                        # Create unique identifier for this field (name + position + page)
                        field_id = (field_name, page_num, tuple(pdf_rect))
                        
                        # Skip if we've already seen this field
                        if field_id in seen_fields:
                            print(f"Skipping duplicate field: '{field_name}' on page {page_num + 1}")
                            continue
                        
                        seen_fields.add(field_id)
                        
                        # Create FormField object
                        field = FormField(
                            name=clean_field_name,
                            type=field_type,
                            page_num=page_num,
                            rect=pdf_rect.copy(),  # Store PDF coordinates
                            value=widget.field_value or ""
                        )
                        
                        # Add type-specific properties
                        if field_type == FieldType.DATE:
                            # Extract date format from field name or use default
                            field.date_format = self._extract_date_format_from_name(field_name) or self._detect_date_format(clean_field_name, widget.field_value)
                        
                        detected_fields.append(field)
                        print(f"Detected {field_type.value} field: '{field.name}' on page {page_num + 1}")
                        
                    except Exception as e:
                        print(f"Error processing widget: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error detecting fields: {e}")
        
        print(f"Total detected fields: {len(detected_fields)}")
        return detected_fields
    
    def _map_pdf_field_type(self, pdf_field_type: int) -> Optional['FieldType']:
        """
        Map PDF field type to our FieldType enum
        
        Args:
            pdf_field_type: PyMuPDF field type constant
            
        Returns:
            Corresponding FieldType or None if unsupported
        """
        import fitz
        from models import FieldType
        
        type_mapping = {
            fitz.PDF_WIDGET_TYPE_TEXT: FieldType.TEXT,
            fitz.PDF_WIDGET_TYPE_CHECKBOX: FieldType.CHECKBOX,
            fitz.PDF_WIDGET_TYPE_SIGNATURE: FieldType.SIGNATURE,
            # Map combobox to date field for now, could be enhanced with detection logic
            fitz.PDF_WIDGET_TYPE_COMBOBOX: FieldType.DATE,
        }
        
        return type_mapping.get(pdf_field_type)
    
    def _detect_date_format(self, field_name: str, field_value: str) -> str:
        """
        Try to detect date format from field name or value
        
        Args:
            field_name: Name of the field
            field_value: Current field value
            
        Returns:
            Detected date format or default format
        """
        # Default format
        default_format = "MM/DD/YYYY"
        
        if not field_name and not field_value:
            return default_format
        
        # Check field name for format hints
        name_lower = (field_name or "").lower()
        if "date" in name_lower or "birth" in name_lower or "expire" in name_lower:
            # Try to detect format from common patterns
            if "dd/mm" in name_lower or "european" in name_lower:
                return "DD/MM/YYYY"
            elif "yyyy-mm-dd" in name_lower or "iso" in name_lower:
                return "YYYY-MM-DD"
            elif "mmm" in name_lower:
                return "DD MMM YYYY"
        
        # Try to detect from field value pattern
        if field_value:
            value = str(field_value).strip()
            if len(value) >= 8:
                # Look for common separators and patterns
                if "/" in value and value.count("/") == 2:
                    parts = value.split("/")
                    if len(parts[0]) == 2 and len(parts[1]) == 2 and len(parts[2]) == 4:
                        return "MM/DD/YYYY"  # or DD/MM/YYYY - ambiguous
                elif "-" in value and value.count("-") == 2:
                    parts = value.split("-")
                    if len(parts[0]) == 4:
                        return "YYYY-MM-DD"
        
        return default_format
    
    def _is_date_field(self, field_name):
        """Check if a field is a DATE field based on its name pattern."""
        if not field_name:
            return False
        
        # Check for date type encoding in field name
        if field_name.startswith("date_") or "_date_" in field_name:
            return True
        
        # Check for common date field names
        date_keywords = ["date", "birth", "created", "modified", "expiry", "deadline"]
        name_lower = field_name.lower()
        return any(keyword in name_lower for keyword in date_keywords)
    
    def _is_image_field(self, field_name):
        """Check if a field is an IMAGE field based on its name pattern."""
        if not field_name:
            return False
        
        # Check for image type encoding in field name
        if field_name.startswith("image_") or "_image_" in field_name:
            return True
        
        # Check for common image field names
        image_keywords = ["image", "photo", "picture", "pic", "logo", "avatar", "thumbnail"]
        name_lower = field_name.lower()
        return any(keyword in name_lower for keyword in image_keywords)
    
    def _clean_field_name(self, field_name):
        """Remove field type encoding from field name."""
        if not field_name:
            return field_name
        
        # Remove date type prefix
        if field_name.startswith("date_"):
            return field_name[5:]  # Remove "date_" prefix
        
        # Remove image type prefix
        if field_name.startswith("image_"):
            return field_name[6:]  # Remove "image_" prefix
        
        # Remove date type infix
        if "_date_" in field_name:
            parts = field_name.split("_date_")
            if len(parts) == 2:
                return parts[0] + "_" + parts[1]
        
        # Remove image type infix
        if "_image_" in field_name:
            parts = field_name.split("_image_")
            if len(parts) == 2:
                return parts[0] + "_" + parts[1]
        
        return field_name
    
    def _extract_date_format_from_name(self, field_name):
        """Extract date format information from encoded field name."""
        if not field_name or "_date_" not in field_name:
            return None
        
        # Look for format information after _date_
        parts = field_name.split("_date_")
        if len(parts) >= 2:
            format_part = parts[1]
            # Common format encodings
            format_mapping = {
                "mmddyyyy": "MM/DD/YYYY",
                "ddmmyyyy": "DD/MM/YYYY",
                "yyyymmdd": "YYYY-MM-DD",
                "iso": "YYYY-MM-DD"
            }
            return format_mapping.get(format_part.lower())
        
        return None
    
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
        if not self.pdf_doc:
            return False
        
        try:
            # Create a copy of the document for saving
            temp_doc = fitz.open()
            for page_num in range(len(self.pdf_doc)):
                temp_doc.insert_pdf(self.pdf_doc, from_page=page_num, to_page=page_num)
            
            # IMPORTANT: Remove all existing form fields first
            # This ensures that deleted fields are actually removed from the PDF
            self._remove_all_existing_fields(temp_doc)
            
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
    
    def _remove_all_existing_fields(self, doc: fitz.Document):
        """
        Remove all existing form fields from the PDF document
        
        Args:
            doc: PDF document to remove fields from
        """
        try:
            # Iterate through all pages and remove form fields
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get all widgets on this page
                widgets = page.widgets()
                
                # Remove each widget
                for widget in widgets:
                    try:
                        widget_name = getattr(widget, 'field_name', f'widget_{widget.xref}')
                        page.delete_widget(widget)
                        print(f"Removed existing field: {widget_name}")
                    except Exception as e:
                        widget_name = getattr(widget, 'field_name', f'widget_{getattr(widget, "xref", "unknown")}')
                        print(f"Warning: Could not remove widget {widget_name}: {e}")
                        
        except Exception as e:
            print(f"Warning: Error removing existing fields: {e}")
    
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
            
        elif field.type == FieldType.DATE:
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_value = field.value or ""
            widget.text_font = "helv"
            widget.text_fontsize = 11
            widget.fill_color = (1, 1, 1)
            widget.border_color = (0.2, 0.4, 0.8)  # Blue border to indicate date field
            widget.border_width = 1
            
            # Try to set text format to DATE (may not persist due to PyMuPDF limitations)
            widget.text_format = fitz.PDF_WIDGET_TX_FORMAT_DATE
            
            # Encode the field type in the field name for preservation
            widget.field_name = f"date_{field.name}"
            
            # Add comprehensive JavaScript for date validation and formatting
            date_format = getattr(field, 'date_format', 'MM/DD/YYYY')
            widget.script_change = self._generate_date_validation_script(date_format)
            widget.script_format = self._generate_date_format_script(date_format)
            widget.script_focus = self._generate_date_focus_script(date_format)
            
        elif field.type == FieldType.SIGNATURE:
            # For signature fields, create a text field with signature appearance
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_value = ""
            widget.text_font = "helv"
            widget.text_fontsize = 12
            widget.fill_color = (0.95, 0.95, 0.95)  # Light gray background
            widget.border_color = (0.5, 0.5, 0.5)
            widget.border_width = 2
            
        elif field.type == FieldType.IMAGE:
            # IMAGE fields in PDFs work differently than web forms
            # PDF forms don't support interactive file uploads like web pages
            # Instead, we create informational fields that guide users
            
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_name = f"image_{field.name}"
            widget.text_font = "helv"
            widget.text_fontsize = 10
            widget.fill_color = (0.95, 0.95, 1.0)  # Very light blue background
            widget.border_color = (0.6, 0.3, 0.8)  # Purple border for image fields
            widget.border_width = 2
            widget.text_color = (0.4, 0.4, 0.4)  # Gray text
            
            # Set instructions based on whether image is pre-loaded
            if hasattr(field, 'image_path') and field.image_path:
                try:
                    # Embed the actual image as static content
                    self._embed_image_from_path(page, rect, field.image_path)
                    
                    # Update field to show image is present
                    import os
                    filename = os.path.basename(field.image_path)
                    widget.field_value = f"📷 {filename}"
                    widget.fill_color = (0.9, 1.0, 0.9)  # Light green background
                    widget.text_color = (0.2, 0.6, 0.2)  # Green text
                    print(f"Embedded static image '{field.image_path}' for field '{field.name}'")
                except Exception as e:
                    print(f"Warning: Could not embed image '{field.image_path}': {e}")
                    widget.field_value = "📷 [Image load failed]"
            
            elif hasattr(field, 'image_data') and field.image_data:
                try:
                    # Embed image data as static content
                    self._embed_image_in_rect(page, rect, field.image_data)
                    widget.field_value = "📷 Image attached"
                    widget.fill_color = (0.9, 1.0, 0.9)  # Light green background
                    widget.text_color = (0.2, 0.6, 0.2)  # Green text
                    print(f"Embedded image data for field '{field.name}'")
                except Exception as e:
                    print(f"Warning: Could not embed image data: {e}")
                    widget.field_value = "📷 [Image load failed]"
            else:
                # No image - provide clear instructions
                widget.field_value = "📷 [Image placeholder - attach file using browser tools]"
            
            print(f"Created browser-compatible image field for '{field.name}'")
        
        # Add the widget to the page (IMAGE fields handle their own widget logic above)
        if field.type != FieldType.IMAGE:
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
    
    def _generate_date_validation_script(self, date_format):
        """Generate JavaScript for date field validation"""
        return f"""
// Date validation for format: {date_format}
var value = event.value;
if (value && value.length > 0) {{
    // Remove any non-numeric characters except slashes
    var cleanValue = value.replace(/[^\\d\\/]/g, '');
    
    // Check basic format
    var datePattern = /^\\d{{1,2}}\\/\\d{{1,2}}\\/\\d{{4}}$/;
    if (!datePattern.test(cleanValue)) {{
        app.alert('Please enter date in {date_format} format (e.g., 12/31/2024)', 1);
        event.value = '';
        return;
    }}
    
    // Validate actual date values
    var parts = cleanValue.split('/');
    var month = parseInt(parts[0], 10);
    var day = parseInt(parts[1], 10);
    var year = parseInt(parts[2], 10);
    
    if (month < 1 || month > 12) {{
        app.alert('Month must be between 1 and 12', 1);
        event.value = '';
        return;
    }}
    
    if (day < 1 || day > 31) {{
        app.alert('Day must be between 1 and 31', 1);
        event.value = '';
        return;
    }}
    
    if (year < 1900 || year > 2100) {{
        app.alert('Year must be between 1900 and 2100', 1);
        event.value = '';
        return;
    }}
    
    // Check for valid date (e.g., not Feb 30)
    var testDate = new Date(year, month - 1, day);
    if (testDate.getMonth() !== (month - 1) || testDate.getDate() !== day) {{
        app.alert('This is not a valid calendar date', 1);
        event.value = '';
        return;
    }}
    
    // If we get here, format the date properly
    event.value = (month < 10 ? '0' + month : month) + '/' + 
                  (day < 10 ? '0' + day : day) + '/' + year;
}}
"""
    
    def _generate_date_format_script(self, date_format):
        """Generate JavaScript for date field formatting"""
        return f"""
// Auto-format date as user types for {date_format}
var value = event.value;
if (value) {{
    // Remove non-numeric characters except slashes
    var cleaned = value.replace(/[^\\d\\/]/g, '');
    
    // Auto-add slashes as user types
    if (cleaned.length >= 3 && cleaned.charAt(2) !== '/') {{
        cleaned = cleaned.substring(0, 2) + '/' + cleaned.substring(2);
    }}
    if (cleaned.length >= 6 && cleaned.charAt(5) !== '/') {{
        cleaned = cleaned.substring(0, 5) + '/' + cleaned.substring(5);
    }}
    
    // Limit to MM/DD/YYYY format length
    if (cleaned.length > 10) {{
        cleaned = cleaned.substring(0, 10);
    }}
    
    event.value = cleaned;
}}
"""
    
    def _generate_date_focus_script(self, date_format):
        """Generate JavaScript for date field focus events"""
        return f"""
// Date field focus script for {date_format}
if (!event.value || event.value.length === 0) {{
    // Show placeholder text or help
    event.target.strokeColor = ['RGB', 0.2, 0.4, 0.8];
    // Note: We can't set placeholder text directly, but the blue border indicates date field
}}
"""
    
    def _embed_image_from_path(self, page: fitz.Page, rect: fitz.Rect, image_path: str):
        """Embed an image from file path into the PDF at the specified rectangle"""
        try:
            # Insert image into the PDF page at the specified rectangle
            page.insert_image(rect, filename=image_path, keep_proportion=True)
            print(f"Embedded image from {image_path}")
        except Exception as e:
            print(f"Error embedding image from {image_path}: {e}")
            raise
    
    def _embed_image_in_rect(self, page: fitz.Page, rect: fitz.Rect, image_data: bytes):
        """Embed image data into the PDF at the specified rectangle"""
        try:
            # Insert image data into the PDF page at the specified rectangle
            page.insert_image(rect, stream=image_data, keep_proportion=True)
            print(f"Embedded image data ({len(image_data)} bytes)")
        except Exception as e:
            print(f"Error embedding image data: {e}")
            raise