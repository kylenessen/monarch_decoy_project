"""
File input/output utilities.
"""

import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple


def save_rois_to_json(
    filename: str, 
    file_name: str, 
    rois: List[Dict[str, Any]], 
    white_balance: Optional[Tuple[float, float, float]] = None
) -> bool:
    """
    Save ROIs to a JSON file.
    
    Args:
        filename: Path to save the JSON file
        file_name: Original image filename
        rois: List of ROI dictionaries
        white_balance: Optional white balance multipliers
        
    Returns:
        bool: True if successful, False otherwise
    """
    data = {
        "file_name": file_name,
        "rois": rois
    }
    
    # Add white balance if provided
    if white_balance:
        data["white_balance"] = {
            "red": white_balance[0],
            "green": white_balance[1],
            "blue": white_balance[2]
        }
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def load_rois_from_json(filename: str) -> Dict[str, Any]:
    """
    Load ROIs from a JSON file.
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        Dict containing file_name and rois
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return data


def save_pixel_data_to_csv(filename: str, data: List[Dict[str, Any]]) -> None:
    """
    Save pixel data to a CSV file.
    
    Args:
        filename: Path to save the CSV file
        data: List of pixel data dictionaries
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)