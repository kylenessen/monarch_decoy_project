"""
Command-line interface for NEF ROI Extractor.
"""

import os
import sys
import argparse
from .roi_manager import ROIManager


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