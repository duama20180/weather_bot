import asyncpg
from asyncpg import exceptions
from dotenv import load_dotenv
import os

async def create_database():
    """
    Створює базу даних weather_bot, якщо вона ще не існує.
    """
    # Підключаємося до стандартної бази postgres
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="postgres"
    )
    try:
        await conn.execute("CREATE DATABASE weather_bot;")
        print("Database 'weather_bot' created successfully.")
    except exceptions.DuplicateDatabaseError:
        print("Database 'weather_bot' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        await conn.close()

async def create_tables():
    """
    Створює таблицю users у базі даних weather_bot, якщо вона ще не існує.
    """
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="weather_bot"
    )
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                lat_lon TEXT,
                schedule TEXT DEFAULT '0',
                tips BOOLEAN DEFAULT FALSE
            );
        """)
        print("Table 'users' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    load_dotenv()
    import asyncio
    asyncio.run(create_database())
    asyncio.run(create_tables())