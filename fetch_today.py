import requests
from bs4 import BeautifulSoup
import datetime

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        matches = []
        
        for item in soup.find_all('li'):
            if not item.find('div', class_='vs'): continue
            
            link_tag = item.find('a', href=True)
            if not link_tag: continue
            
            # Correctly format the play-url
            raw_path = link_tag['href'].rstrip('/')
            if raw_path.endswith('/play'):
                api_url = f"https://www.popozhibo.tv{raw_path}-url"
            else:
                api_url = f"https://www.popozhibo.tv{raw_path}/play-url"

            t1 = item.find('div', class_='left-team-name').text.strip() if item.find('div', class_='left-team-name') else "T1"
            t2 = item.find('div', class_='right-team-name').text.strip() if item.find('div', class_='right-team-name') else "T2"
            
            def fix_img(cls):
                img = item.find('img', class_=cls)
                if not img: return ""
                src = img.get('src', '')
                return f"https://www.popozhibo.tv{src}" if src.startswith('/') else src

            matches.append({
                "league": item.find('div', class_='game-name').text.strip() if item.find('div', class_='game-name') else "Match",
                "time": item.find('div', class_='game-time').text.strip() if item.find('div', class_='game-time') else "--:--",
                "team1": t1, "team2": t2,
                "logo1": fix_img('left-team-logo'),
                "logo2": fix_img('right-team-logo'),
                "api": api_url
            })
        return matches
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_start = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="no-referrer">
    <title>Stream Center</title>
    <style>
        body {{ font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 10px; }}
        .list {{ max-width: 500px; margin: auto; }}
        .card {{ background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px; margin-bottom: 10px; }}
        .teams {{ display: flex; align-items: center; justify-content: space-between; margin: 10px 0; }}
        .team img {{ width: 35px; height: 35px; object-fit: contain; }}
        .vs {{ color: #ff4444; font-weight: bold; }}
        .play-btn {{ 
            background: #00ff88; color: #000; padding: 10px; border-radius: 6px; 
            cursor: pointer; font-weight: bold; width: 100%; border: none;
        }}
        .play-btn:disabled {{ background: #555; cursor: not-allowed; }}
    </style>
</head>
<body>
    <h2>Live Match Center</h2>
    <p style="color: #555; font-size: 11px;">Synced: {now}</p>
    <div class="list">"""

    cards = ""
    for m in matches:
        cards += f"""
        <div class="card">
            <div style="font-size: 11px; color: #00ff88;">{m['league']} | {m['time']}</div>
            <div class="teams">
                <div class="team"><img src="{m['logo1']}"><br><span>{m['team1']}</span></div>
                <div class="vs">VS</div>
                <div class="team"><img src="{m['logo2']}"><br><span>{m['team2']}</span></div>
            </div>
            <button class="play-btn" onclick="decodeAndPlay(this, '{m['api']}')">PLAY STREAM</button>
        </div>"""

    html_end = """
    </div>
    <script>
        async function decodeAndPlay(btn, apiUrl) {
            btn.disabled = true;
            btn.innerText = "Bypassing Security...";
            
            // Using a CORS proxy to bypass the browser block
            const proxy = "https://api.allorigins.win/get?url=";
            
            try {
                const res = await fetch(proxy + encodeURIComponent(apiUrl));
                const data = await res.json();
                
                // AllOrigins returns the result inside a 'contents' string
                const jsonPayload = JSON.parse(data.contents);
                const encodedData = jsonPayload.data;
                
                // Remove the 2-character suffix (e.g., 'Gg', 'zy')
                let b64 = encodedData.slice(0, -2);
                
                // Standard Base64 Decode
                let decoded = JSON.parse(atob(b64));
                let streamUrl = decoded.links[0].url;
                
                window.location.href = streamUrl;
            } catch (err) {
                console.error(err);
                alert("Decryption failed. Try again in a few seconds.");
            } finally {
                btn.disabled = false;
                btn.innerText = "PLAY STREAM";
            }
        }
    </script>
</body>
</html>"""
    
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_start + cards + html_end)

if __name__ == "__main__":
    generate_html(get_matches())
