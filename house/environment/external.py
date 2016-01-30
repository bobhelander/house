import urllib
import simplejson as json
import datetime
from house.environment.cache import WeatherCache


URL = "http://openweathermap.org/data/2.1/weather/station/%s?type=json&APPID="
URL2 = "http://api.openweathermap.org/data/2.5/weather?id=%s&type=json&APPID="
HISTORY_URL = "http://api.openweathermap.org/data/2.5/history/city?id=%s&cnt=10&APPID="

def convert_from_kelvin(temp_in_kelvin):
    return temp_in_kelvin - 273.15

def convert_to_fahrenheit(temp_in_celsius):
    return (temp_in_celsius*1.8)+32

WEATHER_DATA_CACHE = WeatherCache()
WEATHER_STATION_CACHE = WeatherCache()


def read_weather(station_number, api_key):
    """
    Retrieve openweathermap 2.5 weather data
    """
    if WEATHER_DATA_CACHE.get() is None:
        url = (URL2 + api_key) % station_number
        weather_data = urllib.urlopen(url).read()
        WEATHER_DATA_CACHE.set(json.loads(weather_data))
    
    if datetime.datetime.fromtimestamp(WEATHER_DATA_CACHE.get()["dt"]) < datetime.datetime.now() - datetime.timedelta(minutes=15):
        url = (URL2 + api_key) % station_number
        weather_data = urllib.urlopen(url).read()
        WEATHER_DATA_CACHE.set(json.loads(weather_data))
    
    return WEATHER_DATA_CACHE.get()


def read_weather_station(station_number, api_key):
    """
    Retrieve openweathermap 2.1 weather data
    """
    if WEATHER_STATION_CACHE.get() is None:
        url = (URL + api_key) % station_number
        weather_data = urllib.urlopen(URL % station_number).read()
        WEATHER_STATION_CACHE.set(json.loads(weather_data))
    
    if datetime.datetime.fromtimestamp(WEATHER_STATION_CACHE.get()["dt"]) < datetime.datetime.now() - datetime.timedelta(minutes=15):
        url = (URL + api_key) % station_number
        weather_data = urllib.urlopen(url).read()
        WEATHER_STATION_CACHE.set(json.loads(weather_data))
    
    return WEATHER_STATION_CACHE.get()


def read_history(station_number, api_key):
    """
    Read some history from the selected station
    """
    url = (HISTORY_URL + api_key) % station_number
    weather_data = urllib.urlopen(url).read()
    return json.loads(weather_data)


def current_temperature(station_number, api_key):
    """
    Read the current temperature
    """
    return convert_to_fahrenheit(convert_from_kelvin(read_weather(station_number, api_key)["main"]["temp"]))


def temperature(weather_data):
    """
    Read the temperature from the cache
    """
    return convert_to_fahrenheit(convert_from_kelvin(weather_data["main"]["temp"]))


def wind_speed(weather_data):
    """
    Read the wind speed from the cache
    """
    return weather_data["wind"]["speed"]


def humidity(weather_data):
    """
    Read the humidity from the cache
    """
    return weather_data["main"]["humidity"]


def current_rain(weather_data):
    """
    Read the rainfall amount from the cache
    """
    if "rain" in weather_data:
        return weather_data["rain"].values()[0]
    
    return 0


def history_rain(weather_data):
    """
    Read the 3 hour rainfall amount from the cache
    """
    return weather_data["rain"]["3h"]