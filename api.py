import json
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

BASE_DIR = Path(__file__).parent
CHEATSHEET_DIR = Path("output/cheatsheet")

def load_data(file_path):
    path = BASE_DIR / file_path  
    # path = file_path  

    data = json.loads(path.read_text())
    return data

def standard_name(name: str) -> str: 
    return "_".join(name.split()).lower()


app = FastAPI()

@app.get("/")
def list_dojo():
    file_path = "output/all_dojos.json"
    data = load_data(file_path)
    return data

@app.get("/dojo")
def list_dojo(
    filter: Optional[str] = Query(None, description="name or slug"),
    search: Optional[str] = Query(None, description="search for dojo using slug or name")
    ):
    valid_filter = ["name", "slug"]
    file_path = "output/all_dojos.json"
    data = load_data(file_path)
    data_list = data
    if filter:
        if filter not in valid_filter:
            raise HTTPException(status_code=404, detail=f"Invalid Query choose from {valid_filter}")
        
        if filter == "slug":
            data_list = list(data.keys())
        elif filter == "name":
            data_list = list(data.values())
        else:
            data_list = data
        
    
    if search:
        search = standard_name(search)  

        if filter == "name":
            data_list = [v for v in data_list if search in standard_name(v)]
        elif filter == "slug":
            data_list = [k for k in data_list if search in k]
        else:
            data_list = {
                k: v for k, v in data_list.items()
                if search in k or search in standard_name(str(v))
            }
    return data_list

@app.get("/dojo/{slug}")
def cheatsheet_slug(
    slug: str
    
    ):
    data_path = "output/all_dojos.json"
    data = load_data(data_path)
    
    if slug not in list(data.keys()):
        return HTTPException(status_code=404, detail="invalid slug")
    
    cheatsheet_path = CHEATSHEET_DIR / f"{slug}.json"
    cheatsheet = load_data(cheatsheet_path)
    return cheatsheet

@app.get("/dojo/{slug}/sections")
def cheatsheet_sections(
    slug: str,
    search: Optional[str] = Query(None, description="search in sections")
    
    ):
    data_path = "output/all_dojos.json"
    data = load_data(data_path)
    
    if slug not in list(data.keys()):
        return HTTPException(status_code=404, detail="invalid slug")
    
    cheatsheet_path = CHEATSHEET_DIR / f"{slug}.json"
    cheatsheet = load_data(cheatsheet_path)
    
    section_names = [section["name"] for section in cheatsheet if "name" in section]
    

    if search:
        search_lower = search.lower()  # lowercase search string
        # Filter sections by lowercase comparison, but keep original names
        section_names = [
            name for name in section_names
            if search_lower in name.lower()
        ]
        
    return section_names

