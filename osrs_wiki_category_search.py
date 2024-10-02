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

def main():
    category = input("Enter the OSRS Wiki category to search: ")
    items = get_category_members(category)
    
    print(f"\nItems in category '{category}':")
    for item in items:
        print(f"- {item}")

if __name__ == "__main__":
    main()
