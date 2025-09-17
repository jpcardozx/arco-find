#!/usr/bin/env python3
"""
ARCO-FIND ngrok URL Updater
Script to automatically update ngrok URLs across the project
"""

import os
import re
import json
import requests
from pathlib import Path

def get_current_ngrok_url():
    """Get current ngrok public URL from local API"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        tunnels = response.json()['tunnels']
        
        for tunnel in tunnels:
            if tunnel['config']['addr'] == 'http://localhost:8081':
                return tunnel['public_url']
        
        return None
    except Exception as e:
        print(f"❌ Error getting ngrok URL: {e}")
        return None

def update_file_urls(file_path, old_pattern, new_url):
    """Update URLs in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all occurrences of the old ngrok URL pattern
        updated_content = re.sub(old_pattern, new_url, content)
        
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def update_all_ngrok_urls():
    """Update all ngrok URLs in the project"""
    print("🔄 ARCO-FIND ngrok URL Updater")
    print("=" * 40)
    
    # Get current ngrok URL
    current_url = get_current_ngrok_url()
    if not current_url:
        print("❌ Could not get current ngrok URL")
        return False
    
    print(f"📡 Current ngrok URL: {current_url}")
    
    # Files to update
    files_to_update = [
        '.env.example',
        'docs/examples.md', 
        'config/ngrok_config.py'
    ]
    
    # Old URL pattern (matches any ngrok URL)
    old_pattern = r'https://[a-f0-9]+\.ngrok-free\.app'
    
    updated_files = []
    
    for file_path in files_to_update:
        full_path = Path(file_path)
        if full_path.exists():
            if update_file_urls(full_path, old_pattern, current_url):
                updated_files.append(file_path)
                print(f"✅ Updated: {file_path}")
            else:
                print(f"ℹ️  No changes: {file_path}")
        else:
            print(f"⚠️  Not found: {file_path}")
    
    print("=" * 40)
    if updated_files:
        print(f"✅ Updated {len(updated_files)} files with new ngrok URL")
        print(f"🔗 New URL: {current_url}")
    else:
        print("ℹ️  No files needed updating")
    
    return True

if __name__ == "__main__":
    update_all_ngrok_urls()