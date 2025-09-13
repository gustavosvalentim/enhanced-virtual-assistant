import logging
import os
import requests

from langchain.tools import tool


logger = logging.getLogger(__name__)
weather_api_url = 'http://api.weatherapi.com/v1'


@tool
def get_weather(city: str, state: str) -> str:
    """Get weather forecast.
    
    Parameters:
        city (str): City to get weather forecast
        state (str): Regional state
    """
   
    query_params = {
        'key': os.getenv('WEATHER_API_KEY', ''),
        'fields': 'temp_c,wind_kph',
        'q': ' '.join((city, state,)),
    }
    response = requests.get(
        weather_api_url + '/forecast.json',
        params=query_params,
    )

    logger.debug(f'Weather API response: {response.text}')

    if response.status_code != 200:
        logger.error('Error getting weather forecast with URL %s. Error: %s',
                     response.request.url, response.text)
        return 'Could not get weather'
    
    weather = response.json().get('current', {})

    return (f'Temperature (Celcius): {weather["temp_c"]}\r\n'
            f'Wind (KM/H): {weather["wind_kph"]}')
