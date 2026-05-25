import os,sys
import platform
import re
import smtplib
import subprocess
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_EMAIL_PASS")
# RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
RECEIVER_EMAIL = "testeremail8877@gmail.com"
PROFILE_DIR = "complaint_bot_chrome_profile"
NEED_REFRESH_FLAG = ".need_refresh"


def get_chrome_version():
    """Returns the major version of installed Chrome."""
    try:
        if platform.system() == "Darwin":
            cmd = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]
        else:
            cmd = ["google-chrome", "--version"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        match = re.search(r'(\d+)\.', result.stdout)
        if match:
            return int(match.group(1))
    except:
        pass
    return 134   # fallback


def send_alert(subject, body):
    with smtplib.SMTP(host='smtp.gmail.com') as conn:
        conn.starttls()
        conn.login(user=SENDER_EMAIL, password=SENDER_PASSWORD)
        message = f"Subject: {subject}\n\n{body}"
        conn.sendmail(from_addr=SENDER_EMAIL, to_addrs=RECEIVER_EMAIL, msg=message.encode("utf-8"))


def build_chrome_profile():
    profile_path = os.path.join(os.getcwd(), PROFILE_DIR)
    os.makedirs(profile_path, exist_ok=True)
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-GB")
    driver = uc.Chrome(options=options, version_main=get_chrome_version())
    driver.get("https://x.com")
    input("Log in manually, then press Enter here to save the profile and continue...")
    driver.quit()
    print("Profile saved.")


def profile_valid():
    profile_path = os.path.join(os.getcwd(), PROFILE_DIR)
    
    # Check if the folder physically exists on disk first
    if not os.path.exists(profile_path):
        if not sys.stdin.isatty(): 
            print("Flag file exists, but running via Cron. Skipping window build to prevent hanging.")
            return
        print("Chrome Profile directory missing.")
        return "MISSING"

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-GB")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # --- Headless arguments added here ---
    # options.add_argument("--headless=new")                     # Run silently in background
    options.add_argument("--disable-gpu")                      # Stability for headless
    options.add_argument("--no-sandbox")                       # Avoid permission bugs
    options.add_argument("--disable-dev-shm-usage")            # Overcomes limited resource issues
    options.add_argument("--disable-setuid-sandbox")           
    options.add_argument("--remote-debugging-port=9222")       
    
    chrome_ver = get_chrome_version()   
    options.add_argument(f"--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36")
    driver = None

    try:
        driver = uc.Chrome(options=options, version_main=chrome_ver)
        driver.set_page_load_timeout(30)
        driver.get("https://x.com/home")
        time.sleep(3)

        if "login" in driver.current_url or driver.current_url == "https://x.com/":
            print("⚠️ Not logged in. Headless cannot log in automatically.")
            return "EXPIRED"
        else:
            print("Chrome Profile is valid.")
            return "VALID"
    except Exception as e:
        print(f"Error checking profile: {e}")
        return "EXPIRED"
    finally:
        if driver:
            driver.quit()


def post_tweets(complaints):
    flag_path = os.path.join(os.getcwd(), NEED_REFRESH_FLAG)
    profile_path = os.path.join(os.getcwd(), PROFILE_DIR)

    if os.path.exists(flag_path):
        build_chrome_profile()
        # FLAG DELETION REMOVED – let the caller (main.py) delete the flag
        print("Profile refreshed. The flag will be deleted by the main script.")
        return "REFRESHED"
        
    status = profile_valid()
    
    # Alert 1: Directory missing entirely
    if status == "MISSING":
        with open(flag_path, "w") as f:
            f.write("1")
        send_alert(
            subject="X Bot Alert: Profile Does Not Exist",
            body=f"The Chrome profile directory '{PROFILE_DIR}' was not found. Please deploy or build the profile."
        )
        print("Alert sent: Profile folder does not exist. Exiting.")
        return

    # Alert 2: Profile directory exists but login cookies expired
    if status == "EXPIRED":
        print("The Chrome Profile is invalid or expired.")
        with open(flag_path, "w") as f:
            f.write("1")
        send_alert(
            subject="X Bot Profile Expired",
            body="The Chrome profile for the X bot is invalid. Please run the script again, it will open a browser for you to log in manually."
        )
        print("Alert sent. Exiting. Run the script again to refresh the profile.")
        return

    # Proceed with posting if profile status is "VALID"
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-GB")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # options.add_argument("--headless=new")                     
    options.add_argument("--disable-gpu")                      
    options.add_argument("--no-sandbox")                       
    options.add_argument("--disable-dev-shm-usage")            
    options.add_argument("--disable-setuid-sandbox")           
    options.add_argument("--remote-debugging-port=9222")       
    
    chrome_ver = get_chrome_version()   
    options.add_argument(f"--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=options, version_main=chrome_ver)
    driver.set_page_load_timeout(60)
    wait = WebDriverWait(driver, 20)
    driver.get("https://x.com/home")
    time.sleep(3)
    try:
        for complaint in complaints:
            time.sleep(2)
            textbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".public-DraftStyleDefault-block")))
            textbox.click()
            textbox.send_keys(complaint.strip('"'))
            time.sleep(2)
            tweet_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='tweetButtonInline']")))
            driver.execute_script("arguments[0].click();", tweet_btn)
            print(f"\nPosted: {complaint}...")
            time.sleep(3)

        return True
    except Exception as e:
        print(f"Failed to post tweets: {e}")
        return False
    finally:
        driver.quit()

# post_tweets(['hi'])