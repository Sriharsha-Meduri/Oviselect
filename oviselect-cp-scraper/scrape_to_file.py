#!/usr/bin/env python3
"""Scrape all colleges and save to JSON file."""

import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from scraper.fetcher import fetch_page
from scraper.parser import parse_college_page
from scraper.structurer import structure_with_llm
from pipeline.loader import get_colleges
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO")

def scrape_all_to_file(college_type="ALL"):
    colleges = get_colleges(college_type)
    logger.info(f"Found {len(colleges)} colleges to scrape")
    
    all_data = []
    
    for i, college in enumerate(colleges):
        name = college["name"]
        slug = college["slug"]
        
        logger.info(f"[{i+1}/{len(colleges)}] Processing: {name}")
        
        if slug is None:
            logger.warning(f"  No slug for {name}, skipping")
            continue
        
        try:
            html = fetch_page(slug)
            if not html:
                logger.error(f"  Failed to fetch {name}")
                continue
            
            parsed = parse_college_page(html, name, slug)
            structured = structure_with_llm(slug, parsed)
            
            all_data.append({
                "institute": name,
                "slug": slug,
                "type": college.get("type", college_type),
                "scraped_at": datetime.now().isoformat(),
                "data": structured
            })
            
            conf = structured.get('confidence_score', 0)
            logger.info(f"  ✓ Done - {conf}% confidence")
            
            if (i + 1) % 10 == 0:
                save_to_file(all_data, partial=True)
                logger.info(f"  [Auto-saved {i+1} colleges]")
            
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            continue
    
    save_to_file(all_data, partial=False)
    logger.info(f"✓ Complete! Saved {len(all_data)} colleges to colleges_data.json")
    
    return all_data

def save_to_file(data, partial=False):
    filename = "colleges_data_partial.json" if partial else "colleges_data.json"
    filepath = Path(__file__).parent / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved to {filepath}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", default="ALL", choices=["IIT", "NIT", "IIIT", "GFTI", "ALL"])
    args = parser.parse_args()
    
    scrape_all_to_file(args.type)
