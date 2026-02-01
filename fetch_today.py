import requests
from bs4 import BeautifulSoup
import datetime

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        matches = []
        # Target match containers - adjust class names if the site structure changes
        items = soup.find_all(['div', 'li'], class_=['match-item', 'game-item', 'list-item'])
        
        if not items: # Fallback: search for any div containing "vs"
            items = [el.parent for el in soup.find_all(string=lambda t: "vs" in t.lower())]

        for item in items:
            imgs = item.find_all('img')
            # Extract team names from text
            text = item.get_text(separator=" ", strip=True)
            
            if len(imgs) >= 2 and "vs" in text.lower():
                logo1 = imgs[0].get('src') or imgs[0].get('data-src')
                logo2 = imgs[1].get('src') or imgs[1].get('data-src')
                
                # Logic to clean names (e.g., "10:00 Team A vs Team B" -> "Team A vs Team B")
                display_text = text.split("直播")[0] # Common on Chinese sports sites
                
                matches.append({
                    "text": display_text,
                    "logo1": logo1 if logo1.startswith('http') else f"https:{logo1}",
                    "logo2": logo2 if logo2.startswith('http') else f"https:{logo2}"
                })
        return matches
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Today's Matches</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f4f4; text-align: center; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
            .match {{ display: flex; align-items: center; justify-content: space-between; 
                      padding: 15px; border-bottom: 1px solid #eee; }}
            .team-img {{ width: 40px; height: 40px; object-fit: contain; }}
            .match-info {{ flex-grow: 1; font-weight: bold; font-size: 1.1em; }}
            .update-time {{ color: #888; font-size: 0.8em; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Live Matches</h1>
            <p class="update-time">Last Updated: {now}</p>
            <div id="list">
    """
    
    for m in matches:
        html_template += f"""
            <div class="match">
                <img src="{m['logo1']}" class="team-img" alt="logo1">
                <div class="match-info">{m['text']}</div>
                <img src="{m['logo2']}" class="team-img" alt="logo2">
            </div>
        """
    
    html_template += """
            </div>
        </div>
    </body>
    </html>
    """
    
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    match_data = get_matches()
    generate_html(match_data)
