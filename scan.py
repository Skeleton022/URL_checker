import json
import hashlib
import requests
import sqlite3
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


# Read the configuration files
sites = read_json_config_file(sites_config_path)
tags = read_json_config_file(tags_config_path)


# Scanning function adapted for scan.py
def scan_and_report(sites, tags):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for site in sites:
        # Get the website_id from Websites table
        website_id = cursor.execute("SELECT website_id FROM Websites WHERE url = ?", (site,)).fetchone()
        if website_id is None:
            print(f"error_db: Website {site} not found in the database. Skipping.")
            continue
        website_id = website_id[0]

        for tag in tags:
            # Get the tag_id from Tags table
            tag_id = cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,)).fetchone()
            if tag_id is None:
                print(f"error_db: Tag {tag} not found in the database. Skipping.")
                continue
            tag_id = tag_id[0]

            try:
                # Perform scanning
                response = requests.get(site, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Handle different tag types (ID, class, or plain tag)
                if '#' in tag:
                    tag_name, id_value = tag.split('#')
                    content = soup.find(tag_name, id=id_value)
                elif '.' in tag:
                    tag_name, class_value = tag.split('.')
                    content = soup.find(tag_name, class_=class_value)
                else:
                    content = soup.find(tag)

                if content:
                    content_text = content.get_text().strip()
                    content_hash = hashlib.sha256(content_text.encode()).hexdigest()
                    created_at = datetime.now(pytz.timezone('Europe/Budapest')).strftime('%Y-%m-%d %H:%M:%S')

                    # Log the scan result
                    last_scan = cursor.execute(
                        "SELECT content_hash FROM InitScan WHERE website_id = ? AND tag_id = ? ORDER BY created_at DESC LIMIT 1",
                        (website_id, tag_id)).fetchone()
                    result = "success" if last_scan and content_hash == last_scan[0] else "fail"
                    cursor.execute(
                        "INSERT INTO ScanLogs (website_id, tag_id, result, content_text, content_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (website_id, tag_id, result, content_text, content_hash, created_at))

                    print(f"{result}: Scan result for {site} [{tag}]")
                    if result == "fail":
                        print("\tFAIL!!!!")

            except requests.RequestException as e:
                print(f"error_web: Failed to scan {site} with tag {tag}: {e}")
                cursor.execute(
                    "INSERT INTO ScanLogs (website_id, tag_id, result, created_at) VALUES (?, ?, 'error_web', ?)",
                    (website_id, tag_id, created_at))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    # Run the scan and report function
    scan_and_report(sites, tags)
