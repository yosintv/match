import asyncio
import json
import re
from curl_cffi.requests import AsyncSession

TARGET_URL = "https://crex.com/schedule"

async def fetch_crex_schedule():
    async with AsyncSession() as session:
        print("Connecting to CREX...")
        
        # Using a very modern browser fingerprint
        res = await session.get(TARGET_URL, impersonate="chrome120", timeout=30)
        
        if res.status_code != 200:
            print(f"Failed to load page. Status: {res.status_code}")
            return

        # CREX stores match data in a JavaScript object. 
        # We use regex to find the 'scheduleList' array inside the scripts.
        pattern = r'"scheduleList"\s*:\s*(\[.*?\])\s*,\s*"filter"'
        match = re.search(pattern, res.text)

        if not match:
            # Fallback pattern if the first one fails
            pattern = r'"matchList"\s*:\s*(\[.*?\])'
            match = re.search(pattern, res.text)

        if match:
            try:
                raw_json = match.group(1)
                match_data = json.loads(raw_json)
                
                final_matches = []
                for m in match_data:
                    # We only want entries that have team names
                    if m.get('team1Name') and m.get('team2Name'):
                        final_matches.append({
                            "match_name": f"{m.get('team1Name')} vs {m.get('team2Name')}",
                            "time": m.get('startTime'),
                            "series": m.get('seriesName', 'International'),
                            "venue": m.get('venue', 'TBA')
                        })
                
                with open("matches.json", "w", encoding="utf-8") as f:
                    json.dump(final_matches, f, indent=4)
                
                print(f"Success! Found {len(final_matches)} matches.")
                
            except Exception as e:
                print(f"Error parsing JSON: {e}")
        else:
            print("Could not find the match data in the page source. CREX might be blocking or changed layout again.")
            # For debugging, save a snippet of the page to see what's happening
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(res.text[:2000])

if __name__ == "__main__":
    asyncio.run(fetch_crex_schedule())
