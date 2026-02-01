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
        res = requests.get(api_url, headers=headers, timeout=10)
        data_json = res.json()
        encoded_data = data_json.get('data', '')
        if not encoded_data: return "#"
        
        clean_b64 = encoded_data.replace("zh", "")
        clean_b64 += "=" * ((4 - len(clean_b64) % 4) % 4)
        decoded_bytes = base64.b64decode(clean_b64)
        decoded_json = json.loads(decoded_bytes)
        return decoded_json['links'][0]['url']
    except:
        return "#"

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []

        # Target all VS containers
        vs_elements = soup.find_all(string=lambda t: "VS" in t.upper())

        for vs in vs_elements:
            # Move up to find the container (li or div)
            parent = vs.find_parent(['li', 'div', 'a'], class_=lambda x: x != 'vs')
            if not parent: continue

            # Extract Data based on classes or relative position
            time = parent.find(class_='game-time')
            league = parent.find(class_='game-name')
            t1_name = parent.find(class_='left-team-name')
            t2_name = parent.find(class_='right-team-name')
            t1_logo = parent.find('img', class_='left-team-logo')
            t2_logo = parent.find('img', class_='right-team-logo')
            link_tag = parent.find('a', href=True) or (parent if parent.name == 'a' else None)

            if t1_name and t2_name:
                t1 = t1_name.get_text(strip=True)
                t2 = t2_name.get_text(strip=True)
                
                # Get the link and decode it immediately
                real_link = "#"
                if link_tag and 'live' in link_tag['href']:
                    play_path = link_tag['href'].rstrip('/')
                    api_url = f"https://www.popozhibo.tv{play_path}-url"
                    real_link = get_real_stream_url(api_url)

                def fix_img(img):
                    if not img or not img.get('src'): return ""
                    p = img.get('src')
                    return f"https://www.popozhibo.tv{p}" if p.startswith('/') else p

                matches.append({
                    "time": time.get_text(strip=True) if time else "",
                    "league": league.get_text(strip=True) if league else "",
                    "team1": t1,
                    "team2": t2,
                    "logo1": fix_img(t1_logo),
                    "logo2": fix_img(t2_logo),
                    "link": real_link
                })
        
        # Deduplicate
        seen = set()
        unique_matches = []
        for m in matches:
            identifier = f"{m['team1']}{m['team2']}"
            if identifier not in seen:
                unique_matches.append(m)
                seen.add(identifier)
        return unique_matches

    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(matches):
    now = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M") # CST Time
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
        .match-row {{ background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px; margin-bottom: 10px; display: flex; align-items: center; text-decoration: none; color: inherit; }}
        .time-box {{ width: 80px; font-size: 11px; border-right: 1px solid #333; margin-right: 10px; }}
        .league {{ color: #00ff88; font-weight: bold; display: block; }}
        .game {{ flex: 1; display: flex; justify-content: space-around; align-items: center; text-align: center; }}
        .team img {{ width: 32px; height: 32px; object-fit: contain; }}
        .name {{ font-size: 12px; display: block; margin-top: 4px; }}
        .vs {{ color: #ff4444; font-weight: bold; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#00ff88;">Live Stream List</h2>
        <p style="text-align:center; font-size:10px; color:#555;">Updated: {now} (CST)</p>
        <div id="list">
    """
    for m in matches:
        html_template += f"""
        <a href="{m['link']}" class="match-row" target="_blank">
            <div class="time-box">
                <span class="league">{m['league']}</span>
                <span>{m['time']}</span>
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
