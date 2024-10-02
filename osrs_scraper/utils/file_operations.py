import os
import os
import json
from datetime import datetime
from typing import List, Tuple, Optional

def save_drops_to_file(category: str, monster_name: str, drops: List[Tuple[str, Optional[int]]], file_path: str, txt_output: bool = False, id_only: bool = False, sort_ids: bool = False, banklayout: bool = False) -> None:
    """Save the drop table for a given monster to a single file for the category."""
    # Save to JSON (always)
    json_file_path = file_path.rsplit('.', 1)[0] + '.json'
    
    # Check if the file exists, if not create it with an empty JSON object
    if not os.path.exists(json_file_path):
        with open(json_file_path, 'w') as json_file:
            json.dump({}, json_file)
    
    # Now open the file in read and write mode
    with open(json_file_path, 'r+') as json_file:
        try:
            data = json.load(json_file)
        except json.JSONDecodeError:
            data = {}
        
        data[monster_name] = [{"item": item, "id": item_id} for item, item_id in drops]
        
        json_file.seek(0)
        json.dump(data, json_file, indent=2, ensure_ascii=False)
        json_file.truncate()

    # Save to TXT if txt_output is True
    if txt_output and not id_only:
        with open(file_path, "a") as txt_file:
            txt_file.write(f"Drop table for {monster_name}:\n")
            for drop, item_id in drops:
                txt_file.write(f"{drop} (ID: {item_id if item_id is not None else 'Not found'})\n")
            txt_file.write("\n")  # Add a blank line between monsters

    # Save only item IDs if id_only is True
    if id_only:
        id_file_path = file_path.rsplit('.', 1)[0] + '_ids.txt'
        with open(id_file_path, "a") as id_file:
            unique_ids = set(item_id for _, item_id in drops if item_id is not None)
            if sort_ids:
                unique_ids = sorted(unique_ids)
            id_file.write(','.join(map(str, unique_ids)) + '\n')

        # Save RuneLite bank layout if banklayout is True
        if banklayout:
            banklayout_file_path = file_path.rsplit('.', 1)[0] + '_banklayout.txt'
            with open(banklayout_file_path, "a") as banklayout_file:
                unique_ids = list(set(item_id for _, item_id in drops if item_id is not None))
                if sort_ids:
                    unique_ids.sort()
                banklayout_content = f"banktaglayoutsplugin:{category.lower()},"
                banklayout_content += ','.join(f"{id}:{i}" for i, id in enumerate(unique_ids))
                banklayout_content += f",banktag:{category.lower()},"
                banklayout_content += ','.join(map(str, unique_ids))
                banklayout_file.write(banklayout_content)

def create_output_file(category: str) -> str:
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"droplist_{category}_{current_time}.txt"
    folder_path = "Droplists"
    file_path = os.path.join(folder_path, file_name)
    os.makedirs(folder_path, exist_ok=True)
    return file_path
