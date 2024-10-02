import os
import sys
import shutil

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import argparse
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, TaskID

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

def remove_existing_logs():
    log_dir = os.path.join(current_dir, "Logs")
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)

def main():
    parser = argparse.ArgumentParser(
        description="OSRS Wiki Category Search",
        epilog="Example usage: python osrs_scraper/main.py --logs --txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Enable logging of API responses and parsed data"
    )
    parser.add_argument(
        "--txt",
        action="store_true",
        help="Output drop tables as a txt file in addition to JSON"
    )
    parser.add_argument(
        "--id",
        action="store_true",
        default=True,
        help="Output only item IDs as a comma-separated list in a txt file (default: True)"
    )
    parser.add_argument(
        "--sort",
        action="store_true",
        default=True,
        help="Sort the item IDs from small to large (default: True)"
    )
    parser.add_argument(
        "--banklayout",
        action="store_true",
        default=True,
        help="Create a RuneLite bank layout file (default: True)"
    )
    
    # Add a more detailed description
    parser.description = """
OSRS Wiki Category Search

A tool to fetch and save drop tables for monsters in a specified
Old School RuneScape Wiki category.

This script allows you to:
1. Search for monsters within a specific OSRS Wiki category
2. Fetch drop tables for all monsters in that category
3. Save the drop tables in JSON format (always)
4. Optionally save the drop tables in TXT format
5. Optionally save only item IDs as a comma-separated list
6. Display progress and results in a rich, interactive console interface

Use the --logs option to enable detailed logging for debugging.
Use the --txt option to save drop tables in both JSON and TXT formats.
Use the --id option to save only item IDs as a comma-separated list in a txt file.
Use the --sort option with --id to sort the item IDs from small to large.
    """
    
    args = parser.parse_args()

    # Remove this check as --id and --banklayout are now true by default

    remove_existing_logs()
    set_logging(args.logs)
    console = Console()
    
    # Display welcome screen
    welcome_screen = create_welcome_screen(console)
    with Live(welcome_screen, console=console, screen=True, refresh_per_second=4):
        console.input()
    
    console.clear()
    
    category = get_category_input(console)
    item_db = load_item_database()
    if not item_db:
        console.print("[bold red]Warning: Item database is empty. Item IDs will not be available.[/bold red]")
        console.print("Press Enter to continue anyway, or Ctrl+C to exit.")
        console.input()

    all_entries = get_category_members(category)
    
    layout = create_layout()
    
    file_path = create_output_file(category)
    
    completed_steps = [False, False, False, False, False, False]
    
    with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
        update_layout(layout, category, [], console.height, completed_steps)
        live.refresh()

        completed_steps[0] = True  # Initializing
        update_layout(layout, category, [], console.height, completed_steps)
        live.refresh()

        all_entries = get_category_members(category)
        completed_steps[1] = True  # Fetching category members
        update_layout(layout, category, [], console.height, completed_steps)
        live.refresh()

        monster_progress = Progress()
        drop_progress = Progress()
        monster_task = monster_progress.add_task("[cyan]Filtering monsters...", total=len(all_entries))
        
        monsters = []
        for entry in all_entries:
            if is_monster(entry):
                monsters.append(entry)
            monster_progress.update(monster_task, advance=1)
            update_layout(layout, category, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
            live.refresh()
        
        completed_steps[2] = True  # Filtering monsters
        update_layout(layout, category, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
        live.refresh()
        
        if args.logs:
            log_parsed_data(category, "filtered_monsters", monsters)
        
        if not monsters:
            update_layout(layout, category, [], console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
            live.refresh()
            return
        
        drop_task = drop_progress.add_task("[yellow]Fetching drops...", total=len(monsters))
        
        completed_steps[3] = True  # Fetching drop tables
        update_layout(layout, category, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
        live.refresh()

        all_unique_ids = set()
        for monster in monsters:
            drops = get_monster_drops(monster)
            drops_with_ids = [(item, get_item_id(item, item_db)) for item in drops if item.lower() != "nothing"]
            monster_unique_ids = save_drops_to_file(category, monster, drops_with_ids, file_path.rsplit('.', 1)[0], args.txt, args.id, args.sort, args.banklayout)
            if args.banklayout:
                all_unique_ids.update(monster_unique_ids)
            
            if not args.id:
                drops_table = create_drops_table(drops_with_ids)
                update_layout(layout, category, monsters, console.height, completed_steps, monster, drops_table, progress_bars=(monster_progress, drop_progress))
            drop_progress.update(drop_task, advance=1)
            live.refresh()
        
        if args.banklayout:
            save_banklayout(category, all_unique_ids, file_path.rsplit('.', 1)[0], args.sort)
        
        completed_steps[4] = True  # Saving data
        update_layout(layout, category, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
        live.refresh()

        completed_steps[5] = True  # Finalizing
        update_layout(layout, category, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
        live.refresh()
    
    if args.id:
        console.print(f"\n[green]Item IDs for all monsters in category '{category}' have been saved to {file_path.rsplit('.', 1)[0]}_ids.txt")
    if args.banklayout:
        console.print(f"[green]RuneLite bank layout for category '{category}' has been saved to {file_path.rsplit('.', 1)[0]}_banklayout.txt")
    if not args.id:
        console.print(f"\n[green]Drop tables for all monsters in category '{category}' have been saved to {file_path}")

if __name__ == "__main__":
    main()
