import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

def get_links():
    # 1. Calculate Unix Timestamp for 00:00 AM JST
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(now_jst.timestamp())

    # 2. Construct the URL
    base_url = "https://sakjhqs.tijing2.com:9967/matches"
    params = f"?tab=202&status=upcoming&date={timestamp}"
    target_url = base_url + params
    
    print(f"Targeting URL: {target_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 3. Fetch the page
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 4. Extract links (Finds all <a> tags with an href)
        # Note: You can filter these further if you know the specific class or ID
        all_links = soup.find_all('a', href=True)
        
        match_links = []
        for a in all_links:
            href = a['href']
            # Convert relative links to absolute links
            if href.startswith('/'):
                href = f"https://sakjhqs.tijing2.com:9967{href}"
            
            # Optional: Only keep links that look like match links
            if "match" in href: 
                match_links.append(href)

        # 5. Save to file
        with open("links.txt", "w") as f:
            if match_links:
                for link in sorted(set(match_links)): # Removes duplicates
                    f.write(link + "\n")
                print(f"Success: {len(match_links)} links saved to links.txt")
            else:
                print("No links found on the page.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_links()
