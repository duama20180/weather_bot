# Weather Bot

A Telegram bot that delivers real-time weather forecasts using Weatherstack API, AI-based clothing recommendations powered by Gemini AI, and scheduled notifications.

## Features
- Get current weather by location (via geolocation or manual input).
- Receive AI-generated clothing tips based on weather conditions.
- Set daily weather notification schedules.
- Supports multiple locations with inline keyboard selection.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/твій_нік/weather_bot.git

2. Create a virtual environment:
   ```bash
    python -m venv .venv

3. Activate it:
   ```bash
   .\.venv\Scripts\activate  # Windows
    source .venv/bin/activate  # Linux/macOS

4. Install dependencies:
   ```bash
   pip install -r requirements.txt

5. Create a .env file in the project root with:
   ```bash
    API_KEY_WEATHER=your_weatherstack_api_key
    API_KEY_AI=your_gemini_api_key
    DB_HOST=localhost
    DB_PORT=5433
    DB_NAME=weather_bot
    DB_USER=postgres
    DB_PASSWORD=your_password

6. Run the bot:
   ```bash
   python main.py

## Usage

- Send /start to initialize the bot.
- Select Forecast for current weather or AI tips for clothing recommendations.
- Customize notifications with Current schedule and Change or set schedule.

## Dependencies

- aiogram: For Telegram bot framework
- aiohttp: For asynchronous HTTP requests
- asyncpg: For PostgreSQL database integration
- google-genai: For AI-powered weather descriptions and tips

## License
#### MIT License