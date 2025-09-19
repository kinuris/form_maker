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
from ui_components import ToolbarFrame, NavigationFrame, StatusBar, ScrollableCanvas


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
        
        # Create UI components
        self._create_ui_components()
        
        # Create core handlers
        self.pdf_handler = PDFHandler(self.canvas_frame.canvas)
        self.field_manager = FieldManager(self.canvas_frame.canvas)
        
        # Bind events
        self._bind_events()
        
        # Set initial status
        self.status_bar.set_status("Ready - Open a PDF to get started")
    
    def _create_ui_components(self):
        """Create all UI components"""
        # Top toolbar
        self.toolbar = ToolbarFrame(
            self.root,
            on_open_pdf=self.open_pdf,
            on_tool_select=self.select_tool
        )
        self.toolbar.pack(fill='x', padx=5, pady=5)
        
        # Main canvas area
        self.canvas_frame = ScrollableCanvas(self.root)
        self.canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bottom navigation
        self.navigation = NavigationFrame(
            self.root,
            on_prev_page=self.previous_page,
            on_next_page=self.next_page,
            on_save_pdf=self.save_pdf
        )
        self.navigation.pack(fill='x', padx=5, pady=5)
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill='x', side='bottom')
    
    def _bind_events(self):
        """Bind keyboard and mouse events"""
        # Keyboard events
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-s>', lambda e: self.save_pdf())
        self.root.bind('<Escape>', lambda e: self.clear_selection())
        self.root.focus_set()
        
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
                # Clear existing fields
                self.field_manager.clear_all_fields()
                
                # Update UI
                self._update_navigation()
                self.navigation.set_save_enabled(True)
                self.status_bar.set_status(f"PDF loaded: {self.pdf_handler.total_pages} pages - Use toolbar to add form fields")
                
                messagebox.showinfo("Success", f"PDF loaded successfully!\\nPages: {self.pdf_handler.total_pages}")
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
            self.mouse_state.start_drag(x, y)
            self.status_bar.set_status(f"Selected {clicked_field.type.value} field - Drag to move, use handles to resize, or press Delete to remove")
            
        elif self.current_tool:
            # Create new field at click position
            field = self.field_manager.create_field(
                self.current_tool, x, y, self.pdf_handler.current_page
            )
            
            # Draw and select the new field
            self.field_manager.draw_field(field)
            self.field_manager.select_field(field)
            
            # Clear tool selection
            self.current_tool = None
            self.toolbar.clear_tool_selection()
            self.status_bar.set_status(f"Created {field.type.value} field - Use mouse to move/resize or Delete key to remove")
            
        else:
            # Clear selection if clicking on empty space
            self.field_manager.clear_selection()
    
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
            self.field_manager.delete_field(field)
            self.status_bar.set_status(f"Deleted {field.type.value} field")
    
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
        if not self.pdf_handler.pdf_doc or not self.field_manager.fields:
            messagebox.showwarning("Warning", "No PDF loaded or no fields to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save PDF with form fields",
            defaultextension=".pdf",
            filetypes=AppConstants.PDF_FILE_TYPES
        )
        
        if not file_path:
            return
        
        # Save the PDF with fields
        if self.pdf_handler.save_pdf_with_fields(file_path, self.field_manager.fields):
            messagebox.showinfo(
                "Success",
                f"PDF saved successfully!\\nFile: {file_path}\\nFields added: {len(self.field_manager.fields)}"
            )
            self.status_bar.set_status(f"PDF saved: {len(self.field_manager.fields)} fields added")
        else:
            messagebox.showerror("Error", "Failed to save PDF")
    
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