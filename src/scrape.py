import os
import re
import json
import requests
import time
import random
from bs4 import BeautifulSoup

# Configuration
DOJOS_URL = 'https://www.shortcutfoo.com/app/dojos'
OUTPUT_DIR = './output'
DOJOS_FILE = os.path.join(OUTPUT_DIR, 'all_dojos.json')
CHEATSHEET_DIR = os.path.join(OUTPUT_DIR, 'cheatsheet')
MIN_DELAY = 2  # seconds
MAX_DELAY = 5  # seconds

def create_dirs():
    """Create necessary output directories"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CHEATSHEET_DIR, exist_ok=True)

def scrape_all_dojos():
    """Fetch and extract all dojos from main page"""
    print("🌐 Fetching dojos list...")
    try:
        response = requests.get(DOJOS_URL)
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
        return {dojo['slug']: dojo['name'] for dojo in sorted(dojo_list, key=lambda x: x['slug'])}
    
    except requests.exceptions.RequestException as e:
        print(f"🚨 Network error: {e}")
        return {}
    except (ValueError, json.JSONDecodeError) as e:
        print(f"🚨 Data extraction error: {e}")
        return {}

def scrape_cheatsheet(slug):
    """Scrape cheatsheet for a single dojo"""
    url = f'https://www.shortcutfoo.com/app/dojos/{slug}/cheatsheet'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        units = []
        for unit_section in soup.select('div.pt-10'):
            unit_title = unit_section.select_one('h2.text-xl')
            if not unit_title:
                continue
                
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
        return None
    except Exception as e:
        print(f"🚨 Processing error for {slug}: {e}")
        return None

def save_data(data, path):
    """Save data to JSON file"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved to {os.path.abspath(path)}")

def main():
    create_dirs()
    
    # Step 1: Scrape all dojos
    dojos = scrape_all_dojos()
    if not dojos:
        print("❌ Aborting: No dojos found")
        return
    
    save_data(dojos, DOJOS_FILE)
    print(f"✅ Found {len(dojos)} dojos")
    
    # Step 2: Scrape cheatsheets for each dojo
    total = len(dojos)
    for i, (slug, name) in enumerate(dojos.items(), 1):
        print(f"\n⏳ [{i}/{total}] Scraping {name} ({slug})...")
        
        # Check if we already have this cheatsheet
        cheatsheet_path = os.path.join(CHEATSHEET_DIR, f"{slug}.json")
        if os.path.exists(cheatsheet_path):
            print(f"🔍 Cheatsheet already exists, skipping...")
            continue
            
        cheatsheet_data = scrape_cheatsheet(slug)
        
        if cheatsheet_data:
            save_data(cheatsheet_data, cheatsheet_path)
            print(f"✅ Saved {len(cheatsheet_data)} sections")
        else:
            print(f"❌ Failed to scrape {slug}")
        
        # Add random delay between requests
        if i < total:  # Skip delay after last item
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"⏱️ Sleeping for {delay} seconds...")
            time.sleep(delay)
    
    print("\n✨ All dojos processed!")

if __name__ == "__main__":
    main()
