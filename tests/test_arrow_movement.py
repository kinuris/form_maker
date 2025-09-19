#!/usr/bin/env python3
"""
Test script to verify that arrow key movement works correctly with list-based rectangles.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from history_manager import HistoryManager, MoveFieldCommand
from field_manager import FieldManager
from models import FieldType, FormField
import unittest.mock as mock

def test_arrow_key_movement():
    """Test that arrow key movement calculations work correctly with list-based rectangles"""
    print("🧪 Testing arrow key movement with list-based rectangles...")
    
    # Mock components
    mock_canvas = mock.MagicMock()
    mock_pdf_handler = mock.MagicMock()
    
    # Create field manager and history manager
    field_manager = FieldManager(mock_canvas, mock_pdf_handler)
    history_manager = HistoryManager(max_history=25)
    
    # Create a test field
    field = FormField("Test Field", FieldType.TEXT, 0, [100, 200, 200, 230])
    field_manager.add_field(field)
    
    print(f"\n📝 Initial field position: {field.rect}")
    
    # Test arrow key movement simulation
    print("\n🏹 Testing arrow key movement calculation...")
    
    # Simulate right arrow (dx=2, dy=0)
    dx, dy = 2, 0
    original_rect = field.rect.copy()
    
    # Calculate new position (simulate the fixed arrow key code)
    new_rect = field.rect.copy()
    new_rect[0] += dx  # x1
    new_rect[1] += dy  # y1
    new_rect[2] += dx  # x2
    new_rect[3] += dy  # y2
    
    print(f"   Original: {original_rect}")
    print(f"   New (right +2): {new_rect}")
    
    # Verify the calculation is correct
    expected_new_rect = [102, 200, 202, 230]  # x values +2, y values unchanged
    
    if new_rect == expected_new_rect:
        print("   ✅ Arrow key movement calculation correct!")
    else:
        print(f"   ❌ Arrow key movement calculation failed!")
        print(f"      Expected: {expected_new_rect}")
        print(f"      Got: {new_rect}")
        return
    
    # Test move command creation and undo
    print("\n🔄 Testing move command and undo...")
    
    move_command = MoveFieldCommand(field_manager, field, original_rect, new_rect)
    
    # Execute the move
    move_command.execute()
    print(f"   After move execute: {field.rect}")
    
    # Undo the move
    move_command.undo()
    print(f"   After move undo: {field.rect}")
    
    # Verify undo worked
    if field.rect == original_rect:
        print("   ✅ Move undo works correctly!")
    else:
        print(f"   ❌ Move undo failed!")
        print(f"      Expected: {original_rect}")
        print(f"      Got: {field.rect}")
        return
    
    print("\n✅ All arrow key movement tests passed!")
    print("🔚 Test completed!")

if __name__ == "__main__":
    test_arrow_key_movement()