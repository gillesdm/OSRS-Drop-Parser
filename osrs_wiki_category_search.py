import argparse
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn
from components.wiki_api import get_category_members, get_monster_drops, is_monster
from components.item_database import load_item_database, get_item_id
from components.file_operations import save_drops_to_file, create_output_file
from components.ui import (
    create_header, create_layout, update_monsters_panel,
    create_progress_bars, create_drops_table, create_welcome_screen,
    get_category_input, create_monster_search_panel
)
from components.logging_utils import log_parsed_data, set_logging

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
    
    # Clear the screen after welcome screen
    console.clear()
    
    # Get category input
    category = get_category_input(console)
    
    item_db = load_item_database()
    all_entries = get_category_members(category)
    
    layout = create_layout()
    layout["title"].update(create_header())
    
    console_height = console.height
    
    layout["monster_search"].update(create_monster_search_panel())
    
    monsters_panel = update_monsters_panel("", console_height, layout)
    layout["monsters"].update(monsters_panel)
    
    progress_drops = create_progress_bar()
    
    layout["drop_progress"].update(Panel(progress_drops, title="Drop Table Progress", border_style="yellow"))
    
    file_path = create_output_file(category)
    
    with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
        monsters = []
        total_entries = len(all_entries)
        
        for i, entry in enumerate(all_entries, 1):
            if is_monster(entry):
                monsters.append(entry)
            progress_percentage = (i / total_entries) * 100
            layout["monster_search"].update(Panel(f"Checking for monsters... {progress_percentage:.1f}%", title="Monster Search", border_style="cyan"))
            live.refresh()
        
        if args.logs:
            log_parsed_data(category, "filtered_monsters", monsters)
        
        if not monsters:
            layout["monster_search"].update(Panel(f"[red]No monsters found in the category '{category}'.[/red]", title="Monster Search", border_style="cyan"))
            live.refresh()
            return
        
        layout["monster_search"].update(Panel(f"Found {len(monsters)} monsters", title="Monster Search", border_style="cyan"))
        monsters_list = "\n".join(monsters)
        monsters_panel = update_monsters_panel(monsters_list, console_height, layout)
        layout["monsters"].update(monsters_panel)
        
        task_drops = progress_drops.add_task("[yellow]Fetching drops", total=len(monsters))
        
        for monster in monsters:
            progress_drops.update(task_drops, completed=0, description=f"[yellow]Fetching drops for {monster}")
            drops = get_monster_drops(monster)
            drops_with_ids = [(item, get_item_id(item, item_db)) for item in drops if item.lower() != "nothing"]
            save_drops_to_file(category, monster, drops_with_ids, file_path)
            progress_drops.update(task_drops, total=len(drops_with_ids), completed=len(drops_with_ids))
            
            # Update the monster name to green and add a checkmark in the monsters list
            monsters_list = "\n".join(["✓ " + m if m == monster else m for m in monsters_list.split("\n")])
            
            # Auto-scroll the monsters list
            monsters_panel = update_monsters_panel(monsters_list, console_height, layout)
            layout["monsters"].update(monsters_panel)
            
            drops_table = create_drops_table(drops_with_ids)
            
            layout["drops"].update(Panel(drops_table, title=f"Drops for {monster}", border_style="yellow"))
            progress_monsters.update(task_monsters, advance=1)
            live.refresh()
    
    console.print(f"\n[green]Drop tables for all monsters in category '{category}' have been saved to {file_path}")

if __name__ == "__main__":
    main()
