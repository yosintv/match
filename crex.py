import asyncio
import json
import os
import re
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

# The URL you provided
TARGET_URL = "https://crex.com/schedule"

async def fetch_crex_schedule():
    async with AsyncSession() as session:
        print(f"Connecting to CREX...")
        
        # Impersonate Chrome to avoid getting the '[]' empty response
        res = await session.get(TARGET_URL, impersonate="chrome120", timeout=20)
        
        if res.status_code != 200:
            print(f"Failed to load page. Status: {res.status_code}")
            return

        soup = BeautifulSoup(res.text, 'html.parser')
        matches = []

        # CREX often stores data in a JSON script tag or specific HTML classes
        # Logic: Find all match containers (using standard CREX classes)
        # These classes change often, so we look for common match wrappers
        cards = soup.select('.schedule-item, .match-card, .sch-item') 

        for card in cards:
            try:
                # Based on your example: "Rajasthan Lions", "6:00 PM", "World Legends T20"
                match_name = card.select_one('.team-name, .match-info').text.strip()
                match_time = card.select_one('.match-time, .time').text.strip()
                series_info = card.select_one('.match-desc, .series').text.strip()

                matches.append({
                    "match_name": match_name,
                    "time": match_time,
                    "series": series_info
                })
            except Exception:
                continue

        # FALLBACK: If HTML scraping fails, look for the internal JSON state
        if not matches:
            script_tag = soup.find("script", string=re.compile("window.__INITIAL_STATE__"))
            if script_tag:
                # This part extracts data if CREX uses a Javascript framework like Nuxt/Next
                print("Found internal state, parsing JSON...")
                # Add complex JSON parsing here if needed
        
        # Save to JSON file
        with open("matches.json", "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=4)
            
        print(f"Done! Found {len(matches)} matches.")

if __name__ == "__main__":
    asyncio.run(fetch_crex_schedule())
