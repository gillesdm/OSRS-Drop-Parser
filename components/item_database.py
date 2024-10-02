import json

def load_item_database(file_path='assets/item-db.json'):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_item_id(item_name, item_db):
    """
    Look up the item ID for a given item name.
    If not found, try searching without suffixes like '(m)'.
    """
    for item_id, item_data in item_db.items():
        if item_data['name'].lower() == item_name.lower():
            return int(item_id)
    
    # If not found, try without suffixes
    base_name = item_name.split('(')[0].strip()
    if base_name != item_name:
        for item_id, item_data in item_db.items():
            if item_data['name'].lower() == base_name.lower():
                return int(item_id)
    
    return None
