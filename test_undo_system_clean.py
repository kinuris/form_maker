#!/usr/bin/env python3
"""
Test script for undo/redo functionality in PDF Form Maker
"""

import tkinter as tk
from models import FormField, FieldType
from history_manager import HistoryManager, CreateFieldCommand, DeleteFieldCommand, MoveFieldCommand
from field_manager import FieldManager
from pdf_handler import PDFHandler

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
        history_text = f"History: {info['current_index'] + 1}/{info['total_commands']} commands"
        history_text += f" | Can undo: {info['can_undo']} | Can redo: {info['can_redo']}"
        if info['undo_description']:
            history_text += f"\\nNext undo: {info['undo_description']}"
        history_label.config(text=history_text)
    
    def create_test_field():
        # Create a test field
        field = FormField(
            name=f"test_field_{len(field_manager.fields) + 1}",
            type=FieldType.TEXT,
            page_num=0,
            rect=[50 + len(field_manager.fields) * 30, 50 + len(field_manager.fields) * 40, 200, 80]
        )
        
        # Use command to create field
        create_command = CreateFieldCommand(field_manager, field)
        history_manager.execute_command(create_command)
        
        log_operation(f"Created field '{field.name}'")
        return field
    
    def delete_selected_field():
        if field_manager.selected_field:
            field = field_manager.selected_field
            delete_command = DeleteFieldCommand(field_manager, field)
            history_manager.execute_command(delete_command)
            log_operation(f"Deleted field '{field.name}'")
        else:
            log_operation("No field selected to delete")
    
    def move_selected_field():
        if field_manager.selected_field:
            field = field_manager.selected_field
            old_rect = field.rect.copy()
            new_rect = [old_rect[0] + 20, old_rect[1] + 20, old_rect[2] + 20, old_rect[3] + 20]
            
            move_command = MoveFieldCommand(field_manager, field, old_rect, new_rect)
            history_manager.execute_command(move_command)
            log_operation(f"Moved field '{field.name}'")
        else:
            log_operation("No field selected to move")
    
    def undo_action():
        if history_manager.undo():
            log_operation("Undone action")
        else:
            log_operation("Nothing to undo")
    
    def redo_action():
        if history_manager.redo():
            log_operation("Redone action")
        else:
            log_operation("Nothing to redo")
    
    def select_field(event):
        x, y = event.x, event.y
        # Simple field selection
        for field in field_manager.fields:
            if (field.rect[0] <= x <= field.rect[2] and 
                field.rect[1] <= y <= field.rect[3]):
                field_manager.select_field(field)
                log_operation(f"Selected field '{field.name}'")
                return
        field_manager.clear_selection()
        log_operation("Cleared selection")
    
    # Bind canvas click
    canvas.bind('<Button-1>', select_field)
    
    # Control buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Create Field", command=create_test_field, bg='#4CAF50', fg='white').pack(side='left', padx=2)
    tk.Button(button_frame, text="Delete Selected", command=delete_selected_field, bg='#f44336', fg='white').pack(side='left', padx=2)
    tk.Button(button_frame, text="Move Selected", command=move_selected_field, bg='#2196F3', fg='white').pack(side='left', padx=2)
    
    # Undo/Redo buttons
    undo_frame = tk.Frame(root)
    undo_frame.pack(pady=10)
    
    tk.Button(undo_frame, text="⟲ Undo (Ctrl+Z)", command=undo_action, bg='#FF9800', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)
    tk.Button(undo_frame, text="⟳ Redo", command=redo_action, bg='#9C27B0', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=5)
    
    # Bind Ctrl+Z
    root.bind('<Control-z>', lambda e: undo_action())
    root.bind('<Control-y>', lambda e: redo_action())
    
    # Status display
    status_label = tk.Label(root, text="Ready - Click buttons to test undo functionality", 
                           font=('Arial', 10), wraplength=550, justify='left')
    status_label.pack(pady=5)
    
    # History display
    history_label = tk.Label(root, text="No history yet", 
                            font=('Arial', 9), wraplength=550, justify='left', fg='blue')
    history_label.pack(pady=5)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Instructions:\\n" +
             "1. Click 'Create Field' to add new fields\\n" +
             "2. Click on fields to select them\\n" +
             "3. Use 'Delete Selected' or 'Move Selected' to modify\\n" +
             "4. Press 'Undo' or Ctrl+Z to undo actions\\n" +
             "5. Watch the history counter update",
        font=('Arial', 9),
        wraplength=550,
        justify='left',
        bg='#f0f0f0'
    )
    instructions.pack(pady=10, padx=10, fill='x')
    
    # Initialize display
    update_history_display()
    
    print("Undo system test window created!")
    print("Test the undo functionality with the buttons and keyboard shortcuts.")
    
    root.mainloop()
    
    return operations

if __name__ == "__main__":
    operations = test_undo_system()
    print(f"\\nTest completed. Total operations: {len(operations)}")