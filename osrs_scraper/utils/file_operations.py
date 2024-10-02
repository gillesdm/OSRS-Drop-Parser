import os
from datetime import datetime
from typing import List, Tuple, Optional

def save_drops_to_file(category: str, monster_name: str, drops: List[Tuple[str, Optional[int]]], file_path: str) -> None:
    """Save the drop table for a given monster to a single file for the category."""
    with open(file_path, "a") as file:
        file.write(f"Drop table for {monster_name}:\n")
        for drop, item_id in drops:
            file.write(f"{drop} (ID: {item_id if item_id is not None else 'Not found'})\n")
        file.write("\n")  # Add a blank line between monsters

def create_output_file(category: str) -> str:
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"droplist_{category}_{current_time}.txt"
    folder_path = "Droplists"
    file_path = os.path.join(folder_path, file_name)
    os.makedirs(folder_path, exist_ok=True)
    return file_path
