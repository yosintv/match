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

        # Find all match list items
        items = soup.find_all('li')

        for item in items:
            # Verify it's a match row
            if not item.find('div', class_='vs'):
                continue
            
            # 1. Get Meta Info
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            
            # 2. Get Teams
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else "Team 1"
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else "Team 2"
            
            # 3. Get Logos
            t1_img = item.find('img', class_='left-team-logo')
            t2_img = item.find('img', class_='right-team-logo')
            
            # 4. Get and Modify Link
            link_tag = item.find('a', href=True)
            raw_link = link_tag['href'] if link_tag else ""

            def fix_link_with_suffix(path):
                if not path: return "#"
                # Remove trailing slashes if they exist so -url attaches correctly
                path = path.rstrip('/')
                # Construct full URL
                full_url = f"https://www.popozhibo.tv{path}" if path.startswith('/') else path
                # Add the -url suffix
                return f"{full_url}-url"

            def fix_img_url(path):
                if not path: return ""
                if path.startswith('//'): return f"https:{path}"
                if path.startswith('/'): return f"https://www.popozhibo.tv{path}"
                return path

            matches.append({
                "time": time,
                "league": league,
                "team1": t1_name,
                "team2": t2_name,
                "logo1": fix_img_url(t1_img.get('src')) if t1_img else "",
                "logo2": fix_img_url(t2_img.get('src')) if t2_img else "",
                "link": fix_link_with_suffix(raw_link)
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
    <title>Today's Live Match</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #080808; color: #fff; margin: 0; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        h2 {{ text-align: center; color: #00ff88; letter-spacing: 1px; }}
        .update {{ text-align: center; color: #444; font-size: 10px; margin-bottom: 20px; }}
        .match-link {{ text-decoration: none; color: inherit; display: block; margin-bottom: 12px; }}
        .match-row {{ 
            background: #121212; border: 1px solid #222; border-radius: 15px; 
            padding: 15px; display: flex; align-items: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}
        .time-col {{ width: 80px; font-size: 11px; border-right: 1px solid #2a2a2a; margin-right: 10px; }}
        .league-text {{ color: #00ff88; font-weight: bold; display: block; margin-bottom: 3px; }}
        .game-area {{ flex: 1; display: flex; align-items: center; justify-content: space-around; }}
        .team-box {{ width: 40%; text-align: center; }}
        .team-logo {{ width: 38px; height: 38px; object-fit: contain; }}
        .name {{ font-size: 13px; display: block; margin-top: 6px; font-weight: 500; }}
        .vs-text {{ font-weight: bold; color: #ff4444; font-size: 14px; opacity: 0.8; }}
        .play-btn {{ 
            background: #00ff88; color: #000; font-size: 9px; 
            font-weight: bold; padding: 2px 6px; border-radius: 4px; 
            display: inline-block; margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Live Streams</h2>
        <p class="update">Last Sync: {now}</p>
        <div id="list">
    """
    
    if not matches:
        html_template += "<p style='text-align:center; color:#666;'>No matches live. Checking again soon...</p>"
    else:
        for m in matches:
            html_template += f"""
            <a href="{m['link']}" class="match-link" target="_blank">
                <div class="match-row">
                    <div class="time-col">
                        <span class="league-text">{m['league']}</span>
                        <span>{m['time']}</span>
                        <div class="play-btn">WATCH</div>
                    </div>
                    <div class="game-area">
                        <div class="team-box">
                            <img class="team-logo" src="{m['logo1']}" referrerPolicy="no-referrer">
                            <span class="name">{m['team1']}</span>
                        </div>
                        <div class="vs-text">VS</div>
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
