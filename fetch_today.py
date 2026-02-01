import requests
from bs4 import BeautifulSoup
import datetime
import base64
import json

def get_real_stream_url(api_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.popozhibo.tv/",
        "X-Requested-With": "XMLHttpRequest"
    }
    try:
        res = requests.get(api_url, headers=headers, timeout=10)
        # Debugging output for your GitHub Action Logs
        print(f"Status for {api_url}: {res.status_code}")
        
        data_json = res.json()
        encoded_data = data_json.get('data', '')
        if not encoded_data:
            return None
        
        clean_b64 = encoded_data.replace("zh", "")
        clean_b64 += "=" * ((4 - len(clean_b64) % 4) % 4)
        decoded_bytes = base64.b64decode(clean_b64)
        decoded_json = json.loads(decoded_bytes)
        
        return decoded_json['links'][0]['url']
    except Exception as e:
        print(f"Decode error: {e}")
        return None

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
        items = soup.find_all('li')

        for item in items:
            vs_div = item.find('div', class_='vs')
            if not vs_div: continue

            # 1. Team Info
            t1_name = item.find('div', class_='left-team-name')
            t2_name = item.find('div', class_='right-team-name')
            if not t1_name or not t2_name: continue

            # 2. Link Logic
            link_tag = item.find('a', href=True)
            final_link = "#"
            
            if link_tag:
                original_path = link_tag['href'].rstrip('/')
                # Create the API URL
                api_url = f"https://www.popozhibo.tv{original_path}-url"
                
                # Attempt to get direct link
                decoded_url = get_real_stream_url(api_url)
                
                if decoded_url:
                    final_link = decoded_url
                else:
                    # FALLBACK: If decoding fails, just use the original site link
                    final_link = f"https://www.popozhibo.tv{original_path}"

            # 3. Logos
            def fix_img(cls):
                tag = item.find('img', class_=cls)
                if not tag or not tag.get('src'): return ""
                src = tag.get('src')
                return f"https://www.popozhibo.tv{src}" if src.startswith('/') else src

            matches.append({
                "time": item.find('div', class_='game-time').text if item.find('div', class_='game-time') else "",
                "league": item.find('div', class_='game-name').text if item.find('div', class_='game-name') else "",
                "team1": t1_name.text.strip(),
                "team2": t2_name.text.strip(),
                "logo1": fix_img('left-team-logo'),
                "logo2": fix_img('right-team-logo'),
                "link": final_link
            })
        
        return matches
    except Exception as e:
        print(f"Main Error: {e}")
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
        body {{ font-family: sans-serif; background: #080808; color: #eee; margin: 0; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        .row {{ background: #121212; border: 1px solid #222; border-radius: 10px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; text-decoration: none; color: inherit; }}
        .time-box {{ width: 75px; border-right: 1px solid #333; margin-right: 10px; font-size: 11px; }}
        .league {{ color: #00ff88; font-weight: bold; display: block; }}
        .game {{ flex: 1; display: flex; justify-content: space-around; align-items: center; text-align: center; }}
        .team img {{ width: 30px; height: 30px; object-fit: contain; }}
        .name {{ font-size: 12px; display: block; margin-top: 3px; }}
        .vs {{ color: #ff4444; font-weight: bold; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#00ff88;">Match Center</h2>
        <p style="text-align:center; font-size:10px; color:#555;">Update: {now}</p>
        <div id="list">
    """
    if not matches:
        html_template += "<p style='text-align:center;'>Fetching matches... check back in 1 minute.</p>"
    else:
        for m in matches:
            html_template += f"""
            <a href="{m['link']}" class="row" target="_blank">
                <div class="time-box">
                    <span class="league">{m['league']}</span>
                    <span>{m['time']}</span>
                </div>
                <div class="game">
                    <div class="team"><img src="{m['logo1']}"> <span class="name">{m['team1']}</span></div>
                    <div class="vs">VS</div>
                    <div class="team"><img src="{m['logo2']}"> <span class="name">{m['team2']}</span></div>
                </div>
            </a>"""
    
    html_template += "</div></div></body></html>"
    with open("today.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    generate_html(get_matches())
