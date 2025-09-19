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
            ('Date/Time', FieldType.DATETIME),
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
            scrollregion=(0, 0, 800, 1000),
            takefocus=True  # Allow canvas to receive keyboard focus
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
        
        # Set initial focus on canvas
        self.canvas.focus_set()
        
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


class FieldsSidebar(tk.Frame):
    """Sidebar for managing form fields with quick actions"""
    
    def __init__(self, parent, on_field_select: Callable = None, on_field_delete: Callable = None, 
                 on_field_edit: Callable = None, on_field_duplicate: Callable = None):
        """
        Initialize the fields sidebar
        
        Args:
            parent: Parent widget
            on_field_select: Callback when a field is selected
            on_field_delete: Callback when a field is deleted
            on_field_edit: Callback when a field is edited
            on_field_duplicate: Callback when a field is duplicated
        """
        super().__init__(parent, bg='#f5f5f5', width=250)
        self.pack_propagate(False)
        
        self.on_field_select = on_field_select
        self.on_field_delete = on_field_delete
        self.on_field_edit = on_field_edit
        self.on_field_duplicate = on_field_duplicate
        
        self.fields = []
        self.selected_field = None
        self.field_items = {}  # Map field name to UI items
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create sidebar widgets"""
        # Header
        header_frame = tk.Frame(self, bg='#e0e0e0', height=40)
        header_frame.pack(fill='x', padx=5, pady=5)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="Form Fields",
            bg='#e0e0e0',
            font=('Arial', 12, 'bold'),
            anchor='w'
        )
        header_label.pack(side='left', padx=10, pady=10)
        
        # Fields count
        self.count_label = tk.Label(
            header_frame,
            text="(0)",
            bg='#e0e0e0',
            font=('Arial', 10),
            anchor='e',
            fg='#666666'
        )
        self.count_label.pack(side='right', padx=10, pady=10)
        
        # Scrollable fields list
        self.list_frame = tk.Frame(self, bg='#f5f5f5')
        self.list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar for fields list
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side='right', fill='y')
        
        self.canvas = tk.Canvas(
            self.list_frame,
            bg='#f5f5f5',
            yscrollcommand=self.scrollbar.set,
            highlightthickness=0
        )
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        # Inner frame for field items
        self.inner_frame = tk.Frame(self.canvas, bg='#f5f5f5')
        self.canvas_window = self.canvas.create_window(0, 0, anchor='nw', window=self.inner_frame)
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.inner_frame.bind('<Configure>', self._on_frame_configure)
        
        # Quick actions frame
        actions_frame = tk.Frame(self, bg='#e0e0e0', height=50)
        actions_frame.pack(fill='x', padx=5, pady=5)
        actions_frame.pack_propagate(False)
        
        # Quick action buttons
        self.edit_btn = tk.Button(
            actions_frame,
            text="Edit",
            command=self._edit_selected,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9),
            state='disabled'
        )
        self.edit_btn.pack(side='left', padx=2, pady=5)
        
        self.duplicate_btn = tk.Button(
            actions_frame,
            text="Duplicate",
            command=self._duplicate_selected,
            bg='#2196F3',
            fg='white',
            font=('Arial', 9),
            state='disabled'
        )
        self.duplicate_btn.pack(side='left', padx=2, pady=5)
        
        self.delete_btn = tk.Button(
            actions_frame,
            text="Delete",
            command=self._delete_selected,
            bg='#f44336',
            fg='white',
            font=('Arial', 9),
            state='disabled'
        )
        self.delete_btn.pack(side='left', padx=2, pady=5)
        
        # Clear all button
        self.clear_all_btn = tk.Button(
            actions_frame,
            text="Clear All",
            command=self._clear_all_fields,
            bg='#ff9800',
            fg='white',
            font=('Arial', 9),
            state='disabled'
        )
        self.clear_all_btn.pack(side='right', padx=2, pady=5)
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_frame_configure(self, event):
        """Handle frame resize"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
    
    def update_fields(self, fields):
        """Update the fields list"""
        self.fields = fields
        self._refresh_field_list()
        self._update_count()
        self._update_action_buttons()
    
    def refresh_field_list(self):
        """Public method to refresh the field list (convenience method)"""
        self._refresh_field_list()
        self._update_count()
        self._update_action_buttons()
    
    def _refresh_field_list(self):
        """Refresh the fields list display"""
        # Clear existing items
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.field_items.clear()
        
        # Add field items
        for i, field in enumerate(self.fields):
            self._create_field_item(field, i)
    
    def _create_field_item(self, field, index):
        """Create a field item in the list"""
        # Field container
        item_frame = tk.Frame(
            self.inner_frame,
            bg='white' if field != self.selected_field else '#e3f2fd',
            relief='solid',
            bd=1,
            pady=5
        )
        item_frame.pack(fill='x', padx=2, pady=2)
        
        # Field info
        info_frame = tk.Frame(item_frame, bg=item_frame['bg'])
        info_frame.pack(fill='x', padx=8, pady=4)
        
        # Field type and name
        type_label = tk.Label(
            info_frame,
            text=field.type.value.title(),
            font=('Arial', 10, 'bold'),
            bg=item_frame['bg'],
            fg=AppConstants.FIELD_COLORS[field.type],
            anchor='w'
        )
        type_label.pack(anchor='w')
        
        name_label = tk.Label(
            info_frame,
            text=field.name,
            font=('Arial', 9),
            bg=item_frame['bg'],
            fg='#666666',
            anchor='w'
        )
        name_label.pack(anchor='w')
        
        # Page info
        page_label = tk.Label(
            info_frame,
            text=f"Page {field.page_num + 1}",
            font=('Arial', 8),
            bg=item_frame['bg'],
            fg='#999999',
            anchor='w'
        )
        page_label.pack(anchor='w')
        
        # Click to select
        def on_click(event, f=field):
            self.select_field(f)
            if self.on_field_select:
                self.on_field_select(f)
        
        # Bind click events
        for widget in [item_frame, info_frame, type_label, name_label, page_label]:
            widget.bind('<Button-1>', on_click)
            widget.bind('<Enter>', lambda e, frame=item_frame: frame.config(bg='#f0f0f0' if frame['bg'] == 'white' else '#bbdefb'))
            widget.bind('<Leave>', lambda e, frame=item_frame, f=field: frame.config(bg='white' if f != self.selected_field else '#e3f2fd'))
        
        self.field_items[field.name] = item_frame
    
    def select_field(self, field):
        """Select a field in the list"""
        old_selected = self.selected_field
        self.selected_field = field
        
        # Update visual selection
        if old_selected and old_selected.name in self.field_items:
            self.field_items[old_selected.name].config(bg='white')
            for child in self.field_items[old_selected.name].winfo_children():
                self._update_widget_bg(child, 'white')
        
        if field and field.name in self.field_items:
            self.field_items[field.name].config(bg='#e3f2fd')
            for child in self.field_items[field.name].winfo_children():
                self._update_widget_bg(child, '#e3f2fd')
        
        self._update_action_buttons()
    
    def _update_widget_bg(self, widget, bg):
        """Recursively update widget background"""
        try:
            widget.config(bg=bg)
            for child in widget.winfo_children():
                self._update_widget_bg(child, bg)
        except:
            pass  # Some widgets might not support bg
    
    def _update_count(self):
        """Update the fields count display"""
        count = len(self.fields)
        self.count_label.config(text=f"({count})")
    
    def _update_action_buttons(self):
        """Update action button states"""
        has_fields = len(self.fields) > 0
        has_selection = self.selected_field is not None
        
        state = 'normal' if has_selection else 'disabled'
        self.edit_btn.config(state=state)
        self.duplicate_btn.config(state=state)
        self.delete_btn.config(state=state)
        
        self.clear_all_btn.config(state='normal' if has_fields else 'disabled')
    
    def _edit_selected(self):
        """Edit the selected field"""
        if self.selected_field and self.on_field_edit:
            self.on_field_edit(self.selected_field)
    
    def _duplicate_selected(self):
        """Duplicate the selected field"""
        if self.selected_field and self.on_field_duplicate:
            self.on_field_duplicate(self.selected_field)
    
    def _delete_selected(self):
        """Delete the selected field"""
        if self.selected_field and self.on_field_delete:
            self.on_field_delete(self.selected_field)
    
    def _clear_all_fields(self):
        """Clear all fields with confirmation"""
        if len(self.fields) > 0:
            import tkinter.messagebox as messagebox
            if messagebox.askyesno("Clear All Fields", f"Are you sure you want to delete all {len(self.fields)} fields?"):
                if self.on_field_delete:
                    # Delete all fields
                    for field in self.fields.copy():
                        self.on_field_delete(field)