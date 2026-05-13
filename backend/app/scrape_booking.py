#!/usr/bin/env python3
"""
Scrape booking page structure using Playwright sync API
Extracts form, inputs, tokens, and time slot candidates
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


def extract_form_data(page: Page) -> Dict[str, Any]:
    """Extract first form's action and method"""
    form = page.query_selector("form")
    if not form:
        return {"action": None, "method": None}
    
    action = form.get_attribute("action")
    method = form.get_attribute("method") or "POST"
    
    return {
        "action": action,
        "method": method.upper(),
    }


def extract_inputs(page: Page) -> List[Dict[str, Any]]:
    """Extract all input, select, textarea elements with their properties"""
    inputs_data = []
    
    # Get all input elements
    inputs = page.query_selector_all("input")
    for inp in inputs:
        name = inp.get_attribute("name")
        input_type = inp.get_attribute("type") or "text"
        value = inp.get_attribute("value") or ""
        
        inputs_data.append({
            "element": "input",
            "name": name,
            "type": input_type,
            "value": value,
        })
    
    # Get all select elements
    selects = page.query_selector_all("select")
    for select in selects:
        name = select.get_attribute("name")
        options = []
        
        option_elements = select.query_selector_all("option")
        for opt in option_elements:
            opt_value = opt.get_attribute("value") or ""
            opt_text = opt.inner_text() or ""
            options.append({
                "value": opt_value,
                "text": opt_text,
            })
        
        inputs_data.append({
            "element": "select",
            "name": name,
            "options": options,
        })
    
    # Get all textarea elements
    textareas = page.query_selector_all("textarea")
    for textarea in textareas:
        name = textarea.get_attribute("name")
        value = textarea.inner_text() or ""
        
        inputs_data.append({
            "element": "textarea",
            "name": name,
            "value": value,
        })
    
    return inputs_data


def extract_csrf_tokens(page: Page) -> Dict[str, Optional[str]]:
    """Extract CSRF tokens from meta tags"""
    tokens = {}
    
    # Common CSRF meta tag names
    csrf_names = [
        "csrf-token",
        "csrf_token",
        "_token",
        "authenticity_token",
        "csrfToken",
    ]
    
    for name in csrf_names:
        meta = page.query_selector(f'meta[name="{name}"]')
        if meta:
            content = meta.get_attribute("content")
            if content:
                tokens[name] = content
    
    return tokens


def find_time_slots(page: Page) -> List[Dict[str, Any]]:
    """Find candidate slot elements by scanning clickable elements"""
    slots = []
    time_regex = re.compile(r"\b\d{1,2}:\d{2}\b")
    
    # Selectors for clickable elements
    selectors = ["button", "a", "li", "td", "span"]
    
    for selector in selectors:
        elements = page.query_selector_all(selector)
        for elem in elements:
            # Check data attributes
            data_time = elem.get_attribute("data-time")
            data_date = elem.get_attribute("data-date")
            
            if data_time or data_date:
                slots.append({
                    "element": selector,
                    "text": elem.inner_text() or "",
                    "data-time": data_time,
                    "data-date": data_date,
                    "class": elem.get_attribute("class"),
                })
                continue
            
            # Check inner text for time pattern
            inner_text = elem.inner_text() or ""
            if time_regex.search(inner_text):
                slots.append({
                    "element": selector,
                    "text": inner_text,
                    "data-time": None,
                    "data-date": None,
                    "class": elem.get_attribute("class"),
                })
    
    return slots


def build_sample_payload(
    inputs: List[Dict[str, Any]], tokens: Dict[str, Optional[str]]
) -> Dict[str, Any]:
    """Build a sample POST payload with placeholders"""
    payload = {}
    
    # Add CSRF tokens
    for token_name, token_value in tokens.items():
        if token_value:
            payload[token_name] = token_value
    
    # Add inputs with placeholders
    for inp in inputs:
        if inp["element"] == "input":
            if inp["type"] == "hidden":
                payload[inp["name"]] = inp.get("value", "")
            elif inp["type"] in ("checkbox", "radio"):
                payload[inp["name"]] = "${VALUE}"
            else:
                payload[inp["name"]] = "${INPUT_VALUE}"
        
        elif inp["element"] == "select":
            if inp.get("options"):
                payload[inp["name"]] = inp["options"][0]["value"]
            else:
                payload[inp["name"]] = "${OPTION_VALUE}"
        
        elif inp["element"] == "textarea":
            payload[inp["name"]] = "${TEXT_VALUE}"
    
    return payload


def scrape_booking_page(url: str, output_path: Optional[str] = None) -> str:
    """
    Scrape booking page structure and time slots
    
    Args:
        url: The booking page URL to scrape
        output_path: Optional path to save JSON output
    
    Returns:
        Path to the output JSON file
    """
    browser: Optional[Browser] = None
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context: BrowserContext = browser.new_context()
            page: Page = context.new_page()
            
            # Navigate to URL and wait for network idle
            page.goto(url, wait_until="networkidle")
            
            # Extract page title
            page_title = page.title()
            
            # Extract form data
            form_data = extract_form_data(page)
            
            # Extract inputs
            inputs = extract_inputs(page)
            
            # Extract CSRF tokens
            tokens = extract_csrf_tokens(page)
            
            # Find time slots
            slots = find_time_slots(page)
            
            # Build sample payload
            sample_payload = build_sample_payload(inputs, tokens)
            
            # Prepare output JSON
            output_data = {
                "page_title": page_title,
                "url": url,
                "form": form_data,
                "inputs": inputs,
                "tokens": tokens,
                "slots": slots,
                "sample_payload": sample_payload,
            }
            
            # Determine output path
            if output_path is None:
                output_path = "app/data/booking_page.json"
            
            # Create output directory if it doesn't exist
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON to file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Print and return the path
            abs_path = output_file.resolve()
            print(f"Booking page data saved to: {abs_path}")
            
            return str(abs_path)
    
    finally:
        if browser:
            browser.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Scrape booking page structure and extract time slots"
    )
    parser.add_argument("--url", required=True, help="The booking page URL to scrape")
    parser.add_argument(
        "--output",
        default="app/data/booking_page.json",
        help="Output JSON file path (default: app/data/booking_page.json)",
    )
    
    args = parser.parse_args()
    
    try:
        output_path = scrape_booking_page(args.url, args.output)
        print(f"Success: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
