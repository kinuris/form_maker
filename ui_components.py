#!/usr/bin/env python3
"""
UI Components for PDF Form Maker

Contains reusable UI components and widgets.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict
from models import FieldType, AppConstants


class ToolbarFrame(tk.Frame):
    """Toolbar frame containing field tools and open PDF button"""
    
    def __init__(self, parent, on_open_pdf: Callable, on_tool_select: Callable):
        """
        Initialize the toolbar
        
        Args:
            parent: Parent widget
            on_open_pdf: Callback for opening PDF
            on_tool_select: Callback for tool selection
        """
        super().__init__(parent, bg='#e0e0e0', height=AppConstants.TOOLBAR_HEIGHT)
        self.pack_propagate(False)
        
        self.on_tool_select = on_tool_select
        self.selected_tool: Optional[FieldType] = None
        self.tool_buttons: Dict[FieldType, tk.Button] = {}
        
        self._create_widgets(on_open_pdf)
    
    def _create_widgets(self, on_open_pdf: Callable):
        """Create toolbar widgets"""
        # Open PDF button
        self.open_btn = tk.Button(
            self,
            text="Open PDF",
            command=on_open_pdf,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        self.open_btn.pack(side='left', padx=5, pady=10)
        
        # Separator
        separator1 = tk.Frame(self, width=2, bg='#ccc')
        separator1.pack(side='left', fill='y', padx=10, pady=10)
        
        # Tool buttons
        tools = [
            ('Text Field', FieldType.TEXT),
            ('Checkbox', FieldType.CHECKBOX),
            ('Radio Button', FieldType.RADIO),
            ('Dropdown', FieldType.DROPDOWN),
            ('Signature', FieldType.SIGNATURE)
        ]
        
        for tool_name, field_type in tools:
            color = AppConstants.FIELD_COLORS[field_type]
            btn = tk.Button(
                self,
                text=tool_name,
                command=lambda ft=field_type: self.select_tool(ft),
                bg=color,
                fg='white',
                font=('Arial', 9),
                relief='raised'
            )
            btn.pack(side='left', padx=2, pady=10)
            self.tool_buttons[field_type] = btn
    
    def select_tool(self, field_type: FieldType):
        """Select a tool and update button appearance"""
        # Update selected tool
        self.selected_tool = field_type
        
        # Update button appearance
        for tool, button in self.tool_buttons.items():
            if tool == field_type:
                button.config(relief='sunken', bg='#555555')
            else:
                color = AppConstants.FIELD_COLORS[tool]
                button.config(relief='raised', bg=color)
        
        # Notify callback
        self.on_tool_select(field_type)
    
    def clear_tool_selection(self):
        """Clear tool selection"""
        self.selected_tool = None
        
        # Reset all button appearances
        for tool, button in self.tool_buttons.items():
            color = AppConstants.FIELD_COLORS[tool]
            button.config(relief='raised', bg=color)


class NavigationFrame(tk.Frame):
    """Navigation frame with page controls and save button"""
    
    def __init__(self, parent, on_prev_page: Callable, on_next_page: Callable, on_save_pdf: Callable):
        """
        Initialize the navigation frame
        
        Args:
            parent: Parent widget
            on_prev_page: Callback for previous page
            on_next_page: Callback for next page
            on_save_pdf: Callback for saving PDF
        """
        super().__init__(parent, bg='#e0e0e0', height=AppConstants.NAV_BAR_HEIGHT)
        self.pack_propagate(False)
        
        self._create_widgets(on_prev_page, on_next_page, on_save_pdf)
    
    def _create_widgets(self, on_prev_page: Callable, on_next_page: Callable, on_save_pdf: Callable):
        """Create navigation widgets"""
        # Previous page button
        self.prev_btn = tk.Button(
            self,
            text="← Previous",
            command=on_prev_page,
            state='disabled'
        )
        self.prev_btn.pack(side='left', padx=5, pady=10)
        
        # Page info label
        self.page_label = tk.Label(
            self,
            text="No PDF loaded",
            bg='#e0e0e0'
        )
        self.page_label.pack(side='left', padx=20, pady=10)
        
        # Next page button
        self.next_btn = tk.Button(
            self,
            text="Next →",
            command=on_next_page,
            state='disabled'
        )
        self.next_btn.pack(side='left', padx=5, pady=10)
        
        # Save button
        self.save_btn = tk.Button(
            self,
            text="Save As...",
            command=on_save_pdf,
            bg='#FF5722',
            fg='white',
            font=('Arial', 10, 'bold'),
            state='disabled'
        )
        self.save_btn.pack(side='right', padx=5, pady=10)
    
    def update_page_info(self, current_page: int, total_pages: int):
        """Update page information display"""
        if total_pages > 0:
            self.page_label.config(text=f"Page {current_page + 1} of {total_pages}")
            self.prev_btn.config(state='normal' if current_page > 0 else 'disabled')
            self.next_btn.config(state='normal' if current_page < total_pages - 1 else 'disabled')
        else:
            self.page_label.config(text="No PDF loaded")
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
    
    def set_save_enabled(self, enabled: bool):
        """Enable or disable the save button"""
        self.save_btn.config(state='normal' if enabled else 'disabled')


class StatusBar(tk.Frame):
    """Status bar for showing application status"""
    
    def __init__(self, parent):
        """Initialize the status bar"""
        super().__init__(parent, bg='#d0d0d0', height=AppConstants.STATUS_BAR_HEIGHT)
        self.pack_propagate(False)
        
        self.status_label = tk.Label(
            self,
            text="Ready - Open a PDF to get started",
            bg='#d0d0d0',
            anchor='w',
            font=('Arial', 9)
        )
        self.status_label.pack(fill='x', padx=5, pady=3)
    
    def set_status(self, message: str):
        """Set the status message"""
        self.status_label.config(text=message)


class ScrollableCanvas(tk.Frame):
    """Canvas with scrollbars for PDF display"""
    
    def __init__(self, parent):
        """Initialize the scrollable canvas"""
        super().__init__(parent, bg='white')
        
        # Create canvas
        self.canvas = tk.Canvas(
            self,
            bg='white',
            scrollregion=(0, 0, 800, 1000)
        )
        
        # Create scrollbars
        self.v_scrollbar = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        
        # Configure canvas scrolling
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # Pack scrollbars and canvas
        self.v_scrollbar.pack(side='right', fill='y')
        self.h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
    
    def bind_events(self, **event_handlers):
        """Bind events to the canvas"""
        for event, handler in event_handlers.items():
            self.canvas.bind(event, handler)
    
    def set_cursor(self, cursor: str):
        """Set canvas cursor"""
        self.canvas.config(cursor=cursor)
    
    def get_canvas_coords(self, event):
        """Get canvas coordinates from event (accounting for scrolling)"""
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)