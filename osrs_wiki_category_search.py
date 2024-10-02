import requests
import re
import os
import json
from bs4 import BeautifulSoup

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
        "prop": "text",
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
    soup = BeautifulSoup(html_content, 'html.parser')
    
    drops = []
    drops_tables = soup.find_all('table', class_='item-drops')
    
    for table in drops_tables:
        for row in table.find_all('tr')[1:]:  # Skip header row
            item_cell = row.find('td', class_='item-drop-name')
            if item_cell:
                item_name = item_cell.find('a')
                if item_name:
                    item_name = item_name.text.strip()
                    drops.append(item_name)
    
    if not drops:
        # Try to find drops in the infobox
        infobox = soup.find('table', class_='infobox')
        if infobox:
            drops_row = infobox.find('th', string='Drops')
            if drops_row:
                drops_cell = drops_row.find_next_sibling('td')
                if drops_cell:
                    for item in drops_cell.find_all('a'):
                        drops.append(item.text.strip())
    
    if save_to_file:
        save_drops_to_file(monster_name, drops)
    
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
