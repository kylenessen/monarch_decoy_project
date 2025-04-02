# User Guide: process_image.py

This guide explains how to use the `process_image.py` script to extract specific color channel data from Regions of Interest (ROIs) in VIS and UV JPEG images.

## Purpose

The script processes pre-white-balanced `VIS.jpg` and `UV.jpg` files located in the `images/` directory. It allows you to interactively define polygonal ROIs on each image and extracts pixel data for specific color channels relevant to butterfly vision:
*   **VIS Image:** Extracts Green (G) and Blue (B) channel values (0-255).
*   **UV Image:** Extracts Blue (B) channel values (0-255).

The extracted data for each image is saved into separate CSV files (`VIS.csv`, `UV.csv`) in the main project directory.

## Prerequisites

1.  **Python 3:** Ensure you have Python 3 installed.
2.  **Required Libraries:** Install the necessary Python libraries using pip:
    ```bash
    pip install Pillow numpy matplotlib pandas
    ```
    (If you are using a virtual environment, make sure it's activated before running pip).
3.  **Image Files:** Make sure `VIS.jpg` and `UV.jpg` exist in the `images/` subdirectory relative to where you run the script.

## How to Run

1.  Open your terminal or command prompt.
2.  Navigate to the project directory (`monarch_decoy_project`).
3.  If using a virtual environment, activate it (e.g., `source venv/bin/activate` on macOS/Linux).
4.  Run the script using Python, providing the path to the specific JPEG image you want to process as a command-line argument:
    ```bash
    python process_image.py <path_to_image.jpg>
    ```
    **Examples:**
    ```bash
    # Process the VIS image
    python process_image.py images/VIS.jpg

    # Process the UV image
    python process_image.py images/UV.jpg
    ```

## Interactive ROI Selection

When you run the script with an image path, a window will pop up displaying that specific image:

1.  **Drawing a Polygon:**
    *   **Left-click** on the image to place the vertices (corners) of your desired ROI polygon.
    *   You can add as many vertices as needed to outline the shape accurately.
    *   **Right-click** anywhere on the image to finalize the current polygon.

2.  **Labeling the ROI:**
    *   After you right-click to finalize the polygon, look back at your **terminal**.
    *   You will be prompted: `Enter label for this ROI (cannot be empty):`
    *   Type a descriptive name for the region you just outlined (e.g., "Monarch Orange Wing", "PLA Black Sample", "Teflon Card") and press **Enter**. The label cannot be empty.
    *   The polygon will be drawn on the image window with its label.

3.  **Defining More ROIs:**
    *   After labeling, the terminal will show: `ROI '<your_label>' added. Press 'n' for next ROI or 'q' to quit.`
    *   Make sure the **image window** is the active window (click on it if necessary).
    *   Press the **'n' key** on your keyboard to start drawing the *next* ROI on the *same* image. Repeat steps 1 and 2.

4.  **Finishing an Image:**
    *   Once you have defined all the ROIs you need for the *current* image (e.g., VIS.jpg), make sure the **image window** is active.
    *   Press the **'q' key** on your keyboard.
    *   The terminal will show `Finished defining ROIs.` and the image window will close after a short pause.
    *   The script will then proceed to extract data for the ROIs you defined for that image and save it to the corresponding CSV file (e.g., `VIS.csv` or `UV.csv`).

5.  **Processing Another Image:**
    *   To process a different image (e.g., if you just processed `VIS.jpg` and now want to process `UV.jpg`), you need to run the script again from the terminal, providing the path to the other image file.

6.  **Completion:**
    *   After you press 'q' for the image, the script will finish processing that single file and print `--- Processing Complete for <image_name> ---` in the terminal.

## Output Files

The script generates the following files in the main project directory:

*   **`VIS.csv`:** Contains pixel data from the ROIs defined on `VIS.jpg`. Columns:
    *   `Value`: Pixel brightness (0-255).
    *   `Channel`: 'G' or 'B'.
    *   `Image_Source`: 'VIS'.
    *   `ROI_Label`: The label you provided for the ROI.
*   **`UV.csv`:** Contains pixel data from the ROIs defined on `UV.jpg`. Columns:
    *   `Value`: Pixel brightness (0-255).
    *   `Channel`: 'B'.
    *   `Image_Source`: 'UV'.
    *   `ROI_Label`: The label you provided for the ROI.

Each row represents a single channel value for a single pixel within a defined ROI.
