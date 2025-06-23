# ShortcutFoo Cheatsheet Scraper & Dashboard

A minimal and extensible tool for accessing developer cheatsheets from [ShortcutFoo.com](https://www.shortcutfoo.com). This project enables you to browse, search, and download well-formatted keyboard shortcuts for various tools and technologies — all within a web-based dashboard.

While all data is already scraped and included in the repository, the scraping script is provided in case you want to run it manually or maintain a local version.

---

## Features

* Clean Streamlit-based web dashboard to explore cheatsheets
* Search across available tools and editors
* Download cheatsheets in **HTML** or **Markdown** formats
* Built-in dataset for immediate use, with optional re-scraping
* Backend scraping utilities available in the repo
* Cross-platform support (Windows/macOS/Linux)

---

## Prerequisites

* Python 3.8 or higher
* pip package manager

---

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/viraj-sh/ShortcutFoo-Cheatsheet-Scraper.git
cd ShortcutFoo-Cheatsheet-Scraper
```

### Create and activate the virtual environment

**Windows**:

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

Thanks for the clarification! Based on your update, here's the revised **Usage** section that accurately reflects the setup and expectations for users:

---

## Usage

### Option 1: Launch the Dashboard (recommended)

```bash
streamlit run src/dashboard.py
```

This opens the web-based dashboard in your browser. It uses the pre-scraped data already included in the repository.

> The cheatsheet data is kept **up-to-date** in the repository — no scraping needed. The scraping script is run periodically, and the results are pushed to GitHub.

---

### Option 2: Scrape the data yourself (advanced / optional)

If you'd like to scrape the data from ShortcutFoo manually (e.g., for custom use or to ensure it's the most recent), run:

```bash
python src/scrape.py
```

This will:

* Fetch the list of available dojos
* Scrape and save all cheatsheets to `output/cheatsheet/`

> ⚠️ This is **optional**. Scraping is **not required** to use the dashboard.
> Running this script locally will not auto-update your data — you’ll need to re-run it whenever you want to refresh.

---

## Future Improvements

* ~~Web dashboard for browsing and downloads~~
* Improved visuals and responsiveness
* Enhanced filtering and tagging system
* PDF export support
* Full-text search within individual cheatsheets
* Offline mode bundling
* Custom cheatsheet creation and sharing

---

## Disclaimer

This tool is intended for **educational and accessibility purposes only**. All cheatsheet content is publicly available from [ShortcutFoo.com](https://www.shortcutfoo.com). We do not scrape any gated or paid content.

* We access only open-access content
* We do not replicate proprietary materials
* Users are encouraged to support the original authors
* Use this project responsibly

---

## Contributing

Contributions are welcome! Feel free to open an issue or pull request.

Steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add feature"`
4. Push to your fork: `git push origin feature/my-feature`
5. Submit a pull request

---

Built with Python and Streamlit.