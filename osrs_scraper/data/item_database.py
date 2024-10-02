import json
from typing import Dict, Optional

def load_item_database(file_path: str = 'assets/item-db.json') -> Dict[str, Dict]:
    with open(file_path, 'r') as f:
        return json.load(f)

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

