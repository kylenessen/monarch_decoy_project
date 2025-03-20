# NEF ROI Extractor

A Python tool for extracting pixel data from Regions of Interest (ROIs) in Nikon RAW (.NEF) files.

## Features

- Open and process Nikon RAW (.NEF) files
- Interactive white balance adjustment with eyedropper tool
- Draw multiple polygon ROIs on the image
- Label each ROI
- Save and reload ROI definitions as JSON
- Extract pixel data from each ROI
- Export pixel data to CSV with columns: file_name, roi_label, channel, x, y, pixel_value

## Requirements

- Python 3.6+
- rawpy
- matplotlib
- numpy
- pandas

## Installation

```bash
# Activate the virtual environment first
source activate.sh

# Or use pip to install dependencies
pip install rawpy matplotlib numpy pandas
```

## Usage

### Basic Usage

```bash
python run.py images/YOUR_IMAGE.NEF
```

### Load Existing ROIs

```bash
python run.py images/YOUR_IMAGE.NEF --load rois.json
```

### Specify White Balance

```bash
python run.py images/YOUR_IMAGE.NEF --white-balance 1.2,1.0,0.8
```

### Interactive Controls

1. Click "White Balance" to use the eyedropper tool on a neutral gray/white area
2. Click "New ROI" to start drawing a polygon
3. Click on the image to add points to your polygon
4. Close the polygon by clicking near the first point
5. Enter a label for the ROI when prompted
6. Repeat for additional ROIs
7. Click "Save ROIs" to save your ROI definitions to a JSON file
8. Click "Process" to extract pixel data and save to CSV
9. Click "Reset WB" to remove white balance adjustments
10. Click "Quit" to exit the application

## White Balance

The white balance feature allows you to correct color casts in your NEF images:

- **Interactive**: Use the "White Balance" button and eyedropper tool to select a neutral gray or white area
- **Command Line**: Specify white balance multipliers with `--white-balance r,g,b`
- **Reset**: Click "Reset WB" to revert to the original image colors

## Output Format

The CSV output contains one row per pixel channel with the following columns:
- file_name: The name of the .NEF file
- roi_label: The user-provided label for the ROI
- channel: "R", "G", or "B"
- x: X coordinate of the pixel
- y: Y coordinate of the pixel
- pixel_value: Intensity value of the pixel in that channel

## Notes

- By default, the tool demosaics the RAW image without applying white balance, auto-brightening, or other color corrections
- Use the white balance eyedropper on a neutral gray or white area to get accurate colors
- The image is displayed with normalized values for better visibility but original pixel values are preserved in the output
- For large images or ROIs, processing may take some time