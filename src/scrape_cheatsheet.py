import os
import json
import requests
from bs4 import BeautifulSoup
import time
from random import randint

# Load dojos from the previously generated JSON file
with open('./output/all_dojos.json', 'r') as f:
    dojos = json.load(f)

# Create output directory
os.makedirs('./output/cheatsheet', exist_ok=True)

def scrape_cheatsheet(slug):
    """Scrape cheatsheet for a given dojo slug"""
    url = f'https://www.shortcutfoo.com/app/dojos/{slug}/cheatsheet'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract units (sections)
        units = []
        for unit_section in soup.select('div.pt-10'):
            unit_title = unit_section.select_one('h2.text-xl')
            if not unit_title:
                continue
                
            # Extract commands in this unit
            commands = []
            for cmd_row in unit_section.select('div.flex.p-4.px-6'):
                key_div = cmd_row.select_one('div.flex-1:first-child div:first-child')
                desc_div = cmd_row.select_one('div.flex-1:nth-child(2)')
                
                if key_div and desc_div:
                    commands.append({
                        'key': key_div.get_text(strip=True),
                        'description': desc_div.get_text(strip=True)
                    })
            
            units.append({
                'name': unit_title.get_text(strip=True),
                'commands': commands
            })
        
        return units
    
    except requests.exceptions.RequestException as e:
        print(f"🚨 Network error for {slug}: {e}")
        return []
    except Exception as e:
        print(f"🚨 Processing error for {slug}: {e}")
        return []

# Scrape cheatsheets for all dojos
for slug, name in dojos.items():
    print(f"⏳ Scraping {name} ({slug})...")
    cheatsheet_data = scrape_cheatsheet(slug)
    
    if cheatsheet_data:
        output_path = f'./output/cheatsheet/{slug}.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cheatsheet_data, f, indent=2)
        print(f"✅ Saved {len(cheatsheet_data)} units to {output_path}")
    else:
        print(f"❌ Failed to scrape {slug}")
    
    # Add a random delay between 2 and 5 seconds to avoid detection
    delay = randint(2, 5)
    print(f"Sleeping for {delay} seconds...")
    time.sleep(delay)

print("✨ All dojos processed!")
