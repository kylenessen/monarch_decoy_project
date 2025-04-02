#!/usr/bin/env python3

import rawpy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector, PolygonSelector
import pandas as pd
from pathlib import Path
import sys
import time  # For pausing after plot display

# --- Configuration ---
# Consider making these command-line arguments later
INPUT_DIR = Path("images")
OUTPUT_DIR = Path(".")  # Save CSVs in the current directory
IMAGE_SUFFIX = ".NEF"

# --- Helper Functions ---


def select_rectangle(image, title="Select Rectangle"):
    """
    Displays an image and allows the user to select a rectangular region.
    Returns the coordinates (xmin, ymin, xmax, ymax) of the selected rectangle.
    """
    selected_coords = None
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.set_title(title)

    def onselect(eclick, erelease):
        nonlocal selected_coords
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        selected_coords = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        print(f"Selected region: {selected_coords}")
        plt.close(fig)  # Close the figure once selection is done

    # Use RectangleSelector
    rs = RectangleSelector(ax, onselect, useblit=True,
                           button=[1],  # Left mouse button
                           minspanx=5, minspany=5,
                           spancoords='pixels',
                           interactive=True)

    plt.show(block=True)  # Block execution until the plot is closed

    if selected_coords is None:
        print("Warning: No rectangle selected. Exiting.")
        sys.exit(1)  # Or handle this case differently

    return selected_coords


def calculate_wb_multipliers(raw_obj, raw_image_array, wb_coords):
    """
    Calculates white balance multipliers based on the average raw values
    within the specified coordinates (xmin, ymin, xmax, ymax).
    Uses the rawpy object (raw_obj) to access Bayer pattern info.
    Assumes a Bayer pattern (e.g., RGGB).
    """
    xmin, ymin, xmax, ymax = wb_coords
    # Ensure coordinates are within bounds
    xmin = max(0, xmin)
    ymin = max(0, ymin)
    xmax = min(raw_image_array.shape[1], xmax)
    ymax = min(raw_image_array.shape[0], ymax)

    # Extract the raw Bayer data for the selected region
    wb_region = raw_image_array[ymin:ymax, xmin:xmax]

    # Identify pixel locations based on Bayer pattern (e.g., RGGB) using the rawpy object
    # raw_obj.raw_color(y, x) returns 0 (R), 1 (G1), 2 (B), 3 (G2) typically
    # We need to map these indices to the actual channels
    # Let's assume a common pattern like RGGB for calculation
    # raw_colors gives the index (0-3) for each pixel location
    # Note: Use absolute coordinates y, x for raw_color, not relative to wb_region
    raw_colors = np.array([[raw_obj.raw_color(y, x)
                          for x in range(xmin, xmax)] for y in range(ymin, ymax)])

    # Calculate average for each channel index (0, 1, 2, 3) within the wb_region
    averages = [wb_region[raw_colors == i].mean() for i in range(4)]

    # Assuming RGGB: 0=R, 1=G1, 2=B, 3=G2
    # Use the average of the two green channels as the reference
    avg_g = (averages[1] + averages[3]) / 2.0
    if avg_g == 0:  # Avoid division by zero
        print("Warning: Average green channel value is zero in WB area. Using default multipliers.")
        return [1.0, 1.0, 1.0, 1.0]  # R, G1, B, G2

    # Calculate multipliers to scale R and B to match average Green
    # Multipliers are applied to R, G1, B, G2 respectively by rawpy
    multipliers = [
        avg_g / averages[0] if averages[0] != 0 else 1.0,  # R multiplier
        # G1 multiplier (reference)
        1.0,
        avg_g / averages[2] if averages[2] != 0 else 1.0,  # B multiplier
        # G2 multiplier (reference)
        1.0
    ]

    print(f"Calculated WB Multipliers (R, G1, B, G2): {multipliers}")
    return multipliers


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
        label = input("Enter label for this ROI: ")
        if label:
            self.rois.append(
                {'label': label, 'vertices': self.current_vertices})
            print(
                f"ROI '{label}' added. Press 'n' for next ROI or 'q' to quit.")
            # Draw the completed polygon permanently
            poly = plt.Polygon(self.current_vertices,
                               edgecolor='lime', facecolor='none', lw=2)
            self.ax.add_patch(poly)
            self.ax.text(np.mean([v[0] for v in self.current_vertices]),
                         np.mean([v[1] for v in self.current_vertices]),
                         label, color='lime', ha='center', va='center')
            self.ax.figure.canvas.draw_idle()
        else:
            print("Label cannot be empty. Polygon discarded. Press 'n' or 'q'.")
        # Wait for key press ('n' or 'q')

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


def extract_roi_data(image, rois):
    """
    Extracts pixel data (R, G, B) for each defined ROI.
    Returns a list of dictionaries suitable for DataFrame creation.
    """
    all_pixel_data = []
    height, width, _ = image.shape

    # Create a grid of coordinates
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    pixel_coords = np.vstack((x_coords.flatten(), y_coords.flatten())).T

    for roi in rois:
        label = roi['label']
        vertices = roi['vertices']
        print(f"Extracting data for ROI: '{label}'")

        # Create a mask for the current polygon ROI
        path = plt.matplotlib.path.Path(vertices)
        mask = path.contains_points(pixel_coords).reshape(height, width)

        # Get pixel coordinates within the mask
        roi_y_coords, roi_x_coords = np.where(mask)

        # Extract R, G, B values for pixels within the ROI
        r_values = image[roi_y_coords, roi_x_coords, 0]
        g_values = image[roi_y_coords, roi_x_coords, 1]
        b_values = image[roi_y_coords, roi_x_coords, 2]

        # Append data for each channel
        for val in r_values:
            all_pixel_data.append(
                {'Value': val, 'Channel': 'R', 'ROI_Label': label})
        for val in g_values:
            all_pixel_data.append(
                {'Value': val, 'Channel': 'G', 'ROI_Label': label})
        for val in b_values:
            all_pixel_data.append(
                {'Value': val, 'Channel': 'B', 'ROI_Label': label})

    return all_pixel_data


# --- Main Processing Logic ---

def process_image(nef_path, output_dir):
    """
    Processes a single NEF image: WB, ROI selection, data extraction, CSV saving.
    """
    print(f"\n--- Processing: {nef_path.name} ---")
    image_source = nef_path.stem  # e.g., 'VIS', 'UV', 'NIR'
    output_csv_path = output_dir / f"{image_source}.csv"

    try:
        # 1. Load NEF Image (raw data)
        with rawpy.imread(str(nef_path)) as raw:
            raw_image = raw.raw_image_visible.copy()  # Get the raw Bayer data

            # Display a simple preview for WB selection (might be dark/weird colors)
            # Postprocess with default settings for a quick preview
            try:
                preview_rgb = raw.postprocess(use_camera_wb=True, output_bps=8)
            except Exception as e:
                print(
                    f"Warning: Could not generate initial preview ({e}). Using raw data for WB selection.")
                # Normalize raw data for display if preview fails
                preview_rgb = (raw_image / raw_image.max()
                               * 255).astype(np.uint8)
                if len(preview_rgb.shape) == 2:  # If grayscale, make it 3-channel for imshow
                    preview_rgb = np.stack([preview_rgb]*3, axis=-1)

            # 2. Select White Balance Reference
            print("Select the Teflon white balance card region.")
            wb_coords = select_rectangle(
                preview_rgb, title=f"Select WB Area - {image_source}")

            # 3. Calculate Custom White Balance Multipliers
            # Pass the rawpy object 'raw' and the numpy array 'raw_image'
            wb_mults = calculate_wb_multipliers(raw, raw_image, wb_coords)

            # 4. Process Image with Custom WB
            print("Processing image with custom white balance...")
            # Use 16-bit output for precision, no auto-brightness, custom WB
            processed_image_16bit = raw.postprocess(
                use_camera_wb=False,      # Don't use camera WB
                user_wb=wb_mults,         # Use our calculated multipliers
                output_bps=16,            # Output 16-bit
                no_auto_bright=True,      # Keep linear brightness
                demosaic_algorithm=rawpy.DemosaicAlgorithm.AAHD  # Choose a good algorithm
                # Add other rawpy params as needed, e.g., gamma, exposure
            )
            print(
                f"Processed image shape: {processed_image_16bit.shape}, dtype: {processed_image_16bit.dtype}")

            # 5. Define Regions of Interest (ROIs)
            # Display the processed 16-bit image (normalize for display)
            display_image = (processed_image_16bit /
                             processed_image_16bit.max() * 255).astype(np.uint8)
            fig_roi, ax_roi = plt.subplots()
            ax_roi.imshow(display_image)
            ax_roi.set_title(
                f"Define ROIs - {image_source} (Press 'n' for next, 'q' to finish)")
            roi_selector = ROISelector(ax_roi, processed_image_16bit.shape)
            # Keep plot open until 'q' is pressed in ROISelector
            plt.show(block=True)

            rois = roi_selector.get_rois()
            if not rois:
                print("No ROIs defined. Skipping data extraction for this image.")
                return

            # 6. Extract Pixel Data
            print("Extracting pixel data from ROIs...")
            pixel_data = extract_roi_data(processed_image_16bit, rois)

            if not pixel_data:
                print("No pixel data extracted. Skipping CSV generation.")
                return

            # 7. Format Data for CSV
            df = pd.DataFrame(pixel_data)
            df['Image_Source'] = image_source  # Add the image source column

            # Reorder columns
            df = df[['Value', 'Channel', 'Image_Source', 'ROI_Label']]

            # 8. Save to CSV
            print(f"Saving data to {output_csv_path}...")
            df.to_csv(output_csv_path, index=False)
            print(f"Successfully saved {len(df)} rows to {output_csv_path}")

    except rawpy.LibRawFileUnsupportedError:
        print(f"Error: File format not supported by LibRaw/rawpy: {nef_path}")
    except FileNotFoundError:
        print(f"Error: Input file not found: {nef_path}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {nef_path}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Find NEF files in the input directory
    nef_files = sorted(list(INPUT_DIR.glob(f"*{IMAGE_SUFFIX}")))

    if not nef_files:
        print(
            f"Error: No '{IMAGE_SUFFIX}' files found in directory '{INPUT_DIR}'.")
        sys.exit(1)

    print(f"Found images to process: {[f.name for f in nef_files]}")

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Process each image
    for nef_file in nef_files:
        process_image(nef_file, OUTPUT_DIR)

    print("\n--- Processing Complete ---")
