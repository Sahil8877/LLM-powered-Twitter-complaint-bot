from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chromium import options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import subprocess
import re
import os

def get_chrome_major_version():
    commands = [
        ["google-chrome", "--version"],                          # Linux
        ["google-chrome-stable", "--version"],                   # Linux alt
        ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],  # Mac
    ]
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            match = re.search(r'(\d+)\.', result.stdout)
            if match:
                return int(match.group(1))
        except Exception:
            continue
    return None

URL = 'https://x.com/'

def post_tweets(complaints):
    try:
        options = uc.ChromeOptions()

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--shm-size=2gb")            
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--lang=en-GB")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(options=options,version_main=get_chrome_major_version())
        driver.set_page_load_timeout(60)

        webdriver_wait = WebDriverWait(driver,10)
        driver.get(URL)

        username_input_element = webdriver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[name='username_or_email']")))
        username_input_element.send_keys(os.getenv('X_PASS_EMAIL')) # .env variable

        continue_button = driver.find_element(By.CSS_SELECTOR,"button[type='submit']")
        continue_button.click()

        password_input_element = webdriver_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"input[type='password']")))
        password_input_element.send_keys(os.getenv("X_PASS")) # .env variable

        continue_button = webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button[type='submit']")))
        continue_button.click()

        for complaint in complaints:
            time.sleep(2)
            textbox_element = webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".public-DraftStyleDefault-block")))
            textbox_element.send_keys(complaint)
            time.sleep(2)
            tweet_button = webdriver_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='tweetButtonInline']")))
            driver.execute_script("arguments[0].click();", tweet_button)
    except Exception as e:
        print("Error occured\n",e)
    finally:
        driver.quit()

