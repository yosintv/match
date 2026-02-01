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

        # Target the <li> tags that contain the match info
        items = soup.find_all('li')

        for item in items:
            # Check if this <li> actually contains a match by looking for the "vs" div
            if not item.find('div', class_='vs'):
                continue
            
            # Extract Data
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            
            team_left = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else "Team 1"
            team_right = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else "Team 2"
            
            logo_left = item.find('img', class_='left-team-logo')
            logo_right = item.find('img', class_='right-team-logo')
            
            src_left = logo_left.get('src') if logo_left else ""
            src_right = logo_right.get('src') if logo_right else ""

            matches.append({
                "time": time,
                "league": league,
                "team1": team_left,
                "team2": team_right,
                "logo1": src_left,
                "logo2": src_right
            })
                
        return matches
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Today's Matches</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: auto; }}
        h1 {{ text-align: center; color: #00e676; }}
        .update-time {{ text-align: center; color: #999; font-size: 0.8em; margin-bottom: 30px; }}
        .match-card {{ background: #1e1e1e; border-radius: 12px; padding: 15px; margin-bottom: 15px; display: flex; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .time-box {{ width: 100px; text-align: left; border-right: 1px solid #333; margin-right: 15px; }}
        .league {{ font-size: 0.75em; color: #00e676; display: block; }}
        .time {{ font-weight: bold; font-size: 0.9em; }}
        .teams-container {{ flex-grow: 1; display: flex; align-items: center; justify-content: space-around; }}
        .team {{ width: 40%; display: flex; flex-direction: column; align-items: center; text-align: center; }}
        .team img {{ width: 45px; height: 45px; object-fit: contain; margin-bottom: 5px; }}
        .vs {{ font-weight: bold; color: #ff5252; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Live Schedule</h1>
        <p class="update-time">Last Update: {now}</p>
        <div id="list">
    """
    
    if not matches:
        html_template += "<p style='text-align:center;'>No matches found at the moment.</p>"
    else:
        for m in matches:
            html_template += f"""
            <div class="match-card">
                <div class="time-box">
                    <span class="league">{m['league']}</span>
                    <span class="time">{m['time']}</span>
                </div>
                <div class="teams-container">
                    <div class="team">
                        <img src="{m['logo1']}" onerror="this.src='https://via.placeholder.com/45?text=?'}">
                        <span>{m['team1']}</span>
                    </div>
                    <div class="vs">VS</div>
                    <div class="team">
                        <img src="{m['logo2']}" onerror="this.src='https://via.placeholder.com/45?text=?'}">
                        <span>{m['team2']}</span>
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
    data = get_matches()
    generate_html(data)
