import requests
from bs4 import BeautifulSoup
import mwparserfromhell
from components.logging_utils import log_api_response, log_parsed_data

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
        log_api_response(category_name, base_url, params, response)
        data = response.json()
        
        for member in data["query"]["categorymembers"]:
            items.append(member["title"])
        
        if "continue" in data:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break
    
    log_parsed_data(category_name, "category_members", items)
    return items

def get_monster_drops(monster_name):
    """
    Fetch all drop tables for a given monster from the OSRS Wiki using the API.
    Returns a tuple of (list of tuples (item_name, item_id), total number of drops).
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
    log_api_response(monster_name, base_url, params, response)
    
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
    
    log_parsed_data(monster_name, "monster_drops", drops)
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

def is_monster(entry):
    """
    Check if a given entry is a monster by looking for the "infobox-monster" table.
    """
    base_url = "https://oldschool.runescape.wiki/api.php"
    params = {
        "action": "parse",
        "page": entry,
        "format": "json",
        "prop": "text"
    }
    
    try:
        response = requests.get(base_url, params=params)
        log_api_response(entry, base_url, params, response)
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        
        if 'error' in data:
            return False
        
        if 'parse' not in data or 'text' not in data['parse']:
            return False
        
        html_content = data['parse']['text']['*']
        soup = BeautifulSoup(html_content, 'html.parser')
        
        return bool(soup.find('table', class_='infobox-monster'))
    except Exception as e:
        print(f"Error processing entry '{entry}': {str(e)}")
        return False
