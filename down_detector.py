import os
import platform
import re
import subprocess
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc


def get_chrome_major_version():
    system = platform.system()
    version = None
    
    try:
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
        elif system == "Darwin":  # macOS
            cmd = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            match = re.search(r'(\d+)\.', result.stdout)
            if match:
                version = match.group(1)
        else:  # Linux
            cmd = ["google-chrome", "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            match = re.search(r'(\d+)\.', result.stdout)
            if match:
                version = match.group(1)
                
        if version:
            return int(version.split('.')[0])
    except Exception:
        pass
    
    return 148


companies_to_check = [
    # Global
    {'Google'        : 'https://downdetector.com/status/google/'},
    {'YouTube'       : 'https://downdetector.com/status/youtube/'},
    {'Facebook'      : 'https://downdetector.com/status/facebook/'},
    {'Instagram'     : 'https://downdetector.com/status/instagram/'},
    {'WhatsApp'      : 'https://downdetector.com/status/whatsapp/'},
    {'Amazon'        : 'https://downdetector.com/status/amazon/'},
    {'Netflix'       : 'https://downdetector.com/status/netflix/'},
    {'Spotify'       : 'https://downdetector.com/status/spotify/'},
    # Gaming
    {'Steam'         : 'https://downdetector.com/status/steam/'},
    {'Apex Legends'  : 'https://downdetector.com/status/apex-legends/'},
    # UK
    {'Virgin Media'  : 'https://downdetector.co.uk/status/virgin-media/'},
    {'BT'            : 'https://downdetector.co.uk/status/bt-british-telecom/'},
    {'Sky'           : 'https://downdetector.co.uk/status/sky/'},
    {'Vodafone UK'   : 'https://downdetector.co.uk/status/vodafone/'},
    {'Barclays'      : 'https://downdetector.co.uk/status/barclays/'},
    {'Monzo'         : 'https://downdetector.co.uk/status/monzo/'},
    {'BBC iPlayer'   : 'https://downdetector.co.uk/status/iplayer/'},
    {'Deliveroo'     : 'https://downdetector.co.uk/status/deliveroo/'},
    # US
    {'AT&T'          : 'https://downdetector.com/status/att/'},
    {'Verizon'       : 'https://downdetector.com/status/verizon/'},
]


def get_downdetector_data(list_of_companies):
    down_today = {}
    driver = None
    try:
        options = uc.ChromeOptions()
        options.page_load_strategy = 'eager'
        
        # --- HEADLESS CONFIGURATION APPLIED HERE ---
        # options.add_argument("--headless=new")                     # Run silently in background
        options.add_argument("--disable-gpu")                      # Prevents headless engine crashes
        options.add_argument("--no-sandbox")                       # Required for execution context safety
        options.add_argument("--disable-dev-shm-usage")            # Avoids shared memory crash limitations
        options.add_argument("--disable-setuid-sandbox")                
        options.add_argument("--window-size=1920,1080")
        
        # # Use a localized, dedicated profile folder if anti bot detection kicks inn
        # user_data_dir = os.path.join(os.getcwd(), "complaint_bot")
        # options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Get your installed Chrome version dynamically
        chrome_version = get_chrome_major_version()
        print(f"Syncing driver with local Chrome major version: {chrome_version}")

        # CLOUDFLARE BYPASS: Add user-agent matching the detected major version
        options.add_argument(f"--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36")

        # Explicitly passing version_main matches the driver binary to your browser
        driver = uc.Chrome(options=options, version_main=chrome_version)
        driver.set_page_load_timeout(90)
        wait = WebDriverWait(driver, 15)
        
        for org_data in list_of_companies:
            for org_name, url in org_data.items():
                
                driver.get(url)
                
                # Wait for the status element to be present
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#company-status")))
                time.sleep(2)
                
                # Accept cookies if the banner appears
                try:
                    cookie_button = driver.find_element(By.CSS_SELECTOR, "button[id^='onetrust-accept-btn-handler']")
                    cookie_button.click()
                    time.sleep(1)
                except:
                    pass
                
                banner_element = driver.find_element(By.CSS_SELECTOR, "#company-status")
                banner_attr_color = banner_element.get_attribute('class')
                
                # Check for outage indicators
                if 'border-[var(--color-dd-red)]' in banner_attr_color:
                    data_card = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Most reported problems breakdown']")
                    reported_items = data_card.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
                    reports_dict = {}
                    for item in reported_items:
                        percent = item.find_element(By.CSS_SELECTOR, ".relative").text
                        label = item.find_element(By.CSS_SELECTOR, "div.text-center").text
                        reports_dict[label] = percent
                    down_today[org_name] = {'report': reports_dict, 'desc': banner_element.text}
                else:
                    print(f"{org_name} has no major outage reported.")
                    
    except Exception as e:
        print(f"Error in get_downdetector_data: {e}")
        if driver:
            driver.save_screenshot("downdetector_error.png")
            with open("error_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
    finally:
        if driver:
            driver.quit()
    return down_today


def downdetector_complainer(downdetector_data):
    downdetector_complaints = []
    for org, data in downdetector_data.items():
        reports = ",".join([" " + report + " " + data['report'].get(report) for report in data['report']])
        downdetector_complaints.append(f"{org} is down today, outage report by impact is as follows:{reports}.")
    print(downdetector_complaints)
    return downdetector_complaints

