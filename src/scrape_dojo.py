import os
import re
import json
import requests
from bs4 import BeautifulSoup

def fetch_and_scrape_dojos():
    """Fetch HTML and extract all dojos from embedded JSON"""
    url = 'https://www.shortcutfoo.com/app/dojos'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find script tag containing dojo data
        script_tag = soup.find('script', string=re.compile('"dojos"'))
        if not script_tag:
            raise ValueError("Dojo data script not found")
        
        # Extract JSON string
        json_match = re.search(r'"dojos":(\[.*?\])', script_tag.string, re.DOTALL)
        if not json_match:
            raise ValueError("Dojo JSON pattern not found")
            
        dojo_list = json.loads(json_match.group(1))
        # Build dictionary and sort by slug
        dojo_data = {dojo['slug']: dojo['name'] for dojo in dojo_list}
        sorted_dojo_data = dict(sorted(dojo_data.items()))
        return sorted_dojo_data
    
    except requests.exceptions.RequestException as e:
        print(f"🚨 Network error: {e}")
        return {}
    except (ValueError, json.JSONDecodeError) as e:
        print(f"🚨 Data extraction error: {e}")
        return {}

def save_to_json(data, output_path):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data)} dojos to {os.path.abspath(output_path)}")

if __name__ == "__main__":
    OUTPUT_FILE = "./output/all_dojos.json"
    dojos = fetch_and_scrape_dojos()
    
    if dojos:
        save_to_json(dojos, OUTPUT_FILE)
    else:
        print("❌ Failed to extract dojos")
