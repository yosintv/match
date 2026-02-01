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
        # Request the -url JSON
        res = requests.get(api_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return "#"
            
        data_json = res.json()
        encoded_data = data_json.get('data', '')
        if not encoded_data:
            return "#"
        
        # Decode the encrypted string
        clean_b64 = encoded_data.replace("zh", "")
        clean_b64 += "=" * ((4 - len(clean_b64) % 4) % 4)
        decoded_bytes = base64.b64decode(clean_b64)
        decoded_json = json.loads(decoded_bytes)
        
        # Get the final direct stream URL
        return decoded_json['links'][0]['url']
    except Exception as e:
        print(f"Error decoding {api_url}: {e}")
        return "#"

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []

        # Find all <li> tags which represent match rows
        items = soup.find_all('li')

        for item in items:
            # Check if this <li> is actually a match row
            if not item.find('div', class_='vs'):
                continue

            # 1. Extract Info
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else ""
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else ""
            
            # 2. Extract Link and Get Real URL
            # We look for the play link (e.g., /live/114847/play)
            link_tag = item.find('a', href=True)
            real_link = "#"
            
            if link_tag and '/live/' in link_tag['href']:
                path = link_tag['href'].rstrip('/')
                # If path is just /live/123, we make it /live/123/play-url
                if not path.endswith('/play'):
                    api_url = f"https://www.popozhibo.tv{path}/play-url"
                else:
                    api_url = f"https://www.popozhibo.tv{path}-url"
                
                print(f"Fetching real link for: {t1_name} vs {t2_name}")
                real_link = get_real_stream_url(api_url)

            # 3. Extract Logos
            def fix_img(img_class):
                tag = item.find('img', class_=img_class)
                if not tag or not tag.get('src'): return ""
                src = tag.get('src')
                return f"https://www.popozhibo.tv{src}" if src.startswith('/') else src

            if t1_name and t2_name:
                matches.append({
                    "time": time,
                    "league": league,
                    "team1": t1_name,
                    "team2": t2_name,
                    "logo1": fix_img('left-team-logo'),
                    "logo2": fix_img('right-team-logo'),
                    "link": real_link
                })
        
        return matches

    except Exception as e:
        print(f"Major Error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>Today's Live Matches</title>
    <style>
        body {{ font-family: sans-serif; background: #000; color: #fff; margin: 0; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        .match-row {{ 
            background: #111; border: 1px solid #222; border-radius: 12px; 
            padding: 15px; margin-bottom: 10px; display: flex; align-items: center; 
            text-decoration: none; color: inherit; 
        }}
        .time-box {{ width: 80px; font-size: 11px; border-right: 1px solid #333; margin-right: 10px; }}
        .league {{ color: #00ff88; font-weight: bold; display: block; }}
        .game {{ flex: 1; display: flex; justify-content: space-around; align-items: center; text-align: center; }}
        .team img {{ width: 32px; height: 32px; object-fit: contain; }}
        .name {{ font-size: 12px; display: block; margin-top: 4px; }}
        .vs {{ color: #ff4444; font-weight: bold; font-size: 12px; }}
        .btn {{ font-size: 9px; background: #ff4444; color: white; padding: 2px 4px; border-radius: 3px; margin-top: 5px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#00ff88;">Live Stream List</h2>
        <p style="text-align:center; font-size:10px; color:#555;">Updated: {now}</p>
        <div id="list">
    """
    for m in matches:
        # We only output the row if a real link was found
        if m['link'] != "#":
            html_template += f"""
            <a href="{m['link']}" class="match-row" target="_blank">
                <div class="time-box">
                    <span class="league">{m['league']}</span>
                    <span>{m['time']}</span>
                    <span class="btn">LIVE</span>
                </div>
                <div class="game">
                    <div class="team"><img src="{m['logo1']}"> <span class="name">{m['team1']}</span></div>
                    <div class="vs">VS</div>
                    <div class="team"><img src="{m['logo2']}"> <span class="name">{m['team2']}</span></div>
                </div>
            </a>"""
    
    html_template += "</div></div></body></html>"
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
