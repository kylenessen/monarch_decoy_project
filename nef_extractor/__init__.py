"""
NEF ROI Extractor package

This package allows users to open Nikon RAW (.NEF) files, draw multiple ROIs as polygons,
extract pixel data for each ROI, and save the results to CSV files.
"""

from .roi_manager import ROIManager
from .cli import main

__version__ = "0.1.0"