import asyncio
import json
import os
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup

TARGET_URL = "https://crex.com/schedule"

async def fetch_crex_schedule():
    async with AsyncSession() as session:
        print(f"Connecting to CREX...")
        
        # We MUST use impersonate to avoid the 0 matches/blank screen issue
        res = await session.get(TARGET_URL, impersonate="chrome120", timeout=20)
        
        if res.status_code != 200:
            print(f"Failed! Status Code: {res.status_code}")
            return

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # CREX (Next.js) stores data in a script tag with id "__NEXT_DATA__"
        next_data_script = soup.find("script", id="__NEXT_DATA__")
        
        if not next_data_script:
            print("Could not find data script. The site layout might have changed.")
            return

        # Load the JSON from the script tag
        data = json.loads(next_data_script.string)
        
        # Navigate through the JSON structure to find the match list
        # Based on CREX 2026 structure:
        try:
            # Note: The path below is the standard for Next.js apps like CREX
            match_list_raw = data['props']['pageProps']['initialState']['schedule']['scheduleList']
        except KeyError:
            print("Data structure updated. Manual check required.")
            return

        matches = []
        for item in match_list_raw:
            # We filter for only the actual matches (some items might be dates/headers)
            if 'matchName' in item or 'team1Name' in item:
                matches.append({
                    "match_name": f"{item.get('team1Name', 'TBA')} vs {item.get('team2Name', 'TBA')}",
                    "time": item.get('startTime'), # This is usually a UTC timestamp
                    "series": item.get('seriesName', 'Unknown Series'),
                    "venue": item.get('venue', 'TBA')
                })

        # Save to file
        with open("matches.json", "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=4)
            
        print(f"Done! Found {len(matches)} matches.")

if __name__ == "__main__":
    asyncio.run(fetch_crex_schedule())
