import requests
from bs4 import BeautifulSoup
import datetime

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
        items = soup.find_all('li')

        for item in items:
            if not item.find('div', class_='vs'): continue
            
            # 1. Extract Info
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else ""
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else ""
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""

            # 2. Build the exact "play-url" link
            link_tag = item.find('a', href=True)
            if link_tag and '/live/' in link_tag['href']:
                # Example: /live/114276 -> https://www.popozhibo.tv/live/114276/play-url
                match_id_path = link_tag['href'].rstrip('/')
                final_json_url = f"https://www.popozhibo.tv{match_id_path}/play-url"
            else:
                continue

            # 3. Get Logos
            def fix_img(cls):
                tag = item.find('img', class_=cls)
                if not tag or not tag.get('src'): return ""
                src = tag.get('src')
                return f"https://www.popozhibo.tv{src}" if src.startswith('/') else src

            matches.append({
                "time": time,
                "league": league,
                "team1": t1_name,
                "team2": t2_name,
                "logo1": fix_img('left-team-logo'),
                "logo2": fix_img('right-team-logo'),
                "link": final_json_url
            })
        return matches
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSON Link Center</title>
    <style>
        body {{ font-family: sans-serif; background: #0a0a0a; color: #fff; padding: 20px; }}
        .container {{ max-width: 600px; margin: auto; }}
        .match-card {{ 
            background: #1a1a1a; border: 1px solid #333; border-radius: 8px; 
            padding: 15px; margin-bottom: 12px; display: block; 
            text-decoration: none; color: inherit; transition: 0.2s;
        }}
        .match-card:hover {{ border-color: #00ff88; background: #222; }}
        .meta {{ font-size: 12px; color: #888; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }}
        .teams {{ display: flex; justify-content: space-between; align-items: center; }}
        .team {{ text-align: center; width: 40%; }}
        .team img {{ width: 40px; height: 40px; object-fit: contain; }}
        .vs {{ font-weight: bold; color: #ff4444; }}
        .json-label {{ 
            display: inline-block; background: #00ff88; color: #000; 
            font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center;">Today's JSON Stream Links</h2>
        <p style="text-align:center; font-size:11px; color:#666;">Last Sync: {now}</p>
    """
    for m in matches:
        html_template += f"""
        <a href="{m['link']}" class="match-card" target="_blank">
            <div class="meta"><b>{m['league']}</b> | {m['time']}</div>
            <div class="teams">
                <div class="team"><img src="{m['logo1']}"><br>{m['team1']}</div>
                <div class="vs">VS</div>
                <div class="team"><img src="{m['logo2']}"><br>{m['team2']}</div>
            </div>
            <div class="json-label">CLICK FOR RAW JSON</div>
        </a>"""
    
    html_template += "</div></body></html>"
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
