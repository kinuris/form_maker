#!/usr/bin/env python3
"""
Data models and constants for PDF Form Maker
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class FieldType(Enum):
    """Enumeration of supported form field types"""
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    SIGNATURE = "signature"


@dataclass
class FormField:
    """Represents a form field with its properties"""
    name: str
    type: FieldType
    page_num: int
    rect: List[float]  # [x1, y1, x2, y2] in canvas coordinates
    canvas_id: Optional[int] = None
    
    # Type-specific properties
    options: Optional[List[str]] = None  # For dropdowns
    group: Optional[str] = None  # For radio buttons
    value: Optional[str] = None  # For radio buttons
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type.value,
            'page_num': self.page_num,
            'rect': self.rect,
            'options': self.options,
            'group': self.group,
            'value': self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormField':
        """Create field from dictionary"""
        return cls(
            name=data['name'],
            type=FieldType(data['type']),
            page_num=data['page_num'],
            rect=data['rect'],
            options=data.get('options'),
            group=data.get('group'),
            value=data.get('value')
        )


class AppConstants:
    """Application constants and configuration"""
    
    # UI Layout
    CANVAS_OFFSET = 25  # Pixels offset for PDF display on canvas
    DEFAULT_WINDOW_SIZE = (1000, 700)
    STATUS_BAR_HEIGHT = 25
    TOOLBAR_HEIGHT = 60
    NAV_BAR_HEIGHT = 50
    
    # Field defaults
    DEFAULT_FIELD_SIZES = {
        FieldType.TEXT: (100, 30),
        FieldType.CHECKBOX: (20, 20),
        FieldType.RADIO: (20, 20),
        FieldType.DROPDOWN: (120, 25),
        FieldType.SIGNATURE: (150, 50)
    }
    
    # Colors
    FIELD_COLORS = {
        FieldType.TEXT: '#2196F3',
        FieldType.CHECKBOX: '#FF9800',
        FieldType.RADIO: '#9C27B0',
        FieldType.DROPDOWN: '#607D8B',
        FieldType.SIGNATURE: '#795548'
    }
    
    SELECTION_COLOR = '#0066CC'
    HANDLE_COLOR = '#0066CC'
    HANDLE_SIZE = 6
    
    # File filters
    PDF_FILE_TYPES = [("PDF files", "*.pdf"), ("All files", "*.*")]
    
    # Resize handles
    RESIZE_HANDLES = ['nw', 'ne', 'sw', 'se', 'n', 's', 'w', 'e']
    
    # Resize cursors
    RESIZE_CURSORS = {
        'nw': 'size_nw_se', 'ne': 'size_ne_sw',
        'sw': 'size_ne_sw', 'se': 'size_nw_se',
        'n': 'size_ns', 's': 'size_ns',
        'w': 'size_we', 'e': 'size_we'
    }


class MouseState:
    """Tracks mouse interaction state"""
    
    def __init__(self):
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        self.drag_start_x = 0
        self.drag_start_y = 0
    
    def reset(self):
        """Reset all mouse state"""
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        self.drag_start_x = 0
        self.drag_start_y = 0
    
    def start_drag(self, x, y):
        """Start dragging operation"""
        self.dragging = True
        self.drag_start_x = x
        self.drag_start_y = y
    
    def start_resize(self, x, y, handle):
        """Start resizing operation"""
        self.resizing = True
        self.resize_handle = handle
        self.drag_start_x = x
        self.drag_start_y = y