#!/usr/bin/env python3
"""
Quick test to verify the sidebar fix works with field loading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import FormField, FieldType
from pdf_handler import PDFHandler
from field_manager import FieldManager
from ui_components import FieldsSidebar
import tkinter as tk

def test_sidebar_integration():
    """Test that sidebar integration works without errors"""
    print("Testing sidebar integration with field loading...")
    
    # Create a minimal tkinter setup
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Create components
        canvas = tk.Canvas(root)
        pdf_handler = PDFHandler(canvas)
        field_manager = FieldManager(canvas, pdf_handler)
        
        # Create sidebar frame and sidebar
        sidebar_frame = tk.Frame(root)
        sidebar = FieldsSidebar(
            sidebar_frame,
            on_field_select=lambda f: print(f"Selected: {f.name if f else 'None'}"),
            on_field_delete=lambda f: print(f"Delete: {f.name}"),
            on_field_edit=lambda f: print(f"Edit: {f.name}"),
            on_field_duplicate=lambda f: print(f"Duplicate: {f.name}")
        )
        
        # Test PDF loading with comprehensive test form
        test_pdf = "comprehensive_test_form.pdf"
        if os.path.exists(test_pdf):
            print(f"📄 Testing with {test_pdf}")
            
            # Load PDF
            if pdf_handler.load_pdf(test_pdf):
                print("✅ PDF loaded successfully")
                
                # Detect fields
                detected_fields = pdf_handler.detect_existing_fields()
                print(f"✅ Detected {len(detected_fields)} fields")
                
                # Load fields into field manager
                field_manager.load_existing_fields(detected_fields)
                print("✅ Fields loaded into field manager")
                
                # Update sidebar (this was causing the error)
                sidebar.set_fields(field_manager.fields)
                sidebar.refresh_field_list()
                print("✅ Sidebar updated successfully")
                
                # Test sidebar field selection
                if detected_fields:
                    sidebar.select_field(detected_fields[0])
                    print(f"✅ Selected field: {detected_fields[0].name}")
                
                print("✅ All sidebar integration tests passed!")
                
            else:
                print("❌ Failed to load test PDF")
        else:
            print(f"ℹ️  Test PDF {test_pdf} not found, creating sample fields...")
            
            # Create sample fields for testing
            sample_fields = [
                FormField("test_field_1", FieldType.TEXT, 0, [50, 100, 200, 130]),
                FormField("test_field_2", FieldType.CHECKBOX, 0, [50, 150, 70, 170]),
                FormField("test_date", FieldType.DATETIME, 0, [50, 200, 200, 230], date_format="MM/DD/YYYY")
            ]
            
            field_manager.load_existing_fields(sample_fields)
            sidebar.set_fields(field_manager.fields)
            sidebar.refresh_field_list()
            
            print("✅ Sample fields loaded and sidebar updated successfully!")
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()

if __name__ == "__main__":
    print("🧪 Testing Sidebar Integration Fix")
    print("=" * 40)
    test_sidebar_integration()
    print("✅ Test completed!")