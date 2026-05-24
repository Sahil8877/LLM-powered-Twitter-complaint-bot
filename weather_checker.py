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

def get_chrome_major_version():
    try:
        result = subprocess.run(
            ["google-chrome", "--version"],
            capture_output=True, text=True
        )
        match = re.search(r'(\d+)\.', result.stdout)
        return int(match.group(1)) if match else None
    except Exception:
        return None


#********add a chrome profile********# 
# user_data_dir = os.path.join(os.getcwd(), "complaint_bot")
# chrome_options.add_argument(f"--user-data-dir={user_data_dir}")


URL = "https://weather.com/en-GB/weather/today"
uk_cities = ['London','Glasgow']

def get_weather_data(list_of_cities):

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--shm-size=2gb")            
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-GB")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    )
    driver = uc.Chrome(options=options, version_main=get_chrome_major_version())
    webdriver_wait = WebDriverWait(driver,10)
    driver.set_page_load_timeout(60)
    driver.get(URL)

    weather_today = {}
    # time.sleep(2)
    try:
        iframe_cookie_banner = webdriver_wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='SP Consent Message']")))
        accept_cookie_btn = webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button[title='Accept all']")))
        accept_cookie_btn.click()
    except Exception as e:
        print('Cookie banner not found or some error occured.\n',e)
    finally:
        driver.switch_to.default_content()
        time.sleep(2)

    webdriver_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"input")))
    try: 
        for cities in list_of_cities:
            
            search_box = driver.find_element(By.CSS_SELECTOR,"input")
            search_box.send_keys(cities)
            time.sleep(2)

            # webdriver_wait.until(EC.visibility_of_element_located(((By.CSS_SELECTOR,"#headerSearch_LocationSearch_listbox"))))
            search_button = driver.find_element(By.CSS_SELECTOR,"button[data-testid^='ctaButton']")
            search_button.click()
            time.sleep(2)

            # webdriver_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#todayDetails")))
            weather_data_section = driver.find_element(By.CSS_SELECTOR,"section[data-testid^='TodaysDetailsModule']")
            temperature = weather_data_section.find_element(By.CSS_SELECTOR,"span[data-testid^='TemperatureValue']")
            humidity = weather_data_section.find_element(By.CSS_SELECTOR,"span[data-testid^='PercentageValue']")
            weather_today[cities] = {'temp' : int(temperature.text.replace('°','')),'humi' : int(humidity.text.replace('%',''))}

    except Exception as e:
        print('Error',e)
        
    finally:
        driver.quit()
      
    return weather_today

def weather_complainer(weather_data):
    weather_complaints = []
    for city,data in weather_data.items():
        if data['temp'] > 30:
            weather_complaints.append(f"{city}'s {data['temp']} degree temperature")
        elif data['humi'] > 70:
            weather_complaints.append(f"{city}'s {data['humi']}% humidity")
    return weather_complaints

