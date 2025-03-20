"""
Image processing module for NEF files.
"""

import numpy as np
import rawpy
from typing import Tuple, Optional


def load_nef_image(image_path: str, user_wb: Optional[Tuple[float, float, float]] = None) -> np.ndarray:
    """
    Load and process a NEF image file.
    
    Args:
        image_path: Path to the NEF file
        user_wb: Optional tuple of (red_mult, green_mult, blue_mult) for white balance
        
    Returns:
        np.ndarray: Processed RGB image data
    """
    with rawpy.imread(image_path) as raw:
        # Use user-defined white balance if provided
        if user_wb:
            # Apply user-defined white balance multipliers
            wb_multipliers = [user_wb[0], user_wb[1], user_wb[1], user_wb[2]]  # RGBG pattern
            rgb = raw.postprocess(
                no_auto_bright=True,
                output_bps=16,
                use_camera_wb=False,
                user_wb=wb_multipliers,
                gamma=(1, 1)
            )
        else:
            # Demosaic without white balance, auto-brightening, etc.
            rgb = raw.postprocess(
                no_auto_bright=True,
                output_bps=16,
                use_camera_wb=False,
                gamma=(1, 1)
            )
    
    return rgb


def normalize_for_display(image: np.ndarray) -> np.ndarray:
    """
    Normalize image for display.
    
    Args:
        image: Raw image data
        
    Returns:
        np.ndarray: Normalized image for display
    """
    display_img = image.astype(np.float32)
    display_img = display_img / display_img.max()
    
    return display_img


def calculate_white_balance(image: np.ndarray, x: int, y: int, sample_size: int = 5) -> Tuple[float, float, float]:
    """
    Calculate white balance multipliers from a reference white point.
    
    Args:
        image: RGB image data
        x: X-coordinate of the reference white point
        y: Y-coordinate of the reference white point
        sample_size: Size of the sample area around the point (default 5x5 pixels)
        
    Returns:
        Tuple of (red_mult, green_mult, blue_mult) white balance multipliers
    """
    # Get dimensions of the image
    height, width, _ = image.shape
    
    # Calculate the bounds of the sampling area
    half_size = sample_size // 2
    x_start = max(0, x - half_size)
    x_end = min(width, x + half_size + 1)
    y_start = max(0, y - half_size)
    y_end = min(height, y + half_size + 1)
    
    # Extract the sample area
    sample = image[y_start:y_end, x_start:x_end, :]
    
    # Calculate the average RGB values in the sample
    avg_rgb = np.mean(sample, axis=(0, 1))
    
    # Normalize to middle channel (green)
    green = avg_rgb[1]
    if green == 0:
        return (1.0, 1.0, 1.0)  # Avoid division by zero
        
    red_mult = green / avg_rgb[0] if avg_rgb[0] > 0 else 1.0
    blue_mult = green / avg_rgb[2] if avg_rgb[2] > 0 else 1.0
    
    return (red_mult, 1.0, blue_mult)