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

        # Target the match list items
        items = soup.find_all('li')

        for item in items:
            if not item.find('div', class_='vs'):
                continue
            
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            
            # Exact class names from your source
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else ""
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else ""
            
            t1_logo_tag = item.find('img', class_='left-team-logo')
            t2_logo_tag = item.find('img', class_='right-team-logo')
            
            src1 = t1_logo_tag.get('src') if t1_logo_tag else ""
            src2 = t2_logo_tag.get('src') if t2_logo_tag else ""

            if t1_name and t2_name:
                matches.append({
                    "time": time,
                    "league": league,
                    "team1": t1_name,
                    "team2": t2_name,
                    "logo1": src1,
                    "logo2": src2
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
    <title>Live Sports Today</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #121212; color: #fff; margin: 0; padding: 15px; }}
        .container {{ max-width: 600px; margin: auto; }}
        h1 {{ text-align: center; color: #00ff88; font-size: 24px; }}
        .update-time {{ text-align: center; color: #666; font-size: 11px; margin-bottom: 20px; }}
        .match-card {{ 
            background: #1e1e1e; border-radius: 8px; padding: 12px; 
            margin-bottom: 10px; display: flex; align-items: center; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.4);
        }}
        .info {{ width: 70px; border-right: 1px solid #333; margin-right: 10px; font-size: 12px; }}
        .league {{ color: #00ff88; font-weight: bold; display: block; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
        .teams {{ flex: 1; display: flex; align-items: center; justify-content: space-evenly; }}
        .team {{ width: 42%; text-align: center; }}
        /* Specific sizing for the logos */
        .team-logo-min {{ width: 35px; height: 35px; object-fit: contain; margin-bottom: 4px; }}
        .team-name {{ font-size: 13px; display: block; }}
        .vs {{ font-weight: bold; color: #ff4444; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Today's Schedule</h1>
        <p class="update-time">Synced: {now}</p>
        <div id="list">
    """
    
    for m in matches:
        # Added referrerPolicy="no-referrer" to the img tags
        html_template += f"""
            <div class="match-card">
                <div class="info">
                    <span class="league">{m['league']}</span>
                    <span>{m['time']}</span>
                </div>
                <div class="teams">
                    <div class="team">
                        <img class="team-logo-min" src="{m['logo1']}" referrerPolicy="no-referrer" onerror="this.src='https://via.placeholder.com/35?text=?'">
                        <span class="team-name">{m['team1']}</span>
                    </div>
                    <div class="vs">VS</div>
                    <div class="team">
                        <img class="team-logo-min" src="{m['logo2']}" referrerPolicy="no-referrer" onerror="this.src='https://via.placeholder.com/35?text=?'">
                        <span class="team-name">{m['team2']}</span>
                    </div>
                </div>
            </div>"""
    
    html_template += """
        </div>
    </div>
</body>
</html>"""
    
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
