import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен бота
TOKEN = "7556550957:AAFvp8wDZA-x1m0vCem5iFs6BX8TQVjRKDQ"

# Ініціалізація бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ініціалізація бази даних
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,  -- Telegram ID як ключ
            username TEXT,
            balance INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 10,
            damage INTEGER DEFAULT 1,
            hp INTEGER DEFAULT 100,
            level INTEGER DEFAULT 1,
            monsters_killed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Додаємо користувача або оновлюємо username
def setup_user(user_id, username):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username) 
        VALUES (?, ?)
    ''', (user_id, username))
    conn.commit()
    conn.close()

# Отримання балансу користувача
def get_balance(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    balance = cursor.fetchone()[0]
    conn.close()
    return balance

# Додавання винагороди користувачу
def add_reward(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + 50 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Обробка команди /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    # Додаємо нового користувача або ігноруємо, якщо він уже є
    setup_user(user_id, username)

    start_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Launch App", url=f"http://127.0.0.1:5000/?user_id={user_id}")]
        ]
    )
    await message.answer(f"🎮 Welcome, {username}!\n🚀 Launch the app to start playing.", reply_markup=start_button)
    
# Обробка команди /reward
@dp.message(Command("reward"))
async def cmd_reward(message: types.Message):
    user_id = message.from_user.id
    add_reward(user_id)
    balance = get_balance(user_id)
    await message.answer(f"🎁 You've received 50 coins!\n💰 Your new balance: {balance} coins.")

# Запуск бота
async def main():
    init_db()
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
