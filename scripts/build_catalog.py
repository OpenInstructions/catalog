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

def get_shared_footer():
    """Return the shared footer HTML to be used across all pages."""
    return """    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>OpenInstructions</h3>
                    <p>An open-source initiative for structured, versioned instructions optimized for Large Language Models and developers.</p>
                    <p>The 'OpenInstructions' name and branding are reserved for this project and its officially authorized derivatives.</p>
                </div>
                <div class="footer-col">
                    <h3>Resources</h3>
                    <ul class="footer-links">
                        <li><a href="https://github.com/OpenInstructions/catalog"><i class="fa-solid fa-chevron-right"></i> GitHub Repository</a></li>
                        <li><a href="https://github.com/OpenInstructions/catalog/blob/main/CONTRIBUTING.md"><i class="fa-solid fa-chevron-right"></i> Contributing Guide</a></li>
                        <li><a href="https://github.com/OpenInstructions/catalog/blob/main/SPEC.md"><i class="fa-solid fa-chevron-right"></i> Specification</a></li>
                        <li><a href="https://github.com/OpenInstructions/catalog/blob/main/LICENSE"><i class="fa-solid fa-chevron-right"></i> License</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Project</h3>
                    <ul class="footer-links">
                        <li><a href="index.html#features"><i class="fa-solid fa-chevron-right"></i> Features</a></li>
                        <li><a href="index.html#getting-started"><i class="fa-solid fa-chevron-right"></i> Getting Started</a></li>
                        <li><a href="index.html#catalog"><i class="fa-solid fa-chevron-right"></i> Catalog</a></li>
                        <li><a href="index.html#community"><i class="fa-solid fa-chevron-right"></i> Community</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 OpenInstructions. MIT License.</p>
            </div>
        </div>
    </footer>"""

def get_shared_footer_css():
    """Return the shared footer CSS to be used across all pages."""
    return """
        /* Footer */
        footer {{
            background-color: #2b2d42;
            color: white;
            padding: 5rem 0 1rem;
            position: relative;
        }}
        
        footer::before {{
            content: '';
            position: absolute;
            top: -50px;
            left: 0;
            right: 0;
            height: 100px;
            background: #2b2d42;
            clip-path: ellipse(75% 50% at 50% 0%);
            z-index: -1;
        }}
        
        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
        }}
        
        .footer-col {{
            display: flex;
            flex-direction: column;
        }}
        
        .footer-col h3 {{
            font-size: 1.25rem;
            margin-bottom: 1.5rem;
            position: relative;
            padding-bottom: 0.75rem;
            color: white;
        }}
        
        .footer-col h3:after {{
            content: '';
            position: absolute;
            left: 0;
            bottom: 0;
            width: 40px;
            height: 2px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        }}
        
        .footer-col p {{
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 1rem;
            line-height: 1.7;
        }}
        
        .footer-links {{
            list-style: none;
            padding-left: 0;
        }}
        
        .footer-links li {{
            margin-bottom: 0.75rem;
        }}
        
        .footer-links a {{
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.2s, padding-left 0.2s;
            display: flex;
            align-items: center;
        }}
        
        .footer-links a:hover {{
            color: white;
            padding-left: 5px;
            text-decoration: none;
        }}
        
        .footer-links a i {{
            margin-right: 0.5rem;
            font-size: 0.8rem;
            color: var(--primary-light);
        }}
        
        .footer-bottom {{
            margin-top: 2rem;
            text-align: center;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.8rem;
        }}
    """

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
    
    # Generate a comprehensive HTML landing page for the OpenInstructions project
    generate_html_index(catalog)
    
    log.info("Catalog build completed successfully")
    return 0

def generate_html_index(catalog: Dict) -> None:
    """Generate a comprehensive HTML landing page for the OpenInstructions project."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenInstructions - Structured Instructions for LLMs</title>
    <meta name="description" content="OpenInstructions is an open-source catalog of phase-based instructions for Large Language Models (LLMs) and developers to create and refactor development projects.">
    <meta property="og:title" content="OpenInstructions - Structured Instructions for LLMs">
    <meta property="og:description" content="A public catalog of structured, versioned instructions for Large Language Models">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://openinstructions.org">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📋</text></svg>">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
    <style>
        :root {{
            --primary-color: #4361ee;
            --primary-light: #4895ef;
            --secondary-color: #7209b7;
            --secondary-light: #9d4edd;
            --accent-color: #f72585;
            --text-color: #2b2d42;
            --text-light: #6c757d;
            --background-color: #fff;
            --light-bg-color: #f8f9fa;
            --card-bg-color: #ffffff;
            --border-color: #e9ecef;
            --header-height: 70px;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
            --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
            --border-radius: 8px;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
        }}
        
        .container {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 700;
            line-height: 1.3;
        }}
        
        p {{
            color: var(--text-light);
            margin-bottom: 1.5rem;
        }}
        
        a {{
            color: var(--primary-color);
            text-decoration: none;
            transition: color 0.2s, transform 0.2s;
        }}
        
        a:hover {{
            color: var(--primary-light);
        }}
        
        /* Header */
        header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: var(--shadow-sm);
            z-index: 1000;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
        }}
        
        nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 100%;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            font-weight: 700;
            font-size: 1.5rem;
            color: var(--text-color);
            text-decoration: none;
            height: 100%;
        }}
        
        .logo i {{
            font-size: 1.75rem;
            margin-right: 0.75rem;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .logo span {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .nav-links {{
            display: flex;
            list-style: none;
            height: 100%;
            align-items: center;
        }}
        
        .nav-links li {{
            margin-left: 2rem;
            height: 100%;
            display: flex;
            align-items: center;
        }}
        
        .nav-links a {{
            color: var(--text-color);
            text-decoration: none;
            font-weight: 500;
            font-size: 1rem;
            transition: color 0.2s;
            position: relative;
            padding-bottom: 5px;
        }}
        
        .nav-links a:after {{
            content: '';
            position: absolute;
            width: 0;
            height: 2px;
            bottom: 0;
            left: 0;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            transition: width 0.3s ease;
        }}
        
        .nav-links a:hover:after {{
            width: 100%;
        }}
        
        .nav-links a.github-link:after {{
            display: none;
        }}
        
        .nav-links a:hover {{
            color: var(--primary-color);
        }}
        
        .github-link {{
            display: flex;
            align-items: center;
            background-color: var(--primary-color);
            color: white !important;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .github-link:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        .github-link i {{
            margin-right: 0.5rem;
        }}
        
        /* Hero Section */
        .hero {{
            padding: calc(var(--header-height) + 5rem) 0 5rem;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect fill="none" width="100" height="100"/><rect fill-opacity="0.05" x="25" y="25" width="50" height="50" transform="rotate(45 50 50)"/></svg>');
            background-size: 30px 30px;
            opacity: 0.3;
        }}
        
        .hero h1 {{
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }}
        
        .hero p {{
            font-size: 1.25rem;
            max-width: 800px;
            margin: 0 auto 2rem;
            color: rgba(255, 255, 255, 0.85);
        }}
        
        .hero-buttons {{
            display: flex;
            justify-content: center;
            gap: 1rem;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.75rem 1.75rem;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            border-radius: 50px;
            transition: all 0.3s;
        }}
        
        .btn i {{
            margin-right: 0.5rem;
        }}
        
        .btn-primary {{
            background-color: white;
            color: var(--primary-color);
            box-shadow: var(--shadow-md);
        }}
        
        .btn-primary:hover {{
            background-color: rgba(255, 255, 255, 0.9);
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg);
        }}
        
        .btn-secondary {{
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        .btn-secondary:hover {{
            background-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
        }}
        
        /* Features Section */
        .features {{
            padding: 6rem 0;
            background-color: var(--light-bg-color);
            position: relative;
        }}
        
        .features::before {{
            content: '';
            position: absolute;
            top: -50px;
            left: 0;
            right: 0;
            height: 100px;
            background: var(--light-bg-color);
            clip-path: ellipse(75% 50% at 50% 100%);
            z-index: -1;
        }}
        
        .section-title {{
            text-align: center;
            margin-bottom: 1rem;
            font-size: 2.5rem;
            color: var(--text-color);
        }}
        
        .section-subtitle {{
            text-align: center;
            max-width: 700px;
            margin: 0 auto 4rem;
            color: var(--text-light);
            font-size: 1.1rem;
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
        }}
        
        .feature-card {{
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            padding: 2.5rem;
            box-shadow: var(--shadow-sm);
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        
        .feature-card:hover {{
            transform: translateY(-10px);
            box-shadow: var(--shadow-lg);
        }}
        
        .feature-card::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(to bottom, var(--primary-color), var(--secondary-color));
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .feature-card:hover::after {{
            opacity: 1;
        }}
        
        .feature-icon {{
            font-size: 2.25rem;
            margin-bottom: 1.5rem;
            height: 60px;
            width: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            color: white;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            box-shadow: var(--shadow-md);
        }}
        
        .feature-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--text-color);
        }}
        
        .feature-card p {{
            color: var(--text-light);
            line-height: 1.7;
        }}
        
        /* Getting Started Section */
        .getting-started {{
            padding: 6rem 0;
            background-color: white;
        }}
        
        .steps {{
            counter-reset: step;
            max-width: 850px;
            margin: 0 auto;
        }}
        
        .step {{
            position: relative;
            margin-bottom: 3.5rem;
            padding-left: 4rem;
            transition: transform 0.3s;
        }}
        
        .step:last-child {{
            margin-bottom: 0;
        }}
        
        .step::before {{
            counter-increment: step;
            content: counter(step);
            position: absolute;
            left: 0;
            top: 0;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            width: 2.5rem;
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            font-weight: 600;
            box-shadow: var(--shadow-md);
        }}
        
        .step::after {{
            content: '';
            position: absolute;
            left: 1.25rem;
            top: 2.5rem;
            bottom: -3.5rem;
            width: 1px;
            background: linear-gradient(to bottom, var(--primary-color), transparent);
        }}
        
        .step:last-child::after {{
            display: none;
        }}
        
        .step:hover {{
            transform: translateX(5px);
        }}
        
        .step h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--text-color);
        }}
        
        .step p {{
            margin-bottom: 1rem;
            color: var(--text-light);
        }}
        
        .step ul {{
            margin-bottom: 1.5rem;
            color: var(--text-light);
            padding-left: 1.5rem;
        }}
        
        .step li {{
            margin-bottom: 0.5rem;
        }}
        
        .step code {{
            background-color: var(--light-bg-color);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9rem;
            color: var(--primary-color);
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
        }}
        
        .step pre {{
            background-color: var(--light-bg-color);
            padding: 1.25rem;
            border-radius: var(--border-radius);
            overflow-x: auto;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            color: var(--text-color);
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
        }}
        
        /* Catalog Section */
        .catalog {{
            padding: 6rem 0;
            background-color: var(--light-bg-color);
            position: relative;
        }}
        
        .catalog::before {{
            content: '';
            position: absolute;
            top: -50px;
            left: 0;
            right: 0;
            height: 100px;
            background: white;
            clip-path: ellipse(75% 50% at 50% 100%);
            z-index: -1;
        }}
        
        .catalog-version {{
            text-align: center;
            margin-bottom: 3rem;
            color: var(--text-light);
            font-size: 1rem;
            background-color: rgba(0,0,0,0.03);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            display: inline-block;
            position: relative;
            left: 50%;
            transform: translateX(-50%);
        }}
        
        .catalog-version strong {{
            color: var(--primary-color);
        }}
        
        .project-type {{
            margin-bottom: 4rem;
        }}
        
        .project-type h2 {{
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            position: relative;
            display: inline-block;
        }}
        
        .project-type h2:after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 50%;
            height: 3px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            border-radius: 10px;
        }}
        
        .instruction-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        
        .instruction-card {{
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            padding: 1.75rem;
            box-shadow: var(--shadow-sm);
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }}
        
        .instruction-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-md);
        }}
        
        .instruction-card::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .instruction-card:hover::after {{
            opacity: 1;
        }}
        
        .instruction-card h3 {{
            margin-top: 0;
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
            color: var(--text-color);
        }}
        
        .instruction-card p {{
            margin-bottom: 1.25rem;
            color: var(--text-light);
            line-height: 1.7;
        }}
        
        .meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .version-tag {{
            background-color: rgba(67, 97, 238, 0.1);
            color: var(--primary-color);
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
            border-radius: 50px;
            font-weight: 500;
        }}
        
        .meta a {{
            color: var(--primary-color);
            text-decoration: none;
            display: flex;
            align-items: center;
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        .meta a i {{
            margin-left: 0.3rem;
            transition: transform 0.2s;
        }}
        
        .meta a:hover i {{
            transform: translateX(3px);
        }}
        
        /* Community Section */
        .community {{
            padding: 6rem 0;
            background-color: white;
            position: relative;
        }}
        
        .community::before {{
            content: '';
            position: absolute;
            top: -50px;
            left: 0;
            right: 0;
            height: 100px;
            background: var(--light-bg-color);
            clip-path: ellipse(75% 50% at 50% 100%);
            z-index: -1;
        }}
        
        .community-desc {{
            text-align: center;
            max-width: 700px;
            margin: 0 auto 3rem;
            color: var(--text-light);
            font-size: 1.1rem;
            line-height: 1.7;
        }}
        
        .community-links {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
        }}
        
        .community-link {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: var(--text-color);
            transition: transform 0.3s;
            padding: 2rem;
            border-radius: var(--border-radius);
            background-color: white;
            width: 220px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
        }}
        
        .community-link:hover {{
            transform: translateY(-10px);
            box-shadow: var(--shadow-lg);
        }}
        
        .community-link-icon {{
            width: 70px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
            font-size: 2rem;
            border-radius: 50%;
            color: white;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            box-shadow: var(--shadow-md);
        }}
        
        .community-link h3 {{
            font-size: 1.25rem;
            margin-bottom: 0.75rem;
            color: var(--text-color);
        }}
        
        .community-link p {{
            text-align: center;
            font-size: 0.95rem;
            color: var(--text-light);
            line-height: 1.7;
        }}
        
        /* Specification Section */
        .specification {{
            padding: 6rem 0;
            background-color: var(--light-bg-color);
            position: relative;
        }}
        
        .specification::before {{
            content: '';
            position: absolute;
            top: -50px;
            left: 0;
            right: 0;
            height: 100px;
            background: white;
            clip-path: ellipse(75% 50% at 50% 100%);
            z-index: -1;
        }}
        
        .spec-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
            margin-top: 3rem;
        }}
        
        .spec-card {{
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            padding: 2rem;
            box-shadow: var(--shadow-sm);
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid var(--border-color);
        }}
        
        .spec-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-md);
        }}
        
        .spec-header {{
            margin-bottom: 1.5rem;
        }}
        
        .spec-header h3 {{
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
            color: var(--text-color);
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border-color);
        }}
        
        .spec-header h3 i {{
            margin-right: 0.75rem;
            color: var(--primary-color);
            font-size: 1.25rem;
        }}
        
        .spec-header p {{
            margin-bottom: 0;
            color: var(--text-light);
        }}
        
        .spec-card p {{
            margin-bottom: 1rem;
            color: var(--text-light);
        }}
        
        .spec-card-full {{
            grid-column: span 2;
        }}
        
        /* Schema Table Styles */
        .schema-table-container {{
            overflow-x: auto;
            margin-bottom: 1rem;
        }}
        
        .schema-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }}
        
        .schema-table th {{
            background-color: var(--text-color);
            color: white;
            text-align: left;
            padding: 0.75rem 1rem;
            font-weight: 600;
        }}
        
        .schema-table th:first-child {{
            border-top-left-radius: 6px;
        }}
        
        .schema-table th:last-child {{
            border-top-right-radius: 6px;
        }}
        
        .schema-table td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border-color);
            vertical-align: top;
        }}
        
        .schema-table td code {{
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            font-size: 0.9rem;
            background-color: rgba(0,0,0,0.03);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            color: var(--primary-color);
        }}
        
        .schema-table tr:nth-child(even) {{
            background-color: rgba(0,0,0,0.02);
        }}
        
        .schema-table tr:hover {{
            background-color: rgba(67, 97, 238, 0.05);
        }}
        
        .required {{
            display: inline-block;
            background-color: rgba(67, 97, 238, 0.1);
            color: var(--primary-color);
            font-size: 0.85rem;
            padding: 0.2rem 0.5rem;
            border-radius: 50px;
            font-weight: 500;
        }}
        
        .optional {{
            display: inline-block;
            background-color: rgba(108, 117, 125, 0.1);
            color: var(--text-light);
            font-size: 0.85rem;
            padding: 0.2rem 0.5rem;
            border-radius: 50px;
            font-weight: 500;
        }}
        
        .code-example {{
            background-color: var(--text-color);
            color: #f8f8f2;
            padding: 1.25rem;
            border-radius: var(--border-radius);
            overflow-x: auto;
            font-size: 0.9rem;
            font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            margin-top: 1rem;
        }}
        
        .spec-info {{
            grid-column: span 2;
            background-color: var(--card-bg-color);
            border-radius: var(--border-radius);
            padding: 2rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
            margin-top: 1rem;
        }}
        
        .spec-info-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .spec-info-card {{
            background-color: var(--light-bg-color);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            border: 1px solid var(--border-color);
        }}
        
        .spec-info-card h3 {{
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            color: var(--text-color);
            font-size: 1.2rem;
        }}
        
        .spec-info-card h3 i {{
            margin-right: 0.75rem;
            color: var(--primary-color);
            font-size: 1.1rem;
        }}
        
        .spec-info h3 {{
            margin-bottom: 1rem;
            color: var(--text-color);
            padding-bottom: 0.5rem;
        }}
        
        .spec-info ul {{
            margin-bottom: 1rem;
            color: var(--text-light);
            padding-left: 1.25rem;
        }}
        
        .spec-info li {{
            margin-bottom: 0.75rem;
        }}
        
        .spec-cta {{
            margin-top: 2rem;
            text-align: center;
        }}
        
        @media (max-width: 768px) {{
            .spec-container {{
                grid-template-columns: 1fr;
            }}
            
            .spec-card-full {{
                grid-column: span 1;
            }}
            
            .spec-info {{
                grid-column: span 1;
            }}
            
            .spec-info-container {{
                grid-template-columns: 1fr;
            }}
            
            .nav-links {{
                display: none;
            }}
            
            .page-header h1 {{
                font-size: 2rem;
            }}
            
            .footer-content {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* Footer */
        footer {{
            background-color: #2b2d42;
            color: white;
            padding: 5rem 0 1rem;
            position: relative;
        }}
        
        footer::before {{
            content: '';
            position: absolute;
            top: -50px;
            left: 0;
            right: 0;
            height: 100px;
            background: #2b2d42;
            clip-path: ellipse(75% 50% at 50% 0%);
            z-index: -1;
        }}
        
        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
        }}
        
        .footer-col {{
            display: flex;
            flex-direction: column;
        }}
        
        .footer-col h3 {{
            font-size: 1.25rem;
            margin-bottom: 1.5rem;
            position: relative;
            padding-bottom: 0.75rem;
            color: white;
        }}
        
        .footer-col h3:after {{
            content: '';
            position: absolute;
            left: 0;
            bottom: 0;
            width: 40px;
            height: 2px;
            background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        }}
        
        .footer-col p {{
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 1rem;
            line-height: 1.7;
        }}
        
        .footer-links {{
            list-style: none;
            padding-left: 0;
        }}
        
        .footer-links li {{
            margin-bottom: 0.75rem;
        }}
        
        .footer-links a {{
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: color 0.2s, padding-left 0.2s;
            display: flex;
            align-items: center;
        }}
        
        .footer-links a:hover {{
            color: white;
            padding-left: 5px;
            text-decoration: none;
        }}
        
        .footer-links a i {{
            margin-right: 0.5rem;
            font-size: 0.8rem;
            color: var(--primary-light);
        }}
        
        .footer-bottom {{
            margin-top: 2rem;
            text-align: center;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <div class="container">
            <nav>
                <a href="#" class="logo">
                    <i class="fa-solid fa-clipboard-list"></i>
                    <span>OpenInstructions</span>
                </a>
                <ul class="nav-links">
                    <li><a href="#features">Features</a></li>
                    <li><a href="#getting-started">Getting Started</a></li>
                    <li><a href="#catalog">Catalog</a></li>
                    <li><a href="#specification">Specification</a></li>
                    <li><a href="#community">Community</a></li>
                    <li>
                        <a href="https://github.com/OpenInstructions/catalog" class="github-link" target="_blank">
                            <i class="fa-brands fa-github"></i>
                            GitHub
                        </a>
                    </li>
                </ul>
            </nav>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Structured Instructions for Large Language Models</h1>
            <p>OpenInstructions is an open-source catalog of phase-based instructions for LLMs and developers to create and refactor development projects.</p>
            <div class="hero-buttons">
                <a href="#getting-started" class="btn btn-primary">
                    <i class="fa-solid fa-rocket"></i>
                    Get Started
                </a>
                <a href="https://github.com/OpenInstructions/catalog" class="btn btn-secondary" target="_blank">
                    <i class="fa-brands fa-github"></i>
                    View on GitHub
                </a>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="features">
        <div class="container">
            <h2 class="section-title">Why OpenInstructions?</h2>
            <p class="section-subtitle">OpenInstructions provides developers and LLMs with structured, versioned guidance for efficient project development.</p>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fa-solid fa-layer-group"></i>
                    </div>
                    <h3>Structured</h3>
                    <p>Detailed instructions split by project phase with dependency tracking between phases and tasks for clear implementation guidance.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fa-solid fa-code-branch"></i>
                    </div>
                    <h3>Versioned</h3>
                    <p>Git-based versioning with semantic versioning for instructions and build-time directory structure for reliable access to specific versions.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fa-solid fa-puzzle-piece"></i>
                    </div>
                    <h3>Modular</h3>
                    <p>Support for multiple variants with shared components where appropriate, making it easy to adapt instructions to specific project needs.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fa-solid fa-cube"></i>
                    </div>
                    <h3>Multi-dimensional</h3>
                    <p>Select different options for each variant dimension (e.g., React + GitHub Actions) for flexibility in project configuration and implementation.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fa-solid fa-robot"></i>
                    </div>
                    <h3>AI-Ready</h3>
                    <p>Optimized for LLMs with clear task definitions and examples to ensure consistent and accurate implementation by AI systems.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">
                        <i class="fa-solid fa-users"></i>
                    </div>
                    <h3>Community-Driven</h3>
                    <p>Open to contributions for continuous improvement, ensuring the catalog stays current with industry best practices and emerging technologies.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Getting Started Section -->
    <section class="getting-started" id="getting-started">
        <div class="container">
            <h2 class="section-title">Getting Started</h2>
            <div class="steps">
                <div class="step">
                    <h3>Browse the instructions</h3>
                    <p>Check out our catalog of instructions for various project types:</p>
                    <p><a href="project_types/cli/go/setup.yaml">Go CLI Setup</a> - Initialize a new Go CLI project</p>
                </div>
                <div class="step">
                    <h3>Access via direct URLs</h3>
                    <p>You can access instructions via various patterns:</p>
                    <ul>
                        <li>Latest: <code>https://openinstructions.org/catalog/latest/project_types/cli/go/setup.yaml</code></li>
                        <li>Specific version: <code>https://openinstructions.org/catalog/v1/project_types/cli/go/setup.yaml</code></li>
                    </ul>
                </div>
                <div class="step">
                    <h3>Integrate with your application</h3>
                    <p>Use the OpenInstructions catalog in your own applications:</p>
                    <pre>import yaml
import requests

# Access the CLI setup instructions
setup_url = "https://openinstructions.org/catalog/latest/project_types/cli/go/setup.yaml"
setup = yaml.safe_load(requests.get(setup_url).text)

# Access CI/CD instructions
ci_url = "https://openinstructions.org/catalog/latest/project_types/cli/ci/github_actions/setup.yaml"
ci = yaml.safe_load(requests.get(ci_url).text)

# Process the instructions...
                    </pre>
                </div>
            </div>
        </div>
    </section>

    <!-- Catalog Section -->
    <section class="catalog" id="catalog">
        <div class="container">
            <h2 class="section-title">Instruction Catalog</h2>
            <div class="catalog-version">
                <span>Version: <strong>{catalog["version"]}</strong> (Updated: {catalog["updated_at"].split('T')[0]})</span>
            </div>
"""
    
    # Add each project type
    for project_type, instructions in catalog["projects"].items():
        html += f"""
            <div class="project-type">
                <h2>{project_type.replace('_', ' ').title()}</h2>
                <div class="instruction-cards">
"""
        
        # Add each instruction
        for instruction in instructions:
            description = instruction.get("description", "")
            if len(description) > 100:
                description = description[:100] + "..."
                
            html += f"""
                    <div class="instruction-card">
                        <h3>{instruction["title"]}</h3>
                        <p>{description}</p>
                        <div class="meta">
                            <span class="version-tag">v{instruction["version"]}</span>
                            <a href="{instruction["path"]}">View YAML <i class="fa-solid fa-arrow-right"></i></a>
                        </div>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
    
    html += """
        </div>
    </section>

    <!-- Community Section -->
    <section class="community" id="community">
        <div class="container">
            <h2 class="section-title">Join Our Community</h2>
            <p class="community-desc">OpenInstructions is an open-source initiative. Join us in making instruction-following more structured and effective.</p>
            <div class="community-links">
                <a href="https://github.com/OpenInstructions/catalog" class="community-link" target="_blank">
                    <div class="community-link-icon">
                        <i class="fa-solid fa-star"></i>
                    </div>
                    <h3>Star on GitHub</h3>
                    <p>Show your support by starring our repository and helping us grow</p>
                </a>
                <a href="https://github.com/OpenInstructions/catalog/discussions" class="community-link" target="_blank">
                    <div class="community-link-icon">
                        <i class="fa-solid fa-comments"></i>
                    </div>
                    <h3>Discussions</h3>
                    <p>Join the conversation and share your ideas for improving the catalog</p>
                </a>
                <a href="https://github.com/OpenInstructions/catalog/issues" class="community-link" target="_blank">
                    <div class="community-link-icon">
                        <i class="fa-solid fa-bug"></i>
                    </div>
                    <h3>Issues</h3>
                    <p>Report bugs or request new features to help make the project better</p>
                </a>
                <a href="https://github.com/OpenInstructions/catalog/blob/main/CONTRIBUTING.md" class="community-link" target="_blank">
                    <div class="community-link-icon">
                        <i class="fa-solid fa-code-pull-request"></i>
                    </div>
                    <h3>Contribute</h3>
                    <p>Learn how to contribute to the project and submit your own instructions</p>
                </a>
            </div>
        </div>
    </section>

    <!-- Specification Section -->
    <section class="specification" id="specification">
        <div class="container">
            <h2 class="section-title">Schema Specification</h2>
            <p class="section-subtitle">OpenInstructions uses two primary schema types to define structured instruction sets</p>
            
            <div class="spec-container">
                <div class="spec-card spec-card-full">
                    <div class="spec-header">
                        <h3><i class="fa-solid fa-sitemap"></i> Project Type Root Schema</h3>
                        <p>Defines the structure of a project type with its supported variants and lifecycle phases</p>
                    </div>
                    <div class="schema-table-container">
                        <table class="schema-table">
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><code>catalog_version</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Version of the catalog specification (e.g., "0.1.0")</td>
                                </tr>
                                <tr>
                                    <td><code>project_type</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Project type identifier (e.g., "web_app")</td>
                                </tr>
                                <tr>
                                    <td><code>title</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Human-readable name of the project type</td>
                                </tr>
                                <tr>
                                    <td><code>description</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Description of the project type's purpose</td>
                                </tr>
                                <tr>
                                    <td><code>variants</code></td>
                                    <td>array</td>
                                    <td><span class="required">Required</span></td>
                                    <td>List of variant dimensions available for this project type</td>
                                </tr>
                                <tr>
                                    <td><code>variants[].id</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Variant identifier (e.g., "language", "framework")</td>
                                </tr>
                                <tr>
                                    <td><code>variants[].title</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Human-readable name for this variant dimension</td>
                                </tr>
                                <tr>
                                    <td><code>variants[].options</code></td>
                                    <td>array</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Available options for this variant</td>
                                </tr>
                                <tr>
                                    <td><code>phases</code></td>
                                    <td>array</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Lifecycle phases in recommended sequence</td>
                                </tr>
                                <tr>
                                    <td><code>phases[].id</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Phase identifier (e.g., "setup", "development")</td>
                                </tr>
                                <tr>
                                    <td><code>phases[].title</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Human-readable phase name</td>
                                </tr>
                                <tr>
                                    <td><code>phases[].dependencies</code></td>
                                    <td>array</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Phases that must be completed first</td>
                                </tr>
                                <tr>
                                    <td><code>phases[].required</code></td>
                                    <td>boolean</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Whether phase is mandatory (default: true)</td>
                                </tr>
                                <tr>
                                    <td><code>global_context</code></td>
                                    <td>object</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Project-wide context information</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="spec-card spec-card-full">
                    <div class="spec-header">
                        <h3><i class="fa-solid fa-list-check"></i> Phase Instruction Schema</h3>
                        <p>Defines the detailed implementation instructions for a specific phase</p>
                    </div>
                    <div class="schema-table-container">
                        <table class="schema-table">
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><code>instruction_id</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Unique identifier for this instruction</td>
                                </tr>
                                <tr>
                                    <td><code>title</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Concise title of the instruction set</td>
                                </tr>
                                <tr>
                                    <td><code>version</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Version of this instruction (e.g., "0.1.0")</td>
                                </tr>
                                <tr>
                                    <td><code>catalog_version</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Version of the catalog specification</td>
                                </tr>
                                <tr>
                                    <td><code>project_type</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Must match parent project_type</td>
                                </tr>
                                <tr>
                                    <td><code>phase</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Must match phase.id from root schema</td>
                                </tr>
                                <tr>
                                    <td><code>variant_option</code></td>
                                    <td>string</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Variant this instruction implements (e.g., "react")</td>
                                </tr>
                                <tr>
                                    <td><code>context</code></td>
                                    <td>object</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Information about the "why" of these instructions</td>
                                </tr>
                                <tr>
                                    <td><code>context.objective</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Overall goal of this phase</td>
                                </tr>
                                <tr>
                                    <td><code>context.preconditions</code></td>
                                    <td>array</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Conditions that must be true before starting</td>
                                </tr>
                                <tr>
                                    <td><code>context.postconditions</code></td>
                                    <td>array</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Conditions that must be true after completion</td>
                                </tr>
                                <tr>
                                    <td><code>tasks</code></td>
                                    <td>array</td>
                                    <td><span class="required">Required</span></td>
                                    <td>List of implementation tasks</td>
                                </tr>
                                <tr>
                                    <td><code>tasks[].id</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Task identifier (e.g., "task1")</td>
                                </tr>
                                <tr>
                                    <td><code>tasks[].title</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Short description of the task</td>
                                </tr>
                                <tr>
                                    <td><code>tasks[].description</code></td>
                                    <td>string</td>
                                    <td><span class="required">Required</span></td>
                                    <td>Detailed explanation of the task</td>
                                </tr>
                                <tr>
                                    <td><code>tasks[].priority</code></td>
                                    <td>integer</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Priority level (1-5, where 1 is highest)</td>
                                </tr>
                                <tr>
                                    <td><code>tasks[].dependencies</code></td>
                                    <td>array</td>
                                    <td><span class="optional">Optional</span></td>
                                    <td>Tasks that must be completed before this one</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="spec-info">
                    <div class="spec-info-container">
                        <div class="spec-info-card">
                            <h3><i class="fa-solid fa-diagram-project"></i> Structure Overview</h3>
                            <ul>
                                <li><strong>Project Types</strong> → Define categories</li>
                                <li><strong>Variants</strong> → Implementation options</li>
                                <li><strong>Phases</strong> → Sequential lifecycle stages</li>
                                <li><strong>Tasks</strong> → Specific activities</li>
                            </ul>
                        </div>
                        
                        <div class="spec-info-card">
                            <h3><i class="fa-solid fa-gears"></i> Key Benefits</h3>
                            <ul>
                                <li><strong>Modularity</strong> — Mix and match variants</li>
                                <li><strong>Dependencies</strong> — Clear prerequisites</li>
                                <li><strong>Structured Format</strong> — LLM-optimized</li>
                                <li><strong>Versioning</strong> — Track changes over time</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="spec-cta">
                        <a href="https://github.com/OpenInstructions/catalog/blob/main/SPEC.md" class="btn btn-primary" target="_blank">
                            <i class="fa-solid fa-file-code"></i>
                            View Complete Specification
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-col">
                    <h3>OpenInstructions</h3>
                    <p>An open-source initiative for structured, versioned instructions optimized for Large Language Models and developers.</p>
                    <p>The 'OpenInstructions' name and branding are reserved for this project and its officially authorized derivatives.</p>
                </div>
                <div class="footer-col">
                    <h3>Resources</h3>
                    <ul class="footer-links">
                        <li><a href="https://github.com/OpenInstructions/catalog"><i class="fa-solid fa-chevron-right"></i> GitHub Repository</a></li>
                        <li><a href="https://github.com/OpenInstructions/catalog/blob/main/CONTRIBUTING.md"><i class="fa-solid fa-chevron-right"></i> Contributing Guide</a></li>
                        <li><a href="https://github.com/OpenInstructions/catalog/blob/main/SPEC.md"><i class="fa-solid fa-chevron-right"></i> Specification</a></li>
                        <li><a href="https://github.com/OpenInstructions/catalog/blob/main/LICENSE"><i class="fa-solid fa-chevron-right"></i> License</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3>Project</h3>
                    <ul class="footer-links">
                        <li><a href="index.html#features"><i class="fa-solid fa-chevron-right"></i> Features</a></li>
                        <li><a href="index.html#getting-started"><i class="fa-solid fa-chevron-right"></i> Getting Started</a></li>
                        <li><a href="index.html#catalog"><i class="fa-solid fa-chevron-right"></i> Catalog</a></li>
                        <li><a href="index.html#community"><i class="fa-solid fa-chevron-right"></i> Community</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 OpenInstructions. MIT License.</p>
            </div>
        </div>
    </footer>
</body>
</html>
"""
    
    with open(os.path.join(DIST_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(html)
    
    log.info("Generated comprehensive HTML landing page")

if __name__ == "__main__":
    sys.exit(main()) 