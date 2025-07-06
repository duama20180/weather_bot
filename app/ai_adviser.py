import json
from google import genai
from .config import API_KEY_AI

async def get_weather_fit_advice(current_forecast):

    client = genai.Client(api_key=API_KEY_AI)

    forecast_str = json.dumps(current_forecast, indent=2)

    response = client.models.generate_content(
        model="gemini-2.0-flash",

        contents="Given the following weather data in JSON format,"
                 "Provide a practical clothing recommendation based on the current weather conditions."
                 "Given the temperature, wind speed, humidity, and overall weather condition, suggest appropriate layers of clothing,"
                 "accessories and footwear. Write in less than 200 characters. do not include weather details in the report."
                 f"Weather Data \n```json\n{forecast_str}\n```"
    )

    return response.text

# example = {'request': {'type': 'LatLon', 'query': 'Lat 40.84 and Lon 14.25', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'Naples', 'country': 'Italy', 'region': 'Campania', 'lat': '40.833', 'lon': '14.250', 'timezone_id': 'Europe/Rome', 'localtime': '2025-02-12 17:08', 'localtime_epoch': 1739380080, 'utc_offset': '1.0'}, 'current': {'observation_time': '04:08 PM', 'temperature': 14, 'weather_code': 116, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png'], 'weather_descriptions': ['Partly cloudy'], 'wind_speed': 13, 'wind_degree': 169, 'wind_dir': 'S', 'pressure': 1021, 'precip': 0, 'humidity': 63, 'cloudcover': 25, 'feelslike': 13, 'uv_index': 0, 'visibility': 10, 'is_day': 'yes'}}
# a =  get_weather_fit_advice(example)
# print(a)