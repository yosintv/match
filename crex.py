import asyncio
import json
import re
from curl_cffi.requests import AsyncSession

TARGET_URL = "https://crex.com/schedule"

async def fetch_crex_schedule():
    async with AsyncSession() as session:
        print("Connecting to CREX...")
        
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://crex.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1"
        }

        # Impersonate a real Chrome browser session
        res = await session.get(TARGET_URL, impersonate="chrome120", headers=headers, timeout=30)
        
        if res.status_code != 200:
            print(f"Failed! Status: {res.status_code}")
            return

        # NEW APPROACH: Search for the common 'matchList' or 'scheduleList' patterns 
        # inside the raw JavaScript state blocks.
        print("Searching for match data in page source...")
        
        # This regex looks for any JSON-like list that contains team names
        # It's more flexible than looking for a specific variable name.
        data_match = re.search(r'\[\{"matchId".*?\}\]', res.text)
        
        if not data_match:
            # Secondary check: Look for the Next.js/React state object
            data_match = re.search(r'\{"matchSchedule".*?\}\]', res.text)

        if data_match:
            try:
                raw_data = data_match.group(0)
                # If the string ends prematurely, we fix it (common with regex on long scripts)
                if not raw_data.endswith(']'): raw_data += ']'
                
                json_data = json.loads(raw_data)
                
                matches = []
                for m in json_data:
                    # Filter for actual matches by checking for team names
                    t1 = m.get('team1Name') or m.get('t1n')
                    t2 = m.get('team2Name') or m.get('t2n')
                    
                    if t1 and t2:
                        matches.append({
                            "match_name": f"{t1} vs {t2}",
                            "time": m.get('startTime') or m.get('st'),
                            "series": m.get('seriesName') or m.get('sn', 'Cricket Match'),
                            "venue": m.get('venue') or m.get('v', 'TBA')
                        })

                if matches:
                    with open("matches.json", "w", encoding="utf-8") as f:
                        json.dump(matches, f, indent=4)
                    print(f"Success! Found {len(matches)} matches.")
                else:
                    print("Found data block but no valid matches inside.")
                    
            except Exception as e:
                print(f"Extraction error: {e}")
        else:
            print("CRITICAL: No data pattern found. CREX has likely obfuscated the data.")
            # Save a snippet for your inspection
            with open("source_debug.txt", "w", encoding="utf-8") as f:
                f.write(res.text[:5000])
            print("Check source_debug.txt in your repo to see what CREX is returning.")

if __name__ == "__main__":
    asyncio.run(fetch_crex_schedule())
