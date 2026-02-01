import requests
from bs4 import BeautifulSoup
import datetime

def fetch_matches():
    url = "https://www.popozhibo.tv/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This selector depends on the site's specific HTML. 
        # Most sports sites use <li> or <div> with class names like 'match-item' or 'game'.
        matches = []
        
        # Searching for elements that typically contain "vs" or team names
        # You may need to inspect the site and update these classes (e.g., 'match-list-item')
        items = soup.find_all(['li', 'div'], class_=['match-item', 'list-item', 'game'])

        for item in items:
            text = item.get_text(separator=" ", strip=True)
            if "vs" in text.lower():
                matches.append(text)

        # Fallback: if no specific classes found, find all text with 'vs'
        if not matches:
            for element in soup.find_all(string=lambda text: "vs" in text.lower()):
                parent = element.find_parent()
                if parent:
                    matches.append(parent.get_text(strip=True))

        return list(set(matches)) # Remove duplicates

    except Exception as e:
        return [f"Error fetching matches: {e}"]

if __name__ == "__main__":
    print(f"--- Matches for {datetime.date.today()} ---")
    results = fetch_matches()
    if results:
        for match in results:
            print(match)
    else:
        print("No matches found or structure changed.")
