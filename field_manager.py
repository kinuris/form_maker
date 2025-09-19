#!/usr/bin/env python3
"""
Field Manager for PDF Form Maker

Handles creation, selection, manipulation, and rendering of form fields.
"""

import tkinter as tk
from typing import List, Optional, Tuple
from models import FormField, FieldType, AppConstants, MouseState


class FieldManager:
    """Manages form fields - creation, selection, manipulation, and rendering"""
    
    def __init__(self, canvas: tk.Canvas, pdf_handler=None):
        """
        Initialize the field manager
        
        Args:
            canvas: The tkinter Canvas widget for drawing fields
            pdf_handler: Reference to PDFHandler for coordinate transformation
        """
        self.canvas = canvas
        self.pdf_handler = pdf_handler
        self.fields: List[FormField] = []
        self.selected_field: Optional[FormField] = None
        self.field_counter = 0
        self.mouse_state = MouseState()
    
    def create_field(self, field_type: FieldType, x: float, y: float, page_num: int) -> FormField:
        """
        Create a new form field at the specified position
        
        Args:
            field_type: Type of field to create
            x, y: Position on canvas
            page_num: PDF page number
            
        Returns:
            The created FormField
        """
        # Get default size for this field type
        width, height = AppConstants.DEFAULT_FIELD_SIZES[field_type]
        
        # Generate unique name
        self.field_counter += 1
        field_name = f"{field_type.value}_{self.field_counter}"
        
        # Convert canvas coordinates to PDF coordinates for storage
        canvas_rect = [x, y, x + width, y + height]
        
        # Store in PDF coordinates so field stays relative to PDF content
        if self.pdf_handler and hasattr(self.pdf_handler, 'pdf_scale'):
            # Convert to PDF coordinates
            pdf_x1 = (canvas_rect[0] - AppConstants.CANVAS_OFFSET) / self.pdf_handler.pdf_scale
            pdf_y1 = (canvas_rect[1] - AppConstants.CANVAS_OFFSET) / self.pdf_handler.pdf_scale
            pdf_x2 = (canvas_rect[2] - AppConstants.CANVAS_OFFSET) / self.pdf_handler.pdf_scale
            pdf_y2 = (canvas_rect[3] - AppConstants.CANVAS_OFFSET) / self.pdf_handler.pdf_scale
            pdf_rect = [pdf_x1, pdf_y1, pdf_x2, pdf_y2]
        else:
            pdf_rect = canvas_rect.copy()
        
        # Create field with PDF coordinates (will convert to canvas when displaying)
        field = FormField(
            name=field_name,
            type=field_type,
            page_num=page_num,
            rect=pdf_rect  # Store PDF coordinates
        )
        
        # Store PDF coordinates as the authoritative position
        field.pdf_rect = pdf_rect.copy()
        
        # Add type-specific properties
        if field_type == FieldType.DATETIME:
            field.date_format = "MM/DD/YYYY"  # Default format
            field.value = ""  # Default empty value
        
        # Add to fields list
        self.fields.append(field)
        
        print(f"Created field '{field.name}' at canvas ({x:.1f}, {y:.1f})")
        
        return field
    
    def add_field(self, field: FormField):
        """Add an existing field to the manager (used for paste operations)"""
        self.fields.append(field)
        
        # Draw the field on the canvas
        self.draw_field(field)
        
        print(f"Added field '{field.name}' to page {field.page_num + 1}")
    
    def get_canvas_rect_for_field(self, field: FormField) -> List[float]:
        """
        Get the current canvas coordinates for a field based on zoom level
        
        Args:
            field: The form field
            
        Returns:
            List of canvas coordinates [x1, y1, x2, y2] scaled for current zoom
        """
        # Get PDF coordinates (stored in field.rect)
        pdf_rect = field.rect.copy()
        
        # Convert to canvas coordinates using current zoom
        if self.pdf_handler and hasattr(self.pdf_handler, 'pdf_scale'):
            canvas_x1 = pdf_rect[0] * self.pdf_handler.pdf_scale + AppConstants.CANVAS_OFFSET
            canvas_y1 = pdf_rect[1] * self.pdf_handler.pdf_scale + AppConstants.CANVAS_OFFSET
            canvas_x2 = pdf_rect[2] * self.pdf_handler.pdf_scale + AppConstants.CANVAS_OFFSET
            canvas_y2 = pdf_rect[3] * self.pdf_handler.pdf_scale + AppConstants.CANVAS_OFFSET
            return [canvas_x1, canvas_y1, canvas_x2, canvas_y2]
        else:
            # Fallback if no PDF handler
            return pdf_rect.copy()
    
    def get_pdf_rect_for_field(self, field: FormField) -> List[float]:
        """
        Get PDF coordinates for a field (already stored in PDF coordinates)
        
        Args:
            field: The form field
            
        Returns:
            List of PDF coordinates [x1, y1, x2, y2]
        """
        # Field.rect now contains PDF coordinates directly
        return field.rect.copy()
    
    def select_field(self, field: Optional[FormField]):
        """Select a field and update visual representation"""
        # If selecting the same field, do nothing
        if self.selected_field == field:
            return
            
        # Clear any existing selection first
        if self.selected_field:
            self.clear_selection()
        
        # Select the new field
        self.selected_field = field
        if field:
            # Redraw the field with selection highlighting
            self.canvas.delete(f"field_{field.name}")
            self.canvas.delete(f"field_{field.name}_label")
            self.draw_field(field)
    
    def clear_selection(self):
        """Clear the currently selected field"""
        if self.selected_field:
            # Store reference to previously selected field
            previously_selected = self.selected_field
            
            # Clear the selection first
            self.selected_field = None
            
            # Remove resize handles
            for handle in AppConstants.RESIZE_HANDLES:
                self.canvas.delete(f"handle_{handle}")
            
            # Redraw field without selection highlighting
            self.canvas.delete(f"field_{previously_selected.name}")
            self.canvas.delete(f"field_{previously_selected.name}_label")
            self.draw_field(previously_selected)
    
    def delete_field(self, field: FormField) -> bool:
        """
        Delete a field
        
        Args:
            field: Field to delete
            
        Returns:
            True if field was deleted, False otherwise
        """
        if field not in self.fields:
            return False
        
        # Remove from canvas
        self.canvas.delete(f"field_{field.name}")
        self.canvas.delete(f"field_{field.name}_label")
        
        # Remove resize handles if this field is selected
        if field == self.selected_field:
            for handle in AppConstants.RESIZE_HANDLES:
                self.canvas.delete(f"handle_{handle}")
            self.selected_field = None
        
        # Remove from fields list
        self.fields.remove(field)
        return True
    
    def get_field_at_position(self, x: float, y: float, page_num: int) -> Optional[FormField]:
        """
        Get the field at the specified canvas position
        
        Args:
            x, y: Canvas coordinates
            page_num: Current page number
            
        Returns:
            Field at position, or None if no field found
        """
        for field in self.fields:
            if field.page_num != page_num:
                continue
            
            # Use canvas coordinates for hit detection
            canvas_rect = self.get_canvas_rect_for_field(field)
            x1, y1, x2, y2 = canvas_rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                return field
        
        return None
    
    def draw_field(self, field: FormField):
        """Draw a field on the canvas"""
        # First, remove any existing canvas elements for this field
        self.canvas.delete(f"field_{field.name}")
        self.canvas.delete(f"field_{field.name}_label")
        
        # Also remove resize handles if this field is selected
        if field == self.selected_field:
            for handle in AppConstants.RESIZE_HANDLES:
                self.canvas.delete(f"handle_{handle}")
        
        # Use canvas coordinates for drawing
        canvas_rect = self.get_canvas_rect_for_field(field)
        x1, y1, x2, y2 = canvas_rect
        
        # Determine colors
        color = AppConstants.FIELD_COLORS[field.type]
        outline_color = AppConstants.SELECTION_COLOR if field == self.selected_field else color
        outline_width = 3 if field == self.selected_field else 2
        
        # Draw main rectangle
        field.canvas_id = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=outline_color,
            width=outline_width,
            fill='',
            tags=f"field_{field.name}"
        )
        
        # Draw field type label
        label_x = x1 + 3
        label_y = y1 + 3
        self.canvas.create_text(
            label_x, label_y,
            anchor='nw',
            text=field.type.value,
            fill=outline_color,
            font=('Arial', 8, 'bold'),
            tags=f"field_{field.name}_label"
        )
        
        # Draw resize handles if this field is selected
        if field == self.selected_field:
            self.draw_resize_handles(field)
    
    def draw_resize_handles(self, field: FormField):
        """Draw resize handles around a selected field"""
        canvas_rect = self.get_canvas_rect_for_field(field)
        x1, y1, x2, y2 = canvas_rect
        handle_size = AppConstants.HANDLE_SIZE
        
        # Calculate handle positions
        handles = {
            'nw': (x1 - handle_size//2, y1 - handle_size//2),  # Top-left
            'ne': (x2 - handle_size//2, y1 - handle_size//2),  # Top-right
            'sw': (x1 - handle_size//2, y2 - handle_size//2),  # Bottom-left
            'se': (x2 - handle_size//2, y2 - handle_size//2),  # Bottom-right
            'n': ((x1 + x2)//2 - handle_size//2, y1 - handle_size//2),   # Top
            's': ((x1 + x2)//2 - handle_size//2, y2 - handle_size//2),   # Bottom
            'w': (x1 - handle_size//2, (y1 + y2)//2 - handle_size//2),   # Left
            'e': (x2 - handle_size//2, (y1 + y2)//2 - handle_size//2),   # Right
        }
        
        for direction, (x, y) in handles.items():
            self.canvas.create_rectangle(
                x, y, x + handle_size, y + handle_size,
                fill=AppConstants.HANDLE_COLOR,
                outline='white',
                width=1,
                tags=f"handle_{direction}"
            )
    
    def redraw_fields_for_page(self, page_num: int):
        """Redraw all fields for the specified page"""
        for field in self.fields:
            if field.page_num == page_num:
                self.draw_field(field)
    
    def check_resize_handle_click(self, x: float, y: float) -> Optional[str]:
        """
        Check if click is on a resize handle
        
        Args:
            x, y: Canvas coordinates
            
        Returns:
            Handle direction if clicked, None otherwise
        """
        if not self.selected_field:
            return None
        
        # Use canvas coordinates for handle detection
        canvas_rect = self.get_canvas_rect_for_field(self.selected_field)
        x1, y1, x2, y2 = canvas_rect
        handle_size = AppConstants.HANDLE_SIZE
        
        handles = {
            'nw': (x1 - handle_size//2, y1 - handle_size//2),
            'ne': (x2 - handle_size//2, y1 - handle_size//2),
            'sw': (x1 - handle_size//2, y2 - handle_size//2),
            'se': (x2 - handle_size//2, y2 - handle_size//2),
            'n': ((x1 + x2)//2 - handle_size//2, y1 - handle_size//2),
            's': ((x1 + x2)//2 - handle_size//2, y2 - handle_size//2),
            'w': (x1 - handle_size//2, (y1 + y2)//2 - handle_size//2),
            'e': (x2 - handle_size//2, (y1 + y2)//2 - handle_size//2),
        }
        
        for direction, (hx, hy) in handles.items():
            if hx <= x <= hx + handle_size and hy <= y <= hy + handle_size:
                return direction
        
        return None
    
    def move_field(self, field: FormField, dx: float, dy: float):
        """
        Move a field by the specified delta (in canvas coordinates)
        
        Args:
            field: Field to move
            dx, dy: Movement delta in canvas coordinates
        """
        # Convert canvas delta to PDF delta
        if self.pdf_handler and hasattr(self.pdf_handler, 'pdf_scale'):
            pdf_dx = dx / self.pdf_handler.pdf_scale
            pdf_dy = dy / self.pdf_handler.pdf_scale
        else:
            pdf_dx, pdf_dy = dx, dy
        
        # Update PDF coordinates
        x1, y1, x2, y2 = field.rect
        field.rect = [x1 + pdf_dx, y1 + pdf_dy, x2 + pdf_dx, y2 + pdf_dy]
        
        # Redraw the field
        self.canvas.delete(f"field_{field.name}")
        self.canvas.delete(f"field_{field.name}_label")
        for handle in AppConstants.RESIZE_HANDLES:
            self.canvas.delete(f"handle_{handle}")
        self.draw_field(field)
    
    def resize_field(self, field: FormField, handle: str, x: float, y: float):
        """
        Resize a field based on handle movement (canvas coordinates input)
        
        Args:
            field: Field to resize
            handle: Which handle is being dragged
            x, y: New position of the handle in canvas coordinates
        """
        # Convert canvas coordinates to PDF coordinates
        if self.pdf_handler and hasattr(self.pdf_handler, 'pdf_scale'):
            pdf_x = (x - AppConstants.CANVAS_OFFSET) / self.pdf_handler.pdf_scale
            pdf_y = (y - AppConstants.CANVAS_OFFSET) / self.pdf_handler.pdf_scale
        else:
            pdf_x, pdf_y = x, y
        
        x1, y1, x2, y2 = field.rect  # PDF coordinates
        
        # Update rectangle based on resize handle
        if 'n' in handle:
            y1 = min(pdf_y, y2 - 10/self.pdf_handler.pdf_scale)  # Minimum height in PDF units
        if 's' in handle:
            y2 = max(pdf_y, y1 + 10/self.pdf_handler.pdf_scale)
        if 'w' in handle:
            x1 = min(pdf_x, x2 - 10/self.pdf_handler.pdf_scale)  # Minimum width in PDF units
        if 'e' in handle:
            x2 = max(pdf_x, x1 + 10/self.pdf_handler.pdf_scale)
        
        field.rect = [x1, y1, x2, y2]
        
        # Redraw the field
        self.canvas.delete(f"field_{field.name}")
        self.canvas.delete(f"field_{field.name}_label")
        for h in AppConstants.RESIZE_HANDLES:
            self.canvas.delete(f"handle_{h}")
        self.draw_field(field)
    
    def get_fields_for_page(self, page_num: int) -> List[FormField]:
        """Get all fields for a specific page"""
        return [field for field in self.fields if field.page_num == page_num]
    
    def clear_all_fields(self):
        """Clear all fields"""
        for field in self.fields:
            self.canvas.delete(f"field_{field.name}")
            self.canvas.delete(f"field_{field.name}_label")
        
        for handle in AppConstants.RESIZE_HANDLES:
            self.canvas.delete(f"handle_{handle}")
        
        self.fields.clear()
        self.selected_field = None
        self.field_counter = 0
    
    def load_existing_fields(self, detected_fields: List[FormField]):
        """
        Load existing fields detected from PDF
        
        Args:
            detected_fields: List of FormField objects detected from PDF
        """
        # Clear current fields first
        self.clear_all_fields()
        
        # Add each detected field
        for field in detected_fields:
            # Ensure field has proper canvas coordinates
            # The PDF coordinates are already stored in field.rect
            
            # Add to fields list
            self.fields.append(field)
            
            # Update field counter to avoid name conflicts
            # Extract number from field name if present
            import re
            match = re.search(r'(\d+)$', field.name)
            if match:
                field_num = int(match.group(1))
                self.field_counter = max(self.field_counter, field_num)
        
        # Increment counter for next new field
        self.field_counter += 1
        
        # Draw all fields for current page
        if self.pdf_handler and hasattr(self.pdf_handler, 'current_page'):
            self.redraw_fields_for_page(self.pdf_handler.current_page)
        
        print(f"Loaded {len(detected_fields)} existing fields from PDF")