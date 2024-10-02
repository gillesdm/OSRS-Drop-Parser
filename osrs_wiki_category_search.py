import requests
import mwparserfromhell
import re

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
    base_url = "https://oldschool.runescape.wiki/api.php"
    
    params = {
        "action": "parse",
        "page": monster_name,
        "prop": "wikitext",
        "format": "json"
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if 'error' in data:
        return []
    
    wikitext = data['parse']['wikitext']['*']
    parsed = mwparserfromhell.parse(wikitext)
    
    drops = []
    for template in parsed.filter_templates():
        if template.name.matches('DropsLine'):
            try:
                item = str(template.get('Item').value).strip()
                drops.append(item)
            except ValueError:
                # If 'Item' is not found, try 'Name'
                try:
                    item = str(template.get('Name').value).strip()
                    drops.append(item)
                except ValueError:
                    # If neither 'Item' nor 'Name' is found, skip this template
                    continue
    
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
