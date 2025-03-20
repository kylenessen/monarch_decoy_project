"""
Command-line interface for NEF ROI Extractor.
"""

import os
import sys
import argparse
from typing import Optional, Tuple
from .roi_manager import ROIManager


def parse_white_balance(wb_str: Optional[str]) -> Optional[Tuple[float, float, float]]:
    """
    Parse a white balance string into RGB multipliers.
    
    Args:
        wb_str: String in format "r,g,b" where r, g, b are float values
        
    Returns:
        Tuple of (red_mult, green_mult, blue_mult) or None if invalid
    """
    if not wb_str:
        return None
        
    try:
        # Split and convert to floats
        r, g, b = map(float, wb_str.split(","))
        
        # Normalize to green = 1.0
        if g == 0:
            return None
            
        r_norm = r / g
        b_norm = b / g
        
        return (r_norm, 1.0, b_norm)
    except ValueError:
        print("Error: White balance must be in format 'r,g,b' with decimal values")
        return None


def main():
    """Parse arguments and run the application."""
    parser = argparse.ArgumentParser(description="NEF ROI Extractor")
    parser.add_argument("image_path", help="Path to NEF file")
    parser.add_argument("--load", "-l", help="Load ROIs from JSON file")
    parser.add_argument("--white-balance", "-wb", 
                        help="Apply white balance in format 'r,g,b' (e.g. '1.2,1.0,0.8')")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file not found: {args.image_path}")
        return 1
    
    # Parse white balance if provided
    white_balance = parse_white_balance(args.white_balance)
    
    # Create the manager with the parsed white balance
    manager = ROIManager(args.image_path, args.load, white_balance)
    
    manager.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())