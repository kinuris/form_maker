#!/usr/bin/env python3
"""
Test script to verify that move undo operations properly update the UI.
This test focuses on the canvas element cleanup during undo.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from history_manager import HistoryManager, MoveFieldCommand
from field_manager import FieldManager
from models import FieldType, FormField
import unittest.mock as mock

def test_move_undo_ui_update():
    """Test that move undo operations properly clean up canvas elements"""
    print("🧪 Testing move undo UI update...")
    
    # Mock canvas with tracking for delete calls
    mock_canvas = mock.MagicMock()
    mock_pdf_handler = mock.MagicMock()
    delete_calls = []
    
    def track_delete(tag):
        delete_calls.append(tag)
        print(f"   Canvas delete called with tag: '{tag}'")
    
    mock_canvas.delete.side_effect = track_delete
    
    # Create field manager and history manager
    field_manager = FieldManager(mock_canvas, mock_pdf_handler)
    history_manager = HistoryManager(max_history=25)
    
    # Create a test field
    field = FormField("Test Field", FieldType.TEXT, 0, [10, 10, 100, 30])
    field_manager.add_field(field)
    
    # Test move operation and undo
    print("\n📝 Test: Move field and undo")
    old_rect = [10, 10, 100, 30]
    new_rect = [50, 50, 140, 70]
    
    # Simulate the move
    field.rect = new_rect.copy()
    
    # Create move command and add to history
    move_command = MoveFieldCommand(field_manager, field, old_rect, new_rect)
    history_manager.add_command(move_command)
    
    print(f"   Field moved to: {field.rect}")
    print(f"   History length: {len(history_manager.history)}")
    
    # Clear delete calls tracking
    delete_calls.clear()
    
    # Undo the move
    print("\n↩️ Undoing move...")
    success = history_manager.undo()
    print(f"   Undo success: {success}")
    print(f"   Field position after undo: {field.rect}")
    
    # Check if canvas delete was called for cleanup
    print(f"\n🔍 Canvas delete calls during undo:")
    for call in delete_calls:
        print(f"   - {call}")
    
    # Verify that the proper cleanup occurred
    expected_deletes = [
        f"field_{field.name}",           # Main field rectangle
        f"field_{field.name}_label",     # Field label
    ]
    
    cleanup_successful = all(expected_delete in delete_calls for expected_delete in expected_deletes)
    
    if cleanup_successful:
        print(f"\n✅ SUCCESS: Canvas cleanup occurred during move undo!")
        print(f"   - Field rectangle cleanup: {'✅' if f'field_{field.name}' in delete_calls else '❌'}")
        print(f"   - Field label cleanup: {'✅' if f'field_{field.name}_label' in delete_calls else '❌'}")
    else:
        print(f"\n❌ FAILED: Canvas cleanup did not occur properly")
        print(f"   Expected: {expected_deletes}")
        print(f"   Got: {delete_calls}")
    
    # Verify field position was restored
    if field.rect == old_rect:
        print(f"   - Field position restored: ✅")
    else:
        print(f"   - Field position restored: ❌ (Expected {old_rect}, got {field.rect})")
    
    print("\n🔚 Test completed!")

if __name__ == "__main__":
    test_move_undo_ui_update()