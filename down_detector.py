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


companies_to_check = [{'Apex Legends' : 'https://downdetector.co.uk/status/apex-legends/'},
                      {'Virgin Media' : 'https://downdetector.co.uk/status/virgin-media/'}]

def get_downdetector_data(list_of_companies):
    down_today = {}

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
    driver.set_page_load_timeout(60)
    webdriver_wait = WebDriverWait(driver,10)

    try:
        for org_data in list_of_companies:
            
            for org_name in org_data:
                driver.get(org_data.get(org_name))
                webdriver_wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"#company-status")))

                time.sleep(2)
                try:
                    cookie_button = driver.find_element(By.CSS_SELECTOR,"button[id^='onetrust-accept-btn-handler']")
                    cookie_button.click()
                except:
                    pass

                time.sleep(2)
                banner_element = driver.find_element(By.CSS_SELECTOR,"#company-status")
                banner_element_attr_color = banner_element.get_attribute('class')

                if 'border-[var(--color-dd-red)]' in banner_element_attr_color:
                    data_card_element = driver.find_element(By.CSS_SELECTOR,"div[aria-label='Most reported problems breakdown']")
                    reported_problems = data_card_element.find_elements(By.CSS_SELECTOR,"div[role='listitem']")
                    reported_data_dict = {}
                    
                    for reports in reported_problems:
                        reported_data = reports.find_element(By.CSS_SELECTOR,".relative").text
                        reported_text = reports.find_element(By.CSS_SELECTOR,"div.text-center").text
                        reported_data_dict[reported_text] = reported_data

                    down_today[org_name] = {'report': reported_data_dict, 'desc' : banner_element.text}

                else:
                    print(org_name, "has no major outage reported. ")
        driver.quit()
    except Exception as e:
        print('Error',e)
    finally:
        driver.quit()

    return down_today

def downdetector_complainer(downdetector_data):
    downdetector_complaints = []
    for org,data in downdetector_data.items():
        reports = ",".join([" " + report + " " + data['report'].get(report) for report in data['report']])
        downdetector_complaints.append(f"{org} is down today, outage report by impact is as follows:{reports}.")
    print(downdetector_complaints)
    return downdetector_complaints

