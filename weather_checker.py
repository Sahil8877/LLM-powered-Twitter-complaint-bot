import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

URL = "https://weather.com/en-GB/weather/today"
cities = [
    # 🇬🇧 UK
    'London', 'Glasgow', 'Manchester', 'Birmingham', 'Edinburgh',
    'Liverpool', 'Leeds', 'Bristol', 'Sheffield', 'Newcastle',

    # 🇺🇸 USA
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami',
    'San Francisco', 'Seattle', 'Boston', 'Dallas', 'Atlanta',

    # 🇪🇺 Europe
    'Paris', 'Berlin', 'Madrid', 'Rome', 'Amsterdam',
    'Barcelona', 'Vienna', 'Stockholm', 'Oslo', 'Zurich',

    # 🇮🇳 India
    'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',

    # 🇦🇺 Australia
    'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide',

    # 🇨🇦 Canada
    'Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa',

    # 🌏 Asia
    'Tokyo', 'Seoul', 'Shanghai', 'Singapore', 'Hong Kong',
    'Bangkok', 'Kuala Lumpur', 'Jakarta', 'Dubai', 'Riyadh',

    # 🌍 Africa & Middle East
    'Cairo', 'Lagos', 'Nairobi', 'Johannesburg', 'Casablanca',
]

CITY_THRESHOLDS = {
    # 🇬🇧 UK
    'London': {'max_temp': 27, 'max_humi': 75},
    'Glasgow': {'max_temp': 25, 'max_humi': 75},
    'Manchester': {'max_temp': 26, 'max_humi': 75},
    'Birmingham': {'max_temp': 26, 'max_humi': 75},
    'Edinburgh': {'max_temp': 24, 'max_humi': 75},
    'Liverpool': {'max_temp': 25, 'max_humi': 75},
    'Leeds': {'max_temp': 26, 'max_humi': 75},
    'Bristol': {'max_temp': 26, 'max_humi': 75},
    'Sheffield': {'max_temp': 26, 'max_humi': 75},
    'Newcastle': {'max_temp': 24, 'max_humi': 75},

    # 🇺🇸 USA
    'New York': {'max_temp': 34, 'max_humi': 75},
    'Los Angeles': {'max_temp': 33, 'max_humi': 75},
    'Chicago': {'max_temp': 32, 'max_humi': 75},
    'Houston': {'max_temp': 36, 'max_humi': 82},
    'Miami': {'max_temp': 34, 'max_humi': 85},
    'San Francisco': {'max_temp': 28, 'max_humi': 80},
    'Seattle': {'max_temp': 29, 'max_humi': 75},
    'Boston': {'max_temp': 31, 'max_humi': 75},
    'Dallas': {'max_temp': 38, 'max_humi': 75},
    'Atlanta': {'max_temp': 34, 'max_humi': 75},

    # 🇪🇺 Europe
    'Paris': {'max_temp': 29, 'max_humi': 75},
    'Berlin': {'max_temp': 30, 'max_humi': 70},
    'Madrid': {'max_temp': 36, 'max_humi': 60},
    'Rome': {'max_temp': 34, 'max_humi': 70},
    'Amsterdam': {'max_temp': 26, 'max_humi': 75},
    'Barcelona': {'max_temp': 31, 'max_humi': 75},
    'Vienna': {'max_temp': 30, 'max_humi': 70},
    'Stockholm': {'max_temp': 25, 'max_humi': 75},
    'Oslo': {'max_temp': 25, 'max_humi': 75},
    'Zurich': {'max_temp': 28, 'max_humi': 75},

    # 🇮🇳 India
    'Mumbai': {'max_temp': 35, 'max_humi': 85},
    'Delhi': {'max_temp': 41, 'max_humi': 80},
    'Bangalore': {'max_temp': 34, 'max_humi': 75},
    'Chennai': {'max_temp': 38, 'max_humi': 80},
    'Kolkata': {'max_temp': 37, 'max_humi': 85},

    # 🇦🇺 Australia
    'Sydney': {'max_temp': 30, 'max_humi': 75},
    'Melbourne': {'max_temp': 31, 'max_humi': 70},
    'Brisbane': {'max_temp': 32, 'max_humi': 80},
    'Perth': {'max_temp': 36, 'max_humi': 65},
    'Adelaide': {'max_temp': 34, 'max_humi': 65},

    # 🇨🇦 Canada
    'Toronto': {'max_temp': 29, 'max_humi': 75},
    'Vancouver': {'max_temp': 26, 'max_humi': 75},
    'Montreal': {'max_temp': 28, 'max_humi': 75},
    'Calgary': {'max_temp': 27, 'max_humi': 65},
    'Ottawa': {'max_temp': 28, 'max_humi': 75},

    # 🌏 Asia
    'Tokyo': {'max_temp': 32, 'max_humi': 80},
    'Seoul': {'max_temp': 31, 'max_humi': 80},
    'Shanghai': {'max_temp': 33, 'max_humi': 80},
    'Singapore': {'max_temp': 33, 'max_humi': 85},
    'Hong Kong': {'max_temp': 32, 'max_humi': 85},
    'Bangkok': {'max_temp': 36, 'max_humi': 85},
    'Kuala Lumpur': {'max_temp': 34, 'max_humi': 85},
    'Jakarta': {'max_temp': 34, 'max_humi': 85},
    'Dubai': {'max_temp': 42, 'max_humi': 65},
    'Riyadh': {'max_temp': 44, 'max_humi': 40},

    # 🌍 Africa & Middle East
    'Cairo': {'max_temp': 38, 'max_humi': 65},
    'Lagos': {'max_temp': 34, 'max_humi': 85},
    'Nairobi': {'max_temp': 28, 'max_humi': 75},
    'Johannesburg': {'max_temp': 28, 'max_humi': 60},
    'Casablanca': {'max_temp': 30, 'max_humi': 75},

    'DEFAULT': {'max_temp': 32, 'max_humi': 75}
}

def create_driver():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    
    # --- HEADLESS CONFIGURATION APPLIED HERE ---
    # options.add_argument("--headless=new")                     # Run silently in the background
    options.add_argument("--disable-gpu")                      # Prevents headless rendering engine crashes
    options.add_argument("--no-sandbox")                       # Ensures execution stability in isolated spaces
    options.add_argument("--disable-dev-shm-usage")            # Bypasses shared memory resource limitations
    options.add_argument("--disable-setuid-sandbox")                  
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-GB")
    
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(90)
    return driver

def get_weather_data(list_of_cities, retry=True):
    driver = None
    weather_today = {}

    try:
        driver = create_driver()
        wait = WebDriverWait(driver, 15)
        driver.get(URL)
        time.sleep(3)

        # Accept cookies (same as before)
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title='SP Consent Message']")
            ))
            accept_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[title='Accept all']")
            ))
            driver.execute_script("arguments[0].click();", accept_btn)
        except Exception as e:
            print(f"Cookie banner skipped: {e}")
        finally:
            try:
                driver.switch_to.default_content()
            except:
                pass
            time.sleep(2)

        # Wait for the initial search box to be ready (only once)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input")))

        for city in list_of_cities:
            # --- Re‑wait for the search box to be ready each time ---
            search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input")))
            search_box.clear()
            search_box.send_keys(city)
            time.sleep(2)   # reduced from 5 seconds

            # Wait for the search button to be clickable
            search_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid^='ctaButton']")))
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(2)

            # Wait for the weather section to appear
            section = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "section[data-testid^='TodaysDetailsModule']")
            ))
            temp = section.find_element(By.CSS_SELECTOR, "span[data-testid^='TemperatureValue']")
            hum = section.find_element(By.CSS_SELECTOR, "span[data-testid^='PercentageValue']")
            weather_today[city] = {
                'temp': int(temp.text.replace('°', '')),
                'humi': int(hum.text.replace('%', ''))
            }
            print(f"{city}: {weather_today[city]}")

    except Exception as e:
        print(f"Weather error: {e}")
        if retry:
            print("Retrying with fresh driver...")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            return get_weather_data(list_of_cities, retry=False)

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    return weather_today

def weather_complainer(weather_data):
    weather_complaints = []
    for city, data in weather_data.items():
        limits = CITY_THRESHOLDS.get(city, CITY_THRESHOLDS['DEFAULT'])
        if data['temp'] > limits['max_temp']:
            weather_complaints.append(f"{city}'s {data['temp']} degree temperature")
        elif data['humi'] > limits['max_humi']:
            weather_complaints.append(f"{city}'s {data['humi']}% humidity")
    return weather_complaints
