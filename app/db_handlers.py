import asyncpg
from .config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

async def init_db():
    """
    Ініціалізація підключення до бази даних і створення таблиці, якщо вона ще не існує
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                lat_lon TEXT,
                schedule TEXT DEFAULT '0',
                tips BOOLEAN DEFAULT FALSE
            )
        ''')
    finally:
        await conn.close()

async def save_user_location(user_id, lat_lon):
    """
    Зберігає геолокацію користувача
    Якщо користувач уже існує, оновлює тільки lat_lon
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        # Перевіряємо, чи існує користувач
        exists = await conn.fetchval(
            'SELECT EXISTS (SELECT 1 FROM users WHERE user_id = $1)', user_id
        )
        if exists:
            await conn.execute(
                'UPDATE users SET lat_lon = $1 WHERE user_id = $2',
                lat_lon, user_id
            )
        else:
            await conn.execute(
                'INSERT INTO users (user_id, lat_lon, schedule, tips) VALUES ($1, $2, $3, $4)',
                user_id, lat_lon, '0', False
            )
    finally:
        await conn.close()

async def get_user_location(user_id):
    """
    Отримує геолокацію користувача.
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        result = await conn.fetchval(
            'SELECT lat_lon FROM users WHERE user_id = $1', user_id
        )
        return result
    finally:
        await conn.close()

async def save_user_hour(user_id, hour):
    """
    Зберігає годину розкладу користувача
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        # Отримуємо поточний розклад
        schedule = await conn.fetchval(
            'SELECT schedule FROM users WHERE user_id = $1', user_id
        ) or '0'
        minutes = '00' if ':' not in schedule else schedule.split(':')[1]
        new_schedule = f"{hour}:{minutes}"
        await conn.execute(
            'UPDATE users SET schedule = $1 WHERE user_id = $2',
            new_schedule, user_id
        )
    finally:
        await conn.close()

async def save_user_minute(user_id, minute):
    """
    Зберігає хвилини розкладу користувача
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        schedule = await conn.fetchval(
            'SELECT schedule FROM users WHERE user_id = $1', user_id
        ) or '0'
        hours = '0' if ':' not in schedule else schedule.split(':')[0]
        minute = f"0{minute}" if len(minute) == 1 else minute
        new_schedule = f"{hours}:{minute}"
        await conn.execute(
            'UPDATE users SET schedule = $1 WHERE user_id = $2',
            new_schedule, user_id
        )
    finally:
        await conn.close()

async def get_user_schedule(user_id):
    """
    Отримує розклад користувача
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        schedule = await conn.fetchval(
            'SELECT schedule FROM users WHERE user_id = $1', user_id
        ) or '0'
        return schedule
    finally:
        await conn.close()

async def delete_user_schedule(user_id):
    """
    Видаляє розклад користувача
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        await conn.execute(
            'UPDATE users SET schedule = $1 WHERE user_id = $2',
            '0', user_id
        )
    finally:
        await conn.close()

async def tips_on_off(user_id):
    """
    On/Off AI-підказки
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        current_tips = await conn.fetchval(
            'SELECT tips FROM users WHERE user_id = $1', user_id
        ) or False
        new_tips = not current_tips
        await conn.execute(
            'UPDATE users SET tips = $1 WHERE user_id = $2',
            new_tips, user_id
        )
        return new_tips
    finally:
        await conn.close()

async def check_if_tip_is_on(user_id):
    """
    Перевіряє, чи увімкнені AI-підказки.
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        tips = await conn.fetchval(
            'SELECT tips FROM users WHERE user_id = $1', user_id
        ) or False
        return tips
    finally:
        await conn.close()

async def delete_user_info(user_id):
    """
    Видаляє всі дані користувача.
    """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        await conn.execute(
            'DELETE FROM users WHERE user_id = $1', user_id
        )
        print(f"Deleted user {user_id} successfully.")
    finally:
        await conn.close()