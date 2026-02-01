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

        # Target all <li> tags
        items = soup.find_all('li')

        for item in items:
            # Only process if it has the 'vs' element
            if not item.find('div', class_='vs'):
                continue
            
            # Extract Data using the classes from your view-source
            time = item.find('div', class_='game-time').get_text(strip=True) if item.find('div', class_='game-time') else ""
            league = item.find('div', class_='game-name').get_text(strip=True) if item.find('div', class_='game-name') else ""
            
            t1_name = item.find('div', class_='left-team-name').get_text(strip=True) if item.find('div', class_='left-team-name') else "Team 1"
            t2_name = item.find('div', class_='right-team-name').get_text(strip=True) if item.find('div', class_='right-team-name') else "Team 2"
            
            t1_logo = item.find('img', class_='left-team-logo')
            t2_logo = item.find('img', class_='right-team-logo')
            
            src1 = t1_logo.get('src') if t1_logo else ""
            src2 = t2_logo.get('src') if t2_logo else ""

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
        print(f"Error fetching data: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Note: Double curly braces {{ }} are used below to escape them in the f-string
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Today's Match Schedule</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0f0f0f; color: #fff; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: auto; }}
        h1 {{ text-align: center; color: #00ff88; margin-bottom: 5px; }}
        .update-tag {{ text-align: center; color: #777; font-size: 12px; margin-bottom: 25px; }}
        .match-card {{ 
            background: #1a1a1a; border-radius: 10px; padding: 15px; 
            margin-bottom: 12px; display: flex; align-items: center;
            border-left: 4px solid #00ff88; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}
        .meta-info {{ width: 80px; font-size: 12px; border-right: 1px solid #333; padding-right: 10px; }}
        .league-name {{ color: #00ff88; display: block; font-weight: bold; }}
        .match-box {{ flex: 1; display: flex; align-items: center; justify-content: space-evenly; padding-left: 10px; }}
        .team {{ text-align: center; width: 40%; }}
        .team img {{ width: 35px; height: 35px; object-fit: contain; display: block; margin: 0 auto 5px; }}
        .team span {{ font-size: 14px; font-weight: 500; }}
        .vs-text {{ font-weight: bold; color: #ff3e3e; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Live Matches</h1>
        <p class="update-tag">Updated: {now}</p>
        <div id="list">
    """
    
    if not matches:
        html_template += "<p style='text-align:center;'>No matches found right now.</p>"
    else:
        for m in matches:
            # We use {{ }} for the JS onerror to avoid Python f-string errors
            html_template += f"""
            <div class="match-card">
                <div class="meta-info">
                    <span class="league-name">{m['league']}</span>
                    <span>{m['time']}</span>
                </div>
                <div class="match-box">
                    <div class="team">
                        <img src="{m['logo1']}" onerror="this.src='https://via.placeholder.com/35?text=?'">
                        <span>{m['team1']}</span>
                    </div>
                    <div class="vs-text">VS</div>
                    <div class="team">
                        <img src="{m['logo2']}" onerror="this.src='https://via.placeholder.com/35?text=?'">
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
    match_data = get_matches()
    generate_html(match_data)
