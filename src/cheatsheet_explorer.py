import os
import json
import re
import difflib
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import html

# Initialize rich console
console = Console()

def load_dojos():
    """Load dojos from all_dojos.json"""
    with open('./output/all_dojos.json', 'r') as f:
        return json.load(f)

def search_dojos(query, dojos):
    """Fuzzy search for dojos matching query"""
    matches = []
    for slug, name in dojos.items():
        # Calculate match score for both name and slug
        name_score = difflib.SequenceMatcher(None, query.lower(), name.lower()).ratio()
        slug_score = difflib.SequenceMatcher(None, query.lower(), slug.lower()).ratio()
        score = max(name_score, slug_score)
        if score > 0.5:  # Only consider reasonable matches
            matches.append((score, name, slug))
    
    # Sort by best match first
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches

def display_matches(matches):
    """Display search results in a table"""
    if not matches:
        console.print("[bold red]❌ No matches found[/bold red]")
        return False
    
    table = Table(title="Matching Dojos", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Name", style="green")
    table.add_column("Slug", style="yellow")
    
    for i, (score, name, slug) in enumerate(matches[:10], 1):  # Show top 10 matches
        table.add_row(str(i), name, slug)
    
    console.print(table)
    return True

def load_cheatsheet(slug):
    """Load cheatsheet for a specific dojo"""
    path = f"./output/cheatsheet/{slug}.json"
    if not os.path.exists(path):
        console.print(f"[bold red]❌ Cheatsheet not found for {slug}[/bold red]")
        return None
    
    with open(path, 'r') as f:
        return json.load(f)

def display_terminal(cheatsheet, dojo_name):
    """Display cheatsheet in terminal with rich formatting"""
    console.print(f"\n[bold cyan]📝 Cheatsheet for {dojo_name}[/bold cyan]\n")
    
    for section in cheatsheet:
        table = Table(title=section['name'], show_header=True, 
                      header_style="bold yellow", box=None)
        table.add_column("Key", style="cyan", width=20)
        table.add_column("Description", style="white")
        
        for command in section['commands']:
            table.add_row(command['key'], command['description'])
        
        console.print(table)
        console.print()  # Add space between sections

def generate_markdown(cheatsheet, dojo_name, slug):
    """Generate markdown file for cheatsheet"""
    os.makedirs('./data', exist_ok=True)
    filename = f"./data/{slug}.md"
    
    md_content = f"# {dojo_name} Cheatsheet\n\n"
    
    for section in cheatsheet:
        md_content += f"## {section['name']}\n\n"
        md_content += "| Key | Description |\n"
        md_content += "|-----|-------------|\n"
        
        for command in section['commands']:
            # Escape pipes in markdown
            key = command['key'].replace('|', '&#124;')
            desc = command['description'].replace('|', '&#124;')
            md_content += f"| `{key}` | {desc} |\n"
        
        md_content += "\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return filename

def generate_html(cheatsheet, dojo_name, slug):
    """Generate HTML file for cheatsheet"""
    os.makedirs('./data', exist_ok=True)
    filename = f"./data/{slug}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{dojo_name} Cheatsheet</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th {{ background-color: #f8f9fa; text-align: left; }}
            td, th {{ padding: 8px; border: 1px solid #ddd; }}
            .key {{ font-family: monospace; background-color: #f1f8ff; }}
        </style>
    </head>
    <body>
        <h1>{dojo_name} Cheatsheet</h1>
    """
    
    for section in cheatsheet:
        html_content += f"<h2>{html.escape(section['name'])}</h2>\n"
        html_content += "<table>\n"
        html_content += "  <tr><th>Key</th><th>Description</th></tr>\n"
        
        for command in section['commands']:
            html_content += "  <tr>\n"
            html_content += f"    <td class='key'>{html.escape(command['key'])}</td>\n"
            html_content += f"    <td>{html.escape(command['description'])}</td>\n"
            html_content += "  </tr>\n"
        
        html_content += "</table>\n"
    
    html_content += "</body>\n</html>"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def main():
    console.print("[bold green]🚀 ShortcutFoo Cheatsheet Explorer[/bold green]\n")
    
    # Load dojos
    dojos = load_dojos()
    
    # Search loop
    while True:
        query = Prompt.ask("🔍 Search for a dojo", default="vscode")
        matches = search_dojos(query, dojos)
        
        if not display_matches(matches):
            continue
            
        try:
            choice = int(Prompt.ask("Select a dojo (enter ID)", choices=[str(i) for i in range(1, len(matches)+1)]))
            _, name, slug = matches[choice-1]
            break
        except (ValueError, IndexError):
            console.print("[bold red]❌ Invalid selection. Please try again.[/bold red]")
    
    # Load cheatsheet
    cheatsheet = load_cheatsheet(slug)
    if not cheatsheet:
        return
    
    # Output format selection
    format_choice = Prompt.ask(
        "📤 Choose output format",
        choices=["terminal", "markdown", "html"],
        default="terminal"
    )
    
    # Generate output
    if format_choice == "terminal":
        display_terminal(cheatsheet, name)
        console.print(f"\n[bold green]✅ Displayed {name} cheatsheet in terminal[/bold green]")
    else:
        if format_choice == "markdown":
            filename = generate_markdown(cheatsheet, name, slug)
        else:  # html
            filename = generate_html(cheatsheet, name, slug)
        
        console.print(f"\n[bold green]✅ Saved {name} cheatsheet to [cyan]{os.path.abspath(filename)}[/cyan][/bold green]")

if __name__ == "__main__":
    main()
