from aiogram import types, Router, F
from aiogram.filters import Command, CommandStart, or_f
import asyncpg

from . import keyboards as kb
from . import forecast
from . import ai_adviser as adviser
from . import db_handlers as db

router = Router()

# Debug function to print message details
# def debug_message(message: types.Message):
    # print(f"Message received: {message.text} | Type: {message.content_type}")

# interaction when starting up a bot
@router.message(CommandStart())
async def send_welcome(message: types.Message):

    """
    This handler will be called when user sends `/start` command
    """

    # debug_message(message)

    await message.answer("👋")
    await message.answer("Your pocket-sized meteorologist. Get precise weather reports in seconds!")

    await set_location(message)


#location
@router.message(Command("set_location"))
async def set_location(message: types.Message):
    # debug_message(message)

    """
    This handler will be called when user sends `/set_location` command and allow user to type their location
    """

    await message.answer("Let's proceed to setting your location: 📍", reply_markup = kb.location_keyboard)

@router.message(F.text == "Customize location")
async def location_changer(message: types.Message):

    if await db.get_user_location(message.from_user.id) is None:
        await message.answer("You haven't set a location yet")
    else:
        await message.answer("Set your new location:", reply_markup=kb.location_keyboard_2)

@router.message(F.location)
async def location_handler(message: types.Message):
    """
    This handler will be called when user sends location through telegram inner method
    """
    user_id = message.from_user.id
    lat = message.location.latitude
    lon = message.location.longitude

    # debug_message(message)

    await message.answer("✅ Location received!", reply_markup=types.ReplyKeyboardRemove())

    if user_id in allowed_users:
        del allowed_users[user_id]

    await db.save_user_location(user_id, f"{lat},{lon}")

    await message.answer("Choose an option:",reply_markup=kb.main_keyboard)

#experimental dictionary
allowed_users = {}
@router.message(F.text == "Manual input")
async def manual_input(message: types.Message):

    user_id = message.from_user.id
    allowed_users[user_id] = {"manual_input": True}

    await message.answer("‼️The weather forecast may be inaccurate when using the text method of entering the location‼️",
                         show_alert=True)
    await message.answer("Type your settlement️ ⌨️")
#continued in the end of file

# Forecast
@router.message(F.text == "Forecast")
async def get_forecast(message: types.Message):

    # debug_message(message)

    user_id = message.from_user.id
    lat_lon = await db.get_user_location(user_id)

    if not lat_lon:
        await message.answer("🚨 You haven't provided a geolocation yet! Send it to get a forecast.",
                             reply_markup=kb.location_keyboard)
        return

    await message.answer("Detecting the weather for you..")

    weather = await forecast.get_weather_json(lat_lon)
    # print(weather)
    answer = await forecast.format_weather_message(weather)
    # print(answer)

    await message.answer(answer)

    await get_tip(message, weather=weather)

#AI tips
@router.message(F.text == "AI tips")
async def get_ai_tips_keyboard(message: types.Message):
    # debug_message(message)
    await message.answer("Customize your recommendations:", reply_markup=kb.ai_tips_keyboard)

@router.message(F.text == "Automatic tips on / off")
async def tip_on_off(message: types.Message):
    user_id = message.from_user.id

    await db.tips_on_off(user_id)

    if await db.check_if_tip_is_on(user_id):
        await message.reply("Tips are enabled ✅")
    else:
        await message.reply("Tips are disabled ❌")

@router.message(F.text == "Back")
async def back_to_menu(message: types.Message):
    await message.answer("🔙 Back to menu", reply_markup=kb.main_keyboard)

@router.message(or_f(Command("get_tip"), F.text == "Get a tip"))
async def get_tip(message: types.Message, weather = None):
    user_id = message.from_user.id

    # Якщо це виклик підказки з кнопки, пропускаємо перевірку
    if message.text.startswith("Get a tip") or not weather:
        lat_lon = await db.get_user_location(user_id)
        weather = await forecast.get_weather_json(lat_lon)

    if not message.text.startswith("Get a tip") and not await db.check_if_tip_is_on(user_id):
        return

    if not weather or not isinstance(weather, dict) or "current" not in weather:
        await message.answer("Failed to fetch weather data for clothing recommendation.")
        return

    await message.answer("Weather fit for you:")
    tip = await adviser.get_weather_fit_advice(weather)
    await message.answer(tip)


#schedule
@router.message(F.text == "Current schedule")
async def get_schedule(message: types.Message):

    user_id = message.from_user.id
    schedule = await db.get_user_schedule(user_id)

    if schedule == "" or schedule == "0":
        return await message.answer(f"You haven't set a schedule yet ❌",reply_markup=kb.schedule_keyboard)
    else:
        await message.answer(f"⏰ Time for notifications, daily in {schedule}", reply_markup=kb.schedule_keyboard)

@router.message(F.text == "Delete schedule")
async def delete_schedule(message: types.Message):
    user_id = message.from_user.id
    await db.delete_user_schedule(user_id)
    await message.answer("🗑 Schedule deleted ❌")

@router.message(F.text == "Customize schedule")
async def schedule_handler(message: types.Message):
    # debug_message(message)
    await message.answer("📅 Customize your schedule 🛠", reply_markup=kb.schedule_keyboard)

@router.message(F.text == "Change or set schedule")
async def set_schedule(message: types.Message):
    await message.answer("Adjust the hour 🕰",reply_markup=kb.generate_hour_keyboard())

@router.callback_query(lambda c: c.data.startswith("hour_"))
async def select_hour(callback: types.CallbackQuery):
    hour = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await db.save_user_hour(user_id, hour)
    await callback.message.delete()

    await callback.answer(f"Selected {hour}:00" )
    await callback.message.answer ("Adjust the minutes 🕰", reply_markup=kb.generate_minute_keyboard())

@router.callback_query(lambda c: c.data.startswith("minute_"))
async def select_minute(callback: types.CallbackQuery):

    minute = callback.data.split("_")[1]
    user_id = callback.from_user.id

    await db.save_user_minute(user_id, minute)
    await callback.message.delete()

    await callback.answer(f"Selected {minute} minutes" )

    await callback.message.answer("Schedule successfully set! ✅")

    schedule = await db.get_user_schedule(user_id)
    await callback.message.answer(f"⏰ Time for notifications, daily in {schedule}")


# remover
@router.message(F.text == "Delete info")
async def delete_info(message: types.Message):
    # debug_message(message)

    await db.delete_user_info(message.from_user.id)

    await message.answer("all your personal info deleted 🗑 ")

    await message.answer("🔄 Let's start from the beginning 🔃", reply_markup=kb.location_keyboard)

#very experimental, fully AI generated
@router.message()
async def location_text_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in allowed_users:
        return

    try:
        if allowed_users[user_id].get("awaiting_choice"):
            # Користувач уточнює область
            if allowed_users[user_id].get("clarifying_region"):
                region = message.text
                city_name = allowed_users[user_id]["city_name"]
                # Повторний запит до Gemini із уточненою областю
                result = await forecast.get_lat_lon_from_name(f"{city_name}, {region}", user_id, message.bot, message)
                if isinstance(result, str):
                    if result == "Error city":
                        await message.answer("🚨 Error with the name or region. Try another settlement.", reply_markup=kb.location_keyboard)
                    else:
                        await db.save_user_location(user_id, result)
                        await message.answer("✅ Location received!", reply_markup=types.ReplyKeyboardRemove())
                        del allowed_users[user_id]
                        await message.answer("Choose an option:", reply_markup=kb.main_keyboard)
                elif isinstance(result, list):
                    # Якщо все ще кілька варіантів, показуємо інлайн-клавіатуру
                    await message.answer(
                        f"Several locations found for '{city_name}, {region}'. Please select one:",
                        reply_markup=kb.generate_location_keyboard(result)
                    )
                    allowed_users[user_id] = {"locations": result, "awaiting_choice": True, "city_name": city_name}
            else:
                # Користувач обирає варіант із кількох локацій
                try:
                    choice = int(message.text) - 1
                    locations = allowed_users[user_id]["locations"]
                    if 0 <= choice < len(locations):
                        lat = locations[choice]["lat"]
                        lon = locations[choice]["lon"]
                        lat_lon = f"{lat},{lon}"
                        await db.save_user_location(user_id, lat_lon)
                        await message.answer("✅ Location received!", reply_markup=types.ReplyKeyboardRemove())
                        del allowed_users[user_id]
                        await message.answer("Choose an option:", reply_markup=kb.main_keyboard)
                    else:
                        await message.answer("Invalid choice. Please select a valid number or clarify the region.", reply_markup=kb.location_keyboard)
                except ValueError:
                    await message.answer("Please enter a valid number or clarify the region.", reply_markup=kb.location_keyboard)
        elif allowed_users[user_id].get("manual_input"):
            # Користувач ввів назву міста
            city_name = message.text
            result = await forecast.get_lat_lon_from_name(city_name, user_id, bot=message.bot, message=message)
            if isinstance(result, str):
                if result == "Error city":
                    await message.answer("🚨 Error with the name. Try another settlement.", reply_markup=kb.location_keyboard)
                else:
                    await db.save_user_location(user_id, result)
                    await message.answer("✅ Location received!", reply_markup=types.ReplyKeyboardRemove())
                    del allowed_users[user_id]
                    await message.answer("Choose an option:", reply_markup=kb.main_keyboard)
            elif isinstance(result, list):
                # Отримано кілька локацій, надсилаємо інлайн-клавіатуру
                await message.answer(
                    f"Several locations found for '{city_name}'. Please select one:",
                    reply_markup=kb.generate_location_keyboard(result)
                )
                allowed_users[user_id] = {"locations": result, "awaiting_choice": True, "city_name": city_name}
    except asyncpg.exceptions.PostgresError as e:
        await message.answer("🚨 Database error. Please try again later.")
        print(f"Database error in location_text_handler: {e}")

@router.callback_query(lambda c: c.data.startswith("location_"))
async def select_location(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in allowed_users or not allowed_users[user_id].get("awaiting_choice"):
        await callback.answer("Invalid action.")
        return
    try:
        choice = int(callback.data.split("_")[1])
        locations = allowed_users[user_id]["locations"]
        if 0 <= choice < len(locations):
            lat = locations[choice]["lat"]
            lon = locations[choice]["lon"]
            lat_lon = f"{lat},{lon}"
            await db.save_user_location(user_id, lat_lon)
            await callback.message.delete()
            await callback.answer(f"Selected {locations[choice]['name']}, {locations[choice]['region']}")
            await callback.message.answer("✅ Location received!", reply_markup=types.ReplyKeyboardRemove())
            del allowed_users[user_id]
            await callback.message.answer("Choose an option:", reply_markup=kb.main_keyboard)
        else:
            await callback.answer("Invalid choice.")
    except asyncpg.exceptions.PostgresError as e:
        await callback.message.answer("🚨 Database error. Please try again later.")
        print(f"Database error in select_location: {e}")
    except ValueError:
        await callback.answer("Invalid choice format.")

@router.callback_query(lambda c: c.data == "location_clarify")
async def clarify_region(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in allowed_users or not allowed_users[user_id].get("awaiting_choice"):
        await callback.answer("Invalid action.")
        return

    await callback.message.delete()
    await callback.answer("Please specify the region.")
    await callback.message.answer(
        f"Please enter the region for '{allowed_users[user_id]['city_name']}' (e.g., Запорізька область):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    allowed_users[user_id]["clarifying_region"] = True