from complain_writer import response
from weather_checker import weather_complainer, get_weather_data, cities
from down_detector import downdetector_complainer, get_downdetector_data, companies_to_check
from twitter import post_tweets, NEED_REFRESH_FLAG, profile_valid, send_alert
import os

def run():
    flag_path = os.path.join(os.getcwd(), NEED_REFRESH_FLAG)
    
    # ----- FIRST: handle refresh flag -----
    if os.path.exists(flag_path):
        print("🔄 Refresh flag found. Running interactive profile refresh...")
        post_tweets([])          # This will open browser and save profile (but NOT delete flag)
        # Now delete the flag (only once)
        try:
            os.remove(flag_path)
            print("✅ Profile refreshed. Flag removed. Please run the script again to post tweets.")
        except FileNotFoundError:
            print("⚠️ Flag file already removed (possibly by another process).")
        return
    
    # ----- NO flag – now check profile validity -----
    status = profile_valid()
    
    if status == "MISSING":
        print("❌ Profile missing. Sending alert and creating flag.")
        send_alert(
            subject="X Bot Alert: Profile Does Not Exist",
            body="The Chrome profile directory was not found. Please run the script again – it will open a browser for you to log in and create the profile."
        )
        with open(flag_path, "w") as f:
            f.write("1")
        return
    
    if status == "EXPIRED":
        print("❌ Profile expired. Sending alert and creating flag.")
        send_alert(
            subject="X Bot Alert: Profile Expired",
            body="The Chrome profile for the X bot has expired. Please run the script again – it will open a browser for you to log in manually and refresh the session."
        )
        with open(flag_path, "w") as f:
            f.write("1")
        return
    
    # ----- Profile valid – proceed with data collection and posting -----
    print("✅ Profile valid. Proceeding with data collection and posting.")
    
    down_detector_data = get_downdetector_data(companies_to_check)
    down_detector_complaints_list = downdetector_complainer(down_detector_data)

    weather_data = get_weather_data(cities)
    weather_complaints_list = weather_complainer(weather_data)

    all_complaints = []
    if down_detector_complaints_list:
        down_detector_tweets = response(down_detector_complaints_list, "website down")
        all_complaints.extend(down_detector_tweets)
    else:
        print("No outages detected.")
    
    if weather_complaints_list:
        weather_tweets = response(weather_complaints_list, "weather")
        all_complaints.extend(weather_tweets)
    else:
        print("No notable weather conditions.")
    
    if all_complaints:
        print(f"📝 Total complaints to post: {len(all_complaints)}")
        post_tweets(all_complaints)
    else:
        print("Nothing to post. Exiting.")

run()