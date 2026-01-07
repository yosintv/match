import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import re

def get_links():
    # 1. Calculate JST Unix Timestamp
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(now_jst.timestamp())

    # 2. Main URL
    target_url = f"https://sakjhqs.tijing2.com:9967/matches?tab=202&status=upcoming&date={timestamp}"
    print(f"Scraping Main URL: {target_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Find sub-links
        # We look for links containing '/matches/' followed by a number
        all_hrefs = [a['href'] for a in soup.find_all('a', href=True)]
        
        sub_links = []
        for href in all_hrefs:
            # Check if it matches the match link pattern
            if "/matches/" in href and "sport_id=202" in href:
                # Ensure it's a full URL
                full_link = href if href.startswith('http') else f"https://sakjhqs.tijing2.com:9967{href}"
                sub_links.append(full_link)

        # 4. Save unique links to file
        unique_links = sorted(list(set(sub_links)))
        with open("links.txt", "w") as f:
            for link in unique_links:
                f.write(link + "\n")
        
        print(f"Successfully saved {len(unique_links)} sub-links.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_links()
