# NEF ROI Extractor

A Python tool for extracting pixel data from Regions of Interest (ROIs) in Nikon RAW (.NEF) files.

## Features

- Open and process Nikon RAW (.NEF) files
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
pip install rawpy matplotlib numpy pandas
```

## Usage

### Basic Usage

```bash
python nef_roi_extractor.py images/YOUR_IMAGE.NEF
```

### Load Existing ROIs

```bash
python nef_roi_extractor.py images/YOUR_IMAGE.NEF --load rois.json
```

### Interactive Controls

1. Click "New ROI" to start drawing a polygon
2. Click on the image to add points to your polygon
3. Close the polygon by clicking near the first point
4. Enter a label for the ROI when prompted
5. Repeat for additional ROIs
6. Click "Save ROIs" to save your ROI definitions to a JSON file
7. Click "Process & Export" to extract pixel data and save to CSV
8. Click "Quit" to exit the application

## Output Format

The CSV output contains one row per pixel channel with the following columns:
- file_name: The name of the .NEF file
- roi_label: The user-provided label for the ROI
- channel: "R", "G", or "B"
- x: X coordinate of the pixel
- y: Y coordinate of the pixel
- pixel_value: Intensity value of the pixel in that channel

## Notes

- The tool demosaics the RAW image without applying white balance, auto-brightening, or other color corrections
- The image is displayed with normalized values for better visibility but original pixel values are preserved in the output
- For large images or ROIs, processing may take some time