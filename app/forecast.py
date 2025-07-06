import aiohttp
import json
from google import genai
from .config import API_KEY_WEATHER,API_KEY_AI


async def get_lat_lon_from_name(city_name, user_id=None, bot=None, message=None):
    """
    Отримує координати (широта, довгота) за назвою населеного пункту, використовуючи Gemini AI.
    Якщо є кілька варіантів, запитує уточнення у користувача.
    """
    client = genai.Client(api_key=API_KEY_AI)

    prompt = (
        f"Find the latitude and longitude for the location '{city_name}'. "
        "If there are multiple locations with this name, provide a list of possible locations with their regions or countries. "
        "Return the result in JSON format with fields: 'locations' (list of objects with 'name', 'region', 'lat', 'lon'). "
        "If no location is found, return an empty list. "
        "Ensure the response is valid JSON."
    )

    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents = prompt)
        try:
            result = json.loads(response.text.strip("```json\n").strip("```"))
        except json.JSONDecodeError:
            return "Error city"

        if not result.get("locations"):
            return "Error city"

        locations = result["locations"]
        if len(locations) == 1:
            lat = locations[0]["lat"]
            lon = locations[0]["lon"]
            # print(f"Found single location: {locations[0]['name']}, {locations[0]['region']} ({lat}, {lon})")
            return f"{lat},{lon}"
        else:
            if user_id and bot and message:
                # Повертаємо список локацій для обробки в handlers.py
                # print(f"Multiple locations found for '{city_name}': {locations}")
                return locations
            else:
                # Якщо уточнення неможливе, повертаємо першу локацію
                lat = locations[0]["lat"]
                lon = locations[0]["lon"]
                # print(f"Multiple locations found for '{city_name}', selecting first: {locations[0]['name']}, {locations[0]['region']}")
                return f"{lat},{lon}"
    except Exception as e:
        print(f"Error fetching coordinates from Gemini: {e}")
        return "Error city"

async def get_weather_json(lat_lon):
    '''
        function receives weather api url, api key and string that contains lat and lon of location
    '''

    query = lat_lon
    url = f"http://api.weatherstack.com/current?access_key={API_KEY_WEATHER}&query={query}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Weatherstack API error: status {response.status}")
                    return None
                return await response.json()
    except Exception as e:
        print(f"Error fetching weather from Weatherstack: {e}")
        return None

async def format_weather_message(weather_json):
    """
        Formats the weather JSON into a readable message in english with emojis.
    """

    temp = weather_json['current']['temperature']
    feels_like = weather_json['current']['feelslike']
    weather_desc = weather_json['current']['weather_descriptions'][0].strip()
    wind_speed = weather_json['current']['wind_speed']
    wind_dir = weather_json['current']['wind_dir']
    pressure = weather_json['current']['pressure']
    humidity = weather_json['current']['humidity']
    cloudcover = weather_json['current']['cloudcover']
    visibility = weather_json['current']['visibility']

    # static version of forecast
    static_message = (
        f"🌤 Current weather 🌍\n\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"❄️ Feels like: {feels_like}°C\n"
        f"🌙 Weather: {weather_desc}\n"
        f"🌬️ Wind: {wind_speed} km/h, {wind_dir}\n"
        f"⬆️ Pressure: {pressure} hPa\n"
        f"💧 Humidity: {humidity}%\n"
        f"☁️ Cloud cover: {cloudcover}%\n"
        f"👀 Visibility: {visibility} km\n\n"
    )

    # new version with AI
    client = genai.Client(api_key=API_KEY_AI)
    prompt = (
        f"Create a concise and varied weather forecast message in English based on the following data: "
        f"Temperature: {temp}°C, Feels like: {feels_like}°C, Weather: {weather_desc}, "
        f"Wind: {wind_speed} km/h ({wind_dir}), Pressure: {pressure} hPa, Humidity: {humidity}%, "
        f"Cloud cover: {cloudcover}%, Visibility: {visibility} km. "
        f"Use a friendly and natural tone, include all provided parameters, and add appropriate emojis for each parameter. "
        f"Keep the structure similar to this example, with a header and each parameter on a new line: "
        f"'🌤 Current weather 🌍\n\n🌡️ Temperature: X°C\n❄️ Feels like: Y°C\n...' "
        f"Avoid repeating the exact phrasing of the example. Return only the formatted message."
    )

    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents = prompt)
        ai_message = response.text.strip()
        if all(param in ai_message for param in [str(temp), str(feels_like), weather_desc, str(wind_speed), wind_dir, str(pressure), str(humidity), str(cloudcover), str(visibility)]):
            return ai_message
        else:
            print(f"AI response incomplete: {ai_message}")
            return static_message
    except Exception as e:
        print(f"Error generating AI weather message: {e}")
        return static_message


# for test
async def main():
    city_name = 'Неаполь'
    coordinates = await get_lat_lon_from_name(city_name)
    print(coordinates)
    weather_json = await get_weather_json(coordinates)
    print()
    print(weather_json)

    weather_message = await format_weather_message(weather_json)
    print(weather_message)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

