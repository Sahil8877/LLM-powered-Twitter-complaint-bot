from complain_writer import response
from weather_checker import weather_complainer, get_weather_data, uk_cities
from down_detector import downdetector_complainer, get_downdetector_data, companies_to_check
from twitter import post_tweets

down_detector_data = get_downdetector_data(companies_to_check)
down_detector_complaints_list = downdetector_complainer(down_detector_data)

weather_data = get_weather_data(uk_cities)
weather_complaints_list = weather_complainer(weather_data)

down_detector_tweets = response(down_detector_complaints_list, "website down")
post_tweets(down_detector_tweets)

weather_tweets = response(weather_complaints_list, "weather")
post_tweets(weather_tweets)      

print(down_detector_tweets, "\n")
print(weather_tweets)