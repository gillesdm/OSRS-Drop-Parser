import requests
import re
from bs4 import BeautifulSoup
import mwparserfromhell
from osrs_scraper.utils.logging import log_api_response, log_parsed_data

BASE_URL = "https://oldschool.runescape.wiki/api.php"

def get_category_members(category_name: str) -> list[str]:
    """Fetch all items in a given category from the OSRS Wiki."""
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category_name}",
        "cmlimit": "500",
        "format": "json"
    }
    
    items = []
    
    while True:
        response = requests.get(BASE_URL, params=params)
        log_api_response(category_name, BASE_URL, params, response)
        data = response.json()
        
        items.extend(member["title"] for member in data["query"]["categorymembers"])
        
        if "continue" not in data:
            break
        params["cmcontinue"] = data["continue"]["cmcontinue"]
    
    log_parsed_data(category_name, "category_members", items)
    return items

def get_monster_drops(monster_name: str) -> list[str]:
    """Fetch all drop tables for a given monster from the OSRS Wiki using the API."""
    params = {
        "action": "parse",
        "page": monster_name,
        "format": "json",
        "prop": "text|wikitext",
        "contentmodel": "wikitext"
    }
    
    response = requests.get(BASE_URL, params=params)
    log_api_response(monster_name, BASE_URL, params, response)
    
    if response.status_code != 200:
        print(f"Failed to fetch data for {monster_name}")
        return []
    
    data = response.json()
    
    if 'error' in data:
        print(f"Error fetching data for {monster_name}: {data['error']['info']}")
        return []
    
    html_content = data['parse']['text']['*']
    wikitext_content = data['parse']['wikitext']['*']
    
    drops = parse_drops(html_content) or parse_wikitext_drops(wikitext_content)
    
    log_parsed_data(monster_name, "monster_drops", drops)
    return drops

def parse_drops(content: str) -> list[str]:
    soup = BeautifulSoup(content, 'html.parser')
    drops = [
        cells[1].text.strip()
        for drops_table in soup.find_all('table', class_='item-drops')
        for row in drops_table.find_all('tr')[1:]
        if (cells := row.find_all('td')) and len(cells) >= 2
    ]
    return list(set(drops))  # Remove duplicates

def parse_wikitext_drops(content: str) -> list[str]:
    wikicode = mwparserfromhell.parse(content)
    drops = [
        drop
        for template in wikicode.filter_templates()
        if template.name.strip().lower() == "droptable"
        for drop in parse_drop_template(template)
    ]
    return list(set(drops))  # Remove duplicates

def parse_drop_template(template):
    drops = []
    for param in template.params:
        param_name = param.name.strip().lower()
        if param_name.isdigit() or param_name.startswith("item"):
            item_info = str(param.value).strip().split('|')
            item_name = item_info[0].strip()
            if item_name and not item_name.startswith("{{"):
                drops.append(item_name)
        elif param_name in ["droptable", "subtable"]:
            nested_template = mwparserfromhell.parse(str(param.value)).filter_templates()
            if nested_template:
                drops.extend(parse_drop_template(nested_template[0]))
    return drops

def is_monster(entry: str) -> bool:
    """Check if a given entry is a monster by looking for the "infobox-monster" table."""
    params = {
        "action": "parse",
        "page": entry,
        "format": "json",
        "prop": "text"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        log_api_response(entry, BASE_URL, params, response)
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        
        if 'error' in data or 'parse' not in data or 'text' not in data['parse']:
            return False
        
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        return bool(soup.find('table', class_='infobox-monster'))
    except Exception as e:
        print(f"Error processing entry '{entry}': {str(e)}")
        return False
