import streamlit as st
import json
import os

st.set_page_config(
    page_title="ShortcutFoo Cheatsheet Dashboard",
    page_icon=":material/bookmark_manager:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 20px !important;
        scrollbar-color: #444 #1a1a1a;
        scrollbar-width: thin;
    }

    /* Scrollbar styling for modern browsers (Chrome, Edge, Safari) */
    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    ::-webkit-scrollbar-thumb {
        background-color: #444;
        border-radius: 6px;
        border: 2px solid #1a1a1a;
    }

    ::-webkit-scrollbar-thumb:hover {
        background-color: #666;
    }

    .download-button {
        display: inline-block;
        padding: 8px 16px;
        background: #4a90e2;
        color: white;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.95rem;
        transition: background 0.2s ease;
    }

    .download-button:hover {
        background: #357ABD;
    }

    .download-button i {
        margin-right: 6px;
    }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)


@st.cache_data
def load_dojos():
    try:
        with open('./output/all_dojos.json', 'r') as f:
            return json.load(f)
    except Exception:
        st.error("Dojos file not found. Please run the scraper first.")
        return {}

def load_cheatsheet(slug):
    path = f"./output/cheatsheet/{slug}.json"
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def get_placeholder_description(name):
    descriptions = {
        "vscode": "Visual Studio Code keyboard shortcuts for efficient coding.",
        "git": "Essential Git commands for version control.",
        "bash": "Bash shell commands for Linux/macOS.",
        "chrome": "Chrome browser shortcuts for developers.",
        "intellij": "IntelliJ IDEA shortcuts for Java development.",
        "sublime": "Sublime Text editor shortcuts.",
        "excel": "Microsoft Excel shortcuts for data manipulation.",
        "atom": "Atom text editor shortcuts.",
        "emacs": "Emacs editor commands.",
        "vim": "Vim editor commands for power users."
    }
    for key, desc in descriptions.items():
        if key in name.lower():
            return desc
    return f"Keyboard shortcuts and commands for {name}."

def generate_html_content(cheatsheet, dojo_name):
    import html

    def format_keys(raw):
        key_map = {
            '^': 'Ctrl',
            '⇧': 'Shift',
            '⌥': 'Alt',
            '⌘': 'Cmd',
            '↵': 'Enter',
            '⎋': 'Esc',
            '⇥': 'Tab',
            '←': 'Left',
            '→': 'Right',
            '↑': 'Up',
            '↓': 'Down',
            '␣': 'Space',
            '+': '+'
        }

        parts = []
        buffer = ""
        for char in raw:
            if char in key_map:
                if buffer:
                    parts.append(buffer)
                    buffer = ""
                parts.append(key_map[char])
            else:
                buffer += char
        if buffer:
            parts.append(buffer)

        return ' '.join(f"<kbd>{html.escape(p.strip())}</kbd>" for p in parts if p.strip())

    template_path = os.path.join("src", "template.html")
    if not os.path.exists(template_path):
        return f"<h1>Error: HTML template not found at {template_path}</h1>"

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    section_html = ""
    for section in cheatsheet:
        rows = ""
        for cmd in section['commands']:
            formatted_keys = format_keys(cmd['key'])
            rows += f"<tr><td>{formatted_keys}</td><td>{html.escape(cmd['description'])}</td></tr>"
        section_html += f"<h2>{html.escape(section['name'])}</h2><table><tr><th>Key</th><th>Description</th></tr>{rows}</table>"

    filled = template.replace("{{ dojo_name }}", html.escape(dojo_name)).replace("{{ sections }}", section_html)
    return filled




def generate_markdown_content(cheatsheet, dojo_name):
    md = f"# {dojo_name} Cheatsheet\n\n"
    for section in cheatsheet:
        md += f"## {section['name']}\n\n| Key | Description |\n|-----|-------------|\n"
        for cmd in section['commands']:
            key = cmd['key'].replace('|', '&#124;')
            desc = cmd['description'].replace('|', '&#124;')
            md += f"| `{key}` | {desc} |\n"
        md += "\n"
    return md

def main():
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
        st.session_state.selected_dojo = None

    if st.session_state.current_page == "dashboard":
        st.title("⌘ ShortcutFoo Cheatsheets")
        st.caption("UI to explore and download developer cheatsheets")

        dojos = load_dojos()
        if not dojos:
            return

        search_query = st.text_input("Search", placeholder="e.g. vim, git, vscode")
        filtered_dojos = [(name, slug) for slug, name in dojos.items()
                        if not search_query or search_query.lower() in name.lower() or search_query.lower() in slug.lower()]
        filtered_dojos.sort(key=lambda x: x[0].lower())

        cols = st.columns(3)
        for idx, (name, slug) in enumerate(filtered_dojos):
            with cols[idx % 3]:
                with st.expander(f"{name} ({slug})"):
                    st.write(get_placeholder_description(name))
                    cheatsheet = load_cheatsheet(slug)
                    buttons = st.columns(3)
                    with buttons[0]:
                        if cheatsheet:
                            if st.button("View", key=f"view_{slug}"):
                                st.session_state.selected_dojo = slug
                                st.session_state.current_page = "viewer"
                                st.rerun()
                    with buttons[1]:
                        if cheatsheet:
                            html = generate_html_content(cheatsheet, name)
                            st.download_button("🗁 HTML", html, f"{slug}_cheatsheet.html", mime="text/html")
                    with buttons[2]:
                        if cheatsheet:
                            md = generate_markdown_content(cheatsheet, name)
                            st.download_button("🗁 Markdown", md, f"{slug}_cheatsheet.md", mime="text/markdown")

    elif st.session_state.current_page == "viewer":
        dojo_name = st.session_state.selected_dojo
        dojos = load_dojos()
        name = dojos.get(dojo_name, dojo_name)
        cheatsheet = load_cheatsheet(dojo_name)
        
        if cheatsheet:
            st.button("← Back", on_click=lambda: st.session_state.update({"current_page": "dashboard"}))
            st.markdown(f"### {name} Cheatsheet")

            html_content = generate_html_content(cheatsheet, name)
            st.markdown(
                html_content,
                unsafe_allow_html=True
            )
        else:
            st.error(f"Cheatsheet not found for {dojo_name}")

if __name__ == "__main__":
    main()
