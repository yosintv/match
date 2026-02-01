import requests
from bs4 import BeautifulSoup
import datetime

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

        # Find all list items (li)
        items = soup.find_all('li')

        for item in items:
            # Check for the 'vs' indicator to ensure it's a match row
            vs_div = item.find('div', class_='vs')
            if not vs_div:
                continue
            
            # 1. Get Time and League
            time_tag = item.find('div', class_='game-time')
            league_tag = item.find('div', class_='game-name')
            
            time = time_tag.get_text(strip=True) if time_tag else ""
            league = league_tag.get_text(strip=True) if league_tag else ""
            
            # 2. Get Teams
            t1_name_tag = item.find('div', class_='left-team-name')
            t2_name_tag = item.find('div', class_='right-team-name')
            
            t1_name = t1_name_tag.get_text(strip=True) if t1_name_tag else "Team 1"
            t2_name = t2_name_tag.get_text(strip=True) if t2_name_tag else "Team 2"
            
            # 3. Get Logos
            t1_img = item.find('img', class_='left-team-logo')
            t2_img = item.find('img', class_='right-team-logo')
            
            # 4. Get Link
            link_tag = item.find('a', href=True)
            raw_link = link_tag['href'] if link_tag else "#"

            def fix_url(path):
                if not path or path == "#": return "#"
                if path.startswith('//'): return f"https:{path}"
                if path.startswith('/'): return f"https://www.popozhibo.tv{path}"
                return path

            matches.append({
                "time": time,
                "league": league,
                "team1": t1_name,
                "team2": t2_name,
                "logo1": fix_url(t1_img.get('src')) if t1_img else "",
                "logo2": fix_url(t2_img.get('src')) if t2_img else "",
                "link": fix_url(raw_link)
            })
                
        return matches
    except Exception as e:
        print(f"Scraper Error: {e}")
        return []

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
        h2 {{ text-align: center; color: #00ff88; margin-top: 10px; }}
        .update {{ text-align: center; color: #555; font-size: 10px; margin-bottom: 15px; }}
        .match-link {{ text-decoration: none; color: inherit; display: block; margin-bottom: 10px; }}
        .match-row {{ 
            background: #111; border: 1px solid #222; border-radius: 10px; 
            padding: 12px; display: flex; align-items: center; 
        }}
        .time-col {{ width: 70px; font-size: 11px; border-right: 1px solid #333; margin-right: 10px; }}
        .league-text {{ color: #00ff88; font-weight: bold; display: block; }}
        .game-area {{ flex: 1; display: flex; align-items: center; justify-content: space-around; }}
        .team-box {{ width: 40%; text-align: center; }}
        .team-logo {{ width: 32px; height: 32px; object-fit: contain; }}
        .name {{ font-size: 13px; display: block; margin-top: 5px; }}
        .vs-text {{ font-weight: bold; color: #ff4444; font-size: 12px; }}
        .watch {{ font-size: 9px; background: #333; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Live Schedule</h2>
        <p class="update">Last Sync: {now}</p>
        <div id="list">
    """
    
    if not matches:
        html_template += "<p style='text-align:center; color:#888;'>No matches found. Refreshing soon...</p>"
    else:
        for m in matches:
            html_template += f"""
            <a href="{m['link']}" class="match-link" target="_blank">
                <div class="match-row">
                    <div class="time-col">
                        <span class="league-text">{m['league']}</span>
                        <span>{m['time']}</span>
                        <span class="watch">PLAY</span>
                    </div>
                    <div class="game-area">
                        <div class="team-box">
                            <img class="team-logo" src="{m['logo1']}">
                            <span class="name">{m['team1']}</span>
                        </div>
                        <div class="vs-text">VS</div>
                        <div class="team-box">
                            <img class="team-logo" src="{m['logo2']}">
                            <span class="name">{m['team2']}</span>
                        </div>
                    </div>
                </div>
            </a>"""
    
    html_template += """
        </div>
    </div>
</body>
</html>"""
    
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
