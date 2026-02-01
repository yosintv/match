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

        # 1. Try targeting common streaming site structures (list items or match divs)
        items = soup.find_all(['div', 'li', 'a'], class_=['match', 'game', 'list-item', 'match-item'])

        # 2. If nothing found, find everything that looks like a match row
        if not items:
            items = soup.find_all(True, class_=lambda x: x and ('item' in x or 'match' in x))

        for item in items:
            # Look for images (logos)
            imgs = item.find_all('img')
            
            # Cleanly extract text
            text = item.get_text(" ", strip=True)
            
            if "vs" in text.lower() and len(imgs) >= 2:
                # Use data-src if src is just a placeholder (lazy loading)
                logo1 = imgs[0].get('data-src') or imgs[0].get('src')
                logo2 = imgs[1].get('data-src') or imgs[1].get('src')

                # Ensure URL is absolute
                def fix_url(u):
                    if not u: return ""
                    if u.startswith('//'): return f"https:{u}"
                    if u.startswith('/'): return f"https://www.popozhibo.tv{u}"
                    return u

                matches.append({
                    "text": text,
                    "logo1": fix_url(logo1),
                    "logo2": fix_url(logo2)
                })

        # Remove duplicates
        unique_matches = []
        seen = set()
        for m in matches:
            if m['text'] not in seen:
                unique_matches.append(m)
                seen.add(m['text'])
                
        return unique_matches
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>Today's Matches</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 20px; }}
        .container {{ max-width: 700px; margin: auto; background: #2d2d2d; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
        .match {{ display: flex; align-items: center; justify-content: space-between; 
                  padding: 15px; border-bottom: 1px solid #444; transition: background 0.3s; }}
        .match:hover {{ background: #3d3d3d; }}
        .team-img {{ width: 50px; height: 50px; object-fit: contain; background: #eee; border-radius: 50%; padding: 5px; }}
        .match-info {{ flex-grow: 1; font-weight: bold; font-size: 1.1em; padding: 0 15px; }}
        .update-time {{ color: #aaa; font-size: 0.8em; margin-bottom: 20px; }}
        h1 {{ color: #00ff88; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Live Matches List</h1>
        <p class="update-time">Last Updated: {now}</p>
        <div id="list">
    """
    
    if not matches:
        html_template += "<p>No matches found right now. Check back later!</p>"
    else:
        for m in matches:
            html_template += f"""
            <div class="match">
                <img src="{m['logo1']}" class="team-img" onerror="this.src='https://via.placeholder.com/50?text=T1'">
                <div class="match-info">{m['text']}</div>
                <img src="{m['logo2']}" class="team-img" onerror="this.src='https://via.placeholder.com/50?text=T2'">
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
