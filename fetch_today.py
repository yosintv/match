import requests
from bs4 import BeautifulSoup
import datetime
import base64
import json

def get_plain_stream_url(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.popozhibo.tv/"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200: return "#"
        
        # Extract the "data" field from the JSON
        payload = response.json().get('data', '')
        if not payload: return "#"

        # Step 1: Remove the 2-character suffix (like 'zy' or 'Gg')
        clean_b64 = payload[:-2] 
        
        # Step 2: Fix padding for Base64
        missing_padding = len(clean_b64) % 4
        if missing_padding:
            clean_b64 += '=' * (4 - missing_padding)
            
        # Step 3: Decode Base64 and parse JSON
        decoded_str = base64.b64decode(clean_b64).decode('utf-8')
        data_obj = json.loads(decoded_str)
        
        # Step 4: Get the first URL from the links list
        return data_obj['links'][0]['url']
    except Exception as e:
        print(f"Failed to decode {api_url}: {e}")
        return "#"

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        matches = []
        
        for item in soup.find_all('li'):
            if not item.find('div', class_='vs'): continue
            
            # Identify the match link
            link_tag = item.find('a', href=True)
            if not link_tag: continue
            
            # Fix URL logic: ensure it ends in /play-url without doubling up
            raw_path = link_tag['href'].rstrip('/')
            if raw_path.endswith('/play'):
                api_url = f"https://www.popozhibo.tv{raw_path}-url"
            else:
                api_url = f"https://www.popozhibo.tv{raw_path}/play-url"

            # Fetch and decode to get the plain URL
            print(f"Decoding link for match: {api_url}")
            plain_url = get_plain_stream_url(api_url)

            # Metadata
            t1 = item.find('div', class_='left-team-name').text.strip() if item.find('div', class_='left-team-name') else "T1"
            t2 = item.find('div', class_='right-team-name').text.strip() if item.find('div', class_='right-team-name') else "T2"
            
            def fix_img(cls):
                img = item.find('img', class_=cls)
                if not img: return ""
                src = img.get('src', '')
                return f"https://www.popozhibo.tv{src}" if src.startswith('/') else src

            matches.append({
                "league": item.find('div', class_='game-name').text.strip() if item.find('div', class_='game-name') else "",
                "time": item.find('div', class_='game-time').text.strip() if item.find('div', class_='game-time') else "",
                "team1": t1, "team2": t2,
                "logo1": fix_img('left-team-logo'),
                "logo2": fix_img('right-team-logo'),
                "link": plain_url
            })
        return matches
    except Exception as e:
        print(f"Scraper error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>Live Stream Decoder</title>
    <style>
        body {{ font-family: sans-serif; background: #000; color: #fff; text-align: center; }}
        .list {{ max-width: 500px; margin: auto; padding: 10px; }}
        .card {{ background: #111; border: 1px solid #222; border-radius: 10px; padding: 15px; margin-bottom: 10px; display: block; text-decoration: none; color: inherit; }}
        .teams {{ display: flex; align-items: center; justify-content: space-between; }}
        .team img {{ width: 35px; height: 35px; }}
        .vs {{ color: #ff4444; font-weight: bold; }}
        .play-btn {{ background: #00ff88; color: #000; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-top: 10px; font-weight: bold; font-size: 12px; }}
    </style>
</head>
<body>
    <h2>Live Streams (Plain URLs)</h2>
    <p style="color: #666; font-size: 10px;">Updated: {now}</p>
    <div class="list">
    """
    for m in matches:
        if m['link'] == "#": continue
        html += f"""
        <a href="{m['link']}" class="card" target="_blank">
            <div style="font-size: 11px; color: #00ff88; margin-bottom: 5px;">{m['league']} | {m['time']}</div>
            <div class="teams">
                <div class="team"><img src="{m['logo1']}"><br>{m['team1']}</div>
                <div class="vs">VS</div>
                <div class="team"><img src="{m['logo2']}"><br>{m['team2']}</div>
            </div>
            <div class="play-btn">OPEN PLAIN URL</div>
        </a>"""
    html += "</div></body></html>"
    with open("today.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generate_html(get_matches())
