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

        # Target the <li> items
        items = soup.find_all('li')

        for item in items:
            if not item.find('div', class_='vs'):
                continue
            
            # Extract Meta info
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            
            # Extract Teams and Logos
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else ""
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else ""
            
            t1_logo_tag = item.find('img', class_='left-team-logo')
            t2_logo_tag = item.find('img', class_='right-team-logo')
            
            # Extract Watch Link
            play_tag = item.find('div', class_='game-play')
            link_tag = play_tag.find('a') if play_tag else None
            raw_link = link_tag.get('href') if link_tag else "#"

            def fix_url(src):
                if not src or src == "#": return "#"
                if src.startswith('//'): return f"https:{src}"
                if src.startswith('/'): return f"https://www.popozhibo.tv{src}"
                return src

            matches.append({
                "time": time,
                "league": league,
                "team1": t1_name,
                "team2": t2_name,
                "logo1": fix_url(src1 if (src1 := t1_logo_tag.get('src')) else ""),
                "logo2": fix_url(src2 if (src2 := t2_logo_tag.get('src')) else ""),
                "link": fix_url(raw_link)
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
    <meta name="referrer" content="no-referrer">
    <title>Live Match Schedule</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #0a0a0a; color: #fff; margin: 0; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        h2 {{ text-align: center; color: #00ff88; margin: 15px 0; }}
        .update {{ text-align: center; color: #555; font-size: 10px; margin-bottom: 15px; }}
        
        .match-link {{ text-decoration: none; color: inherit; display: block; }}
        
        .match-row {{ 
            background: #161616; border: 1px solid #222; border-radius: 12px; 
            padding: 12px; margin-bottom: 10px; display: flex; align-items: center;
            transition: transform 0.2s, background 0.2s;
        }}
        .match-row:hover {{ background: #1f1f1f; transform: scale(1.01); }}
        
        .time-col {{ width: 70px; font-size: 11px; border-right: 1px solid #333; margin-right: 10px; }}
        .league-text {{ color: #00ff88; font-weight: bold; display: block; }}
        
        .game-area {{ flex: 1; display: flex; align-items: center; justify-content: space-around; }}
        .team-box {{ width: 40%; text-align: center; }}
        .team-logo {{ width: 35px; height: 35px; object-fit: contain; }}
        .name {{ font-size: 13px; display: block; margin-top: 5px; color: #eee; }}
        .vs-sign {{ font-weight: bold; color: #ff4444; font-size: 12px; padding: 0 5px; }}
        
        .live-btn {{ 
            font-size: 10px; background: #ff4444; color: white; 
            padding: 2px 6px; border-radius: 4px; margin-top: 4px; display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Live Streams</h2>
        <p class="update">Synced: {now}</p>
        <div id="list">
    """
    
    for m in matches:
        html_template += f"""
        <a href="{m['link']}" class="match-link" target="_blank">
            <div class="match-row">
                <div class="time-col">
                    <span class="league-text">{m['league']}</span>
                    <span>{m['time']}</span>
                    <span class="live-btn">WATCH</span>
                </div>
                <div class="game-area">
                    <div class="team-box">
                        <img class="team-logo" src="{m['logo1']}" referrerPolicy="no-referrer">
                        <span class="name">{m['team1']}</span>
                    </div>
                    <div class="vs-sign">VS</div>
                    <div class="team-box">
                        <img class="team-logo" src="{m['logo2']}" referrerPolicy="no-referrer">
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
