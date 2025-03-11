"""
Image processing module for NEF files.
"""

import numpy as np
import rawpy


def load_nef_image(image_path: str) -> np.ndarray:
    """
    Load and process a NEF image file.
    
    Args:
        image_path: Path to the NEF file
        
    Returns:
        np.ndarray: Processed RGB image data
    """
    with rawpy.imread(image_path) as raw:
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