#!/usr/bin/env python3
"""
PDF Form Maker - A GUI application for creating interactive PDF forms

This application allows users to:
- Open PDF files and display them in a canvas
- Add interactive form fields (text, checkbox, radio, dropdown, signature)
- Position and resize fields with mouse interaction
- Navigate through multiple pages
- Save the result as a fillable PDF

Requirements: 
pip install PyMuPDF Pillow

Usage:
python pdf_form_maker.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io


class PdfFormMaker:
    """Main application class for the PDF Form Maker"""
    
    def __init__(self):
        """Initialize the application"""
        self.root = tk.Tk()
        self.root.title("PDF Form Maker")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Application state
        self.pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.current_tool = None
        self.selected_field = None
        self.fields = []  # List of all form fields across all pages
        self.canvas_image = None
        self.pdf_scale = 1.0
        self.pdf_width = 0
        self.pdf_height = 0
        
        # Mouse interaction state
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.field_counter = 0  # For generating unique field names
        
        # Create the UI
        self.create_widgets()
        self.bind_events()
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Top toolbar frame
        self.toolbar_frame = tk.Frame(self.root, bg='#e0e0e0', height=60)
        self.toolbar_frame.pack(fill='x', padx=5, pady=5)
        self.toolbar_frame.pack_propagate(False)
        
        # Open PDF button
        self.open_btn = tk.Button(
            self.toolbar_frame, 
            text="Open PDF", 
            command=self.open_pdf,
            bg='#4CAF50', 
            fg='white', 
            font=('Arial', 10, 'bold')
        )
        self.open_btn.pack(side='left', padx=5, pady=10)
        
        # Separator
        separator1 = tk.Frame(self.toolbar_frame, width=2, bg='#ccc')
        separator1.pack(side='left', fill='y', padx=10, pady=10)
        
        # Tool buttons
        self.tool_buttons = {}
        tools = [
            ('Text Field', 'text', '#2196F3'),
            ('Checkbox', 'checkbox', '#FF9800'),
            ('Radio Button', 'radio', '#9C27B0'),
            ('Dropdown', 'dropdown', '#607D8B'),
            ('Signature', 'signature', '#795548')
        ]
        
        for tool_name, tool_type, color in tools:
            btn = tk.Button(
                self.toolbar_frame,
                text=tool_name,
                command=lambda t=tool_type: self.select_tool(t),
                bg=color,
                fg='white',
                font=('Arial', 9),
                relief='raised'
            )
            btn.pack(side='left', padx=2, pady=10)
            self.tool_buttons[tool_type] = btn
        
        # Main canvas frame
        self.canvas_frame = tk.Frame(self.root, bg='white')
        self.canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Canvas with scrollbars
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg='white', 
            scrollregion=(0, 0, 800, 1000)
        )
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(self.canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Bottom navigation frame
        self.nav_frame = tk.Frame(self.root, bg='#e0e0e0', height=50)
        self.nav_frame.pack(fill='x', padx=5, pady=5)
        self.nav_frame.pack_propagate(False)
        
        # Previous page button
        self.prev_btn = tk.Button(
            self.nav_frame,
            text="← Previous",
            command=self.prev_page,
            state='disabled'
        )
        self.prev_btn.pack(side='left', padx=5, pady=10)
        
        # Page info label
        self.page_label = tk.Label(
            self.nav_frame,
            text="No PDF loaded",
            bg='#e0e0e0'
        )
        self.page_label.pack(side='left', padx=20, pady=10)
        
        # Next page button
        self.next_btn = tk.Button(
            self.nav_frame,
            text="Next →",
            command=self.next_page,
            state='disabled'
        )
        self.next_btn.pack(side='left', padx=5, pady=10)
        
        # Save button
        self.save_btn = tk.Button(
            self.nav_frame,
            text="Save As...",
            command=self.save_pdf,
            bg='#FF5722',
            fg='white',
            font=('Arial', 10, 'bold'),
            state='disabled'
        )
        self.save_btn.pack(side='right', padx=5, pady=10)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg='#d0d0d0', height=25)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready - Open a PDF to get started",
            bg='#d0d0d0',
            anchor='w',
            font=('Arial', 9)
        )
        self.status_label.pack(fill='x', padx=5, pady=3)
        
    def bind_events(self):
        """Bind keyboard and mouse events"""
        # Keyboard events
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-s>', lambda e: self.save_pdf())
        self.root.bind('<Escape>', lambda e: self.clear_selection())
        self.root.focus_set()
        
        # Canvas mouse events
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        
        # Window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def open_pdf(self):
        """Open and load a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Close existing document if any
            if self.pdf_doc:
                self.pdf_doc.close()
                
            # Open new document
            self.pdf_doc = fitz.open(file_path)
            self.total_pages = len(self.pdf_doc)
            self.current_page = 0
            self.fields = []  # Clear existing fields
            
            # Display first page
            self.display_page()
            
            # Update UI state
            self.update_navigation_buttons()
            self.save_btn.config(state='normal')
            self.status_label.config(text=f"PDF loaded: {self.total_pages} pages - Use toolbar to add form fields")
            
            messagebox.showinfo("Success", f"PDF loaded successfully!\nPages: {self.total_pages}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
    
    def display_page(self):
        """Display the current PDF page on canvas"""
        if not self.pdf_doc or self.current_page >= self.total_pages:
            return
            
        try:
            # Get the page
            page = self.pdf_doc[self.current_page]
            
            # Calculate scale to fit canvas nicely
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                # Canvas not yet properly sized, use default
                canvas_width = 800
                canvas_height = 600
                
            page_rect = page.rect
            scale_x = (canvas_width - 50) / page_rect.width
            scale_y = (canvas_height - 50) / page_rect.height
            self.pdf_scale = min(scale_x, scale_y, 2.0)  # Cap at 2x zoom
            
            print(f"Display scaling: canvas={canvas_width}x{canvas_height}, PDF={page_rect.width}x{page_rect.height}, scale={self.pdf_scale:.3f}")
            
            # Render page to pixmap
            matrix = fitz.Matrix(self.pdf_scale, self.pdf_scale)
            pixmap = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image then to PhotoImage
            img_data = pixmap.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            self.canvas_image = ImageTk.PhotoImage(pil_image)
            
            # Store PDF dimensions
            self.pdf_width = pixmap.width
            self.pdf_height = pixmap.height
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(
                25, 25, 
                anchor='nw', 
                image=self.canvas_image, 
                tags="pdf_page"
            )
            
            # Update canvas scroll region
            self.canvas.configure(scrollregion=(0, 0, self.pdf_width + 50, self.pdf_height + 50))
            
            # Redraw fields for current page
            self.redraw_fields()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page:\n{str(e)}")
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons and page label"""
        if not self.pdf_doc:
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            self.page_label.config(text="No PDF loaded")
            return
            
        # Update page label
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
        
        # Update button states
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < self.total_pages - 1 else 'disabled')
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            self.update_navigation_buttons()
            self.clear_selection()
    
    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()
            self.update_navigation_buttons()
            self.clear_selection()
    
    def redraw_fields(self):
        """Redraw all fields for the current page"""
        for field in self.fields:
            if field['page_num'] == self.current_page:
                self.draw_field(field)
    
    def draw_field(self, field):
        """Draw a field rectangle on the canvas"""
        x1, y1, x2, y2 = field['rect']
        
        # Determine color based on field type
        colors = {
            'text': '#2196F3',
            'checkbox': '#FF9800', 
            'radio': '#9C27B0',
            'dropdown': '#607D8B',
            'signature': '#795548'
        }
        
        color = colors.get(field['type'], '#666666')
        outline_color = '#0066CC' if field == self.selected_field else color
        outline_width = 3 if field == self.selected_field else 2
        
        # Draw main rectangle
        field['canvas_id'] = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=outline_color,
            width=outline_width,
            fill='',
            tags=f"field_{field['name']}"
        )
        
        # Draw field type label
        label_x = x1 + 3
        label_y = y1 + 3
        self.canvas.create_text(
            label_x, label_y,
            anchor='nw',
            text=f"{field['type']}",
            fill=outline_color,
            font=('Arial', 8, 'bold'),
            tags=f"field_{field['name']}_label"
        )
        
        # Draw resize handles if this field is selected
        if field == self.selected_field:
            self.draw_resize_handles(field)
    
    def draw_resize_handles(self, field):
        """Draw resize handles around a selected field"""
        x1, y1, x2, y2 = field['rect']
        handle_size = 6
        
        # Corner handles
        handles = [
            (x1 - handle_size//2, y1 - handle_size//2, 'nw'),  # Top-left
            (x2 - handle_size//2, y1 - handle_size//2, 'ne'),  # Top-right
            (x1 - handle_size//2, y2 - handle_size//2, 'sw'),  # Bottom-left
            (x2 - handle_size//2, y2 - handle_size//2, 'se'),  # Bottom-right
        ]
        
        # Edge handles
        handles.extend([
            ((x1 + x2)//2 - handle_size//2, y1 - handle_size//2, 'n'),   # Top
            ((x1 + x2)//2 - handle_size//2, y2 - handle_size//2, 's'),   # Bottom
            (x1 - handle_size//2, (y1 + y2)//2 - handle_size//2, 'w'),   # Left
            (x2 - handle_size//2, (y1 + y2)//2 - handle_size//2, 'e'),   # Right
        ])
        
        for x, y, direction in handles:
            self.canvas.create_rectangle(
                x, y, x + handle_size, y + handle_size,
                fill='#0066CC',
                outline='white',
                width=1,
                tags=f"handle_{direction}"
            )
    
    def select_tool(self, tool_type):
        """Select a form field tool"""
        # Clear previous selection
        self.clear_selection()
        
        # Update current tool
        self.current_tool = tool_type
        
        # Update button appearance
        for tool, button in self.tool_buttons.items():
            if tool == tool_type:
                button.config(relief='sunken', bg='#555555')
            else:
                # Restore original colors
                colors = {
                    'text': '#2196F3',
                    'checkbox': '#FF9800',
                    'radio': '#9C27B0',
                    'dropdown': '#607D8B',
                    'signature': '#795548'
                }
                button.config(relief='raised', bg=colors.get(tool, '#666666'))
        
        # Update status
        self.status_label.config(text=f"Selected tool: {tool_type.title()} - Click on the PDF to add a field")
    
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if not self.pdf_doc:
            return
            
        # Convert event coordinates to canvas coordinates (accounting for scrolling)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        print(f"Canvas click at: ({x:.1f}, {y:.1f})")  # Debug output
        
        # Check if clicking on a resize handle
        handle_clicked = self.check_resize_handle_click(x, y)
        if handle_clicked:
            self.resizing = True
            self.resize_handle = handle_clicked
            self.drag_start_x = x
            self.drag_start_y = y
            return
        
        # Check if clicking on an existing field
        clicked_field = self.get_field_at_position(x, y)
        
        if clicked_field:
            # Select the field
            self.clear_selection()
            self.selected_field = clicked_field
            self.redraw_fields()  # Redraw to show selection
            
            # Prepare for dragging
            self.dragging = True
            self.drag_start_x = x
            self.drag_start_y = y
            
        elif self.current_tool:
            # Create new field at click position
            self.create_field(x, y)
            
        else:
            # Clear selection if clicking on empty space
            self.clear_selection()
    
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        if not self.pdf_doc:
            return
            
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.resizing and self.selected_field:
            self.resize_field(x, y)
        elif self.dragging and self.selected_field:
            self.move_field(x, y)
    
    def on_canvas_release(self, event):
        """Handle canvas mouse release events"""
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
    
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion for cursor changes"""
        if not self.pdf_doc or not self.selected_field:
            self.canvas.config(cursor="")
            return
            
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Check if over a resize handle
        handle = self.check_resize_handle_click(x, y)
        if handle:
            cursors = {
                'nw': 'size_nw_se', 'ne': 'size_ne_sw',
                'sw': 'size_ne_sw', 'se': 'size_nw_se',
                'n': 'size_ns', 's': 'size_ns',
                'w': 'size_we', 'e': 'size_we'
            }
            self.canvas.config(cursor=cursors.get(handle, ""))
        elif self.get_field_at_position(x, y):
            self.canvas.config(cursor="fleur")  # Move cursor
        else:
            self.canvas.config(cursor="")
    
    def create_field(self, x, y):
        """Create a new form field at the specified position"""
        if not self.current_tool:
            return
            
        # Default field size
        width, height = 100, 30
        if self.current_tool == 'checkbox':
            width = height = 20
        elif self.current_tool == 'signature':
            width, height = 150, 50
        elif self.current_tool == 'dropdown':
            width, height = 120, 25
            
        # Create field dictionary
        self.field_counter += 1
        field = {
            'name': f"{self.current_tool}_{self.field_counter}",
            'type': self.current_tool,
            'page_num': self.current_page,
            'rect': [x, y, x + width, y + height],
            'canvas_id': None
        }
        
        # Store field creation info for debugging
        print(f"Creating field '{field['name']}' at canvas ({x:.1f}, {y:.1f})")
        
        # Add type-specific properties
        if self.current_tool == 'dropdown':
            field['options'] = ['Option 1', 'Option 2', 'Option 3']
        elif self.current_tool == 'radio':
            field['group'] = f"radio_group_{self.field_counter}"
            field['value'] = f"option_{self.field_counter}"
        
        # Add to fields list
        self.fields.append(field)
        
        # Draw the field
        self.draw_field(field)
        
        # Select the new field
        self.clear_selection()
        self.selected_field = field
        self.redraw_fields()
        
        # Clear tool selection after creating field
        self.current_tool = None
        for button in self.tool_buttons.values():
            colors = {
                'text': '#2196F3', 'checkbox': '#FF9800', 'radio': '#9C27B0',
                'dropdown': '#607D8B', 'signature': '#795548'
            }
            button.config(relief='raised')
            
        # Update status
        self.status_label.config(text=f"Created {field['type']} field - Use mouse to move/resize or Delete key to remove")
    
    def get_field_at_position(self, x, y):
        """Get the field at the specified canvas position"""
        for field in self.fields:
            if field['page_num'] != self.current_page:
                continue
                
            x1, y1, x2, y2 = field['rect']
            if x1 <= x <= x2 and y1 <= y <= y2:
                return field
        return None
    
    def check_resize_handle_click(self, x, y):
        """Check if click is on a resize handle"""
        if not self.selected_field:
            return None
            
        x1, y1, x2, y2 = self.selected_field['rect']
        handle_size = 6
        
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
    
    def move_field(self, x, y):
        """Move the selected field"""
        if not self.selected_field:
            return
            
        # Calculate movement delta
        dx = x - self.drag_start_x
        dy = y - self.drag_start_y
        
        # Update field rectangle
        x1, y1, x2, y2 = self.selected_field['rect']
        self.selected_field['rect'] = [x1 + dx, y1 + dy, x2 + dx, y2 + dy]
        
        # Update drag start position
        self.drag_start_x = x
        self.drag_start_y = y
        
        # Redraw the field
        self.canvas.delete(f"field_{self.selected_field['name']}")
        self.canvas.delete(f"field_{self.selected_field['name']}_label")
        self.canvas.delete("handle_nw", "handle_ne", "handle_sw", "handle_se",
                         "handle_n", "handle_s", "handle_w", "handle_e")
        self.draw_field(self.selected_field)
    
    def resize_field(self, x, y):
        """Resize the selected field"""
        if not self.selected_field or not self.resize_handle:
            return
            
        x1, y1, x2, y2 = self.selected_field['rect']
        
        # Update rectangle based on resize handle
        if 'n' in self.resize_handle:
            y1 = min(y, y2 - 10)  # Minimum height of 10
        if 's' in self.resize_handle:
            y2 = max(y, y1 + 10)
        if 'w' in self.resize_handle:
            x1 = min(x, x2 - 10)  # Minimum width of 10
        if 'e' in self.resize_handle:
            x2 = max(x, x1 + 10)
            
        self.selected_field['rect'] = [x1, y1, x2, y2]
        
        # Redraw the field
        self.canvas.delete(f"field_{self.selected_field['name']}")
        self.canvas.delete(f"field_{self.selected_field['name']}_label")
        self.canvas.delete("handle_nw", "handle_ne", "handle_sw", "handle_se",
                         "handle_n", "handle_s", "handle_w", "handle_e")
        self.draw_field(self.selected_field)
    
    def on_key_press(self, event):
        """Handle key press events"""
        if event.keysym == 'Delete' and self.selected_field:
            self.delete_selected_field()
        elif event.keysym == 'Escape':
            self.clear_selection()
            self.current_tool = None
            # Reset all tool buttons
            for button in self.tool_buttons.values():
                button.config(relief='raised')
    
    def on_closing(self):
        """Handle application closing"""
        if self.pdf_doc:
            self.pdf_doc.close()
        self.root.destroy()
    
    def delete_selected_field(self):
        """Delete the currently selected field"""
        if not self.selected_field:
            return
            
        # Ask for confirmation
        result = messagebox.askyesno(
            "Delete Field", 
            f"Are you sure you want to delete the {self.selected_field['type']} field '{self.selected_field['name']}'?"
        )
        
        if not result:
            return
            
        # Remove from canvas
        self.canvas.delete(f"field_{self.selected_field['name']}")
        self.canvas.delete(f"field_{self.selected_field['name']}_label")
        self.canvas.delete("handle_nw", "handle_ne", "handle_sw", "handle_se",
                         "handle_n", "handle_s", "handle_w", "handle_e")
        
        # Remove from fields list
        self.fields.remove(self.selected_field)
        self.selected_field = None
    
    def clear_selection(self):
        """Clear the currently selected field"""
        if self.selected_field:
            # Remove resize handles
            self.canvas.delete("handle_nw", "handle_ne", "handle_sw", "handle_se",
                             "handle_n", "handle_s", "handle_w", "handle_e")
            # Redraw the field without selection highlighting
            self.canvas.delete(f"field_{self.selected_field['name']}")
            self.canvas.delete(f"field_{self.selected_field['name']}_label")
            self.draw_field(self.selected_field)
            
        self.selected_field = None
    
    def save_pdf(self):
        """Save the PDF with form fields"""
        if not self.pdf_doc or not self.fields:
            messagebox.showwarning("Warning", "No PDF loaded or no fields to save.")
            return
            
        # Get save file path
        file_path = filedialog.asksaveasfilename(
            title="Save PDF with form fields",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Create a copy of the document for saving
            temp_doc = fitz.open()
            for page_num in range(len(self.pdf_doc)):
                temp_doc.insert_pdf(self.pdf_doc, from_page=page_num, to_page=page_num)
            
            # Add form fields to each page
            for field in self.fields:
                page = temp_doc[field['page_num']]
                
                # Get original page dimensions
                original_page_rect = page.rect
                
                # Convert canvas coordinates to PDF coordinates
                # This must be the exact inverse of how we display the PDF
                
                canvas_x1, canvas_y1, canvas_x2, canvas_y2 = field['rect']
                
                # CRITICAL: We display the PDF image at (25, 25) on the canvas
                # So to convert back, we subtract this offset first
                relative_x1 = canvas_x1 - 25
                relative_y1 = canvas_y1 - 25  
                relative_x2 = canvas_x2 - 25
                relative_y2 = canvas_y2 - 25
                
                # Then we scale back from display coordinates to PDF coordinates
                # Display coordinates = PDF coordinates * scale
                # So: PDF coordinates = Display coordinates / scale
                pdf_x1 = relative_x1 / self.pdf_scale
                pdf_y1 = relative_y1 / self.pdf_scale
                pdf_x2 = relative_x2 / self.pdf_scale  
                pdf_y2 = relative_y2 / self.pdf_scale
                
                # Convert coordinate systems
                # Let's try NOT flipping the Y coordinates and see what happens
                # Sometimes the PDF library handles the coordinate system conversion internally
                page_height = original_page_rect.height
                
                # Try direct mapping first (no Y-axis flip)
                final_x1 = pdf_x1
                final_y1 = pdf_y1  # Keep original Y coordinates
                final_x2 = pdf_x2
                final_y2 = pdf_y2  # Keep original Y coordinates
                
                print(f"  Direct mapping: y1={final_y1:.1f}, y2={final_y2:.1f}")
                
                # Ensure proper rectangle ordering
                if final_x1 > final_x2:
                    final_x1, final_x2 = final_x2, final_x1
                if final_y1 > final_y2:
                    final_y1, final_y2 = final_y2, final_y1
                
                # Ensure valid rectangle (x1 < x2, y1 < y2)
                if final_x1 > final_x2:
                    final_x1, final_x2 = final_x2, final_x1
                if final_y1 > final_y2:
                    final_y1, final_y2 = final_y2, final_y1
                    
                # Clamp to page boundaries and ensure minimum size
                final_x1 = max(0, min(final_x1, original_page_rect.width - 10))
                final_y1 = max(0, min(final_y1, original_page_rect.height - 10))
                final_x2 = max(final_x1 + 10, min(final_x2, original_page_rect.width))
                final_y2 = max(final_y1 + 10, min(final_y2, original_page_rect.height))
                
                # Create the rectangle for PyMuPDF
                rect = fitz.Rect(final_x1, final_y1, final_x2, final_y2)
                
                # Add the appropriate widget based on field type
                if field['type'] == 'text':
                    widget = fitz.Widget()
                    widget.field_name = field['name']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                    widget.rect = rect
                    widget.field_value = ""
                    widget.text_font = "helv"
                    widget.text_fontsize = 12
                    widget.fill_color = (1, 1, 1)  # White background
                    page.add_widget(widget)
                    
                elif field['type'] == 'checkbox':
                    widget = fitz.Widget()
                    widget.field_name = field['name']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
                    widget.rect = rect
                    widget.field_value = False
                    widget.fill_color = (1, 1, 1)
                    page.add_widget(widget)
                    
                elif field['type'] == 'radio':
                    widget = fitz.Widget()
                    widget.field_name = field.get('group', field['name'])
                    widget.field_type = fitz.PDF_WIDGET_TYPE_RADIOBUTTON
                    widget.rect = rect
                    widget.field_value = field.get('value', field['name'])
                    widget.fill_color = (1, 1, 1)
                    page.add_widget(widget)
                    
                elif field['type'] == 'dropdown':
                    widget = fitz.Widget()
                    widget.field_name = field['name']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
                    widget.rect = rect
                    widget.choice_values = field.get('options', ['Option 1', 'Option 2'])
                    widget.field_value = widget.choice_values[0] if widget.choice_values else ""
                    widget.text_font = "helv"
                    widget.text_fontsize = 11
                    widget.fill_color = (1, 1, 1)
                    page.add_widget(widget)
                    
                elif field['type'] == 'signature':
                    # For signature fields, create a text field with signature appearance
                    widget = fitz.Widget()
                    widget.field_name = field['name']
                    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                    widget.rect = rect
                    widget.field_value = ""
                    widget.text_font = "helv"
                    widget.text_fontsize = 12
                    widget.fill_color = (0.95, 0.95, 0.95)  # Light gray background
                    # Add border to indicate signature field
                    widget.border_color = (0.5, 0.5, 0.5)
                    widget.border_width = 2
                    page.add_widget(widget)
            
            # Save the document
            temp_doc.save(file_path, incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
            temp_doc.close()
            
            messagebox.showinfo("Success", f"PDF saved successfully!\nFile: {file_path}\nFields added: {len(self.fields)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = PdfFormMaker()
    app.run()