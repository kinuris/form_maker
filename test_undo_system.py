#!/usr/bin/env python3
"""
Test script for undo/redo functionality in PDF Form Maker
"""

import tkinter as tk
from models import FormField, FieldType
from history_manager import HistoryManager, CreateFieldCommand, DeleteFieldCommand, MoveFieldCommand
from field_manager import FieldManager
from pdf_handler import PDFHandler
import copy

def test_undo_system():
    """Test the undo system with various operations"""
    
    # Create test window
    root = tk.Tk()
    root.title("Undo System Test")
    root.geometry("600x700")
    
    # Create canvas
    canvas = tk.Canvas(root, bg='white', width=400, height=500)
    canvas.pack(padx=10, pady=10)
    
    # Create test handlers (minimal setup)
    pdf_handler = PDFHandler(canvas)
    field_manager = FieldManager(canvas, pdf_handler)
    history_manager = HistoryManager(max_history=25)
    
    # Track operations
    operations = []
    
    def log_operation(op):
        operations.append(op)
        status_label.config(text=f"Last operation: {op}")
        update_history_display()
    
    def update_history_display():
        info = history_manager.get_history_info()
        history_text = f"History: {info['current_index'] + 1}/{info['total_commands']} commands\n"
        history_text += f"Can undo: {info['can_undo']} | Can redo: {info['can_redo']}\n"
        if info['undo_description']:
            history_text += f"Next undo: {info['undo_description']}"
        history_label.config(text=history_text)\n    \n    def create_test_field():\n        # Create a test field\n        field = FormField(\n            name=f\"test_field_{len(field_manager.fields) + 1}\",\n            type=FieldType.TEXT,\n            page_num=0,\n            rect=[50 + len(field_manager.fields) * 30, 50 + len(field_manager.fields) * 40, 200, 80]\n        )\n        \n        # Use command to create field\n        create_command = CreateFieldCommand(field_manager, field)\n        history_manager.execute_command(create_command)\n        \n        log_operation(f\"Created field '{field.name}'\")\n        return field\n    \n    def delete_selected_field():\n        if field_manager.selected_field:\n            field = field_manager.selected_field\n            delete_command = DeleteFieldCommand(field_manager, field)\n            history_manager.execute_command(delete_command)\n            log_operation(f\"Deleted field '{field.name}'\")\n        else:\n            log_operation(\"No field selected to delete\")\n    \n    def move_selected_field():\n        if field_manager.selected_field:\n            field = field_manager.selected_field\n            old_rect = field.rect.copy()\n            new_rect = [old_rect[0] + 20, old_rect[1] + 20, old_rect[2] + 20, old_rect[3] + 20]\n            \n            move_command = MoveFieldCommand(field_manager, field, old_rect, new_rect)\n            history_manager.execute_command(move_command)\n            log_operation(f\"Moved field '{field.name}'\")\n        else:\n            log_operation(\"No field selected to move\")\n    \n    def undo_action():\n        if history_manager.undo():\n            description = history_manager.get_undo_description()\n            log_operation(f\"Undone action\")\n        else:\n            log_operation(\"Nothing to undo\")\n    \n    def redo_action():\n        if history_manager.redo():\n            description = history_manager.get_redo_description()\n            log_operation(f\"Redone action\")\n        else:\n            log_operation(\"Nothing to redo\")\n    \n    def select_field(event):\n        x, y = event.x, event.y\n        # Simple field selection\n        for field in field_manager.fields:\n            if (field.rect[0] <= x <= field.rect[2] and \n                field.rect[1] <= y <= field.rect[3]):\n                field_manager.select_field(field)\n                log_operation(f\"Selected field '{field.name}'\")\n                return\n        field_manager.clear_selection()\n        log_operation(\"Cleared selection\")\n    \n    # Bind canvas click\n    canvas.bind('<Button-1>', select_field)\n    \n    # Control buttons\n    button_frame = tk.Frame(root)\n    button_frame.pack(pady=10)\n    \n    tk.Button(button_frame, text=\"Create Field\", command=create_test_field, bg='#4CAF50', fg='white').pack(side='left', padx=2)\n    tk.Button(button_frame, text=\"Delete Selected\", command=delete_selected_field, bg='#f44336', fg='white').pack(side='left', padx=2)\n    tk.Button(button_frame, text=\"Move Selected\", command=move_selected_field, bg='#2196F3', fg='white').pack(side='left', padx=2)\n    \n    # Undo/Redo buttons\n    undo_frame = tk.Frame(root)\n    undo_frame.pack(pady=10)\n    \n    tk.Button(undo_frame, text=\"⟲ Undo (Ctrl+Z)\", command=undo_action, bg='#FF9800', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)\n    tk.Button(undo_frame, text=\"⟳ Redo\", command=redo_action, bg='#9C27B0', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)\n    \n    # Bind Ctrl+Z\n    root.bind('<Control-z>', lambda e: undo_action())\n    root.bind('<Control-y>', lambda e: redo_action())\n    \n    # Status display\n    status_label = tk.Label(root, text=\"Ready - Click buttons to test undo functionality\", \n                           font=('Arial', 10), wraplength=550, justify='left')\n    status_label.pack(pady=5)\n    \n    # History display\n    history_label = tk.Label(root, text=\"No history yet\", \n                            font=('Arial', 9), wraplength=550, justify='left', fg='blue')\n    history_label.pack(pady=5)\n    \n    # Instructions\n    instructions = tk.Label(\n        root,\n        text=\"Instructions:\\n\" +\n             \"1. Click 'Create Field' to add new fields\\n\" +\n             \"2. Click on fields to select them\\n\" +\n             \"3. Use 'Delete Selected' or 'Move Selected' to modify\\n\" +\n             \"4. Press 'Undo' or Ctrl+Z to undo actions\\n\" +\n             \"5. Watch the history counter update\",\n        font=('Arial', 9),\n        wraplength=550,\n        justify='left',\n        bg='#f0f0f0'\n    )\n    instructions.pack(pady=10, padx=10, fill='x')\n    \n    # Initialize display\n    update_history_display()\n    \n    print(\"Undo system test window created!\")\n    print(\"Test the undo functionality with the buttons and keyboard shortcuts.\")\n    \n    root.mainloop()\n    \n    return operations\n\nif __name__ == \"__main__\":\n    operations = test_undo_system()\n    print(f\"\\nTest completed. Total operations: {len(operations)}\")