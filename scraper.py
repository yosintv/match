import time
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta

def get_links():
    # 1. Calculate JST Timestamp for today
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = int(now_jst.timestamp())

    target_url = f"https://sakjhqs.tijing2.com:9967/matches?tab=202&status=upcoming&date={timestamp}"
    print(f"Targeting: {target_url}")

    with sync_playwright() as p:
        # Launch with a realistic User-Agent to avoid being limited
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # Increase timeout for slow-loading betting sites
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        
        # 2. Aggressive Scroll Loop
        print("Starting deep scroll to fetch all matches...")
        for i in range(15):  # Scroll 15 times to ensure all 24h data loads
            page.mouse.wheel(0, 2000)
            time.sleep(2) # Wait for Javacript to trigger the next batch
            
            # If "Load More" button exists, click it
            load_more = page.locator("text=Load More").first
            if load_more.is_visible():
                load_more.click()
                time.sleep(2)

        # 3. Final Extraction
        # We grab all links that contain /matches/
        hrefs = page.eval_on_selector_all(
            'a[href*="/matches/"]', 
            'elements => elements.map(e => e.href)'
        )
        
        # Filter for sub-links that belong to sport_id 202
        sub_links = [link for link in hrefs if "sport_id=202" in link]
        unique_links = sorted(list(set(sub_links)))

        # 4. Save results
        with open("links.txt", "w") as f:
            for link in unique_links:
                f.write(link + "\n")
        
        print(f"Done! Found and saved {len(unique_links)} matches.")
        browser.close()

if __name__ == "__main__":
    get_links()
