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
    
    def __init__(self, parent, on_open_pdf: Callable, on_tool_select: Callable, 
                 on_zoom_in: Callable = None, on_zoom_out: Callable = None, 
                 on_fit_window: Callable = None):
        """
        Initialize the toolbar
        
        Args:
            parent: Parent widget
            on_open_pdf: Callback for opening PDF
            on_tool_select: Callback for tool selection
            on_zoom_in: Callback for zoom in
            on_zoom_out: Callback for zoom out
            on_fit_window: Callback for fit to window
        """
        super().__init__(parent, bg='#e0e0e0', height=AppConstants.TOOLBAR_HEIGHT)
        self.pack_propagate(False)
        
        self.on_tool_select = on_tool_select
        self.on_zoom_in = on_zoom_in
        self.on_zoom_out = on_zoom_out
        self.on_fit_window = on_fit_window
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
        
        # Add zoom controls
        if self.on_zoom_in or self.on_zoom_out or self.on_fit_window:
            # Separator
            separator2 = tk.Frame(self, width=2, bg='#ccc')
            separator2.pack(side='left', fill='y', padx=10, pady=10)
            
            # Zoom label
            zoom_label = tk.Label(self, text="Zoom:", bg='#e0e0e0', font=('Arial', 9))
            zoom_label.pack(side='left', padx=(5, 2), pady=10)
            
            # Zoom in button
            if self.on_zoom_in:
                self.zoom_in_btn = tk.Button(
                    self,
                    text="🔍+",
                    command=self.on_zoom_in,
                    bg='#2196F3',
                    fg='white',
                    font=('Arial', 9),
                    width=3
                )
                self.zoom_in_btn.pack(side='left', padx=1, pady=10)
            
            # Zoom out button
            if self.on_zoom_out:
                self.zoom_out_btn = tk.Button(
                    self,
                    text="🔍-",
                    command=self.on_zoom_out,
                    bg='#2196F3',
                    fg='white',
                    font=('Arial', 9),
                    width=3
                )
                self.zoom_out_btn.pack(side='left', padx=1, pady=10)
            
            # Fit to window button
            if self.on_fit_window:
                self.fit_btn = tk.Button(
                    self,
                    text="Fit",
                    command=self.on_fit_window,
                    bg='#2196F3',
                    fg='white',
                    font=('Arial', 9),
                    width=4
                )
                self.fit_btn.pack(side='left', padx=1, pady=10)
    
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
        
        # Left side - status message
        self.status_label = tk.Label(
            self,
            text="Ready - Open a PDF to get started",
            bg='#d0d0d0',
            anchor='w',
            font=('Arial', 9)
        )
        self.status_label.pack(side='left', fill='x', expand=True, padx=5, pady=3)
        
        # Right side - zoom percentage
        self.zoom_label = tk.Label(
            self,
            text="100%",
            bg='#d0d0d0',
            anchor='e',
            font=('Arial', 9),
            width=8
        )
        self.zoom_label.pack(side='right', padx=5, pady=3)
    
    def set_status(self, message: str):
        """Set the status message"""
        self.status_label.config(text=message)
    
    def set_zoom(self, zoom_percentage: str):
        """Set the zoom percentage display"""
        self.zoom_label.config(text=zoom_percentage)


class ScrollableCanvas(tk.Frame):
    """Canvas with scrollbars for PDF display"""
    
    def __init__(self, parent, on_mouse_wheel_zoom: Callable = None):
        """
        Initialize the scrollable canvas
        
        Args:
            parent: Parent widget
            on_mouse_wheel_zoom: Callback for mouse wheel zoom
        """
        super().__init__(parent, bg='white')
        
        self.on_mouse_wheel_zoom = on_mouse_wheel_zoom
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        
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
        
        # Bind mouse wheel events for zoom
        if self.on_mouse_wheel_zoom:
            self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_mouse_wheel)
            self.canvas.bind("<Control-Button-4>", self._on_ctrl_mouse_wheel)  # Linux
            self.canvas.bind("<Control-Button-5>", self._on_ctrl_mouse_wheel)  # Linux
        
        # Bind panning events (middle mouse button)
        self.canvas.bind("<Button-2>", self._start_pan)  # Middle mouse button press
        self.canvas.bind("<B2-Motion>", self._do_pan)    # Middle mouse button drag
        self.canvas.bind("<ButtonRelease-2>", self._end_pan)  # Middle mouse button release
        
        # Allow canvas to receive focus for keyboard events
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set())
        
        # Pack scrollbars and canvas
        self.v_scrollbar.pack(side='right', fill='y')
        self.h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
    
    def _on_ctrl_mouse_wheel(self, event):
        """Handle Ctrl+mouse wheel for zooming"""
        if self.on_mouse_wheel_zoom:
            self.on_mouse_wheel_zoom(event)
            return "break"  # Prevent default scrolling
    
    def _start_pan(self, event):
        """Start panning with middle mouse button"""
        self.panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.canvas.config(cursor="fleur")  # Change cursor to indicate panning
    
    def _do_pan(self, event):
        """Perform panning"""
        if not self.panning:
            return
        
        # Calculate pan distance
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        
        # Get current view
        x_view = self.canvas.xview()
        y_view = self.canvas.yview()
        
        # Get scroll region
        scroll_region = self.canvas.cget("scrollregion").split()
        if len(scroll_region) == 4:
            scroll_width = float(scroll_region[2])
            scroll_height = float(scroll_region[3])
            
            # Calculate new positions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Convert pixel movement to scroll fraction
            if scroll_width > canvas_width:
                x_fraction = -dx / scroll_width
                new_x = max(0, min(1 - (canvas_width / scroll_width), x_view[0] + x_fraction))
                self.canvas.xview_moveto(new_x)
            
            if scroll_height > canvas_height:
                y_fraction = -dy / scroll_height
                new_y = max(0, min(1 - (canvas_height / scroll_height), y_view[0] + y_fraction))
                self.canvas.yview_moveto(new_y)
        
        # Update pan start position
        self.pan_start_x = event.x
        self.pan_start_y = event.y
    
    def _end_pan(self, event):
        """End panning"""
        self.panning = False
        self.canvas.config(cursor="")  # Reset cursor
    
    def handle_keyboard_pan(self, event):
        """Handle keyboard panning (arrow keys)"""
        key = event.keysym
        pan_distance = 0.05  # Fraction to pan
        
        if key == "Left":
            x_view = self.canvas.xview()
            new_x = max(0, x_view[0] - pan_distance)
            self.canvas.xview_moveto(new_x)
            return "break"
        elif key == "Right":
            x_view = self.canvas.xview()
            canvas_width = self.canvas.winfo_width()
            scroll_region = self.canvas.cget("scrollregion").split()
            if len(scroll_region) == 4:
                scroll_width = float(scroll_region[2])
                max_x = max(0, 1 - (canvas_width / scroll_width))
                new_x = min(max_x, x_view[0] + pan_distance)
                self.canvas.xview_moveto(new_x)
            return "break"
        elif key == "Up":
            y_view = self.canvas.yview()
            new_y = max(0, y_view[0] - pan_distance)
            self.canvas.yview_moveto(new_y)
            return "break"
        elif key == "Down":
            y_view = self.canvas.yview()
            canvas_height = self.canvas.winfo_height()
            scroll_region = self.canvas.cget("scrollregion").split()
            if len(scroll_region) == 4:
                scroll_height = float(scroll_region[3])
                max_y = max(0, 1 - (canvas_height / scroll_height))
                new_y = min(max_y, y_view[0] + pan_distance)
                self.canvas.yview_moveto(new_y)
            return "break"
    
    def bind_events(self, **event_handlers):
        """Bind events to the canvas"""
        for event, handler in event_handlers.items():
            self.canvas.bind(event, handler)
    
    def set_cursor(self, cursor: str):
        """Set canvas cursor"""
        if not self.panning:  # Don't override panning cursor
            self.canvas.config(cursor=cursor)
    
    def get_canvas_coords(self, event):
        """Get canvas coordinates from event (accounting for scrolling)"""
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)