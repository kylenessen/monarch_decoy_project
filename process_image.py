#!/usr/bin/env python3

# import rawpy # No longer needed
from PIL import Image  # Use Pillow for JPEG loading
import numpy as np
import matplotlib.pyplot as plt
# from matplotlib.widgets import RectangleSelector # No longer needed for WB
from matplotlib.widgets import PolygonSelector
import pandas as pd
from pathlib import Path
import sys
import time  # For pausing after plot display
# Consider adding scikit-image if matplotlib.path is insufficient for masking complex polygons
# from skimage import draw # Example if needed

# --- Configuration ---
# INPUT_DIR = Path("images") # Input path now comes from command line
OUTPUT_DIR = Path(".")  # Save CSVs in the current directory
# IMAGE_SUFFIX = ".NEF" # Changed to specific JPEGs
# TARGET_IMAGES = ["VIS.jpg", "UV.jpg"] # Process only one image specified by arg

# --- Helper Functions ---
# White balance functions (select_rectangle, calculate_wb_multipliers) removed


class ROISelector:
    """
    Allows interactive selection of multiple polygonal ROIs on an image.
    Stores vertices and prompts for labels.
    """

    def __init__(self, ax, image_shape):
        self.ax = ax
        self.image_shape = image_shape
        self.rois = []  # List to store {'label': str, 'vertices': list}
        self.current_vertices = []
        self.selector = PolygonSelector(ax, self.onselect)
        print("\n--- Define ROIs ---")
        print("Left-click to add vertices, right-click to finalize polygon.")
        print("Press 'n' for next ROI after labeling, 'q' to quit ROI selection.")
        self.cid = ax.figure.canvas.mpl_connect('key_press_event', self.on_key)
        self.drawing = True

    def onselect(self, vertices):
        self.current_vertices = vertices
        self.selector.disconnect_events()  # Temporarily disable selector
        self.ax.figure.canvas.draw_idle()  # Update plot
        print(f"Polygon finalized with {len(vertices)} vertices.")
        self.prompt_for_label()

    def prompt_for_label(self):
        while True:  # Loop until a non-empty label is given
            label = input("Enter label for this ROI (cannot be empty): ")
            if label:
                self.rois.append(
                    {'label': label, 'vertices': self.current_vertices})
                print(
                    f"ROI '{label}' added. Press 'n' for next ROI or 'q' to quit.")
                break  # Exit loop on valid label
            else:
                print("Label cannot be empty. Please provide a label.")

        # Draw the completed polygon permanently after getting a valid label
        poly = plt.Polygon(self.current_vertices,
                           edgecolor='lime', facecolor='none', lw=2)
        self.ax.add_patch(poly)
        self.ax.text(np.mean([v[0] for v in self.current_vertices]),
                     np.mean([v[1] for v in self.current_vertices]),
                     label, color='lime', ha='center', va='center')
        self.ax.figure.canvas.draw_idle()
        # Wait for key press ('n' or 'q') in on_key

    def on_key(self, event):
        if event.key == 'n':
            print("Ready for next ROI. Draw polygon...")
            self.current_vertices = []
            # Reconnect the selector for the next polygon
            self.selector = PolygonSelector(self.ax, self.onselect)
        elif event.key == 'q':
            print("Finished defining ROIs.")
            self.drawing = False
            self.selector.disconnect_events()
            self.ax.figure.canvas.mpl_disconnect(self.cid)
            # Give a moment for the user to see the final plot before closing
            plt.pause(1.5)
            plt.close(self.ax.figure)

    def get_rois(self):
        return self.rois


def extract_roi_data(image_array, rois, image_source):
    """
    Extracts pixel data for specified channels (G/B for VIS, B for UV)
    for each defined ROI from an 8-bit image array.
    Returns a list of dictionaries suitable for DataFrame creation.
    """
    all_pixel_data = []
    height, width, _ = image_array.shape

    # Create a grid of coordinates
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    pixel_coords = np.vstack((x_coords.flatten(), y_coords.flatten())).T

    for roi in rois:
        label = roi['label']
        vertices = roi['vertices']
        print(f"Extracting data for ROI: '{label}' ({image_source})")

        # Create a mask for the current polygon ROI using matplotlib.path
        path = plt.matplotlib.path.Path(vertices)
        mask = path.contains_points(pixel_coords).reshape(height, width)

        # Alternative using scikit-image (if needed):
        # rr, cc = draw.polygon(np.array([v[1] for v in vertices]),
        #                       np.array([v[0] for v in vertices]),
        #                       shape=image_array.shape[:2])
        # mask = np.zeros(image_array.shape[:2], dtype=bool)
        # mask[rr, cc] = True

        # Get pixel coordinates within the mask
        roi_y_coords, roi_x_coords = np.where(mask)

        # Extract channel values based on image_source
        if image_source == 'VIS':
            # Extract G (index 1) and B (index 2)
            g_values = image_array[roi_y_coords, roi_x_coords, 1]
            b_values = image_array[roi_y_coords, roi_x_coords, 2]
            for val in g_values:
                all_pixel_data.append(
                    {'Value': val, 'Channel': 'G', 'ROI_Label': label})
            for val in b_values:
                all_pixel_data.append(
                    {'Value': val, 'Channel': 'B', 'ROI_Label': label})
        elif image_source == 'UV':
            # Extract B (index 2) only
            b_values = image_array[roi_y_coords, roi_x_coords, 2]
            for val in b_values:
                all_pixel_data.append(
                    {'Value': val, 'Channel': 'B', 'ROI_Label': label})
        # NIR is ignored based on requirements

    return all_pixel_data


# --- Main Processing Logic ---

def process_image(image_path, output_dir):
    """
    Processes a single JPEG image: ROI selection, data extraction, CSV saving.
    """
    print(f"\n--- Processing: {image_path.name} ---")
    image_source = image_path.stem  # e.g., 'VIS', 'UV'
    output_csv_path = output_dir / f"{image_source}.csv"

    try:
        # 1. Load JPEG Image
        with Image.open(image_path) as img:
            # Ensure image is in RGB format if it's grayscale or has alpha
            img_rgb = img.convert("RGB")
            image_array = np.array(img_rgb)  # Convert to numpy array (0-255)

        print(
            f"Loaded image shape: {image_array.shape}, dtype: {image_array.dtype}")

        # Steps 2, 3, 4 (WB related) are removed

        # 5. Define Regions of Interest (ROIs)
        # Display the loaded 8-bit JPEG image directly
        fig_roi, ax_roi = plt.subplots()
        ax_roi.imshow(image_array)
        ax_roi.set_title(
            f"Define ROIs - {image_source} (Press 'n' for next, 'q' to finish)")
        roi_selector = ROISelector(ax_roi, image_array.shape)

        # Display the plot but manage the event loop manually
        plt.show(block=False)

        # Keep the script running and processing GUI events until 'q' is pressed
        # The roi_selector.drawing flag is set to False in the on_key('q') method
        print("Waiting for ROI selection ('n'/'q' keys in plot window)...")
        while roi_selector.drawing:
            # Pause allows the GUI to remain responsive and process events
            plt.pause(0.1)
        print("ROI selection finished.")  # Add confirmation

        # Now that the loop is finished (because 'q' was pressed), get the ROIs
        rois = roi_selector.get_rois()
        if not rois:
            print("No ROIs defined. Skipping data extraction for this image.")
            return

        # 6. Extract Pixel Data (using the new function signature)
        print("Extracting pixel data from ROIs...")
        pixel_data = extract_roi_data(image_array, rois, image_source)

        if not pixel_data:
            print(
                "No pixel data extracted (check ROIs and channel logic). Skipping CSV generation.")
            return

        # 7. Format Data for CSV
        df = pd.DataFrame(pixel_data)
        df['Image_Source'] = image_source  # Add the image source column

        # Reorder columns to match desired output
        df = df[['Value', 'Channel', 'Image_Source', 'ROI_Label']]

        # 8. Save to CSV
        print(f"Saving data to {output_csv_path}...")
        df.to_csv(output_csv_path, index=False)
        print(f"Successfully saved {len(df)} rows to {output_csv_path}")

    # except rawpy.LibRawFileUnsupportedError: # Remove rawpy exception
    #     print(f"Error: File format not supported by LibRaw/rawpy: {image_path}")
    except FileNotFoundError:
        print(f"Error: Input file not found: {image_path}")
    except Exception as e:
        print(
            f"An unexpected error occurred while processing {image_path}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_image.py <path_to_image.jpg>")
        print("Example: python process_image.py images/VIS.jpg")
        sys.exit(1)

    image_path_arg = sys.argv[1]
    image_file = Path(image_path_arg)

    if not image_file.is_file():
        print(f"Error: Image file not found at '{image_path_arg}'")
        sys.exit(1)

    # Validate supported image types if needed (e.g., check suffix)
    if image_file.suffix.lower() not in ['.jpg', '.jpeg']:
        print(
            f"Error: Only JPEG files (.jpg, .jpeg) are supported. Found: {image_file.suffix}")
        sys.exit(1)

    print(f"Processing image: {image_file.name}")

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process the single specified image
    process_image(image_file, OUTPUT_DIR)

    print(f"\n--- Processing Complete for {image_file.name} ---")
