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
from osrs_scraper.utils.file_operations import save_drops_to_file, create_output_file, save_banklayout
from osrs_scraper.utils.logging import log_parsed_data, set_logging
from osrs_scraper.ui.components import (
    create_welcome_screen,
    get_search_type,
    get_input,
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
        description="OSRS Wiki Search",
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
OSRS Wiki Search

A tool to fetch and save drop tables for monsters in a specified
Old School RuneScape Wiki category or for a specific monster.

This script allows you to:
1. Search for monsters within a specific OSRS Wiki category or search for a specific monster
2. Fetch drop tables for all monsters in that category or for the specific monster
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

    remove_existing_logs()
    set_logging(args.logs)
    console = Console()
    
    # Display welcome screen
    welcome_screen = create_welcome_screen(console)
    with Live(welcome_screen, console=console, screen=True, refresh_per_second=4):
        console.input()
    
    console.clear()
    
    while True:
        search_type = get_search_type()
        if search_type is None:
            console.print("[bold red]Search cancelled. Exiting...[/bold red]")
            return

        search_input = get_input(console, search_type)
        item_db = load_item_database()
        if not item_db:
            console.print("[bold red]Warning: Item database is empty. Item IDs will not be available.[/bold red]")
            console.print("Press Enter to continue anyway, or Ctrl+C to exit.")
            console.input()

        layout = create_layout()
        
        file_path = create_output_file(search_input)
        
        completed_steps = [False, False, False, False, False, False]
        
        with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
            update_layout(layout, search_input, [], console.height, completed_steps)
            live.refresh()

            completed_steps[0] = True  # Initializing
            update_layout(layout, search_input, [], console.height, completed_steps)
            live.refresh()

            while True:
                if search_type == "category":
                    all_entries = get_category_members(search_input)
                    completed_steps[1] = True  # Fetching category members
                    update_layout(layout, search_input, [], console.height, completed_steps)
                    live.refresh()

                    if not all_entries:
                        console.print(f"[bold red]Error: Category '{search_input}' not found or empty.[/bold red]")
                        search_input = get_input(console, search_type)
                        continue

                    monster_progress = Progress()
                    drop_progress = Progress()
                    monster_task = monster_progress.add_task("[cyan]Filtering monsters...", total=len(all_entries))
                    
                    monsters = []
                    for entry in all_entries:
                        if is_monster(entry):
                            monsters.append(entry)
                        monster_progress.update(monster_task, advance=1)
                        update_layout(layout, search_input, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
                        live.refresh()
                    
                    completed_steps[2] = True  # Filtering monsters
                    update_layout(layout, search_input, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
                    live.refresh()
                    
                    if args.logs:
                        log_parsed_data(search_input, "filtered_monsters", monsters)
                    
                    if not monsters:
                        console.print(f"[bold red]Error: No monsters found in category '{search_input}'.[/bold red]")
                        search_input = get_input(console, search_type)
                        continue
                else:
                    monsters = [search_input]
                    completed_steps[1] = True
                    completed_steps[2] = True
                    monster_progress = Progress()
                    drop_progress = Progress()
                
                drop_task = drop_progress.add_task("[yellow]Fetching drops...", total=len(monsters))
                
                completed_steps[3] = True  # Fetching drop tables
                update_layout(layout, search_input, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
                live.refresh()

                all_unique_ids = set()
                monster_not_found = False
                for monster in monsters:
                    drops, redirected_name = get_monster_drops(monster)
                    if not drops:
                        console.print(f"[bold red]Error: Monster '{monster}' not found or has no drops.[/bold red]")
                        monster_not_found = True
                        break
                    
                    # Use redirected_name if available, otherwise use the original monster name
                    monster_name = redirected_name or monster
                    
                    # Update file_path with the redirected name if available
                    if redirected_name:
                        file_path = file_path.replace(search_input, redirected_name)
                    
                    drops_with_ids = [(item, get_item_id(item, item_db)) for item in drops if item.lower() != "nothing"]
                    if args.banklayout:
                        monster_unique_ids = {get_item_id(item, item_db) for item, _ in drops_with_ids if get_item_id(item, item_db) is not None}
                        all_unique_ids.update(monster_unique_ids)
                    else:
                        save_drops_to_file(redirected_name or search_input, monster_name, drops_with_ids, file_path.rsplit('.', 1)[0], args.txt, args.id, args.sort, False)
                    
                    if not args.id and not args.banklayout:
                        drops_table = create_drops_table(drops_with_ids)
                        update_layout(layout, search_input, monsters, console.height, completed_steps, monster_name, drops_table, progress_bars=(monster_progress, drop_progress))
                    drop_progress.update(drop_task, advance=1)
                    live.refresh()
                
                if monster_not_found:
                    search_input = get_input(console, search_type)
                    continue
                
                break  # Exit the loop if everything was successful

            if args.banklayout:
                save_banklayout(search_input, all_unique_ids, file_path.rsplit('.', 1)[0], args.sort)
            
            completed_steps[4] = True  # Saving data
            update_layout(layout, search_input, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
            live.refresh()

            completed_steps[5] = True  # Finalizing
            update_layout(layout, search_input, monsters, console.height, completed_steps, progress_bars=(monster_progress, drop_progress))
            live.refresh()

        break  # Exit the loop if everything was successful
    
    if args.id and not args.banklayout:
        console.print(f"\n[green]Item IDs for {'all monsters in category' if search_type == 'category' else 'monster'} '{search_input}' have been saved to {file_path.rsplit('.', 1)[0]}_ids.txt")
    if args.banklayout:
        console.print(f"[green]RuneLite bank layout for {'category' if search_type == 'category' else 'monster'} '{search_input}' has been saved to {file_path.rsplit('.', 1)[0]}_banklayout.txt")
    if not args.id and not args.banklayout:
        console.print(f"\n[green]Drop tables for {'all monsters in category' if search_type == 'category' else 'monster'} '{search_input}' have been saved to {file_path}")

if __name__ == "__main__":
    main()
