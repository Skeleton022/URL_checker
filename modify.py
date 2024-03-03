import json
import sqlite3
import requests
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# File paths
sites_config_path = "sites.json"
tags_config_path = "tags.json"
db_path = "LS24PR.db"

# Headers for the request
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}


# Function to read content from JSON config files
def read_json_config_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Function to update the database with new websites and tags and return them
def update_db_with_new_entries(sites, tags):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    new_sites = []
    new_tags = []

    # Update Websites table with new websites and collect new sites
    for site in sites:
        cursor.execute("SELECT url FROM Websites WHERE url = ?", (site,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Websites (url) VALUES (?)", (site,))
            new_sites.append(site)

    # Update Tags table with new tags and collect new tags
    for tag in tags:
        cursor.execute("SELECT tag_name FROM Tags WHERE tag_name = ?", (tag,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO Tags (tag_name) VALUES (?)", (tag,))
            new_tags.append(tag)

    conn.commit()
    conn.close()
    return new_sites, new_tags


# Baseline scanning function for new websites and tags
def baseline_scanning(new_sites, new_tags, all_tags):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Scan new sites with all tags
    for site in new_sites:
        website_id = cursor.execute("SELECT website_id FROM Websites WHERE url = ?", (site,)).fetchone()[0]
        scan_site(site, website_id, all_tags, cursor)

    # Scan existing sites with new tags only
    if new_tags:
        existing_sites = set(sites) - set(new_sites)
        for site in existing_sites:
            website_id = cursor.execute("SELECT website_id FROM Websites WHERE url = ?", (site,)).fetchone()[0]
            scan_site(site, website_id, new_tags, cursor)

    conn.commit()
    conn.close()


# Function to scan a specific site with given tags
def scan_site(site, website_id, tags, cursor):
    for tag in tags:
        tag_id = cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,)).fetchone()[0]
        try:
            response = requests.get(site, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Handle tag with ID
            if '#' in tag:
                tag_name, tag_id_value = tag.split('#')
                content = soup.find(tag_name, id=tag_id_value)
            # Handle tag with class
            elif '.' in tag:
                tag_name, class_name = tag.split('.')
                content = soup.find(tag_name, class_=class_name)
            else:
                content = soup.find(tag)

            if content:
                content_text = content.get_text().strip()
                content_hash = hashlib.sha256(content_text.encode()).hexdigest()
                created_at = datetime.now(pytz.timezone('Europe/Budapest')).strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute(
                    "INSERT INTO InitScan (website_id, tag_id, content_hash, content_text, created_at) VALUES (?, ?, ?, ?, ?)",
                    (website_id, tag_id, content_hash, content_text, created_at))
        except requests.RequestException as e:
            print(f"Failed to scan {site} with tag {tag}: {e}")


# Read the updated configuration files
sites = read_json_config_file(sites_config_path)
tags = read_json_config_file(tags_config_path)

# Update the database with any new websites or tags and get them
new_sites, new_tags = update_db_with_new_entries(sites, tags)

# Ask the user if they want to perform a baseline scan for new entries
user_input = input("Do you want to perform a baseline scan for newly added websites and tags? (Y/n) ").strip().lower()
if user_input == 'y':
    print("Starting baseline scanning for new websites and tags...")
    baseline_scanning(new_sites, new_tags, tags)
    print("Baseline scanning completed.")
else:
    print("Baseline scanning skipped.")
