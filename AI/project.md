# Project Description

## Prompt

I would like your help developing a python script to extract pixel values out of three images. The purpose of this project is to see if different 3D printed materials sufficiently mimic the spectral properties of a monarch butterfly. I have taken a photo of different filaments along with a sample monarch under visible, UV, and NIR conditions. The images are currently in Nikon raw format (NEF). I need to set the white balance with an included teflon card in the image. Unfortunately, I cannot do this using traditional software (e.g. Photoshop) as the UV and NIR are so far out of the normal range that I cannot set it correctly. 

The project should do a few things:

1. Set the white balance for each image. We can than save each image as a jpeg to further process. This can be done as its own script. It's important that we are not constrained by a typical white balance range. Ideally, if I understand white balance correctly, the channels should be approximately equal. 
2. Define regions of interest within each photo. Each region should be freely drawn using a polygon tool. It should allow for irregular shapes, such as those found on the monarch. I should also be able to label each ROI so I can classify the values it produces for later analysis (e.g., black PLA vs black part of the monarch wing).
3. Once ROIs are established, extract pixel values per channel in each ROI. I want each pixel value to have its own row. So for example, a single pixel should have a brightness value (0-255), a channel (e.g., Red), the image it came from (e.g., UV), and the ROI (e.g., PLA black). I realize this will create a lot of rows, but that is fine. I want maximize flexibility when doing the analysis. This data should be saved to a csv. OK, to create a CSV per file, as there are relatively few. 

I believe that's it for the extract side of things. I want to do everything in python. Do you have any questions for me?

## Development Plan

The project will be implemented as a single Python script (`process_image.py`) that processes each NEF image (VIS, UV, NIR) individually. The script will perform the following steps for each input image:

1.  **Load NEF Image:** Use the `rawpy` library to load the raw sensor data from the input NEF file.
2.  **Select White Balance Reference:** Display a preview of the raw image using `matplotlib`. Allow the user to interactively select a rectangular region corresponding to the Teflon white balance card.
3.  **Calculate Custom White Balance:** Extract the raw pixel data (from the Bayer pattern) within the selected Teflon region. Calculate the average value for each color channel (e.g., R, G1, B, G2) within this region. Determine the necessary multipliers to make these average channel values approximately equal, establishing the custom white balance for the specific lighting condition (VIS, UV, or NIR).
4.  **Process Image:** Use `rawpy` to process the raw image data. This involves:
    *   Applying the custom white balance multipliers calculated in the previous step.
    *   Performing demosaicing to convert the Bayer pattern data into a full RGB image.
    *   Outputting the result as a high bit-depth RGB image (e.g., 16-bit per channel) stored in a `numpy` array. This avoids loss of precision associated with saving to 8-bit formats like JPEG.
5.  **Define Regions of Interest (ROIs):** Display the processed, white-balanced, high bit-depth image using `matplotlib`. Provide an interactive tool (e.g., `PolygonSelector`) allowing the user to draw multiple irregular polygonal ROIs over different areas of interest (e.g., monarch wing sections, filament samples). After drawing each polygon, prompt the user to enter a descriptive text label for that ROI (e.g., "Monarch Orange", "PLA Black", "PETG White"). Store the polygon coordinates and their corresponding labels.
6.  **Extract Pixel Data:** For each defined ROI:
    *   Create a mask based on the ROI polygon coordinates.
    *   Iterate through all pixels within the image that fall inside the mask.
    *   For each pixel inside the ROI, retrieve its high bit-depth R, G, and B values from the processed `numpy` array.
7.  **Format Data for CSV:** Structure the extracted pixel data into a long format suitable for analysis. Each row in the final CSV will represent a single color channel value for a single pixel within an ROI. The columns will be:
    *   `Value`: The numerical pixel brightness value (high bit-depth).
    *   `Channel`: The color channel ('R', 'G', or 'B').
    *   `Image_Source`: The origin image identifier ('VIS', 'UV', or 'NIR', derived from the input filename).
    *   `ROI_Label`: The user-defined label for the ROI the pixel belongs to.
8.  **Save to CSV:** Collect all the formatted rows for the current image and save them into a CSV file named after the image source (e.g., `VIS.csv`, `UV.csv`, `NIR.csv`) using the `pandas` library.

**Libraries:** The primary Python libraries to be used are `rawpy`, `numpy`, `matplotlib`, and `pandas`.
