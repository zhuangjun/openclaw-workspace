#!/usr/bin/env python3
"""
Add source to NotebookLM via browser automation
Usage: python3 add_to_notebooklm.py <notebook_id> <source_url> [--title <title>]

Note: This script requires the OpenClaw Browser Relay to be connected to Chrome
"""

import sys
import json
import time

def add_to_notebooklm(notebook_id, source_url, title=None):
    """
    Add a source to NotebookLM
    
    This is a placeholder that provides instructions for the agent.
    The actual implementation uses OpenClaw's browser automation.
    """
    
    instructions = f"""
# NotebookLM Source Addition Instructions

## Target URL
https://notebooklm.google.com/notebook/{notebook_id}

## Source to Add
- URL: {source_url}
{f"- Title: {title}" if title else "- Title: (auto-detect)"}

## Steps to Add Source

1. Navigate to the notebook URL
2. Click the "+" button or "Add Source" button (usually at bottom of sources list)
3. Select "Website" or "YouTube" option
4. Paste the URL: {source_url}
5. Wait for the source to be processed
6. Confirm the source appears in the notebook

## Verification
- Check that the source appears in the sources list
- Verify the title and content preview are correct
"""
    
    return {
        "status": "pending",
        "notebook_id": notebook_id,
        "source_url": source_url,
        "title": title,
        "instructions": instructions
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 add_to_notebooklm.py <notebook_id> <source_url> [--title <title>]")
        sys.exit(1)
    
    notebook_id = sys.argv[1]
    source_url = sys.argv[2]
    title = None
    
    # Parse optional title
    for i, arg in enumerate(sys.argv):
        if arg == "--title" and i + 1 < len(sys.argv):
            title = sys.argv[i + 1]
    
    result = add_to_notebooklm(notebook_id, source_url, title)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
