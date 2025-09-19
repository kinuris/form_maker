#!/usr/bin/env python3
"""
Simple arrow key test to verify focus and event handling
"""

import tkinter as tk

def simple_arrow_test():
    """Create a simple test to verify arrow key events work"""
    
    root = tk.Tk()
    root.title("Arrow Key Test - Click Canvas First")
    root.geometry("500x400")
    
    # Create canvas with takefocus=True
    canvas = tk.Canvas(root, bg='lightblue', takefocus=True)
    canvas.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Create a rectangle to move
    rect = canvas.create_rectangle(200, 150, 250, 200, fill='red', outline='black', width=2)
    
    # Status label
    status = tk.Label(root, text="Click on blue canvas area first, then use arrow keys", 
                     font=("Arial", 12), fg="blue")
    status.pack(pady=10)
    
    coords_label = tk.Label(root, text="Rectangle position will show here", 
                           font=("Arial", 10))
    coords_label.pack()
    
    def update_position():
        coords = canvas.coords(rect)
        coords_label.config(text=f"Position: ({coords[0]:.0f}, {coords[1]:.0f})")
    
    def on_arrow_key(event):
        print(f"Arrow key event: {event.keysym}")
        step = 10
        dx, dy = 0, 0
        
        if event.keysym == 'Left':
            dx = -step
            direction = "LEFT"
        elif event.keysym == 'Right':
            dx = step
            direction = "RIGHT"
        elif event.keysym == 'Up':
            dy = -step
            direction = "UP"
        elif event.keysym == 'Down':
            dy = step
            direction = "DOWN"
        else:
            return
            
        canvas.move(rect, dx, dy)
        update_position()
        status.config(text=f"Moved {direction}! Arrow keys are working.", fg="green")
    
    # Bind arrow keys to canvas
    canvas.bind('<Left>', on_arrow_key)
    canvas.bind('<Right>', on_arrow_key)
    canvas.bind('<Up>', on_arrow_key)
    canvas.bind('<Down>', on_arrow_key)
    
    # Set focus when canvas is clicked
    def on_canvas_click(event):
        canvas.focus_set()
        status.config(text="Canvas focused! Now try arrow keys.", fg="orange")
    
    canvas.bind('<Button-1>', on_canvas_click)
    
    # Set initial focus
    canvas.focus_set()
    update_position()
    
    print("Simple arrow key test window created.")
    print("Instructions:")
    print("1. Click on the blue canvas area")
    print("2. Press arrow keys to move the red rectangle")
    print("3. Watch for position updates")
    
    root.mainloop()

if __name__ == "__main__":
    simple_arrow_test()