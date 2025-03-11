"""
Dialog utilities for the ROI Manager.
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox


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