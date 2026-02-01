import requests
from bs4 import BeautifulSoup
import datetime
import base64
import json

def get_real_stream_url(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.popozhibo.tv/"
    }
    try:
        # 1. Fetch the JSON data from the -url endpoint
        res = requests.get(api_url, headers=headers, timeout=10)
        data_json = res.json()
        encoded_data = data_json.get('data', '')

        if not encoded_data:
            return "#"

        # 2. Decode the Base64 data (Removing the "zh" suffix)
        clean_b64 = encoded_data.replace("zh", "")
        # Add padding if needed
        clean_b64 += "=" * ((4 - len(clean_b64) % 4) % 4)
        
        decoded_bytes = base64.b64decode(clean_b64)
        decoded_json = json.loads(decoded_bytes)

        # 3. Extract the actual stream link
        # It's usually the first link in the list
        return decoded_json['links'][0]['url']
    except Exception as e:
        print(f"Failed to decode {api_url}: {e}")
        return "#"

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []
        items = soup.find_all('li')

        for item in items:
            if not item.find('div', class_='vs'): continue
            
            # Extract basic info
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else "T1"
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else "T2"
            
            # Get Logos
            t1_img = item.find('img', class_='left-team-logo')
            t2_img = item.find('img', class_='right-team-logo')
            def fix_img(p):
                if not p: return ""
                return f"https://www.popozhibo.tv{p}" if p.startswith('/') else p

            # GET THE REAL STREAM LINK
            link_tag = item.find('a', href=True)
            real_link = "#"
            if link_tag:
                play_path = link_tag['href'].rstrip('/')
                api_url = f"https://www.popozhibo.tv{play_path}-url"
                print(f"Decoding: {t1_name} vs {t2_name}...")
                real_link = get_real_stream_url(api_url)

            matches.append({
                "time": time, "league": league, "team1": t1_name, "team2": t2_name,
                "logo1": fix_img(t1_img.get('src')) if t1_img else "",
                "logo2": fix_img(t2_img.get('src')) if t2_img else "",
                "link": real_link
            })
        return matches
    except Exception as e:
        print(f"Scraper Error: {e}"); return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>Live Streams</title>
    <style>
        body {{ font-family: sans-serif; background: #000; color: #fff; margin: 0; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        .match-row {{ 
            background: #111; border: 1px solid #222; border-radius: 12px; 
            padding: 15px; margin-bottom: 10px; display: flex; align-items: center; 
            text-decoration: none; color: inherit; 
        }}
        .time-box {{ width: 80px; font-size: 11px; border-right: 1px solid #333; }}
        .league {{ color: #00ff88; font-weight: bold; display: block; }}
        .game {{ flex: 1; display: flex; justify-content: space-around; align-items: center; text-align: center; }}
        .team img {{ width: 32px; height: 32px; object-fit: contain; }}
        .name {{ font-size: 12px; display: block; margin-top: 4px; }}
        .vs {{ color: #ff4444; font-weight: bold; font-size: 12px; }}
        .play-now {{ font-size: 10px; background: #ff4444; padding: 2px 5px; border-radius: 4px; margin-top: 5px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#00ff88;">Live Stream List</h2>
        <p style="text-align:center; font-size:10px; color:#555;">Updated: {now}</p>
        <div id="list">
    """
    for m in matches:
        # Only show matches that actually have a link
        if m['link'] != "#":
            html_template += f"""
            <a href="{m['link']}" class="match-row" target="_blank">
                <div class="time-box">
                    <span class="league">{m['league']}</span>
                    <span>{m['time']}</span>
                    <span class="play-now">LIVE</span>
                </div>
                <div class="game">
                    <div class="team"><img src="{m['logo1']}"> <span class="name">{m['team1']}</span></div>
                    <div class="vs">VS</div>
                    <div class="team"><img src="{m['logo2']}"> <span class="name">{m['team2']}</span></div>
                </div>
            </a>"""
    html_template += "</div></div></body></html>"
    with open("today.html", "w", encoding="utf-8") as f: f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
