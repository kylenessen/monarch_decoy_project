"""
Dialog utilities for the ROI Manager.
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox, Button
from typing import Tuple, Callable, Optional


def create_text_input_dialog(fig, ax, title, label, default, callback, pos_y=0.85):
    """
    Create a text input dialog.
    
    Args:
        fig: Matplotlib figure
        ax: Main axes to avoid
        title: Dialog title
        label: Input label
        default: Default value
        callback: Function to call on submit
        pos_y: Y position for the dialog
        
    Returns:
        TextBox: The created textbox
    """
    # Remove existing text if any
    for txt in fig.texts:
        txt.remove()
    
    # Remove any existing auxiliary axes (like previous textboxes)
    for axes in fig.axes[:]:
        if axes != ax:
            axes.remove()
    
    plt.figtext(0.5, 0.9, title, ha="center")
    ax_textbox = plt.axes([0.3, pos_y, 0.4, 0.05])
    text_box = TextBox(ax_textbox, label, initial=default)
    text_box.on_submit(callback)
    
    plt.draw()
    return text_box


def show_message(fig, message, color="black", pos_y=0.9):
    """
    Show a message on the figure.
    
    Args:
        fig: Matplotlib figure
        message: Message to display
        color: Text color
        pos_y: Y position for the message
    """
    for txt in fig.texts:
        txt.remove()
    
    plt.figtext(0.5, pos_y, message, ha="center", color=color)
    plt.draw()


def clear_dialogs(fig, ax):
    """
    Clear all dialogs and text from the figure.
    
    Args:
        fig: Matplotlib figure
        ax: Main axes to keep
    """
    # Remove any auxiliary axes
    for axes in fig.axes[:]:
        if axes != ax:
            axes.remove()
            
    # Remove any existing text
    for txt in fig.texts:
        txt.remove()
    
    plt.draw()


class WhiteBalanceDialog:
    """Dialog for white balance eyedropper functionality."""
    
    def __init__(self, fig, ax, callback: Callable[[Tuple[int, int]], None]):
        """
        Initialize the white balance dialog.
        
        Args:
            fig: Matplotlib figure
            ax: Matplotlib axes for the image
            callback: Function to call when a point is selected
        """
        self.fig = fig
        self.ax = ax
        self.callback = callback
        self.eyedropper_active = False
        self.click_event = None
        self.instruction_text = None
        self.result_text = None
        self.setup()
        
    def setup(self):
        """Set up the dialog UI."""
        # Clear any existing text
        for txt in self.fig.texts:
            txt.remove()
            
        # Create instruction text
        self.instruction_text = plt.figtext(
            0.5, 0.95, 
            "Click on a neutral gray or white area to set white balance", 
            ha="center", 
            color="blue"
        )
        
        # Create buttons
        ax_pick = plt.axes([0.3, 0.025, 0.2, 0.05])
        ax_cancel = plt.axes([0.55, 0.025, 0.2, 0.05])
        
        self.btn_pick = Button(ax_pick, 'Pick Color')
        self.btn_cancel = Button(ax_cancel, 'Cancel')
        
        self.btn_pick.on_clicked(self.activate_eyedropper)
        self.btn_cancel.on_clicked(self.cancel)
        
        # Add the result text placeholder
        self.result_text = plt.figtext(
            0.5, 0.9, 
            "", 
            ha="center", 
            color="green"
        )
        
        plt.draw()
    
    def activate_eyedropper(self, event):
        """Activate the eyedropper tool."""
        if self.eyedropper_active:
            return
            
        self.eyedropper_active = True
        self.btn_pick.label.set_text("Picking...")
        
        # Update instruction
        self.instruction_text.set_text("Click on a neutral gray or white area")
        
        # Connect the click event
        self.click_event = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        plt.draw()
    
    def on_click(self, event):
        """Handle click events when eyedropper is active."""
        if not self.eyedropper_active or event.inaxes != self.ax:
            return
            
        # Get the click coordinates
        x, y = int(event.xdata), int(event.ydata)
        
        # Disconnect the click event
        self.fig.canvas.mpl_disconnect(self.click_event)
        
        # Update status
        self.eyedropper_active = False
        self.btn_pick.label.set_text("Pick Color")
        
        # Call the callback with the selected point
        self.callback((x, y))
        
        # Cleanup the dialog (buttons and text)
        self.cleanup()
    
    def cancel(self, event):
        """Cancel the white balance dialog."""
        if self.click_event:
            self.fig.canvas.mpl_disconnect(self.click_event)
        self.cleanup()
        
    def cleanup(self):
        """Remove the dialog elements."""
        # Remove text
        if self.instruction_text:
            self.instruction_text.remove()
            self.instruction_text = None
            
        if self.result_text:
            self.result_text.remove()
            self.result_text = None
            
        # Remove buttons
        if hasattr(self, 'btn_pick') and self.btn_pick.ax:
            self.btn_pick.ax.remove()
            
        if hasattr(self, 'btn_cancel') and self.btn_cancel.ax:
            self.btn_cancel.ax.remove()
            
        plt.draw()