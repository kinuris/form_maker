#!/usr/bin/env python3
"""
History management system for PDF Form Maker
Implements undo/redo functionality using the Command pattern
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from models import FormField, FieldType
import copy


class Command(ABC):
    """Abstract base class for all undoable commands"""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command"""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Get a description of what this command does"""
        pass


class CreateFieldCommand(Command):
    """Command for creating a new field"""
    
    def __init__(self, field_manager, field: FormField):
        self.field_manager = field_manager
        self.field = copy.deepcopy(field)
        self.was_executed = False
    
    def execute(self) -> None:
        """Create the field"""
        if not self.was_executed:
            # Add field to manager
            self.field_manager.add_field(self.field)
            self.field_manager.draw_field(self.field)
            self.was_executed = True
    
    def undo(self) -> None:
        """Remove the created field"""
        if self.was_executed:
            if self.field in self.field_manager.fields:
                self.field_manager.delete_field(self.field)
    
    def description(self) -> str:
        return f"Create {self.field.type.value} field '{self.field.name}'"


class DeleteFieldCommand(Command):
    """Command for deleting a field"""
    
    def __init__(self, field_manager, field: FormField):
        self.field_manager = field_manager
        self.field = copy.deepcopy(field)
        self.field_index = None
    
    def execute(self) -> None:
        """Delete the field"""
        if self.field in self.field_manager.fields:
            self.field_index = self.field_manager.fields.index(self.field)
            self.field_manager.delete_field(self.field)
    
    def undo(self) -> None:
        """Restore the deleted field"""
        if self.field_index is not None:
            # Insert at original position
            self.field_manager.fields.insert(self.field_index, self.field)
            self.field_manager.draw_field(self.field)
    
    def description(self) -> str:
        return f"Delete {self.field.type.value} field '{self.field.name}'"


class MoveFieldCommand(Command):
    """Command for moving a field"""
    
    def __init__(self, field_manager, field: FormField, old_rect: List[float], new_rect: List[float]):
        self.field_manager = field_manager
        self.field = field
        self.old_rect = copy.deepcopy(old_rect)
        self.new_rect = copy.deepcopy(new_rect)
    
    def execute(self) -> None:
        """Move the field to new position"""
        self.field.rect = copy.deepcopy(self.new_rect)
        self.field_manager.draw_field(self.field)
    
    def undo(self) -> None:
        """Move the field back to old position"""
        self.field.rect = copy.deepcopy(self.old_rect)
        self.field_manager.draw_field(self.field)
    
    def description(self) -> str:
        return f"Move field '{self.field.name}'"


class EditFieldCommand(Command):
    """Command for editing field properties"""
    
    def __init__(self, field_manager, field: FormField, old_properties: Dict[str, Any], new_properties: Dict[str, Any]):
        self.field_manager = field_manager
        self.field = field
        self.old_properties = copy.deepcopy(old_properties)
        self.new_properties = copy.deepcopy(new_properties)
    
    def execute(self) -> None:
        """Apply new properties to field"""
        for prop, value in self.new_properties.items():
            setattr(self.field, prop, value)
        self.field_manager.draw_field(self.field)
    
    def undo(self) -> None:
        """Restore old properties to field"""
        for prop, value in self.old_properties.items():
            setattr(self.field, prop, value)
        self.field_manager.draw_field(self.field)
    
    def description(self) -> str:
        changed_props = list(self.new_properties.keys())
        return f"Edit field '{self.field.name}' ({', '.join(changed_props)})"


class BatchCommand(Command):
    """Command that groups multiple commands together"""
    
    def __init__(self, commands: List[Command], description: str):
        self.commands = commands
        self._description = description
    
    def execute(self) -> None:
        """Execute all commands in order"""
        for command in self.commands:
            command.execute()
    
    def undo(self) -> None:
        """Undo all commands in reverse order"""
        for command in reversed(self.commands):
            command.undo()
    
    def description(self) -> str:
        return self._description


class HistoryManager:
    """Manages command history for undo/redo functionality"""
    
    def __init__(self, max_history: int = 25):
        self.max_history = max_history
        self.history: List[Command] = []
        self.current_index = -1  # -1 means no commands executed
        self.enabled = True
    
    def execute_command(self, command: Command) -> None:
        """Execute a command and add it to history"""
        if not self.enabled:
            command.execute()
            return
        
        # Execute the command
        command.execute()
        
        # Add command to history
        self.add_command(command)
    
    def add_command(self, command: Command) -> None:
        """Add a command to history without executing it (for commands already executed)"""
        if not self.enabled:
            return
        
        # Remove any commands after current index (for redo functionality)
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add command to history
        self.history.append(command)
        self.current_index += 1
        
        # Maintain max history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def undo(self) -> bool:
        """Undo the last command. Returns True if successful, False if nothing to undo"""
        if not self.can_undo():
            return False
        
        # Double-check bounds for safety
        if self.current_index >= len(self.history):
            self.current_index = len(self.history) - 1
        
        if self.current_index < 0 or len(self.history) == 0:
            return False
        
        command = self.history[self.current_index]
        command.undo()
        self.current_index -= 1
        return True
    
    def redo(self) -> bool:
        """Redo the next command. Returns True if successful, False if nothing to redo"""
        if not self.can_redo():
            return False
        
        # Double-check bounds for safety
        if self.current_index >= len(self.history) - 1:
            return False
        
        self.current_index += 1
        command = self.history[self.current_index]
        command.execute()
        return True
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return (self.current_index >= 0 and 
                self.current_index < len(self.history) and 
                len(self.history) > 0)
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return (self.current_index < len(self.history) - 1 and 
                len(self.history) > 0)
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of what would be undone"""
        if (self.can_undo() and 
            self.current_index < len(self.history) and 
            self.current_index >= 0):
            return self.history[self.current_index].description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of what would be redone"""
        if (self.can_redo() and 
            self.current_index + 1 < len(self.history) and 
            self.current_index >= -1):
            return self.history[self.current_index + 1].description()
        return None
    
    def clear_history(self) -> None:
        """Clear all history"""
        self.history.clear()
        self.current_index = -1
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable history tracking"""
        self.enabled = enabled
    
    def get_history_info(self) -> Dict[str, Any]:
        """Get information about current history state"""
        return {
            'total_commands': len(self.history),
            'current_index': self.current_index,
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo(),
            'undo_description': self.get_undo_description(),
            'redo_description': self.get_redo_description()
        }