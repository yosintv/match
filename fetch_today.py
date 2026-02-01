import requests
from bs4 import BeautifulSoup
import datetime
import urllib.parse

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.popozhibo.tv/"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []
        items = soup.find_all('li')

        for item in items:
            if not item.find('div', class_='vs'): continue
            
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else "Team 1"
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else "Team 2"
            t1_img = item.find('img', class_='left-team-logo')
            t2_img = item.find('img', class_='right-team-logo')
            
            link_tag = item.find('a', href=True)
            raw_path = link_tag['href'].rstrip('/') if link_tag else ""
            
            # Construct the final -url link
            base_stream_url = f"https://www.popozhibo.tv{raw_path}-url"
            # Encode it so it can be passed as a URL parameter safely
            safe_target = urllib.parse.quote(base_stream_url)

            def fix_img(p):
                if not p: return ""
                return f"https://www.popozhibo.tv{p}" if p.startswith('/') else p

            matches.append({
                "time": time, "league": league, "team1": t1_name, "team2": t2_name,
                "logo1": fix_img(t1_img.get('src')) if t1_img else "",
                "logo2": fix_img(t2_img.get('src')) if t2_img else "",
                "link": f"url.html?target={safe_target}"
            })
        return matches
    except Exception as e:
        print(f"Error: {e}"); return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>Live Schedule</title>
    <style>
        body {{ font-family: sans-serif; background: #000; color: #fff; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        .match-card {{ background: #111; border-radius: 12px; padding: 15px; margin-bottom: 10px; display: flex; align-items: center; text-decoration: none; color: inherit; border: 1px solid #222; }}
        .info {{ width: 80px; font-size: 11px; border-right: 1px solid #333; margin-right: 10px; }}
        .league {{ color: #00ff88; font-weight: bold; display: block; }}
        .teams {{ flex: 1; display: flex; justify-content: space-around; align-items: center; }}
        .team {{ text-align: center; width: 40%; }}
        .team img {{ width: 35px; height: 35px; object-fit: contain; }}
        .team span {{ font-size: 13px; display: block; margin-top: 5px; }}
        .vs {{ color: #ff4444; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#00ff88;">Live Streams</h2>
        <p style="text-align:center; font-size:10px; color:#555;">Updated: {now}</p>
    """
    for m in matches:
        html_template += f"""
        <a href="{m['link']}" class="match-card">
            <div class="info">
                <span class="league">{m['league']}</span>
                <span>{m['time']}</span>
            </div>
            <div class="teams">
                <div class="team">
                    <img src="{m['logo1']}" referrerPolicy="no-referrer">
                    <span>{m['team1']}</span>
                </div>
                <div class="vs">VS</div>
                <div class="team">
                    <img src="{m['logo2']}" referrerPolicy="no-referrer">
                    <span>{m['team2']}</span>
                </div>
            </div>
        </a>"""
    html_template += "</div></body></html>"
    with open("today.html", "w", encoding="utf-8") as f: f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
