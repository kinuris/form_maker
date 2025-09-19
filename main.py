#!/usr/bin/env python3
"""
PDF Form Maker - Main Application

A modular GUI application for creating interactive PDF forms.

This is the main entry point that coordinates all the components:
- PDFHandler: Manages PDF operations
- FieldManager: Handles form field creation and manipulation  
- UI Components: Provides the user interface
- CoordinateTransformer: Handles coordinate conversions

Requirements: 
pip install PyMuPDF Pillow

Usage:
python main.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional

# Import our modular components
from models import FieldType, AppConstants, MouseState
from pdf_handler import PDFHandler
from field_manager import FieldManager
from ui_components import ToolbarFrame, NavigationFrame, StatusBar, ScrollableCanvas, FieldsSidebar
from history_manager import HistoryManager, CreateFieldCommand, DeleteFieldCommand, MoveFieldCommand, EditFieldCommand


class PdfFormMakerApp:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        """Initialize the application"""
        # Create main window
        self.root = tk.Tk()
        self.root.title("PDF Form Maker")
        self.root.geometry(f"{AppConstants.DEFAULT_WINDOW_SIZE[0]}x{AppConstants.DEFAULT_WINDOW_SIZE[1]}")
        self.root.configure(bg='#f0f0f0')
        
        # Application state
        self.current_tool: Optional[FieldType] = None
        self.mouse_state = MouseState()
        self.clipboard_field: Optional['FormField'] = None  # For copy/paste functionality
        
        # Create UI components
        self._create_ui_components()
        
        # Create core handlers
        self.pdf_handler = PDFHandler(self.canvas_frame.canvas)
        self.field_manager = FieldManager(self.canvas_frame.canvas, self.pdf_handler)
        self.history_manager = HistoryManager(max_history=25)
        
        # Bind events
        self._bind_events()
        
        # Set initial status
        self.status_bar.set_status("Ready - Open a PDF to get started")
    
    def _create_ui_components(self):
        """Create all UI components"""
        # Top toolbar with zoom controls
        self.toolbar = ToolbarFrame(
            self.root,
            on_open_pdf=self.open_pdf,
            on_tool_select=self.select_tool,
            on_zoom_in=self.zoom_in,
            on_zoom_out=self.zoom_out,
            on_fit_window=self.fit_to_window
        )
        self.toolbar.pack(fill='x', padx=5, pady=5)
        
        # Main content area (canvas + sidebar)
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Fields sidebar
        self.sidebar = FieldsSidebar(
            main_frame,
            on_field_select=self.on_sidebar_field_select,
            on_field_delete=self.on_sidebar_field_delete,
            on_field_edit=self.on_sidebar_field_edit,
            on_field_duplicate=self.on_sidebar_field_duplicate,
            on_field_name_changed=self.on_sidebar_field_name_changed
        )
        self.sidebar.pack(side='left', fill='y')
        
        # Main canvas area with mouse wheel zoom
        self.canvas_frame = ScrollableCanvas(
            main_frame,
            on_mouse_wheel_zoom=self.handle_mouse_wheel_zoom
        )
        self.canvas_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Bottom navigation
        self.navigation = NavigationFrame(
            self.root,
            on_prev_page=self.previous_page,
            on_next_page=self.next_page,
            on_save_pdf=self.save_pdf
        )
        self.navigation.pack(fill='x', padx=5, pady=5)
        
        # Status bar with zoom display
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill='x', side='bottom')
    
    def _bind_events(self):
        """Bind keyboard and mouse events"""
        # Keyboard events
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-s>', lambda e: self.save_pdf())
        self.root.bind('<Control-c>', lambda e: self.copy_field())
        self.root.bind('<Control-v>', lambda e: self.paste_field())
        self.root.bind('<Control-d>', lambda e: self.duplicate_field())
        self.root.bind('<Control-z>', lambda e: self.undo_last_action())
        self.root.bind('<Escape>', lambda e: self.clear_selection())
        
        # Arrow key handling for field movement (bind to root to ensure capture)
        self.root.bind('<Left>', self.handle_arrow_key)
        self.root.bind('<Right>', self.handle_arrow_key)
        self.root.bind('<Up>', self.handle_arrow_key)
        self.root.bind('<Down>', self.handle_arrow_key)
        
        # Arrow keys with Shift modifier for larger movements
        self.root.bind('<Shift-Left>', self.handle_arrow_key)
        self.root.bind('<Shift-Right>', self.handle_arrow_key)
        self.root.bind('<Shift-Up>', self.handle_arrow_key)
        self.root.bind('<Shift-Down>', self.handle_arrow_key)
        
        # Set focus on canvas for keyboard events
        self.canvas_frame.canvas.focus_set()
        
        # Canvas mouse events
        self.canvas_frame.bind_events(
            **{
                '<Button-1>': self.on_canvas_click,
                '<B1-Motion>': self.on_canvas_drag,
                '<ButtonRelease-1>': self.on_canvas_release,
                '<Motion>': self.on_canvas_motion
            }
        )
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def open_pdf(self):
        """Open and load a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=AppConstants.PDF_FILE_TYPES
        )
        
        if not file_path:
            return
        
        # Load the PDF
        if self.pdf_handler.load_pdf(file_path):
            # Display first page
            if self.pdf_handler.display_page():
                # Detect and load existing form fields
                existing_fields = self.pdf_handler.detect_existing_fields()
                self.field_manager.load_existing_fields(existing_fields)
                
                # Update sidebar to show loaded fields
                self._update_sidebar()
                
                # Update UI
                self._update_navigation()
                self._update_zoom_display()  # Initialize zoom display
                self.navigation.set_save_enabled(True)
                
                # Update status message based on whether fields were found
                if existing_fields:
                    self.status_bar.set_status(f"PDF loaded: {self.pdf_handler.total_pages} pages, {len(existing_fields)} existing fields detected")
                    messagebox.showinfo("Success", f"PDF loaded successfully!\\nPages: {self.pdf_handler.total_pages}\\nExisting fields detected: {len(existing_fields)}")
                else:
                    self.status_bar.set_status(f"PDF loaded: {self.pdf_handler.total_pages} pages - Use toolbar to add form fields")
                    messagebox.showinfo("Success", f"PDF loaded successfully!\\nPages: {self.pdf_handler.total_pages}\\nNo existing form fields found")
            else:
                messagebox.showerror("Error", "Failed to display PDF page")
        else:
            messagebox.showerror("Error", "Failed to open PDF file")
    
    def select_tool(self, field_type: FieldType):
        """Select a form field tool"""
        self.current_tool = field_type
        self.field_manager.clear_selection()
        self.status_bar.set_status(f"Selected tool: {field_type.value.title()} - Click on the PDF to add a field")
    
    def clear_selection(self):
        """Clear current selections"""
        self.field_manager.clear_selection()
        self.current_tool = None
        self.toolbar.clear_tool_selection()
        self.status_bar.set_status("Selection cleared")
    
    def handle_arrow_key(self, event):
        """Handle arrow key events for field movement or canvas panning"""
        print(f"DEBUG: Arrow key pressed - {event.keysym}")  # Debug print
        
        # Check if canvas has focus (or any of its children)
        focused_widget = self.root.focus_get()
        canvas_has_focus = (focused_widget == self.canvas_frame.canvas or 
                           (focused_widget and str(focused_widget).startswith(str(self.canvas_frame.canvas))))
        
        if not canvas_has_focus:
            print(f"DEBUG: Canvas doesn't have focus (focused: {focused_widget}), ignoring arrow key")
            return
        
        print(f"DEBUG: Canvas has focus, processing arrow key")
        
        # Check if a field is selected
        if self.field_manager.selected_field:
            print(f"DEBUG: Moving selected field: {self.field_manager.selected_field.name}")  # Debug print
            # Move the selected field
            self.move_selected_field_with_arrow(event)
        else:
            print("DEBUG: No field selected, falling back to canvas panning")  # Debug print
            # Fall back to canvas panning
            self.canvas_frame.handle_keyboard_pan(event)
    
    def move_selected_field_with_arrow(self, event):
        """Move the selected field using arrow keys"""
        print(f"DEBUG: move_selected_field_with_arrow called with {event.keysym}")  # Debug print
        
        if not self.field_manager.selected_field:
            print("DEBUG: No selected field in move method")  # Debug print
            return
        
        # Define movement step size (in canvas pixels)
        step_size = 2  # pixels (reduced to 1/3 of original 5px)
        large_step_size = 7  # pixels for Shift+Arrow (reduced to 1/3 of original 20px)
        
        # Check if Shift modifier is pressed
        shift_pressed = event.state & 0x1  # Shift key state flag
        
        # Use larger step if Shift is pressed
        current_step = large_step_size if shift_pressed else step_size
        
        # Calculate movement delta based on direction
        dx, dy = 0, 0
        direction = event.keysym
        if direction == 'Left':
            dx = -current_step
        elif direction == 'Right':
            dx = current_step
        elif direction == 'Up':
            dy = -current_step
        elif direction == 'Down':
            dy = current_step
        
        # Store original position for undo
        field = self.field_manager.selected_field
        original_rect = field.rect.copy()
        
        # Create move command for history
        new_rect = field.rect.copy()
        new_rect[0] += dx  # x1
        new_rect[1] += dy  # y1
        new_rect[2] += dx  # x2
        new_rect[3] += dy  # y2
        move_command = MoveFieldCommand(self.field_manager, field, original_rect, new_rect)
        
        # Execute the move command through history manager
        self.history_manager.execute_command(move_command)
        
        # Update sidebar if the field was moved
        self._update_sidebar()
        
        # Update status
        field_name = self.field_manager.selected_field.name
        modifier_text = " (large step)" if shift_pressed else ""
        self.status_bar.set_status(f"Moved field '{field_name}' {direction.lower()}{modifier_text}")
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.pdf_handler.pdf_doc:
            return
        
        # Get canvas coordinates
        x, y = self.canvas_frame.get_canvas_coords(event)
        print(f"Canvas click at: ({x:.1f}, {y:.1f})")
        
        # Check if clicking on a resize handle
        handle_clicked = self.field_manager.check_resize_handle_click(x, y)
        if handle_clicked:
            self.mouse_state.start_resize(x, y, handle_clicked)
            return
        
        # Check if clicking on an existing field
        clicked_field = self.field_manager.get_field_at_position(
            x, y, self.pdf_handler.current_page
        )
        
        if clicked_field:
            # Select the field
            self.field_manager.select_field(clicked_field)
            self.sidebar.select_field(clicked_field)  # Update sidebar selection
            
            # Store original field position for undo
            self.original_field_rect = clicked_field.rect.copy()
            
            self.mouse_state.start_drag(x, y)
            self.status_bar.set_status(f"Selected {clicked_field.type.value} field - Drag to move, use arrow keys or handles to resize, or press Delete to remove")
            
        elif self.current_tool:
            # Create new field at click position
            field = self.field_manager.create_field(
                self.current_tool, x, y, self.pdf_handler.current_page
            )
            
            # Create history command for field creation (already executed)
            create_command = CreateFieldCommand(self.field_manager, field)
            create_command.was_executed = True  # Mark as executed since field was already created
            self.history_manager.add_command(create_command)
            
            # Draw and select the new field
            self.field_manager.draw_field(field)
            self.field_manager.select_field(field)
            
            # Update sidebar
            self._update_sidebar()
            
            # Clear tool selection
            self.current_tool = None
            self.toolbar.clear_tool_selection()
            self.status_bar.set_status(f"Created {field.type.value} field - Use mouse to move/resize, arrow keys to fine-tune position, or Delete key to remove")
            
        else:
            # Clear selection if clicking on empty space
            self.field_manager.clear_selection()
            self.sidebar.select_field(None)  # Clear sidebar selection
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if not self.pdf_handler.pdf_doc:
            return
        
        x, y = self.canvas_frame.get_canvas_coords(event)
        
        if self.mouse_state.resizing and self.field_manager.selected_field:
            # Resize the selected field
            self.field_manager.resize_field(
                self.field_manager.selected_field,
                self.mouse_state.resize_handle,
                x, y
            )
            
        elif self.mouse_state.dragging and self.field_manager.selected_field:
            # Move the selected field
            dx = x - self.mouse_state.drag_start_x
            dy = y - self.mouse_state.drag_start_y
            
            self.field_manager.move_field(
                self.field_manager.selected_field,
                dx, dy
            )
            
            # Update drag start position
            self.mouse_state.drag_start_x = x
            self.mouse_state.drag_start_y = y
    
    def on_canvas_release(self, event):
        """Handle canvas mouse release events"""
        # If we were dragging a field, create a move command for history
        if (self.mouse_state.dragging and self.field_manager.selected_field and 
            hasattr(self, 'original_field_rect') and self.original_field_rect):
            
            current_rect = self.field_manager.selected_field.rect
            
            # Only create move command if position actually changed
            if current_rect != self.original_field_rect:
                move_command = MoveFieldCommand(
                    self.field_manager, 
                    self.field_manager.selected_field,
                    self.original_field_rect,
                    current_rect.copy()
                )
                # Add to history without executing since field was already moved during drag
                self.history_manager.add_command(move_command)
            
            self.original_field_rect = None
        
        self.mouse_state.reset()
    
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion for cursor changes"""
        if not self.pdf_handler.pdf_doc or not self.field_manager.selected_field:
            self.canvas_frame.set_cursor("")
            return
        
        x, y = self.canvas_frame.get_canvas_coords(event)
        
        # Check if over a resize handle
        handle = self.field_manager.check_resize_handle_click(x, y)
        if handle:
            cursor = AppConstants.RESIZE_CURSORS.get(handle, "")
            self.canvas_frame.set_cursor(cursor)
        elif self.field_manager.get_field_at_position(x, y, self.pdf_handler.current_page):
            self.canvas_frame.set_cursor("fleur")  # Move cursor
        else:
            self.canvas_frame.set_cursor("")
    
    def on_key_press(self, event):
        """Handle key press events"""
        if event.keysym == 'Delete' and self.field_manager.selected_field:
            self.delete_selected_field()
        elif event.keysym == 'Escape':
            self.clear_selection()
    
    def delete_selected_field(self):
        """Delete the currently selected field"""
        if not self.field_manager.selected_field:
            return
        
        field = self.field_manager.selected_field
        
        # Ask for confirmation
        result = messagebox.askyesno(
            "Delete Field",
            f"Are you sure you want to delete the {field.type.value} field '{field.name}'?"
        )
        
        if result:
            # Create delete command and execute it
            delete_command = DeleteFieldCommand(self.field_manager, field)
            self.history_manager.execute_command(delete_command)
            
            self.status_bar.set_status(f"Deleted {field.type.value} field")
            # Update sidebar after deletion
            self._update_sidebar()
    
    def copy_field(self):
        """Copy the currently selected field to clipboard"""
        if not self.field_manager.selected_field:
            self.status_bar.set_status("No field selected to copy")
            return
        
        # Create a copy of the field (deep copy of properties)
        from copy import deepcopy
        self.clipboard_field = deepcopy(self.field_manager.selected_field)
        # Clear the canvas_id as it will be assigned when pasted
        self.clipboard_field.canvas_id = None
        
        self.status_bar.set_status(f"Copied {self.clipboard_field.type.value} field '{self.clipboard_field.name}'")
    
    def paste_field(self):
        """Paste the copied field at the current mouse position or a default location"""
        if not self.clipboard_field:
            self.status_bar.set_status("No field in clipboard to paste")
            return
        
        if not self.pdf_handler.pdf_doc:
            self.status_bar.set_status("No PDF loaded")
            return
        
        # Create a copy of the clipboard field for pasting
        from copy import deepcopy
        new_field = deepcopy(self.clipboard_field)
        
        # Generate a unique name for the pasted field
        base_name = new_field.name
        counter = 1
        while any(field.name == new_field.name for field in self.field_manager.fields):
            new_field.name = f"{base_name}_copy_{counter}"
            counter += 1
        
        # Set the current page
        new_field.page_num = self.pdf_handler.current_page
        
        # Position the field slightly offset from original or at a default location
        original_rect = new_field.rect
        offset = 20.0  # pixels
        new_field.rect = [
            original_rect[0] + offset,
            original_rect[1] + offset,
            original_rect[2] + offset,
            original_rect[3] + offset
        ]
        
        # Add the field through the field manager
        self.field_manager.add_field(new_field)
        self.field_manager.select_field(new_field)
        
        # Update sidebar
        self._update_sidebar()
        
        self.status_bar.set_status(f"Pasted {new_field.type.value} field '{new_field.name}'")
    
    def duplicate_field(self):
        """Duplicate the currently selected field (copy + paste in one action)"""
        if not self.field_manager.selected_field:
            self.status_bar.set_status("No field selected to duplicate")
            return
        
        # Store the original clipboard field
        original_clipboard = self.clipboard_field
        
        # Copy the current field
        self.copy_field()
        
        # Paste it
        self.paste_field()
        
        # Restore the original clipboard
        self.clipboard_field = original_clipboard
    
    def undo_last_action(self):
        """Undo the last action using the history manager"""
        try:
            if self.history_manager.undo():
                description = self.history_manager.get_undo_description()
                self.status_bar.set_status(f"Undone: {description}" if description else "Undone last action")
                
                # Refresh UI
                self._update_sidebar()
                self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
            else:
                self.status_bar.set_status("Nothing to undo")
        except Exception as e:
            print(f"Error during undo: {e}")
            self.status_bar.set_status("Error during undo operation")
    
    def previous_page(self):
        """Go to previous page"""
        if self.pdf_handler.previous_page():
            self.field_manager.clear_selection()
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
            self._update_navigation()
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_handler.next_page():
            self.field_manager.clear_selection()
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
            self._update_navigation()
    
    def _update_navigation(self):
        """Update navigation button states"""
        self.navigation.update_page_info(
            self.pdf_handler.current_page,
            self.pdf_handler.total_pages
        )
    
    def save_pdf(self):
        """Save the PDF with form fields"""
        if not self.pdf_handler.pdf_doc:
            messagebox.showwarning("Warning", "No PDF loaded.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save PDF with form fields",
            defaultextension=".pdf",
            filetypes=AppConstants.PDF_FILE_TYPES
        )
        
        if not file_path:
            return
        
        # Save the PDF with fields (even if empty - this removes all fields)
        if self.pdf_handler.save_pdf_with_fields(file_path, self.field_manager.fields):
            field_count = len(self.field_manager.fields)
            if field_count > 0:
                messagebox.showinfo(
                    "Success",
                    f"PDF saved successfully!\\nFile: {file_path}\\nFields added: {field_count}"
                )
                self.status_bar.set_status(f"PDF saved: {field_count} fields added")
            else:
                messagebox.showinfo(
                    "Success",
                    f"PDF saved successfully!\\nFile: {file_path}\\nAll form fields removed"
                )
                self.status_bar.set_status("PDF saved: all form fields removed")
        else:
            messagebox.showerror("Error", "Failed to save PDF")
    
    # Zoom control methods
    def zoom_in(self):
        """Zoom in on the PDF"""
        if self.pdf_handler.zoom_in():
            self._update_zoom_display()
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
    
    def zoom_out(self):
        """Zoom out on the PDF"""
        if self.pdf_handler.zoom_out():
            self._update_zoom_display()
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
    
    def fit_to_window(self):
        """Fit PDF to window"""
        if self.pdf_handler.fit_to_window():
            self._update_zoom_display()
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
    
    def handle_mouse_wheel_zoom(self, event):
        """Handle mouse wheel zoom"""
        if self.pdf_handler.handle_mouse_wheel_zoom(event):
            self._update_zoom_display()
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
    
    def _update_zoom_display(self):
        """Update the zoom percentage in status bar"""
        zoom_percentage = self.pdf_handler.get_zoom_percentage()
        self.status_bar.set_zoom(zoom_percentage)
    
    # Sidebar callback methods
    def on_sidebar_field_select(self, field):
        """Handle field selection from sidebar"""
        self.field_manager.select_field(field)
        self.status_bar.set_status(f"Selected {field.type.value} field '{field.name}'")
    
    def on_sidebar_field_delete(self, field):
        """Handle field deletion from sidebar"""
        # Create delete command and execute it
        delete_command = DeleteFieldCommand(self.field_manager, field)
        self.history_manager.execute_command(delete_command)
        
        self._update_sidebar()
        self.status_bar.set_status(f"Deleted {field.type.value} field '{field.name}'")
    
    def on_sidebar_field_edit(self, field):
        """Handle field editing from sidebar"""
        self._edit_field_properties(field)
    
    def on_sidebar_field_duplicate(self, field):
        """Handle field duplication from sidebar"""
        self._duplicate_field(field)
    
    def on_sidebar_field_name_changed(self, field, old_name, new_name):
        """Handle field name change from sidebar"""
        # Update the canvas display to reflect the name change
        self.field_manager.refresh_canvas()
        # Update status bar to show the change
        self.status_bar.set_status(f"Field renamed from '{old_name}' to '{new_name}'")
    
    def _edit_field_properties(self, field):
        """Open field properties dialog"""
        # Create a simple property editor dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {field.type.value} Field")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Field name
        tk.Label(dialog, text="Field Name:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(20, 5))
        name_var = tk.StringVar(value=field.name)
        name_entry = tk.Entry(dialog, textvariable=name_var, font=('Arial', 10))
        name_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Field type (readonly)
        tk.Label(dialog, text="Field Type:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(10, 5))
        type_label = tk.Label(dialog, text=field.type.value.title(), font=('Arial', 10), fg=AppConstants.FIELD_COLORS[field.type])
        type_label.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Page number (readonly)
        tk.Label(dialog, text="Page:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(10, 5))
        page_label = tk.Label(dialog, text=f"Page {field.page_num + 1}", font=('Arial', 10))
        page_label.pack(anchor='w', padx=20, pady=(0, 10))
        
        # Options for dropdown
        format_frame = None
        format_var = None
        if field.type == FieldType.DATE:
            tk.Label(dialog, text="Date Format:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(10, 5))
            format_var = tk.StringVar(value=field.date_format or "MM/DD/YYYY")
            
            format_frame = tk.Frame(dialog)
            format_frame.pack(fill='x', padx=20, pady=(0, 10))
            
            # Format dropdown
            format_options = ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD", "DD MMM YYYY", "MMM DD, YYYY"]
            format_combo = tk.StringVar()
            format_combo.set(format_var.get())
            
            format_entry = tk.Entry(format_frame, textvariable=format_combo, font=('Arial', 10))
            format_entry.pack(fill='x')
            
            # Add some example formats as buttons
            examples_frame = tk.Frame(dialog)
            examples_frame.pack(fill='x', padx=20, pady=(5, 10))
            
            for fmt in format_options:
                btn = tk.Button(examples_frame, text=fmt, 
                              command=lambda f=fmt: format_combo.set(f),
                              font=('Arial', 8), relief='flat', bg='#e0e0e0')
                btn.pack(side='left', padx=(0, 5), pady=2)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def save_changes():
            # Update field name
            new_name = name_var.get().strip()
            if new_name and new_name != field.name:
                field.name = new_name
            
            # Update date format for date fields
            if field.type == FieldType.DATE and format_combo:
                new_format = format_combo.get().strip()
                if new_format:
                    field.date_format = new_format
            
            # Refresh display
            self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
            self._update_sidebar()
            
            dialog.destroy()
            self.status_bar.set_status(f"Updated {field.type.value} field '{field.name}'")
        
        def cancel_changes():
            dialog.destroy()
        
        tk.Button(button_frame, text="Save", command=save_changes, bg='#4CAF50', fg='white', font=('Arial', 10)).pack(side='right', padx=(5, 0))
        tk.Button(button_frame, text="Cancel", command=cancel_changes, bg='#f44336', fg='white', font=('Arial', 10)).pack(side='right')
        
        # Focus on name entry
        name_entry.focus_set()
        name_entry.select_range(0, 'end')
    
    def _duplicate_field(self, field):
        """Duplicate a field"""
        # Create a copy of the field with slight offset
        offset = 20  # PDF units
        
        # Get current field's PDF coordinates
        pdf_rect = field.rect.copy()
        new_rect = [pdf_rect[0] + offset, pdf_rect[1] + offset, pdf_rect[2] + offset, pdf_rect[3] + offset]
        
        # Create new field
        new_field = self.field_manager.create_field(
            field.type, 
            0, 0,  # These will be overridden
            field.page_num
        )
        
        # Set the new position
        new_field.rect = new_rect
        
        # Copy properties
        if hasattr(field, 'options') and field.options:
            new_field.options = field.options.copy()
        if hasattr(field, 'group') and field.group:
            new_field.group = field.group
        if hasattr(field, 'value') and field.value:
            new_field.value = field.value
        
        # Redraw and update
        self.field_manager.redraw_fields_for_page(self.pdf_handler.current_page)
        self._update_sidebar()
        self.status_bar.set_status(f"Duplicated {field.type.value} field")
    
    def _update_sidebar(self):
        """Update the sidebar with current fields"""
        if hasattr(self, 'sidebar'):
            self.sidebar.update_fields(self.field_manager.fields)
    
    def on_closing(self):
        """Handle application closing"""
        self.pdf_handler.close_pdf()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = PdfFormMakerApp()
    app.run()


if __name__ == "__main__":
    main()