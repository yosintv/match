import requests
from bs4 import BeautifulSoup
import datetime

def get_matches():
    url = "https://www.popozhibo.tv/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        matches = []
        for item in soup.find_all('li'):
            if not item.find('div', class_='vs'): continue
            link_tag = item.find('a', href=True)
            if not link_tag: continue
            raw_path = link_tag['href'].rstrip('/')
            api_url = f"https://www.popozhibo.tv{raw_path}-url" if raw_path.endswith('/play') else f"https://www.popozhibo.tv{raw_path}/play-url"
            
            t1 = item.find('div', class_='left-team-name').text.strip() if item.find('div', class_='left-team-name') else "T1"
            t2 = item.find('div', class_='right-team-name').text.strip() if item.find('div', class_='right-team-name') else "T2"
            
            def fix_img(cls):
                img = item.find('img', class_=cls)
                return f"https://www.popozhibo.tv{img.get('src')}" if img and img.get('src','').startswith('/') else (img.get('src','') if img else "")

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
        print(f"Error: {e}"); return []

def generate_html(matches):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Decoder Hub</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #050505; color: #fff; margin: 0; padding: 10px; }}
        .container {{ max-width: 500px; margin: auto; }}
        .card {{ background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px; margin-bottom: 10px; }}
        .teams {{ display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }}
        .team {{ text-align: center; width: 40%; font-size: 13px; }}
        .team img {{ width: 35px; height: 35px; object-fit: contain; }}
        .vs {{ color: #ff4444; font-weight: bold; }}
        .play-btn {{ background: #00ff88; color: #000; padding: 10px; border-radius: 8px; width: 100%; border: none; font-weight: bold; cursor: pointer; }}
        
        /* Modal Styles */
        #modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 1000; overflow-y: auto; }}
        .modal-content {{ max-width: 450px; margin: 40px auto; background: #111; padding: 20px; border-radius: 15px; border: 1px solid #333; }}
        .close-btn {{ float: right; color: #ff4444; font-weight: bold; cursor: pointer; }}
        .link-card {{ background: #1a1a1a; padding: 10px; border-radius: 8px; margin-top: 10px; border: 1px solid #222; word-break: break-all; font-size: 11px; }}
        .copy-btn {{ background: #0044cc; color: #fff; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-top: 5px; }}
        #status {{ font-size: 12px; margin-bottom: 10px; padding: 5px; border-radius: 4px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#00ff88;">Live Match Center</h2>
        <p style="text-align:center; font-size:10px; color:#555;">Updated: {now}</p>
        <div id="list">
    """
    for m in matches:
        html_content += f"""
        <div class="card">
            <div style="font-size: 11px; color: #00ff88;">{m['league']} | {m['time']}</div>
            <div class="teams">
                <div class="team"><img src="{m['logo1']}"><br>{m['team1']}</div>
                <div class="vs">VS</div>
                <div class="team"><img src="{m['logo2']}"><br>{m['team2']}</div>
            </div>
            <button class="play-btn" onclick="startFetch('{m['api']}')">FETCH STREAM LINKS</button>
        </div>"""

    html_content += """
        </div>
    </div>

    <div id="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">CLOSE ✖</span>
            <h3 style="margin-top:0;">Stream Links</h3>
            <div id="status">Ready</div>
            <div id="links-output"></div>
        </div>
    </div>

    <script>
        const modal = document.getElementById('modal');
        const status = document.getElementById('status');
        const linksOutput = document.getElementById('links-output');

        function setStatus(msg, type) {
            status.innerText = msg;
            status.style.background = type === 'error' ? '#300' : '#030';
            status.style.color = type === 'error' ? '#f66' : '#6f6';
        }

        function transformUrl(url) {
            if (url.includes('play1nm.hnyongshun.cn')) {
                const match = url.match(/\/live\/([a-zA-Z0-9_-]+)\.m3u8/);
                if (match && match[1]) {
                    return `https://yosintv2.github.io/ads/foot.html?url=https://ytvlive.pages.dev/zhi?m=${match[1]}`;
                }
            }
            return url;
        }

        async function startFetch(apiUrl) {
            modal.style.display = 'block';
            linksOutput.innerHTML = '';
            setStatus('🔄 Fetching from Proxy...', 'info');
            
            const proxy = `https://api.allorigins.win/raw?url=${encodeURIComponent(apiUrl)}`;
            try {
                const res = await fetch(proxy);
                const data = await res.json();
                const raw = data.data;
                
                // YOUR DECODING LOGIC
                const cleaned = raw.substring(6, raw.length - 2);
                const obj = JSON.parse(atob(cleaned));
                
                let html = "";
                obj.links.forEach(item => {
                    let plainUrl = item.url || "";
                    if (plainUrl.includes('url=')) {
                        const urlMatch = plainUrl.match(/url=(.+)$/);
                        if (urlMatch) plainUrl = decodeURIComponent(urlMatch[1].replace(/\\+/g, ' '));
                    }
                    const finalUrl = transformUrl(plainUrl);
                    html += `
                        <div class="link-card">
                            <div>${finalUrl}</div>
                            <button class="copy-btn" onclick="copyText('${finalUrl.replace(/'/g, "\\\\'")}')">📋 Copy Link</button>
                            <button class="copy-btn" style="background:#222" onclick="window.open('${finalUrl}', '_blank')">🚀 Open</button>
                        </div>`;
                });
                linksOutput.innerHTML = html;
                setStatus('✅ Decoded Successfully', 'success');
            } catch (err) {
                setStatus('❌ Failed to fetch/decode', 'error');
            }
        }

        function closeModal() { modal.style.display = 'none'; }
        function copyText(text) {
            navigator.clipboard.writeText(text);
            alert('Copied!');
        }
    </script>
</body>
</html>"""
    with open("today.html", "w", encoding="utf-8") as f: f.write(html_content)

if __name__ == "__main__":
    generate_html(get_matches())
