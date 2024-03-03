import os
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


# Initialize config files with default content if they don't exist
def initialize_json_config_file(file_path, default_content):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(default_content, file, indent=4)


# Initialize database
def initialize_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Websites table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Websites (
        website_id INTEGER PRIMARY KEY,
        url TEXT UNIQUE
    )
    ''')

    # Create Tags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tags (
        tag_id INTEGER PRIMARY KEY,
        tag_name TEXT
    )
    ''')

    # Create InitScan table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS InitScan (
        result_id INTEGER PRIMARY KEY,
        website_id INTEGER,
        tag_id INTEGER,
        content_hash TEXT,
        content_text TEXT,
        created_at DATETIME,
        FOREIGN KEY(website_id) REFERENCES Websites(website_id),
        FOREIGN KEY(tag_id) REFERENCES Tags(tag_id)
    )
    ''')

    # Create ScanLogs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ScanLogs (
        log_id INTEGER PRIMARY KEY,
        website_id INTEGER,
        tag_id INTEGER,
        result TEXT,
        content_text TEXT NULLABLE,
        content_hash TEXT NULLABLE,
        created_at DATETIME,
        FOREIGN KEY(website_id) REFERENCES Websites(website_id),
        FOREIGN KEY(tag_id) REFERENCES Tags(tag_id)
    )
    ''')

    conn.commit()
    conn.close()


# Function to read content from JSON config files
def read_json_config_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Initialize JSON config files if they don't exist
initialize_json_config_file(sites_config_path, ["https://example.com", "http://test.example.com"])
initialize_json_config_file(tags_config_path, ["title", "div.class_test", "div#id_test"])

# Initialize the database
initialize_db()


# Function to fill the database with configuration data
def fill_db(sites, tags):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for site in sites:
        cursor.execute("INSERT OR IGNORE INTO Websites (url) VALUES (?)", (site,))

    for tag in tags:
        cursor.execute("INSERT OR IGNORE INTO Tags (tag_name) VALUES (?)", (tag,))

    conn.commit()
    conn.close()


# Baseline scanning function
def baseline_scanning(sites, tags):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}

    for site in sites:
        # Get the website_id from Websites table
        website_id = cursor.execute("SELECT website_id FROM Websites WHERE url = ?", (site,)).fetchone()
        if website_id is None:
            print(f"Website {site} not found in the database.")
            continue
        website_id = website_id[0]

        for tag in tags:
            # Get the tag_id from Tags table
            tag_id = cursor.execute("SELECT tag_id FROM Tags WHERE tag_name = ?", (tag,)).fetchone()
            if tag_id is None:
                print(f"Tag {tag} not found in the database.")
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

                    # Insert scan result into InitScan table
                    cursor.execute(
                        "INSERT INTO InitScan (website_id, tag_id, content_hash, content_text, created_at) VALUES (?, ?, ?, ?, ?)",
                        (website_id, tag_id, content_hash, content_text, created_at))
            except requests.RequestException as e:
                print(f"Failed to scan {site} with tag {tag}: {e}")

    conn.commit()
    conn.close()


# Prompt the user to start baseline scanning
print("Change the config files before continuing the script!!!!!!")
user_input = input("Do you want to do the baselining? (Y/n) ").strip().lower()
if user_input == 'y':
    # Update the configuration by re-reading the JSON files
    sites = read_json_config_file(sites_config_path)
    tags = read_json_config_file(tags_config_path)

    fill_db(sites, tags)

    print("Starting baseline scanning...")
    baseline_scanning(sites, tags)
    print("Baseline scanning completed.")
else:
    print("Baseline scanning skipped.")
