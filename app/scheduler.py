from datetime import datetime
import asyncio
import asyncpg
from . import db_handlers as db
from . import forecast
from . import ai_adviser as adviser

async def schedule_checker(bot):
    """
    Перевіряє розклад користувачів і надсилає прогноз погоди та AI-підказки у заданий час.
    """
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            print(f"Checking schedules at {now}")

            conn = await asyncpg.connect(
                host=db.DB_HOST,
                port=db.DB_PORT,
                database=db.DB_NAME,
                user=db.DB_USER,
                password=db.DB_PASSWORD
            )
            try:
                users = await conn.fetch("SELECT user_id, schedule, tips FROM users WHERE schedule != '0'")
                for user in users:
                    user_id = user["user_id"]
                    schedule_time = user["schedule"]
                    tips_enabled = user["tips"]

                    if schedule_time == now:
                        print(f"Sending reminder to user {user_id}")
                        try:
                            lat_lon = await db.get_user_location(user_id)
                            if not lat_lon:
                                print(f"No location for user {user_id}")
                                continue

                            weather = await forecast.get_weather_json(lat_lon)
                            if not weather or not isinstance(weather, dict) or "current" not in weather:
                                print(f"Failed to fetch weather for user {user_id}")
                                await bot.send_message(user_id, "Failed to fetch weather data.")
                                continue

                            answer = await forecast.format_weather_message(weather)
                            await bot.send_message(user_id, answer)

                            if tips_enabled:
                                print(f"Sending AI tip to user {user_id}")
                                await bot.send_message(user_id, "Weather fit for you:")
                                tip = await adviser.get_weather_fit_advice(weather)
                                await bot.send_message(user_id, tip)

                        except Exception as e:
                            print(f"Error sending message to user {user_id}: {e}")
                            await bot.send_message(user_id, "Error processing your reminder. Please try again later.")

            finally:
                await conn.close()

        except asyncpg.exceptions.PostgresError as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"General error in schedule_checker: {e}")

        # Чекаємо 60 секунд перед наступною перевіркою
        await asyncio.sleep(60)