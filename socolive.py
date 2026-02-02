from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_socolive():
    # Setup Chrome Options for Headless Mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    url = "https://socolivezzxz.co/truc-tiep/"
    
    try:
        driver.get(url)
        print("Page loaded. Looking for 'Xem thêm trận đấu' button...")

        while True:
            try:
                # Wait for button to be clickable (timeout after 10 seconds)
                # Note: WordPress "Load More" usually uses a class like 'btn-loadmore' or contains text
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Xem thêm') or contains(text(), 'Load more')]"))
                )
                
                # Scroll to button and click
                driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
                time.sleep(1) # Brief pause for stability
                load_more_button.click()
                print("Clicked 'Load More'...")
                time.sleep(2) # Wait for AJAX content to load
                
            except Exception:
                print("No more 'Load More' buttons found or all matches loaded.")
                break

        # Extract all match links
        links = set()
        elements = driver.find_elements(By.TAG_NAME, "a")
        for el in elements:
            href = el.get_attribute("href")
            if href and "/truc-tiep/" in href and len(href.split('-')) > 2:
                # Exclude the main category page
                if href != "https://socolivezzxz.co/truc-tiep/":
                    links.add(href.rstrip('/'))

        # Save to file
        with open("socolive_links.txt", "w") as f:
            for link in sorted(links):
                f.write(link + "\n")
        
        print(f"Extraction complete. {len(links)} unique links found.")

    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_socolive()
