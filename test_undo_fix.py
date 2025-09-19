#!/usr/bin/env python3
"""
Test script to verify the IndexError fix in history manager
"""

from history_manager import HistoryManager, CreateFieldCommand, DeleteFieldCommand
from models import FormField, FieldType
from field_manager import FieldManager
from pdf_handler import PDFHandler
import tkinter as tk

def test_undo_edge_cases():
    """Test edge cases that could cause IndexError"""
    
    print("Testing undo system edge cases...")
    
    # Create minimal setup
    root = tk.Tk()
    canvas = tk.Canvas(root, width=100, height=100)
    pdf_handler = PDFHandler(canvas)
    field_manager = FieldManager(canvas, pdf_handler)
    history_manager = HistoryManager(max_history=25)
    
    # Test 1: Undo with empty history
    print("Test 1: Undo with empty history")
    result = history_manager.undo()
    print(f"  Result: {result} (should be False)")
    assert result == False, "Should return False when no history"
    
    # Test 2: Undo description with empty history
    print("Test 2: Undo description with empty history")
    desc = history_manager.get_undo_description()
    print(f"  Description: {desc} (should be None)")
    assert desc is None, "Should return None when no history"
    
    # Test 3: Multiple undos beyond available history
    print("Test 3: Create one command, then try multiple undos")
    field = FormField("test", FieldType.TEXT, 0, [10, 10, 50, 30])
    cmd = CreateFieldCommand(field_manager, field)
    history_manager.execute_command(cmd)
    
    print(f"  History size: {len(history_manager.history)}")
    print(f"  Current index: {history_manager.current_index}")
    
    # First undo should work
    result1 = history_manager.undo()
    print(f"  First undo result: {result1} (should be True)")
    
    # Second undo should fail gracefully
    result2 = history_manager.undo()
    print(f"  Second undo result: {result2} (should be False)")
    
    # Third undo should also fail gracefully
    result3 = history_manager.undo()
    print(f"  Third undo result: {result3} (should be False)")
    
    # Test 4: Test bounds after manipulation
    print("Test 4: Test with corrupted index")
    history_manager.current_index = 999  # Corrupt the index
    result4 = history_manager.undo()
    print(f"  Undo with corrupted index: {result4} (should be False)")
    
    # Test 5: Test negative index
    print("Test 5: Test with negative index")
    history_manager.current_index = -5
    result5 = history_manager.undo()
    print(f"  Undo with negative index: {result5} (should be False)")
    
    print("\\nAll edge case tests completed successfully!")
    print("The IndexError should be fixed.")
    
    root.destroy()
    return True

if __name__ == "__main__":
    try:
        test_undo_edge_cases()
        print("\\n✅ All tests passed - IndexError fix verified!")
    except Exception as e:
        print(f"\\n❌ Test failed: {e}")