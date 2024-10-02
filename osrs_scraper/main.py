import os
import sys

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import argparse
from rich.console import Console
from rich.live import Live

from osrs_scraper.api.wiki_api import get_category_members, get_monster_drops, is_monster
from osrs_scraper.data.item_database import load_item_database, get_item_id
from osrs_scraper.utils.file_operations import save_drops_to_file, create_output_file
from osrs_scraper.utils.logging import log_parsed_data, set_logging
from osrs_scraper.ui.components import (
    create_welcome_screen,
    get_category_input,
    create_drops_table,
)
from osrs_scraper.ui.layout import (
    create_layout,
    update_layout,
)

def main():
    parser = argparse.ArgumentParser(description="OSRS Wiki Category Search")
    parser.add_argument("--logs", action="store_true", help="Enable logging")
    args = parser.parse_args()

    set_logging(args.logs)
    console = Console()
    
    # Display welcome screen
    welcome_screen = create_welcome_screen(console)
    with Live(welcome_screen, console=console, screen=True, refresh_per_second=4):
        console.input()
    
    console.clear()
    
    category = get_category_input(console)
    item_db = load_item_database()
    all_entries = get_category_members(category)
    
    layout = create_layout()
    
    file_path = create_output_file(category)
    
    with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
        monsters = [entry for entry in all_entries if is_monster(entry)]
        
        if args.logs:
            log_parsed_data(category, "filtered_monsters", monsters)
        
        if not monsters:
            update_layout(layout, category, [], console.height)
            live.refresh()
            return
        
        update_layout(layout, category, monsters, console.height)
        live.refresh()
        
        for monster in monsters:
            drops = get_monster_drops(monster)
            drops_with_ids = [(item, get_item_id(item, item_db)) for item in drops if item.lower() != "nothing"]
            save_drops_to_file(category, monster, drops_with_ids, file_path)
            
            drops_table = create_drops_table(drops_with_ids)
            update_layout(layout, category, monsters, console.height, monster, drops_table)
            live.refresh()
    
    console.print(f"\n[green]Drop tables for all monsters in category '{category}' have been saved to {file_path}")

if __name__ == "__main__":
    main()
