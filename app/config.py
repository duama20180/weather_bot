from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

DATA_FILE = os.getenv("DATA_FILE")

API_KEY_WEATHER = os.getenv("API_KEY_WEATHER")

API_KEY_AI = os.getenv("API_KEY_AI")

API_KEY_LOCATIONS = os.getenv("API_KEY_LOCATIONS")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")