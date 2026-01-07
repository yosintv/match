import os
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta

def get_links():
    # 1. Calculate JST Timestamp
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(now_jst.timestamp())

    target_url = f"https://sakjhqs.tijing2.com:9967/matches?tab=202&status=upcoming&date={timestamp}"
    print(f"Opening Browser for: {target_url}")

    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to URL and wait for the network to be idle
        page.goto(target_url, wait_until="networkidle")
        
        # Wait specifically for any link containing "/matches/" to appear
        try:
            page.wait_for_selector('a[href*="/matches/"]', timeout=15000)
        except:
            print("Timed out waiting for match links. The page might be empty or layout changed.")

        # 2. Extract all match links
        hrefs = page.eval_on_selector_all('a[href*="/matches/"]', 
                                         'elements => elements.map(e => e.href)')
        
        # 3. Filter for your specific sub-link pattern
        sub_links = [link for link in hrefs if "sport_id=202" in link]
        
        # Remove duplicates
        unique_links = sorted(list(set(sub_links)))

        # 4. Save to file
        with open("links.txt", "w") as f:
            for link in unique_links:
                f.write(link + "\n")
        
        print(f"Successfully saved {len(unique_links)} sub-links to links.txt")
        browser.close()

if __name__ == "__main__":
    get_links()
