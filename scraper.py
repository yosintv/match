import time
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta

def get_links():
    # 1. Calculate JST Timestamp for 00:00 AM
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(now_jst.timestamp())

    target_url = f"https://sakjhqs.tijing2.com:9967/matches?tab=202&status=upcoming&date={timestamp}"
    print(f"Scraping all matches for JST Date: {now_jst.strftime('%Y-%m-%d')}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a realistic viewport to trigger more content loading
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        page.goto(target_url, wait_until="networkidle")

        # 2. Infinite Scroll Logic
        last_height = page.evaluate("document.body.scrollHeight")
        while True:
            # Scroll to the bottom of the page
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for new matches to load (adjust time if your internet is slow)
            page.wait_for_timeout(3000) 
            
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                # If height hasn't changed, we've reached the end of the list
                break
            last_height = new_height
            print("Scrolling to load more matches...")

        # 3. Extract all links that match your pattern
        # We look for links containing /matches/ and sport_id=202
        hrefs = page.eval_on_selector_all(
            'a[href*="/matches/"]', 
            'elements => elements.map(e => e.href)'
        )
        
        # Filter for the specific upcoming match pattern
        sub_links = [link for link in hrefs if "sport_id=202" in link]
        
        # Remove duplicates and sort
        unique_links = sorted(list(set(sub_links)))

        # 4. Save to file
        with open("links.txt", "w") as f:
            for link in unique_links:
                f.write(link + "\n")
        
        print(f"Done! Successfully saved {len(unique_links)} matches.")
        browser.close()

if __name__ == "__main__":
    get_links()
