#!/usr/bin/env python3
"""
NEF ROI Extractor

This script allows users to open Nikon RAW (.NEF) files, draw multiple ROIs as polygons,
extract pixel data for each ROI, and save the results to CSV files.

Requirements:
- rawpy
- matplotlib
- numpy
- pandas
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import rawpy
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.widgets import PolygonSelector, Button
from matplotlib.patches import Polygon


class ROIManager:
    """Handles the drawing, storing, and processing of ROIs."""

    def __init__(self, image_path: str, load_roi_path: Optional[str] = None):
        """
        Initialize the ROI Manager with an image.
        
        Args:
            image_path: Path to the NEF file
            load_roi_path: Optional path to a JSON file with existing ROIs
        """
        self.image_path = image_path
        self.file_name = os.path.basename(image_path)
        
        # Open and process the RAW image
        with rawpy.imread(image_path) as raw:
            # Demosaic without white balance, auto-brightening, etc.
            self.rgb = raw.postprocess(
                no_auto_bright=True,
                output_bps=16,
                use_camera_wb=False,
                gamma=(1, 1)
            )
        
        # Normalize the image for display
        self.display_img = self.rgb.astype(np.float32)
        self.display_img = self.display_img / self.display_img.max()
        
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
        ax_new_roi = plt.axes([0.1, 0.05, 0.15, 0.05])
        ax_save_rois = plt.axes([0.3, 0.05, 0.15, 0.05])
        ax_process = plt.axes([0.5, 0.05, 0.15, 0.05])
        ax_quit = plt.axes([0.7, 0.05, 0.15, 0.05])
        
        self.btn_new_roi = Button(ax_new_roi, 'New ROI')
        self.btn_save_rois = Button(ax_save_rois, 'Save ROIs')
        self.btn_process = Button(ax_process, 'Process & Export')
        self.btn_quit = Button(ax_quit, 'Quit')
        
        self.btn_new_roi.on_clicked(self.start_new_roi)
        self.btn_save_rois.on_clicked(self.save_rois_dialog)
        self.btn_process.on_clicked(self.process_rois)
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
        
        # Create a dialog for label input using matplotlib's built-in dialog
        from matplotlib.widgets import TextBox
        
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
        centroid = np.mean(self.current_vertices, axis=0)
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
            centroid = np.mean(vertices, axis=0)
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
        
        # Create a file input dialog
        from matplotlib.widgets import TextBox
        
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
        
        data = {
            "file_name": self.file_name,
            "rois": self.rois
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Show success message
            plt.figtext(0.5, 0.9, f"ROIs saved to {filename}", ha="center", color="green")
        except Exception as e:
            # Show error message
            plt.figtext(0.5, 0.9, f"Error saving ROIs: {str(e)}", ha="center", color="red")
        
        plt.draw()
    
    def load_rois(self, filename: str):
        """Load ROIs from a JSON file."""
        # This method is primarily called from the command line, but we'll 
        # provide visual feedback if the display is already setup
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Check if the JSON is for the same file
            if data.get("file_name") != self.file_name:
                warning_msg = f"Warning: Loading ROIs from a different file: {data.get('file_name')}"
                print(warning_msg)  # For command line feedback
                
                # If display is setup, show warning in GUI
                if hasattr(self, 'fig') and self.fig is not None:
                    plt.figtext(0.5, 0.95, warning_msg, ha="center", color="orange")
            
            self.rois = data.get("rois", [])
            success_msg = f"Loaded {len(self.rois)} ROIs from {filename}"
            print(success_msg)  # For command line feedback
            
            # If display is setup, show success in GUI
            if hasattr(self, 'fig') and self.fig is not None:
                plt.figtext(0.5, 0.9, success_msg, ha="center", color="green")
                plt.draw()
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            error_msg = f"Error loading ROIs: {e}"
            print(error_msg)  # For command line feedback
            
            # If display is setup, show error in GUI
            if hasattr(self, 'fig') and self.fig is not None:
                plt.figtext(0.5, 0.9, error_msg, ha="center", color="red")
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
        
        # Create a file input dialog
        from matplotlib.widgets import TextBox
        
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
        
        height, width, channels = self.rgb.shape
        for roi in self.rois:
            label = roi["label"]
            polygon = np.array(roi["polygon"])
            
            # Create a Path object for the polygon
            p = Path(polygon)
            
            # Create a grid of all pixel coordinates
            y, x = np.mgrid[:height, :width]
            points = np.vstack((x.ravel(), y.ravel())).T
            
            # Find which points are inside the polygon
            mask = p.contains_points(points)
            points_inside = points[mask]
            
            # Process all pixels inside the polygon
            for x, y in points_inside:
                for c in range(channels):
                    channel_name = "RGB"[c]
                    pixel_value = self.rgb[int(y), int(x), c]
                    
                    all_data.append({
                        "file_name": self.file_name,
                        "roi_label": label,
                        "channel": channel_name,
                        "x": int(x),
                        "y": int(y),
                        "pixel_value": int(pixel_value)
                    })
            
            status_message = f"Processed ROI: {label} with {len(points_inside)} pixels"
            status_messages.append(status_message)
        
        # Create and save DataFrame
        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        
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


def main():
    """Parse arguments and run the application."""
    parser = argparse.ArgumentParser(description="NEF ROI Extractor")
    parser.add_argument("image_path", help="Path to NEF file")
    parser.add_argument("--load", "-l", help="Load ROIs from JSON file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return 1
    
    manager = ROIManager(args.image_path, args.load)
    manager.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())