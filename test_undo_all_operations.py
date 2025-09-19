#!/usr/bin/env python3
"""
Test script to verify that all operations (create, move, delete) are properly recorded in undo history.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from history_manager import HistoryManager, CreateFieldCommand, DeleteFieldCommand, MoveFieldCommand
from field_manager import FieldManager
from models import FieldType, FormField
import unittest.mock as mock

def test_undo_all_operations():
    """Test that create, move, and delete operations are all recorded in history"""
    print("🧪 Testing undo system for all operations...")
    
    # Mock components
    mock_canvas = mock.MagicMock()
    mock_pdf_handler = mock.MagicMock()
    
    # Create field manager and history manager
    field_manager = FieldManager(mock_canvas, mock_pdf_handler)
    history_manager = HistoryManager(max_history=25)
    
    # Test 1: Create field operation recording
    print("\n📝 Test 1: Create field operation")
    field = FormField("Test Field", FieldType.TEXT, 0, [10, 10, 100, 30])
    create_command = CreateFieldCommand(field_manager, field)
    create_command.was_executed = True
    history_manager.add_command(create_command)
    
    print(f"   History length after create: {len(history_manager.history)}")
    print(f"   Can undo: {history_manager.can_undo()}")
    if history_manager.can_undo():
        print(f"   Undo description: {history_manager.get_undo_description()}")
    
    # Test 2: Move field operation recording  
    print("\n🚚 Test 2: Move field operation")
    old_rect = [10, 10, 100, 30]
    new_rect = [15, 15, 105, 35]
    move_command = MoveFieldCommand(field_manager, field, old_rect, new_rect)
    history_manager.add_command(move_command)
    
    print(f"   History length after move: {len(history_manager.history)}")
    print(f"   Can undo: {history_manager.can_undo()}")
    if history_manager.can_undo():
        print(f"   Undo description: {history_manager.get_undo_description()}")
    
    # Test 3: Delete field operation recording
    print("\n🗑️ Test 3: Delete field operation")
    delete_command = DeleteFieldCommand(field_manager, field)
    history_manager.execute_command(delete_command)  # This one executes since it's not done yet
    
    print(f"   History length after delete: {len(history_manager.history)}")
    print(f"   Can undo: {history_manager.can_undo()}")
    if history_manager.can_undo():
        print(f"   Undo description: {history_manager.get_undo_description()}")
    
    # Test 4: Undo operations
    print("\n↩️ Test 4: Undo operations")
    
    # Undo delete
    if history_manager.can_undo():
        desc = history_manager.get_undo_description()
        result = history_manager.undo()
        print(f"   Undid: {desc} - Success: {result}")
    
    # Undo move
    if history_manager.can_undo():
        desc = history_manager.get_undo_description()
        result = history_manager.undo()
        print(f"   Undid: {desc} - Success: {result}")
    
    # Undo create
    if history_manager.can_undo():
        desc = history_manager.get_undo_description()
        result = history_manager.undo()
        print(f"   Undid: {desc} - Success: {result}")
    
    # Final state
    print(f"\n📊 Final state:")
    print(f"   History length: {len(history_manager.history)}")
    print(f"   Current index: {history_manager.current_index}")
    print(f"   Can undo: {history_manager.can_undo()}")
    print(f"   Can redo: {history_manager.can_redo()}")
    
    # Verify all operations were recorded
    expected_operations = 3  # create, move, delete
    if len(history_manager.history) == expected_operations:
        print("\n✅ SUCCESS: All operations were recorded in history!")
    else:
        print(f"\n❌ FAILED: Expected {expected_operations} operations, got {len(history_manager.history)}")
        
    print("\n🔚 Test completed!")

if __name__ == "__main__":
    test_undo_all_operations()