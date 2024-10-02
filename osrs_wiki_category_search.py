import requests
import re
import os
import json
from bs4 import BeautifulSoup
import mwparserfromhell
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import DOUBLE
from rich.style import Style
from rich.layout import Layout

# Load the item database
with open('assets/item-db.json', 'r') as f:
    item_db = json.load(f)

def get_item_id(item_name):
    """
    Look up the item ID for a given item name.
    If not found, try searching without suffixes like '(m)'.
    """
    for item_id, item_data in item_db.items():
        if item_data['name'].lower() == item_name.lower():
            return int(item_id)
    
    # If not found, try without suffixes
    base_name = re.sub(r'\([^)]*\)$', '', item_name).strip()
    if base_name != item_name:
        for item_id, item_data in item_db.items():
            if item_data['name'].lower() == base_name.lower():
                return int(item_id)
    
    return None

def get_category_members(category_name):
    """
    Fetch all items in a given category from the OSRS Wiki.
    """
    base_url = "https://oldschool.runescape.wiki/api.php"
    
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category_name}",
        "cmlimit": "500",
        "format": "json"
    }
    
    items = []
    
    while True:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        for member in data["query"]["categorymembers"]:
            items.append(member["title"])
        
        if "continue" in data:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break
    
    return items

def get_monster_drops(monster_name, save_to_file=False):
    """
    Fetch all drop tables for a given monster from the OSRS Wiki using the API.
    If save_to_file is True, the drop table will be saved to a local file.
    Returns a list of tuples (item_name, item_id).
    """
    base_url = "https://oldschool.runescape.wiki/api.php"
    
    params = {
        "action": "parse",
        "page": monster_name,
        "format": "json",
        "prop": "text|wikitext",
        "contentmodel": "wikitext"
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        print(f"Failed to fetch data for {monster_name}")
        return []
    
    data = response.json()
    
    if 'error' in data:
        print(f"Error fetching data for {monster_name}: {data['error']['info']}")
        return []
    
    html_content = data['parse']['text']['*']
    wikitext_content = data['parse']['wikitext']['*']
    
    drops = parse_drops(html_content)
    
    if not drops:
        drops = parse_wikitext_drops(wikitext_content)
    
    drops_with_ids = [(item, get_item_id(item)) for item in drops]
    
    if save_to_file:
        save_drops_to_file(monster_name, drops_with_ids)
    
    return drops_with_ids

def parse_drops(content):
    soup = BeautifulSoup(content, 'html.parser')
    drops_tables = soup.find_all('table', class_='item-drops')
    drops = []

    for drops_table in drops_tables:
        rows = drops_table.find_all('tr')
        for row in rows[1:]:  # Skip the header row
            cells = row.find_all('td')
            if len(cells) >= 2:
                item_name = cells[1].text.strip()
                drops.append(item_name)

    return list(set(drops))  # Remove duplicates

def parse_wikitext_drops(content):
    wikicode = mwparserfromhell.parse(content)
    templates = wikicode.filter_templates()
    drops = []

    for template in templates:
        if template.name.strip().lower() == "droptable":
            drops.extend(parse_drop_template(template))

    return list(set(drops))  # Remove duplicates

def parse_drop_template(template):
    drops = []
    for param in template.params:
        param_name = param.name.strip().lower()
        if param_name.isdigit() or param_name in ["item", "item1", "item2", "item3", "item4", "item5"]:
            item_info = str(param.value).strip().split('|')
            item_name = item_info[0].strip()
            if item_name and not item_name.startswith("{{"):
                drops.append(item_name)
        elif param_name in ["droptable", "subtable"]:
            nested_template = mwparserfromhell.parse(str(param.value)).filter_templates()
            if nested_template:
                drops.extend(parse_drop_template(nested_template[0]))
    return drops

def save_drops_to_file(monster_name, drops):
    """
    Save the drop table for a given monster to a local file.
    """
    file_name = f"{monster_name.replace(' ', '_')}_drops.txt"
    file_path = os.path.join("drop_tables", file_name)
    
    os.makedirs("drop_tables", exist_ok=True)
    
    with open(file_path, "w") as file:
        for drop, item_id in drops:
            if item_id is not None:
                file.write(f"{drop} (ID: {item_id})\n")
            else:
                file.write(f"{drop} (ID: Not found)\n")
    
    print(f"Drop table for {monster_name} saved to {file_path}")

def main():
    console = Console()
    
    category = console.input("[bold cyan]Enter the OSRS Wiki category to search (e.g., 'Monsters'): [/bold cyan]")
    monsters = get_category_members(category)
    
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    layout["main"].split_row(
        Layout(name="monster", ratio=1),
        Layout(name="drops", ratio=2)
    )
    
    layout["header"].update(Panel(f"[bold green]Monsters in category '{category}'[/bold green]", border_style="green"))
    
    monster_panel = Panel("", title="Monster", border_style="blue")
    layout["monster"].update(monster_panel)
    
    drops_table = Table(title="Drop Table", box=DOUBLE, border_style="yellow", header_style="bold yellow")
    drops_table.add_column("Item", style="green")
    drops_table.add_column("ID", style="cyan")
    layout["drops"].update(drops_table)
    
    with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
        for i, monster in enumerate(monsters, 1):
            layout["header"].update(Panel(f"[bold green]Monsters in category '{category}' - Processing {i}/{len(monsters)}[/bold green]", border_style="green"))
            layout["monster"].update(Panel(Text(monster, style="bold magenta"), title="Monster", border_style="blue"))
            
            drops = get_monster_drops(monster, save_to_file=True)
            
            drops_table = Table(title="Drop Table", box=DOUBLE, border_style="yellow", header_style="bold yellow")
            drops_table.add_column("Item", style="green")
            drops_table.add_column("ID", style="cyan")
            
            if drops:
                for drop, item_id in drops:
                    id_str = str(item_id) if item_id is not None else "Not found"
                    id_style = "cyan" if item_id is not None else "red"
                    drops_table.add_row(drop, id_str, style=Style(color="green", dim=(item_id is None)))
            else:
                drops_table.add_row("No drops found", "N/A", style="red")
            
            layout["drops"].update(drops_table)
            live.refresh()

if __name__ == "__main__":
    main()
