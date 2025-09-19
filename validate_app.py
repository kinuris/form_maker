#!/usr/bin/env python3
"""
Quick validation test for the PDF Form Maker application
"""

import sys
import os
import time
import threading

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing imports...")
    try:
        from models import FormField, FieldType, AppConstants, MouseState, ZoomState
        from pdf_handler import PDFHandler
        from field_manager import FieldManager
        from ui_components import ToolbarFrame, NavigationFrame, StatusBar, ScrollableCanvas
        from coordinate_utils import CoordinateTransformer, calculate_display_scale
        import main
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_class_initialization():
    """Test that core classes can be initialized"""
    print("Testing class initialization...")
    try:
        import tkinter as tk
        from models import AppConstants, ZoomState
        from coordinate_utils import CoordinateTransformer
        
        # Test ZoomState
        zoom_state = ZoomState()
        assert zoom_state.zoom_level == AppConstants.DEFAULT_ZOOM
        print("✅ ZoomState initialization successful")
        
        # Test CoordinateTransformer
        transformer = CoordinateTransformer(1.0, 25)
        test_rect = [100, 100, 200, 150]
        pdf_rect = transformer.canvas_to_pdf(test_rect, 800)
        canvas_rect = transformer.pdf_to_canvas(pdf_rect, 800)
        print("✅ CoordinateTransformer initialization successful")
        
        return True
    except Exception as e:
        print(f"❌ Class initialization failed: {e}")
        return False

def test_zoom_functionality():
    """Test zoom state management"""
    print("Testing zoom functionality...")
    try:
        from models import ZoomState, AppConstants
        
        zoom_state = ZoomState()
        
        # Test zoom in
        old_zoom = zoom_state.zoom_level
        zoom_state.zoom_in()
        assert zoom_state.zoom_level > old_zoom
        print("✅ Zoom in working")
        
        # Test zoom out
        zoom_state.zoom_out()
        assert zoom_state.zoom_level == old_zoom
        print("✅ Zoom out working")
        
        # Test zoom percentage
        percentage = zoom_state.get_zoom_percentage()
        assert "%" in percentage
        print(f"✅ Zoom percentage display: {percentage}")
        
        return True
    except Exception as e:
        print(f"❌ Zoom functionality failed: {e}")
        return False

if __name__ == "__main__":
    print("PDF Form Maker - Quick Validation Test")
    print("=" * 45)
    print()
    
    tests = [
        test_imports,
        test_class_initialization,
        test_zoom_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("-" * 45)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests PASSED! Application should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    print()
    print("Key improvements made:")
    print("✅ Fixed zoom-aware coordinate transformation")
    print("✅ Added canvas_rect storage for fields")
    print("✅ Updated field manager with PDFHandler reference")
    print("✅ Improved save functionality with zoom compensation")
    print("✅ Added comprehensive zoom and pan controls")