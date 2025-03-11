"""
Polygon processing utilities.
"""

import numpy as np
from matplotlib.path import Path
from typing import List, Tuple, Dict, Any


def extract_pixels_from_polygon(
    image: np.ndarray, 
    polygon: List[Tuple[float, float]], 
    roi_label: str,
    file_name: str
) -> List[Dict[str, Any]]:
    """
    Extract pixel data from within a polygon.
    
    Args:
        image: RGB image data
        polygon: List of (x, y) coordinates defining the polygon
        roi_label: Label for the ROI
        file_name: Original image filename
        
    Returns:
        List of dictionaries with pixel data
    """
    height, width, channels = image.shape
    polygon_array = np.array(polygon)
    
    # Create a Path object for the polygon
    p = Path(polygon_array)
    
    # Create a grid of all pixel coordinates
    y, x = np.mgrid[:height, :width]
    points = np.vstack((x.ravel(), y.ravel())).T
    
    # Find which points are inside the polygon
    mask = p.contains_points(points)
    points_inside = points[mask]
    
    # Process all pixels inside the polygon
    all_data = []
    for x, y in points_inside:
        for c in range(channels):
            channel_name = "RGB"[c]
            pixel_value = image[int(y), int(x), c]
            
            all_data.append({
                "file_name": file_name,
                "roi_label": roi_label,
                "channel": channel_name,
                "x": int(x),
                "y": int(y),
                "pixel_value": int(pixel_value)
            })
    
    return all_data


def get_polygon_centroid(vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the centroid of a polygon.
    
    Args:
        vertices: List of (x, y) coordinates defining the polygon
        
    Returns:
        Tuple of (x, y) for the centroid
    """
    return tuple(np.mean(vertices, axis=0))