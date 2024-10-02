import requests
import re
import os
import json
from bs4 import BeautifulSoup
import mwparserfromhell

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
    
    if save_to_file:
        save_drops_to_file(monster_name, drops)
    
    return drops

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
        for drop in drops:
            file.write(drop + "\n")
    
    print(f"Drop table for {monster_name} saved to {file_path}")

def main():
    category = input("Enter the OSRS Wiki category to search (e.g., 'Monsters'): ")
    monsters = get_category_members(category)
    
    print(f"\nMonsters in category '{category}':")
    for monster in monsters:
        print(f"- {monster}")
        drops = get_monster_drops(monster, save_to_file=True)
        if drops:
            print(f"  Drops ({len(drops)} items):")
            for drop in drops:
                print(f"    - {drop}")
        else:
            print("  No drops found or unable to fetch drop table.")
        print()

if __name__ == "__main__":
    main()
