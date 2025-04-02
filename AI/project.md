# Project Description

## Development Plan (Revised for Pre-White-Balanced JPEGs and Butterfly Vision Channels)

The project will be implemented as a Python script (`process_image.py`) that processes pre-white-balanced JPEG images (VIS and UV) individually. The script focuses on extracting channels relevant to butterfly vision (Green/Blue for VIS, Blue for UV). The NIR image is assumed to be excluded from this analysis phase.

The script will perform the following steps for each relevant input image (VIS.jpg, UV.jpg):

1.  **Load JPEG Image:** Use a library like `Pillow` or `opencv-python` to load the input JPEG file (e.g., `VIS.jpg` or `UV.jpg`). Store the image data in a `numpy` array.
2.  **Define Regions of Interest (ROIs):** Display the loaded JPEG image using `matplotlib`. Provide an interactive tool (e.g., `matplotlib.widgets.PolygonSelector`) allowing the user to draw multiple irregular polygonal ROIs over different areas of interest (e.g., monarch wing sections, filament samples). After drawing each polygon, prompt the user to enter a descriptive text label for that ROI (e.g., "Monarch Orange", "PLA Black", "PETG White"). Store the polygon coordinates and their corresponding labels.
3.  **Extract Pixel Data:** For each defined ROI:
    *   Create a mask based on the ROI polygon coordinates using functions from libraries like `skimage.draw` or `opencv-python`.
    *   Iterate through all pixels within the image that fall inside the mask.
    *   For each pixel inside the ROI:
        *   If the `Image_Source` is 'VIS', extract the Green (G) and Blue (B) channel values (0-255).
        *   If the `Image_Source` is 'UV', extract the Blue (B) channel value (0-255).
4.  **Format Data for CSV:** Structure the extracted pixel data into a long format. Each row in the final CSV will represent a single relevant color channel value for a single pixel within an ROI. The columns will be:
    *   `Value`: The numerical pixel brightness value (0-255).
    *   `Channel`: The color channel ('G' or 'B').
    *   `Image_Source`: The origin image identifier ('VIS' or 'UV', derived from the input filename).
    *   `ROI_Label`: The user-defined label for the ROI the pixel belongs to.
5.  **Save to CSV:** Collect all the formatted rows for the current image and save them into a CSV file named after the image source (e.g., `VIS.csv`, `UV.csv`) using the `pandas` library.

**Libraries:** The primary Python libraries suggested are `Pillow` (or `opencv-python`), `numpy`, `matplotlib`, `pandas`, and potentially `scikit-image` for polygon masking.
