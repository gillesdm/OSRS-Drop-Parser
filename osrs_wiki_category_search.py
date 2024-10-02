import requests
import re
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

def get_monster_drops(monster_name):
    """
    Fetch the drop table for a given monster from the OSRS Wiki.
    """
    base_url = "https://oldschool.runescape.wiki/w/"
    
    response = requests.get(base_url + monster_name.replace(' ', '_'))
    
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    drops_table = soup.find('table', class_='item-drops')
    
    if not drops_table:
        return []
    
    drops = []
    for row in drops_table.find_all('tr')[1:]:  # Skip header row
        item_cell = row.find('td', class_='item-drop-name')
        if item_cell:
            item_name = item_cell.text.strip()
            drops.append(item_name)
    
    return drops

def main():
    category = input("Enter the OSRS Wiki category to search (e.g., 'Monsters'): ")
    monsters = get_category_members(category)
    
    print(f"\nMonsters in category '{category}':")
    for monster in monsters:
        print(f"- {monster}")
        drops = get_monster_drops(monster)
        if drops:
            print("  Drops:")
            for drop in drops:
                print(f"    - {drop}")
        else:
            print("  No drops found or unable to fetch drop table.")
        print()

if __name__ == "__main__":
    main()
