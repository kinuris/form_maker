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
    DATETIME = "datetime"
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
    date_format: Optional[str] = None  # For datetime fields (e.g., "MM/DD/YYYY", "DD/MM/YYYY")
    value: Optional[str] = None  # Default value for fields
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type.value,
            'page_num': self.page_num,
            'rect': self.rect,
            'date_format': self.date_format,
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
            date_format=data.get('date_format'),
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
    
    # Zoom settings
    MIN_ZOOM = 0.25  # 25% minimum zoom
    MAX_ZOOM = 5.0   # 500% maximum zoom
    DEFAULT_ZOOM = 1.0  # 100% default zoom
    ZOOM_STEP = 0.25    # 25% zoom increment
    ZOOM_WHEEL_FACTOR = 0.1  # Mouse wheel zoom sensitivity
    
    # PDF rendering settings
    PDF_DPI = 150  # DPI for PDF rendering quality
    
    # Field defaults
    DEFAULT_FIELD_SIZES = {
        FieldType.TEXT: (100, 30),
        FieldType.CHECKBOX: (20, 20),
        FieldType.DATETIME: (120, 30),
        FieldType.SIGNATURE: (150, 50)
    }
    
    # Colors
    FIELD_COLORS = {
        FieldType.TEXT: '#2196F3',
        FieldType.CHECKBOX: '#FF9800',
        FieldType.DATETIME: '#4CAF50',
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
        self.panning = False  # Add panning state
        self.resize_handle = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.pan_start_x = 0  # Panning start coordinates
        self.pan_start_y = 0
    
    def reset(self):
        """Reset all mouse state"""
        self.dragging = False
        self.resizing = False
        self.panning = False
        self.resize_handle = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.pan_start_x = 0
        self.pan_start_y = 0
    
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
    
    def start_pan(self, x, y):
        """Start panning operation"""
        self.panning = True
        self.pan_start_x = x
        self.pan_start_y = y


class ZoomState:
    """Manages zoom and view state"""
    
    def __init__(self):
        self.zoom_level = AppConstants.DEFAULT_ZOOM
        self.fit_to_window = True  # Whether to fit PDF to window initially
        self.center_x = 0  # Center point for zooming
        self.center_y = 0
    
    def set_zoom(self, new_zoom, center_x=None, center_y=None):
        """Set zoom level with optional center point"""
        # Clamp zoom to valid range
        self.zoom_level = max(AppConstants.MIN_ZOOM, 
                             min(AppConstants.MAX_ZOOM, new_zoom))
        
        if center_x is not None:
            self.center_x = center_x
        if center_y is not None:
            self.center_y = center_y
        
        self.fit_to_window = False  # Manual zoom disables auto-fit
        return self.zoom_level
    
    def zoom_in(self, center_x=None, center_y=None):
        """Zoom in by one step"""
        new_zoom = self.zoom_level + AppConstants.ZOOM_STEP
        return self.set_zoom(new_zoom, center_x, center_y)
    
    def zoom_out(self, center_x=None, center_y=None):
        """Zoom out by one step"""
        new_zoom = self.zoom_level - AppConstants.ZOOM_STEP
        return self.set_zoom(new_zoom, center_x, center_y)
    
    def reset_zoom(self):
        """Reset to default zoom and fit to window"""
        self.zoom_level = AppConstants.DEFAULT_ZOOM
        self.fit_to_window = True
    
    def get_zoom_percentage(self):
        """Get zoom level as percentage string"""
        return f"{int(self.zoom_level * 100)}%"