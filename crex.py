import requests
from bs4 import BeautifulSoup
import json

def fetch_crex_schedule():
    url = "https://crex.com/schedule"
    # Headers are necessary to avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Check if the request was successful
        
        soup = BeautifulSoup(response.text, 'html.parser')
        match_list = []

        # CREX usually wraps matches in 'schedule-card' or similar containers
        # Note: You may need to update these class names if the website updates its layout
        schedule_cards = soup.find_all('div', class_='schedule-card')

        for card in schedule_cards:
            # Extracting match details based on your requirements
            try:
                teams = card.find('div', class_='team-info').text.strip()
                time = card.find('div', class_='match-time').text.strip()
                series = card.find('div', class_='series-name').text.strip()
                
                match_list.append({
                    "match_name": teams,
                    "time": time,
                    "series_info": series
                })
            except AttributeError:
                continue # Skip cards that don't match the expected format

        # Save the data to a JSON file for your website to use
        with open('matches.json', 'w') as f:
            json.dump(match_list, f, indent=4)
            
        print(f"Successfully fetched {len(match_list)} matches.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_crex_schedule()
