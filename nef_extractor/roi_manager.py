"""
ROI Manager for NEF ROI Extractor.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import PolygonSelector, Button, TextBox
from matplotlib.patches import Polygon
from typing import Dict, List, Tuple, Any, Optional

from .image_processor import load_nef_image, normalize_for_display, calculate_white_balance
from .utils.file_io import save_rois_to_json, load_rois_from_json, save_pixel_data_to_csv
from .utils.polygon import extract_pixels_from_polygon, get_polygon_centroid
from .ui.dialogs import WhiteBalanceDialog


class ROIManager:
    """Handles the drawing, storing, and processing of ROIs."""

    def __init__(self, image_path: str, load_roi_path: Optional[str] = None, white_balance: Optional[Tuple[float, float, float]] = None):
        """
        Initialize the ROI Manager with an image.
        
        Args:
            image_path: Path to the NEF file
            load_roi_path: Optional path to a JSON file with existing ROIs
            white_balance: Optional tuple of (red_mult, green_mult, blue_mult) for white balance
        """
        self.image_path = image_path
        self.file_name = os.path.basename(image_path)
        
        # White balance multipliers (default to no adjustment)
        self.white_balance = white_balance
        
        # Open and process the RAW image
        self.rgb = load_nef_image(image_path, self.white_balance)
        
        # Normalize the image for display
        self.display_img = normalize_for_display(self.rgb)
        
        # Store ROIs
        self.rois = []
        
        # Initialize display variables
        self.fig, self.ax = None, None
        self.polygon_selector = None
        self.current_roi = []
        self.current_label = ""
        self.current_vertices = []
        self.current_temp_poly = None
        self.text_box = None
        self.drawing_active = False
        
        # Load existing ROIs if provided
        if load_roi_path:
            self.load_rois(load_roi_path)
    
    def setup_display(self):
        """Set up the matplotlib figure and interactive elements."""
        # Create figure and axes
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.15)  # Make room for buttons
        
        # Display the image
        self.ax.imshow(self.display_img)
        self.ax.set_title("Draw ROIs on the image")
        
        # Create selector for polygon drawing
        self.polygon_selector = PolygonSelector(
            self.ax,
            self.on_polygon_created,
            props=dict(color='r', linestyle='-', linewidth=2),
            handle_props=dict(markersize=8, markeredgecolor='r', markerfacecolor='none')
        )
        self.polygon_selector.set_active(False)  # Start inactive
        
        # Add buttons
        ax_new_roi = plt.axes([0.05, 0.05, 0.12, 0.05])
        ax_save_rois = plt.axes([0.2, 0.05, 0.12, 0.05])
        ax_process = plt.axes([0.35, 0.05, 0.12, 0.05])
        ax_white_balance = plt.axes([0.5, 0.05, 0.12, 0.05])
        ax_reset_wb = plt.axes([0.65, 0.05, 0.12, 0.05])
        ax_quit = plt.axes([0.8, 0.05, 0.12, 0.05])
        
        self.btn_new_roi = Button(ax_new_roi, 'New ROI')
        self.btn_save_rois = Button(ax_save_rois, 'Save ROIs')
        self.btn_process = Button(ax_process, 'Process')
        self.btn_white_balance = Button(ax_white_balance, 'White Balance')
        self.btn_reset_wb = Button(ax_reset_wb, 'Reset WB')
        self.btn_quit = Button(ax_quit, 'Quit')
        
        self.btn_new_roi.on_clicked(self.start_new_roi)
        self.btn_save_rois.on_clicked(self.save_rois_dialog)
        self.btn_process.on_clicked(self.process_rois)
        self.btn_white_balance.on_clicked(self.start_white_balance)
        self.btn_reset_wb.on_clicked(self.reset_white_balance)
        self.btn_quit.on_clicked(self.quit_app)
        
        # Display existing ROIs if any
        self.draw_existing_rois()
    
    def start_new_roi(self, event):
        """Start drawing a new ROI."""
        if self.drawing_active:
            return
        
        self.drawing_active = True
        self.current_roi = []
        self.polygon_selector.set_active(True)
        self.btn_new_roi.label.set_text("Drawing...")
        plt.draw()
    
    def on_polygon_created(self, vertices):
        """Callback when a polygon is created."""
        if not self.drawing_active:
            return
        
        # Convert vertices to a list of [x,y] coordinates
        vertices_list = [(x, y) for x, y in zip(vertices[0], vertices[1])]
        
        # Save current vertices for later use
        self.current_vertices = vertices_list
        
        # Important: Release mouse grab by disabling the polygon selector first
        self.polygon_selector.set_active(False)
        
        # Create a simple text input dialog
        ax_textbox = plt.axes([0.3, 0.8, 0.4, 0.05])
        self.text_box = TextBox(ax_textbox, 'ROI Label: ', initial='')
        self.text_box.on_submit(self.finish_roi_creation)
        
        # Show temporary polygon as visual indicator
        temp_poly = Polygon(vertices_list, fill=True, alpha=0.2, color='g')
        self.ax.add_patch(temp_poly)
        self.current_temp_poly = temp_poly
        
        plt.draw()
        
    def finish_roi_creation(self, label):
        """Finish the ROI creation process with the provided label."""
        self.current_label = label
        
        # Remove temporary polygon if it exists
        if hasattr(self, 'current_temp_poly'):
            self.current_temp_poly.remove()
            delattr(self, 'current_temp_poly')
        
        # Create a new ROI
        roi = {
            "label": self.current_label,
            "polygon": self.current_vertices
        }
        
        # Add to the list of ROIs
        self.rois.append(roi)
        
        # Draw the polygon permanently on the plot
        poly = Polygon(self.current_vertices, fill=True, alpha=0.3, color='r')
        self.ax.add_patch(poly)
        
        # Add label text
        centroid = get_polygon_centroid(self.current_vertices)
        self.ax.text(centroid[0], centroid[1], self.current_label, 
                    color='white', fontsize=10, ha='center', va='center')
        
        # Remove the textbox from the plot
        if hasattr(self, 'text_box') and self.text_box is not None:
            self.text_box.ax.remove()
            self.text_box = None
        
        # Reset drawing state
        self.drawing_active = False
        self.btn_new_roi.label.set_text("New ROI")
        plt.draw()
    
    def draw_existing_rois(self):
        """Draw any already loaded ROIs."""
        for roi in self.rois:
            vertices = np.array(roi["polygon"])
            poly = Polygon(vertices, fill=True, alpha=0.3, color='r')
            self.ax.add_patch(poly)
            
            # Add label text
            centroid = get_polygon_centroid(vertices)
            self.ax.text(centroid[0], centroid[1], roi["label"], 
                        color='white', fontsize=10, ha='center', va='center')
    
    def save_rois_dialog(self, event):
        """Save ROIs to a JSON file."""
        if not self.rois:
            # Create a text display instead of print
            plt.figtext(0.5, 0.9, "No ROIs to save.", ha="center", color="red")
            plt.draw()
            return
        
        # Make sure polygon selector is inactive
        if self.polygon_selector.active:
            self.polygon_selector.set_active(False)
        
        # Remove existing text if any
        for txt in self.fig.texts:
            txt.remove()
        
        # Remove any existing auxiliary axes (like previous textboxes)
        for ax in self.fig.axes[:]:
            if ax != self.ax:
                ax.remove()
            
        plt.figtext(0.5, 0.9, "Enter filename to save ROIs:", ha="center")
        ax_textbox = plt.axes([0.3, 0.85, 0.4, 0.05])
        self.text_box = TextBox(ax_textbox, 'Filename: ', initial='rois.json')
        self.text_box.on_submit(self.save_rois)
        plt.draw()
    
    def save_rois(self, filename: str):
        """Save ROIs to a JSON file."""
        # Remove the input box
        for ax in self.fig.axes:
            if ax != self.ax:
                ax.remove()
                
        # Remove existing text
        for txt in self.fig.texts:
            txt.remove()
        
        success = save_rois_to_json(filename, self.file_name, self.rois, self.white_balance)
        
        if success:
            # Show success message
            plt.figtext(0.5, 0.9, f"ROIs saved to {filename}", ha="center", color="green")
        else:
            # Show error message
            plt.figtext(0.5, 0.9, f"Error saving ROIs", ha="center", color="red")
        
        plt.draw()
    
    def load_rois(self, filename: str):
        """Load ROIs from a JSON file."""
        # This method is primarily called from the command line, but we'll 
        # provide visual feedback if the display is already setup
        
        try:
            data = load_rois_from_json(filename)
            
            # Check if the JSON is for the same file
            if data.get("file_name") != self.file_name:
                warning_msg = f"Warning: Loading ROIs from a different file: {data.get('file_name')}"
                print(warning_msg)  # For command line feedback
                
                # If display is setup, show warning in GUI
                if hasattr(self, 'fig') and self.fig is not None:
                    plt.figtext(0.5, 0.95, warning_msg, ha="center", color="orange")
            
            # Load the ROIs
            self.rois = data.get("rois", [])
            
            # Check for white balance information
            wb_data = data.get("white_balance")
            if wb_data and not self.white_balance:
                # Extract white balance if it exists
                try:
                    self.white_balance = (
                        float(wb_data["red"]), 
                        float(wb_data["green"]), 
                        float(wb_data["blue"])
                    )
                    
                    # Reload the image with the white balance
                    self.rgb = load_nef_image(self.image_path, self.white_balance)
                    self.display_img = normalize_for_display(self.rgb)
                    
                    # Update display if it exists
                    if hasattr(self, 'ax') and self.ax is not None:
                        self.ax.clear()
                        self.ax.imshow(self.display_img)
                        self.ax.set_title("Draw ROIs on the image")
                        self.draw_existing_rois()
                        
                    print(f"Loaded white balance: R={self.white_balance[0]:.2f}, G={self.white_balance[1]:.2f}, B={self.white_balance[2]:.2f}")
                except (KeyError, ValueError) as e:
                    print(f"Warning: Could not load white balance from file: {e}")
            
            success_msg = f"Loaded {len(self.rois)} ROIs from {filename}"
            print(success_msg)  # For command line feedback
            
            # If display is setup, show success in GUI
            if hasattr(self, 'fig') and self.fig is not None:
                plt.figtext(0.5, 0.9, success_msg, ha="center", color="green")
                plt.draw()
                
        except Exception as e:
            error_msg = f"Error loading ROIs: {e}"
            print(error_msg)  # For command line feedback
            
            # If display is setup, show error in GUI
            if hasattr(self, 'fig') and self.fig is not None:
                plt.figtext(0.5, 0.9, error_msg, ha="center", color="red")
                plt.draw()
    
    def start_white_balance(self, event):
        """Start the white balance adjustment process."""
        # Make sure polygon selector is inactive
        if self.polygon_selector and self.polygon_selector.active:
            self.polygon_selector.set_active(False)
        
        # Create a white balance dialog
        WhiteBalanceDialog(self.fig, self.ax, self.apply_white_balance)
    
    def apply_white_balance(self, point: Tuple[int, int]):
        """
        Apply white balance based on the selected point.
        
        Args:
            point: Tuple of (x, y) coordinates for the white reference point
        """
        x, y = point
        
        # Calculate white balance multipliers from the selected point
        self.white_balance = calculate_white_balance(self.rgb, x, y)
        
        # Display the white balance values
        wb_text = f"White Balance: R={self.white_balance[0]:.2f}, G=1.00, B={self.white_balance[2]:.2f}"
        plt.figtext(0.5, 0.9, wb_text, ha="center", color="green")
        
        # Reload the image with the new white balance
        self.rgb = load_nef_image(self.image_path, self.white_balance)
        self.display_img = normalize_for_display(self.rgb)
        
        # Redraw the image with the new white balance
        self.ax.clear()
        self.ax.imshow(self.display_img)
        self.ax.set_title("Draw ROIs on the image")
        
        # Redraw existing ROIs
        self.draw_existing_rois()
        
        plt.draw()
    
    def reset_white_balance(self, event):
        """Reset white balance to default."""
        if not self.white_balance:
            # No white balance adjustment to reset
            return
        
        # Reset white balance
        self.white_balance = None
        
        # Reload the image without white balance
        self.rgb = load_nef_image(self.image_path)
        self.display_img = normalize_for_display(self.rgb)
        
        # Redraw the image
        self.ax.clear()
        self.ax.imshow(self.display_img)
        self.ax.set_title("Draw ROIs on the image")
        
        # Redraw existing ROIs
        self.draw_existing_rois()
        
        # Show reset message
        plt.figtext(0.5, 0.9, "White balance reset to default", ha="center", color="green")
        
        plt.draw()
    
    def process_rois(self, event):
        """Process all ROIs and export data to CSV."""
        if not self.rois:
            # Create a text display instead of print
            plt.figtext(0.5, 0.9, "No ROIs to process.", ha="center", color="red")
            plt.draw()
            return
        
        # Make sure polygon selector is inactive
        if self.polygon_selector.active:
            self.polygon_selector.set_active(False)
        
        # Remove existing text if any
        for txt in self.fig.texts:
            txt.remove()
            
        # Remove any existing auxiliary axes (like previous textboxes)
        for ax in self.fig.axes[:]:
            if ax != self.ax:
                ax.remove()
            
        plt.figtext(0.5, 0.9, "Enter filename to save CSV data:", ha="center")
        ax_textbox = plt.axes([0.3, 0.85, 0.4, 0.05])
        self.text_box = TextBox(ax_textbox, 'Filename: ', initial='pixel_data.csv')
        self.text_box.on_submit(self.export_data)
        plt.draw()
    
    def export_data(self, filename):
        """Process and export data based on the provided filename."""
        # Remove the textbox from the plot
        if hasattr(self, 'text_box') and self.text_box is not None:
            self.text_box.ax.remove()
            self.text_box = None
        
        # Remove any other auxiliary axes
        for ax in self.fig.axes[:]:
            if ax != self.ax:
                ax.remove()
                
        # Remove any existing text
        for txt in self.fig.texts:
            txt.remove()
                
        # Show processing message
        plt.figtext(0.5, 0.9, "Processing ROIs...", ha="center")
        plt.draw()
        
        # Process each ROI and collect data
        all_data = []
        status_messages = []
        
        for roi in self.rois:
            label = roi["label"]
            polygon = roi["polygon"]
            
            # Extract pixels within the polygon
            roi_data = extract_pixels_from_polygon(self.rgb, polygon, label, self.file_name)
            all_data.extend(roi_data)
            
            status_message = f"Processed ROI: {label} with {len(roi_data) // 3} pixels"
            status_messages.append(status_message)
        
        # Save the data
        save_pixel_data_to_csv(filename, all_data)
        
        # Update status message
        for txt in self.fig.texts:
            txt.remove()
            
        plt.figtext(0.5, 0.9, f"Data saved to {filename}", ha="center", color="green")
        
        # Display processing results
        y_pos = 0.85
        for message in status_messages:
            plt.figtext(0.5, y_pos, message, ha="center", fontsize=9)
            y_pos -= 0.03
            
        plt.draw()
    
    def quit_app(self, event):
        """Exit the application."""
        plt.close(self.fig)
    
    def run(self):
        """Run the ROI Manager interactive session."""
        self.setup_display()
        plt.show()