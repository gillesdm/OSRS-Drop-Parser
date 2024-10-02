import json
import os
from typing import Dict, Optional

def load_item_database(file_path: str = 'assets/item-db.json') -> Dict[str, Dict]:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Please make sure the item database file exists in the correct location.")
        print(f"Current working directory: {os.getcwd()}")
        print("You may need to download or create the item database file.")
        return {}

def get_item_id(item_name: str, item_db: Dict[str, Dict]) -> Optional[int]:
    """
    Look up the item ID for a given item name.
    If not found, try searching without suffixes like '(m)'.
    """
    item_name_lower = item_name.lower()
    for item_id, item_data in item_db.items():
        if item_data['name'].lower() == item_name_lower:
            return int(item_id)
    
    # If not found, try without suffixes
    base_name = item_name.split('(')[0].strip().lower()
    if base_name != item_name_lower:
        for item_id, item_data in item_db.items():
            if item_data['name'].lower() == base_name:
                return int(item_id)
    
    return None

