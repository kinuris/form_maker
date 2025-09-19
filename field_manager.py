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
    
    def __init__(self, canvas: tk.Canvas):
        """
        Initialize the field manager
        
        Args:
            canvas: The tkinter Canvas widget for drawing fields
        """
        self.canvas = canvas
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
        
        # Create field
        field = FormField(
            name=field_name,
            type=field_type,
            page_num=page_num,
            rect=[x, y, x + width, y + height]
        )
        
        # Add type-specific properties
        if field_type == FieldType.DROPDOWN:
            field.options = ['Option 1', 'Option 2', 'Option 3']
        elif field_type == FieldType.RADIO:
            field.group = f"radio_group_{self.field_counter}"
            field.value = f"option_{self.field_counter}"
        
        # Add to fields list
        self.fields.append(field)
        
        print(f"Created field '{field.name}' at canvas ({x:.1f}, {y:.1f})")
        
        return field
    
    def select_field(self, field: Optional[FormField]):
        """Select a field and update visual representation"""
        if self.selected_field:
            self.clear_selection()
        
        self.selected_field = field
        if field:
            self.draw_field(field)  # Redraw with selection highlighting
    
    def clear_selection(self):
        """Clear the currently selected field"""
        if self.selected_field:
            # Remove resize handles
            for handle in AppConstants.RESIZE_HANDLES:
                self.canvas.delete(f"handle_{handle}")
            
            # Redraw field without selection highlighting
            self.canvas.delete(f"field_{self.selected_field.name}")
            self.canvas.delete(f"field_{self.selected_field.name}_label")
            self.draw_field(self.selected_field)
        
        self.selected_field = None
    
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
            
            x1, y1, x2, y2 = field.rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                return field
        
        return None
    
    def draw_field(self, field: FormField):
        """Draw a field on the canvas"""
        x1, y1, x2, y2 = field.rect
        
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
        x1, y1, x2, y2 = field.rect
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
        
        x1, y1, x2, y2 = self.selected_field.rect
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
        Move a field by the specified delta
        
        Args:
            field: Field to move
            dx, dy: Movement delta
        """
        x1, y1, x2, y2 = field.rect
        field.rect = [x1 + dx, y1 + dy, x2 + dx, y2 + dy]
        
        # Redraw the field
        self.canvas.delete(f"field_{field.name}")
        self.canvas.delete(f"field_{field.name}_label")
        for handle in AppConstants.RESIZE_HANDLES:
            self.canvas.delete(f"handle_{handle}")
        self.draw_field(field)
    
    def resize_field(self, field: FormField, handle: str, x: float, y: float):
        """
        Resize a field based on handle movement
        
        Args:
            field: Field to resize
            handle: Which handle is being dragged
            x, y: New position of the handle
        """
        x1, y1, x2, y2 = field.rect
        
        # Update rectangle based on resize handle
        if 'n' in handle:
            y1 = min(y, y2 - 10)  # Minimum height of 10
        if 's' in handle:
            y2 = max(y, y1 + 10)
        if 'w' in handle:
            x1 = min(x, x2 - 10)  # Minimum width of 10
        if 'e' in handle:
            x2 = max(x, x1 + 10)
        
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