#!/usr/bin/env python3
"""
Build script for OpenInstructions Catalog.
Validates and processes YAML files into a structured catalog.
"""

import os
import sys
import glob
import json
import shutil
import logging
from pathlib import Path
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone  # Import timezone instead of UTC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("catalog-builder")

# Configuration
CATALOG_VERSION = "0.1.0"
DIST_DIR = "dist"
SCHEMA_DIR = "schemas"
PROJECT_TYPES_DIR = "project_types"

def setup_output_directory() -> None:
    """Create or clean the output directory."""
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    log.info(f"Created output directory: {DIST_DIR}")

def load_yaml_file(file_path: str) -> Dict:
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        log.error(f"Error loading YAML file {file_path}: {e}")
        return {}

def validate_yaml_file(file_path: str, schema: Optional[Dict] = None) -> bool:
    """Validate a YAML file against a schema if provided."""
    try:
        data = load_yaml_file(file_path)
        if not data:
            log.error(f"Empty or invalid YAML file: {file_path}")
            return False
        
        # Basic validation
        if 'catalog_version' not in data:
            log.error(f"Missing catalog_version in {file_path}")
            return False
        
        if 'version' not in data:
            log.error(f"Missing version in {file_path}")
            return False
        
        # More detailed schema validation could be added here
        
        log.info(f"Validated: {file_path}")
        return True
    except Exception as e:
        log.error(f"Validation error for {file_path}: {e}")
        return False

def collect_instruction_files() -> List[str]:
    """Find all YAML files in the project directory."""
    yaml_files = []
    for extension in ('*.yaml', '*.yml'):
        yaml_files.extend(glob.glob(f"{PROJECT_TYPES_DIR}/**/{extension}", recursive=True))
    
    log.info(f"Found {len(yaml_files)} YAML files")
    return yaml_files

def build_catalog_index(yaml_files: List[str]) -> Dict:
    """Build a structured index of the catalog."""
    catalog = {
        "version": CATALOG_VERSION,
        "projects": {},
        "updated_at": None
    }
    
    for file_path in yaml_files:
        try:
            data = load_yaml_file(file_path)
            if not data:
                continue
                
            # Extract project type from path
            parts = file_path.split('/')
            if len(parts) < 3:
                continue
                
            project_type = parts[1]  # Assuming project_types/<type>/...
            
            # Initialize project type if not exists
            if project_type not in catalog["projects"]:
                catalog["projects"][project_type] = []
            
            # Add file info to catalog
            catalog["projects"][project_type].append({
                "path": file_path,
                "title": data.get("title", "Untitled"),
                "description": data.get("description", ""),
                "version": data.get("version", "0.0.0"),
                "catalog_version": data.get("catalog_version", "0.0.0")
            })
            
        except Exception as e:
            log.error(f"Error processing {file_path}: {e}")
    
    # Add timestamp - use datetime.now(timezone.utc) instead of UTC
    catalog["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    return catalog

def copy_files_to_dist(yaml_files: List[str]) -> None:
    """Copy original YAML files to the distribution directory."""
    for file_path in yaml_files:
        dest_path = os.path.join(DIST_DIR, file_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(file_path, dest_path)
    
    log.info(f"Copied {len(yaml_files)} files to {DIST_DIR}")

def main() -> int:
    """Main build process."""
    log.info("Starting catalog build process")
    
    # Set up output directory
    setup_output_directory()
    
    # Collect YAML files
    yaml_files = collect_instruction_files()
    
    # Validate files
    valid_files = [f for f in yaml_files if validate_yaml_file(f)]
    if len(valid_files) != len(yaml_files):
        log.warning(f"{len(yaml_files) - len(valid_files)} files failed validation")
    
    # Build catalog index
    catalog = build_catalog_index(valid_files)
    
    # Write catalog index
    with open(os.path.join(DIST_DIR, "catalog.json"), 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    
    # Copy all valid files to dist
    copy_files_to_dist(valid_files)
    
    # Also copy schema files if they exist
    if os.path.exists(SCHEMA_DIR):
        schema_files = glob.glob(f"{SCHEMA_DIR}/**/*.yaml", recursive=True)
        schema_files.extend(glob.glob(f"{SCHEMA_DIR}/**/*.yml", recursive=True))
        schema_files.extend(glob.glob(f"{SCHEMA_DIR}/**/*.json", recursive=True))
        for file_path in schema_files:
            dest_path = os.path.join(DIST_DIR, file_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(file_path, dest_path)
        log.info(f"Copied {len(schema_files)} schema files")
    
    # Generate a simple HTML index for viewing
    generate_html_index(catalog)
    
    log.info("Catalog build completed successfully")
    return 0

def generate_html_index(catalog: Dict) -> None:
    """Generate a simple HTML index page for browsing the catalog."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenInstructions Catalog v{catalog["version"]}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ margin-top: 1.5em; }}
        .project-type {{ margin-bottom: 30px; }}
        .instruction {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .instruction h3 {{ margin-top: 0; }}
        .meta {{ color: #666; font-size: 0.9em; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>OpenInstructions Catalog</h1>
    <p>Version: {catalog["version"]} (Updated: {catalog["updated_at"]})</p>
    
    <div class="catalog-content">
"""
    
    # Add each project type
    for project_type, instructions in catalog["projects"].items():
        html += f"""
        <div class="project-type">
            <h2>{project_type.replace('_', ' ').title()}</h2>
"""
        
        # Add each instruction
        for instruction in instructions:
            html += f"""
            <div class="instruction">
                <h3>{instruction["title"]}</h3>
                <p>{instruction["description"]}</p>
                <p class="meta">
                    Version: {instruction["version"]} | 
                    Catalog Version: {instruction["catalog_version"]} | 
                    <a href="{instruction["path"]}">View YAML</a>
                </p>
            </div>
"""
        
        html += """
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    with open(os.path.join(DIST_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)
    
    log.info("Generated HTML index page")

if __name__ == "__main__":
    sys.exit(main()) 