#!/usr/bin/env python3
"""
PDF Form Inputter - Custom PDF Form Input Dialog

A specialized interface for filling out PDF forms with proper field handling.
Supports all field types: TEXT, CHECKBOX, SIGNATURE, IMAGE, DATE, etc.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import fitz  # PyMuPDF
import os
from typing import List, Dict, Any, Optional
from models import FieldType
from PIL import Image, ImageTk
import io


class PDFFormInputter:
    """Custom PDF form input dialog that allows users to fill out PDF forms"""
    
    def __init__(self, parent_window):
        """Initialize the PDF form inputter"""
        self.parent = parent_window
        self.dialog = None
        self.pdf_doc = None
        self.pdf_path = None
        self.form_fields = []
        self.field_widgets = {}  # Map field names to widgets
        self.field_values = {}   # Map field names to values
        self.pdf_canvas = None   # Canvas for PDF display
        self.pdf_images = {}     # Cached PDF page images
        self.scale_factor = 1.0  # Scale factor for PDF display
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        
    def show_inputter(self):
        """Show the PDF form inputter dialog"""
        # First, let user select a PDF to fill out
        pdf_path = filedialog.askopenfilename(
            title="Select PDF Form to Fill Out",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if not pdf_path:
            return
        
        # Load and analyze the PDF
        if not self._load_pdf_form(pdf_path):
            messagebox.showerror("Error", "Failed to load PDF or no form fields found in the PDF.")
            return
        
        # Create the input dialog
        self._create_input_dialog()
    
    def _load_pdf_form(self, pdf_path: str) -> bool:
        """Load PDF and extract form fields"""
        try:
            self.pdf_doc = fitz.open(pdf_path)
            self.pdf_path = pdf_path
            self.form_fields = []
            
            # Extract form fields from all pages
            for page_num in range(len(self.pdf_doc)):
                page = self.pdf_doc[page_num]
                
                # Get form fields from this page
                widgets = page.widgets()
                
                for widget in widgets:
                    # Get field type and clean name
                    field_type = self._get_field_type_from_widget(widget)
                    raw_field_name = widget.field_name or f"field_{len(self.form_fields)}"
                    clean_field_name = self._clean_field_name(raw_field_name)
                    
                    field_info = {
                        'name': clean_field_name,
                        'raw_name': raw_field_name,  # Keep original for reference
                        'type': field_type,
                        'page': page_num,
                        'rect': widget.rect,
                        'value': widget.field_value or '',
                        'options': getattr(widget, 'choice_values', []),
                        'widget': widget,
                        'required': False  # Could be enhanced to detect required fields
                    }
                    self.form_fields.append(field_info)
            
            print(f"📋 Found {len(self.form_fields)} form fields in PDF")
            return len(self.form_fields) > 0
            
        except Exception as e:
            print(f"Error loading PDF form: {e}")
            return False
    
    def _get_field_type_from_widget(self, widget) -> str:
        """Determine field type from PDF widget"""
        widget_type = widget.field_type
        field_name = widget.field_name or ""
        
        # Map PyMuPDF widget types to our field types
        if widget_type == fitz.PDF_WIDGET_TYPE_TEXT:
            # Check if this is actually a special TEXT field type
            
            # Check for IMAGE field (saved with image_ prefix)
            if field_name.startswith("image_") or "_image_" in field_name:
                return "IMAGE"
            
            # Check for DATE field (saved with date_ prefix)  
            elif field_name.startswith("date_") or "_date_" in field_name:
                return "DATE"
            
            # Check for SIGNATURE field (might have signature styling)
            elif ("signature" in field_name.lower() or 
                  "sign" in field_name.lower() or
                  widget.field_value and "signature" in widget.field_value.lower()):
                return "SIGNATURE"
            
            # Default to TEXT
            else:
                return "TEXT"
                
        elif widget_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
            return "CHECKBOX"
        elif widget_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
            return "RADIO"
        elif widget_type == fitz.PDF_WIDGET_TYPE_COMBOBOX:
            return "DROPDOWN"
        elif widget_type == fitz.PDF_WIDGET_TYPE_LISTBOX:
            return "LISTBOX"
        elif widget_type == fitz.PDF_WIDGET_TYPE_BUTTON:
            return "BUTTON"
        elif widget_type == fitz.PDF_WIDGET_TYPE_SIGNATURE:
            return "SIGNATURE"
        else:
            return "TEXT"  # Default fallback
    
    def _clean_field_name(self, field_name):
        """Clean field name by removing type prefixes (matching main app logic)"""
        if not field_name:
            return field_name
        
        # Remove image type prefix
        if field_name.startswith("image_"):
            return field_name[6:]  # Remove "image_" prefix
        
        # Remove date type prefix
        if field_name.startswith("date_"):
            return field_name[5:]  # Remove "date_" prefix
        
        # Remove image type infix
        if "_image_" in field_name:
            parts = field_name.split("_image_")
            if len(parts) == 2:
                return parts[0] + "_" + parts[1]
        
        # Remove date type infix
        if "_date_" in field_name:
            parts = field_name.split("_date_")
            if len(parts) == 2:
                return parts[0] + "_" + parts[1]
        
        return field_name
    
    def _create_input_dialog(self):
        """Create the enhanced input dialog with PDF backdrop"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"📋 Accomplish PDF Form - {os.path.basename(self.pdf_path)}")
        self.dialog.geometry("1200x800")
        self.dialog.configure(bg='#f0f0f0')
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (800 // 2)
        self.dialog.geometry(f"1200x800+{x}+{y}")
        
        # Create main layout
        self._create_enhanced_layout()
        
        # Render PDF pages and overlay input fields
        self._render_pdf_backdrop()
        
        # Show dialog
        self.dialog.wait_window()
    
    def _create_enhanced_layout(self):
        """Create the enhanced layout with PDF backdrop capability"""
        # Top toolbar
        toolbar = tk.Frame(self.dialog, bg='#2196F3', height=50)
        toolbar.pack(fill='x')
        toolbar.pack_propagate(False)
        
        # Title and info
        tk.Label(
            toolbar,
            text=f"� {os.path.basename(self.pdf_path)}",
            bg='#2196F3',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(side='left', padx=20, pady=15)
        
        tk.Label(
            toolbar,
            text=f"� {len(self.form_fields)} fields to fill",
            bg='#2196F3',
            fg='white',
            font=('Arial', 10)
        ).pack(side='right', padx=20, pady=15)
        
        # Main content area with PDF backdrop
        content_frame = tk.Frame(self.dialog, bg='#e0e0e0')
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # PDF display canvas with scrollbars
        canvas_frame = tk.Frame(content_frame, bg='#e0e0e0')
        canvas_frame.pack(fill='both', expand=True)
        
        # Create scrollable PDF canvas
        self.pdf_canvas = tk.Canvas(
            canvas_frame, 
            bg='white',
            highlightthickness=1,
            highlightbackground='#cccccc'
        )
        
        # Scrollbars for PDF navigation
        v_scrollbar = tk.Scrollbar(canvas_frame, orient='vertical', command=self.pdf_canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient='horizontal', command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Pack canvas and scrollbars
        self.pdf_canvas.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            self.pdf_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.pdf_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Button frame
        button_frame = tk.Frame(self.dialog, bg='#f0f0f0', height=70)
        button_frame.pack(fill='x', padx=10, pady=10)
        button_frame.pack_propagate(False)
        
        # Buttons
        tk.Button(
            button_frame,
            text="📁 Fill & Save PDF",
            command=self._save_completed_form,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2
        ).pack(side='right', padx=5, pady=15)
        
        tk.Button(
            button_frame,
            text="❌ Cancel",
            command=self._cancel,
            bg='#f44336',
            fg='white',
            font=('Arial', 12),
            height=2
        ).pack(side='right', padx=5, pady=15)
        
        tk.Button(
            button_frame,
            text="🔄 Clear All",
            command=self._clear_all_fields,
            bg='#ff9800',
            fg='white',
            font=('Arial', 10),
            height=2
        ).pack(side='left', padx=5, pady=15)
        
        # Zoom controls
        zoom_frame = tk.Frame(button_frame, bg='#f0f0f0')
        zoom_frame.pack(side='left', padx=20)
        
        tk.Button(
            zoom_frame,
            text="🔍+",
            command=self._zoom_in,
            bg='#607D8B',
            fg='white',
            font=('Arial', 10),
            width=3
        ).pack(side='left', padx=2)
        
        tk.Button(
            zoom_frame,
            text="🔍-",
            command=self._zoom_out,
            bg='#607D8B',
            fg='white',
            font=('Arial', 10),
            width=3
        ).pack(side='left', padx=2)
        
        tk.Button(
            zoom_frame,
            text="📐 Fit",
            command=self._zoom_fit,
            bg='#607D8B',
            fg='white',
            font=('Arial', 10),
            width=4
        ).pack(side='left', padx=2)
    
    def _render_pdf_backdrop(self):
        """Render PDF pages as backdrop and overlay input fields"""
        if not self.pdf_doc or not self.form_fields:
            return
        
        # Calculate initial scale to fit page width
        self._calculate_initial_scale()
        
        # Render all pages with overlaid input fields
        total_height = 0
        page_spacing = 20  # Space between pages
        
        for page_num in range(len(self.pdf_doc)):
            page_y_offset = total_height
            
            # Render PDF page as background image
            page_image = self._render_pdf_page(page_num)
            if page_image:
                # Add page image to canvas
                canvas_image = self.pdf_canvas.create_image(
                    10, page_y_offset + 10, 
                    anchor='nw', 
                    image=page_image,
                    tags=f"page_{page_num}"
                )
                
                # Store reference to prevent garbage collection
                if not hasattr(self, 'page_images'):
                    self.page_images = {}
                self.page_images[page_num] = page_image
                
                # Update total height
                page_height = page_image.height()
                total_height += page_height + page_spacing
                
                # Overlay input fields for this page
                self._overlay_page_fields(page_num, 10, page_y_offset + 10)
        
        # Configure canvas scroll region
        self.pdf_canvas.configure(scrollregion=(0, 0, 0, total_height))
    
    def _calculate_initial_scale(self):
        """Calculate initial scale factor to fit PDF in canvas"""
        if not self.pdf_doc:
            return
        
        # Get first page dimensions
        page = self.pdf_doc[0]
        page_rect = page.rect
        
        # Get available canvas width (accounting for scrollbar)
        canvas_width = 1150  # Approximate available width
        
        # Calculate scale to fit width with some padding
        self.scale_factor = min(1.0, (canvas_width - 40) / page_rect.width)
    
    def _render_pdf_page(self, page_num: int):
        """Render a PDF page as a Tkinter-compatible image"""
        try:
            page = self.pdf_doc[page_num]
            
            # Create pixmap with scale factor
            mat = fitz.Matrix(self.scale_factor, self.scale_factor)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Convert to Tkinter PhotoImage
            tk_image = ImageTk.PhotoImage(pil_image)
            
            return tk_image
            
        except Exception as e:
            print(f"Error rendering PDF page {page_num}: {e}")
            return None
    
    def _overlay_page_fields(self, page_num: int, canvas_x_offset: int, canvas_y_offset: int):
        """Overlay input fields on the PDF page"""
        page_fields = [f for f in self.form_fields if f['page'] == page_num]
        
        for field in page_fields:
            # Calculate field position on canvas
            field_rect = field['rect']
            
            # Scale and position the field
            scaled_x = field_rect.x0 * self.scale_factor + canvas_x_offset
            scaled_y = field_rect.y0 * self.scale_factor + canvas_y_offset
            scaled_width = (field_rect.x1 - field_rect.x0) * self.scale_factor
            scaled_height = (field_rect.y1 - field_rect.y0) * self.scale_factor
            
            # Create overlay input widget
            self._create_overlay_field_widget(field, scaled_x, scaled_y, scaled_width, scaled_height)
    
    def _create_overlay_field_widget(self, field: Dict, x: float, y: float, width: float, height: float):
        """Create an input widget overlaid on the PDF at the exact field position"""
        field_name = field['name']
        field_type = field['type']
        
        # Create appropriate widget type based on field
        if field_type == 'TEXT':
            widget = tk.Entry(
                self.pdf_canvas,
                font=('Arial', 10),
                relief='solid',
                bd=1,
                bg='#ffffff'
            )
            widget.insert(0, field.get('value', ''))
            
        elif field_type == 'CHECKBOX':
            var = tk.BooleanVar()
            widget = tk.Checkbutton(
                self.pdf_canvas,
                variable=var,
                bg='white',
                activebackground='#e3f2fd'
            )
            if field.get('value'):
                var.set(True)
            # Store variable reference
            self.field_widgets[f"{field_name}_var"] = var
            
        elif field_type == 'IMAGE':
            # Create image field with preview
            widget = self._create_image_field_overlay(field, width, height)
            
        elif field_type == 'DATE':
            widget = tk.Entry(
                self.pdf_canvas,
                font=('Arial', 10),
                relief='solid',
                bd=1,
                bg='#e3f2fd'
            )
            widget.insert(0, field.get('value', ''))
            
        elif field_type == 'DROPDOWN':
            widget = ttk.Combobox(
                self.pdf_canvas,
                values=field.get('options', []),
                state='readonly',
                font=('Arial', 10)
            )
            if field.get('value'):
                widget.set(field['value'])
                
        else:
            # Default to text entry
            widget = tk.Entry(
                self.pdf_canvas,
                font=('Arial', 10),
                relief='solid',
                bd=1
            )
            widget.insert(0, field.get('value', ''))
        
        # Position widget on canvas
        widget_id = self.pdf_canvas.create_window(
            x, y,
            anchor='nw',
            window=widget,
            width=max(width, 100),  # Minimum width
            height=max(height, 25), # Minimum height
            tags=f"field_{field_name}"
        )
        
        # Store widget reference
        self.field_widgets[field_name] = widget
        
        # Add hover effect to show field info
        def on_enter(event):
            widget.configure(highlightbackground='#2196F3', highlightthickness=2)
        
        def on_leave(event):
            widget.configure(highlightthickness=0)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _create_image_field_overlay(self, field: Dict, width: float, height: float):
        """Create an image field overlay with preview capability"""
        # Create a frame to hold image controls
        image_frame = tk.Frame(self.pdf_canvas, bg='white', relief='solid', bd=2)
        
        # Image preview area
        self.image_preview = tk.Label(
            image_frame,
            text="📷 Click to select image",
            bg='#f5f5f5',
            fg='#666666',
            font=('Arial', 9),
            relief='sunken',
            bd=1,
            cursor='hand2'
        )
        self.image_preview.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Store field reference for this image widget
        field_name = field['name']
        
        def select_image():
            file_path = filedialog.askopenfilename(
                title=f"Select Image for {field_name}",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Store the image path
                self.field_values[field_name] = file_path
                
                # Update preview
                self._update_image_preview(self.image_preview, file_path, width, height)
        
        # Bind click event
        self.image_preview.bind("<Button-1>", lambda e: select_image())
        
        return image_frame
    
    def _update_image_preview(self, preview_label, image_path: str, max_width: float, max_height: float):
        """Update the image preview with the selected image"""
        try:
            # Open and resize image for preview
            pil_image = Image.open(image_path)
            
            # Calculate preview size (smaller than field size for preview)
            preview_width = min(max_width - 4, 150)
            preview_height = min(max_height - 4, 100)
            
            # Maintain aspect ratio
            aspect_ratio = pil_image.width / pil_image.height
            if preview_width / preview_height > aspect_ratio:
                preview_width = int(preview_height * aspect_ratio)
            else:
                preview_height = int(preview_width / aspect_ratio)
            
            # Resize image
            pil_image = pil_image.resize((int(preview_width), int(preview_height)), Image.Resampling.LANCZOS)
            
            # Convert to Tkinter image
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update label
            preview_label.configure(
                image=tk_image,
                text="",  # Remove text
                bg='white'
            )
            
            # Store reference to prevent garbage collection
            preview_label.image = tk_image
            
            # Add filename indicator
            filename = os.path.basename(image_path)
            if len(filename) > 20:
                filename = filename[:17] + "..."
            preview_label.configure(text=f"📷 {filename}", compound='top', fg='#666666', font=('Arial', 8))
            
        except Exception as e:
            print(f"Error updating image preview: {e}")
            preview_label.configure(
                text=f"📷 {os.path.basename(image_path)}\n(Preview error)",
                image="",
                bg='#ffebee',
                fg='#d32f2f'
            )
    
    def _zoom_in(self):
        """Zoom in on the PDF"""
        self.scale_factor *= 1.2
        self._refresh_pdf_display()
    
    def _zoom_out(self):
        """Zoom out on the PDF"""
        self.scale_factor /= 1.2
        self._refresh_pdf_display()
    
    def _zoom_fit(self):
        """Fit PDF to canvas width"""
        self._calculate_initial_scale()
        self._refresh_pdf_display()
    
    def _refresh_pdf_display(self):
        """Refresh the PDF display after zoom changes"""
        # Clear canvas
        self.pdf_canvas.delete("all")
        
        # Clear stored references
        if hasattr(self, 'page_images'):
            self.page_images.clear()
        
        # Re-render with new scale
        self._render_pdf_backdrop()
    
    def _create_page_section(self, page_num: int, fields: List[Dict]):
        """Create a section for fields on a specific page"""
        # Page header
        page_frame = tk.LabelFrame(
            self.scrollable_frame,
            text=f"📄 Page {page_num + 1}",
            font=('Arial', 12, 'bold'),
            bg='#f5f5f5',
            fg='#2196F3',
            relief='solid',
            bd=1
        )
        page_frame.pack(fill='x', padx=10, pady=10)
        
        # Create input widget for each field
        for field in fields:
            self._create_field_input_widget(page_frame, field)
    
    def _create_field_input_widget(self, parent, field: Dict):
        """Create an input widget for a specific field"""
        field_frame = tk.Frame(parent, bg='#f5f5f5')
        field_frame.pack(fill='x', padx=15, pady=8)
        
        # Field label with type indicator
        label_frame = tk.Frame(field_frame, bg='#f5f5f5')
        label_frame.pack(fill='x', pady=(0, 5))
        
        # Field type indicator
        type_colors = {
            'TEXT': '#4CAF50',
            'CHECKBOX': '#FF9800', 
            'SIGNATURE': '#9C27B0',
            'IMAGE': '#9C27B0',
            'DATE': '#2196F3',
            'RADIO': '#FF5722',
            'DROPDOWN': '#607D8B',
            'LISTBOX': '#795548',
            'BUTTON': '#9E9E9E'
        }
        
        field_type = field['type']
        type_label = tk.Label(
            label_frame,
            text=f"[{field_type}]",
            bg=type_colors.get(field_type, '#666666'),
            fg='white',
            font=('Arial', 8, 'bold'),
            padx=6,
            pady=2
        )
        type_label.pack(side='left')
        
        # Field name
        name_label = tk.Label(
            label_frame,
            text=field['name'],
            bg='#f5f5f5',
            font=('Arial', 11, 'bold'),
            anchor='w'
        )
        name_label.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Required indicator (could be enhanced)
        if field.get('required', False):
            req_label = tk.Label(
                label_frame,
                text="*",
                bg='#f5f5f5',
                fg='red',
                font=('Arial', 12, 'bold')
            )
            req_label.pack(side='right')
        
        # Create input widget based on field type
        input_widget = None
        
        if field_type == 'TEXT':
            input_widget = self._create_text_input(field_frame, field)
        elif field_type == 'CHECKBOX':
            input_widget = self._create_checkbox_input(field_frame, field)
        elif field_type == 'SIGNATURE':
            input_widget = self._create_signature_input(field_frame, field)
        elif field_type == 'IMAGE':
            input_widget = self._create_image_input(field_frame, field)
        elif field_type == 'DATE':
            input_widget = self._create_date_input(field_frame, field)
        elif field_type == 'RADIO':
            input_widget = self._create_radio_input(field_frame, field)
        elif field_type == 'DROPDOWN':
            input_widget = self._create_dropdown_input(field_frame, field)
        elif field_type == 'LISTBOX':
            input_widget = self._create_listbox_input(field_frame, field)
        else:
            # Default to text input
            input_widget = self._create_text_input(field_frame, field)
        
        # Store widget reference
        if input_widget:
            self.field_widgets[field['name']] = input_widget
    
    def _create_text_input(self, parent, field: Dict) -> tk.Widget:
        """Create text input widget"""
        var = tk.StringVar(value=field['value'])
        entry = tk.Entry(
            parent,
            textvariable=var,
            font=('Arial', 11),
            bg='white',
            relief='solid',
            bd=1
        )
        entry.pack(fill='x', pady=2)
        
        # Store variable for value retrieval
        self.field_values[field['name']] = var
        return entry
    
    def _create_checkbox_input(self, parent, field: Dict) -> tk.Widget:
        """Create checkbox input widget"""
        var = tk.BooleanVar(value=bool(field['value']))
        checkbox = tk.Checkbutton(
            parent,
            text="✓ Check this box",
            variable=var,
            font=('Arial', 11),
            bg='#f5f5f5',
            activebackground='#f5f5f5'
        )
        checkbox.pack(anchor='w', pady=2)
        
        self.field_values[field['name']] = var
        return checkbox
    
    def _create_signature_input(self, parent, field: Dict) -> tk.Widget:
        """Create signature input widget"""
        sig_frame = tk.Frame(parent, bg='#f5f5f5')
        sig_frame.pack(fill='x', pady=2)
        
        # Text input for typed signature
        var = tk.StringVar(value=field['value'])
        entry = tk.Entry(
            sig_frame,
            textvariable=var,
            font=('Arial', 11, 'italic'),
            bg='#fffacd',  # Light yellow background
            relief='solid',
            bd=1
        )
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Signature style note
        note_label = tk.Label(
            sig_frame,
            text="✍️ Type signature",
            font=('Arial', 9),
            fg='#666666',
            bg='#f5f5f5'
        )
        note_label.pack(side='right')
        
        self.field_values[field['name']] = var
        return entry
    
    def _create_image_input(self, parent, field: Dict) -> tk.Widget:
        """Create image input widget"""
        image_frame = tk.Frame(parent, bg='#f5f5f5')
        image_frame.pack(fill='x', pady=2)
        
        # Image path display
        var = tk.StringVar(value="No image selected")
        entry = tk.Entry(
            image_frame,
            textvariable=var,
            font=('Arial', 10),
            bg='#f0f0ff',  # Light purple background
            state='readonly',
            relief='solid',
            bd=1
        )
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Browse button
        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Image for PDF Form",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                var.set(os.path.basename(file_path))
                # Store full path for processing
                self.field_values[field['name'] + '_path'] = file_path
        
        browse_btn = tk.Button(
            image_frame,
            text="📁 Browse",
            command=select_image,
            bg='#9C27B0',
            fg='white',
            font=('Arial', 9)
        )
        browse_btn.pack(side='right')
        
        # Note about image handling
        note_label = tk.Label(
            parent,
            text="🖼️ Image will be embedded in the PDF form field area",
            font=('Arial', 8),
            fg='#666666',
            bg='#f5f5f5'
        )
        note_label.pack(anchor='w', pady=(2, 0))
        
        self.field_values[field['name']] = var
        return entry
    
    def _create_date_input(self, parent, field: Dict) -> tk.Widget:
        """Create date input widget"""
        date_frame = tk.Frame(parent, bg='#f5f5f5')
        date_frame.pack(fill='x', pady=2)
        
        # Date input
        var = tk.StringVar(value=field['value'])
        entry = tk.Entry(
            date_frame,
            textvariable=var,
            font=('Arial', 11),
            bg='#e3f2fd',  # Light blue background
            relief='solid',
            bd=1
        )
        entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Today button
        def set_today():
            from datetime import datetime
            today = datetime.now().strftime("%m/%d/%Y")
            var.set(today)
        
        today_btn = tk.Button(
            date_frame,
            text="📅 Today",
            command=set_today,
            bg='#2196F3',
            fg='white',
            font=('Arial', 9)
        )
        today_btn.pack(side='right')
        
        # Format hint
        hint_label = tk.Label(
            parent,
            text="📅 Format: MM/DD/YYYY (e.g., 12/25/2023)",
            font=('Arial', 8),
            fg='#666666',
            bg='#f5f5f5'
        )
        hint_label.pack(anchor='w', pady=(2, 0))
        
        self.field_values[field['name']] = var
        return entry
    
    def _create_radio_input(self, parent, field: Dict) -> tk.Widget:
        """Create radio button input widget"""
        radio_frame = tk.Frame(parent, bg='#f5f5f5')
        radio_frame.pack(fill='x', pady=2)
        
        var = tk.StringVar(value=field['value'])
        
        # Create radio buttons for options
        options = field.get('options', ['Option 1', 'Option 2', 'Option 3'])
        if not options:
            options = ['Yes', 'No']  # Default options
        
        for option in options:
            radio = tk.Radiobutton(
                radio_frame,
                text=option,
                variable=var,
                value=option,
                font=('Arial', 10),
                bg='#f5f5f5',
                activebackground='#f5f5f5'
            )
            radio.pack(anchor='w', padx=10)
        
        self.field_values[field['name']] = var
        return radio_frame
    
    def _create_dropdown_input(self, parent, field: Dict) -> tk.Widget:
        """Create dropdown input widget"""
        var = tk.StringVar(value=field['value'])
        
        options = field.get('options', ['Option 1', 'Option 2', 'Option 3'])
        if not options:
            options = ['Select an option...']
        
        combobox = ttk.Combobox(
            parent,
            textvariable=var,
            values=options,
            font=('Arial', 11),
            state='readonly'
        )
        combobox.pack(fill='x', pady=2)
        
        self.field_values[field['name']] = var
        return combobox
    
    def _create_listbox_input(self, parent, field: Dict) -> tk.Widget:
        """Create listbox input widget"""
        list_frame = tk.Frame(parent, bg='#f5f5f5')
        list_frame.pack(fill='x', pady=2)
        
        # Listbox with scrollbar
        listbox = tk.Listbox(
            list_frame,
            font=('Arial', 10),
            height=4,
            selectmode='single'
        )
        
        scrollbar = tk.Scrollbar(list_frame, orient='vertical')
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        # Add options
        options = field.get('options', ['Option 1', 'Option 2', 'Option 3'])
        for option in options:
            listbox.insert(tk.END, option)
        
        # Select current value if it exists
        current_value = field['value']
        if current_value and current_value in options:
            index = options.index(current_value)
            listbox.selection_set(index)
        
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Store listbox for value retrieval
        self.field_values[field['name']] = listbox
        return list_frame
    
    def _clear_all_fields(self):
        """Clear all form input fields"""
        result = messagebox.askyesno(
            "Clear All Fields",
            "Are you sure you want to clear all form inputs?"
        )
        
        if result:
            # Clear overlay widget values
            for field_name, widget in self.field_widgets.items():
                if field_name.endswith('_var'):
                    # Boolean variable for checkbox
                    if isinstance(widget, tk.BooleanVar):
                        widget.set(False)
                elif isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, ttk.Combobox):
                    widget.set('')
                elif isinstance(widget, tk.Frame):
                    # Image field frame - reset preview
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.configure(
                                image="",
                                text="📷 Click to select image",
                                bg='#f5f5f5',
                                fg='#666666'
                            )
            
            # Clear stored values
            self.field_values.clear()
    
    def _save_completed_form(self):
        """Save the completed PDF form"""
        # Get output file path
        output_path = filedialog.asksaveasfilename(
            title="Save Completed PDF Form",
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ],
            initialfile=f"completed_{os.path.basename(self.pdf_path)}"
        )
        
        if not output_path:
            return
        
        # Fill the PDF with form data
        if self._fill_pdf_form(output_path):
            messagebox.showinfo(
                "Success",
                f"✅ PDF form completed and saved!\n\nFile: {output_path}\nFields filled: {len(self.form_fields)}"
            )
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save completed PDF form")
    
    def _fill_pdf_form(self, output_path: str) -> bool:
        """Fill the PDF form with user inputs and save"""
        try:
            # Create a copy of the PDF for editing
            output_doc = fitz.open(self.pdf_path)
            
            filled_count = 0
            
            # Fill each form field
            for field in self.form_fields:
                field_name = field['name']
                field_type = field['type']
                
                # Get user input value from overlay widgets
                value = None
                
                if field_name in self.field_widgets:
                    widget = self.field_widgets[field_name]
                    
                    try:
                        if field_type == 'TEXT' or field_type == 'DATE':
                            value = widget.get()
                        elif field_type == 'CHECKBOX':
                            var = self.field_widgets.get(f"{field_name}_var")
                            if var:
                                value = "Yes" if var.get() else "No"
                        elif field_type == 'DROPDOWN':
                            value = widget.get()
                        elif field_type == 'IMAGE':
                            # Handle image field specially
                            if field_name in self.field_values:
                                image_path = self.field_values[field_name]
                                if image_path and os.path.exists(image_path):
                                    # Embed image in the field area
                                    page = output_doc[field['page']]
                                    page.insert_image(field['rect'], filename=image_path, keep_proportion=True)
                                    
                                    # Remove the text widget to avoid conflict with embedded image
                                    widgets = list(page.widgets())
                                    for widget_obj in widgets:
                                        if (widget_obj.field_name == field.get('raw_name', field_name) or 
                                            widget_obj.field_name == field_name):
                                            page.delete_widget(widget_obj)
                                            print(f"Removed text widget for IMAGE field '{field_name}' to show embedded image")
                                            break
                                    
                                    filled_count += 1
                                    continue  # Skip the normal widget update for IMAGE fields
                        
                        # Update field value in PDF (for non-IMAGE fields)
                        if value is not None and value.strip():
                            # Find and update the widget
                            page = output_doc[field['page']]
                            widgets = list(page.widgets())
                            
                            for widget_obj in widgets:
                                # Check both clean name and raw name for widget matching
                                widget_field_name = widget_obj.field_name
                                raw_field_name = field.get('raw_name', field_name)
                                
                                if (widget_field_name == field_name or 
                                    widget_field_name == raw_field_name):
                                    
                                    if field_type == 'CHECKBOX':
                                        # Set checkbox state
                                        widget_obj.field_value = value == "Yes"
                                    else:
                                        # Set text value
                                        widget_obj.field_value = value
                                    widget_obj.update()
                                    filled_count += 1
                                    break
                    
                    except Exception as e:
                        print(f"Error filling field {field_name}: {e}")
                        continue
            
            # Save the completed PDF
            output_doc.save(output_path)
            output_doc.close()
            
            print(f"✅ Filled {filled_count} form fields and saved to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error filling PDF form: {e}")
            return False
    
    def _cancel(self):
        """Cancel the form input"""
        self.dialog.destroy()
        if self.pdf_doc:
            self.pdf_doc.close()


def test_pdf_form_inputter():
    """Test function for the PDF form inputter"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    inputter = PDFFormInputter(root)
    inputter.show_inputter()
    
    root.mainloop()


if __name__ == "__main__":
    test_pdf_form_inputter()