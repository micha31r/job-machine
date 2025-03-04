import requests, csv, os
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent

def fetch_html(url, headers=None):
    """Fetches HTML content from a given URL."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html, parser="html.parser"):
    """Parses HTML content using BeautifulSoup."""
    return BeautifulSoup(html, parser)

def extract_data(soup, selector):
    """Extracts data based on tag, class, or other attributes."""
    return soup.select(selector)

def save_to_csv(filename, mode, headers, data):
    path = os.path.join(BASE_DIR, filename + ".csv")

    write_headers = os.path.exists(path) and os.stat(path).st_size == 0

    with open(path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if write_headers:
            writer.writerow(headers)
        writer.writerows(data)

def read_csv(filename):
    rows = []
    path = os.path.join(BASE_DIR, filename + ".csv")
    with open(path, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
    return rows
    
def clear_file(filename):
    path = os.path.join(BASE_DIR, filename + ".csv")
    with open(path, "w") as file:
        pass

def create_file(filename):
    path = os.path.join(BASE_DIR, filename + ".csv")
    with open(path, "a") as file:
        pass