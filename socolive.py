import requests
from bs4 import BeautifulSoup
import re

def scrape_socolive():
    url = "https://socolivezzxz.co/truc-tiep/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()

        # Find all anchor tags
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Pattern: Match links usually have multiple hyphens (e.g., team-a-vs-team-b)
            # This filters out the main category page and pagination
            if "/truc-tiep/" in href and len(href.split('-')) > 2:
                # Remove trailing slashes for consistency
                clean_url = href.rstrip('/')
                links.add(clean_url)

        # Save to a dedicated socolive text file
        with open("socolive_links.txt", "w") as f:
            for link in sorted(links):
                f.write(link + "\n")
        
        print(f"Done! {len(links)} match links saved to socolive_links.txt")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_socolive()
