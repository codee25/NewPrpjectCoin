import multiprocessing
import os

# Функція для запуску Flask-сервера
def run_flask():
    os.system("py app.py")

# Функція для запуску Telegram-бота
def run_bot():
    os.system("py main.py")

if __name__ == "__main__":
    # Створюємо процеси для Flask і Telegram-бота
    flask_process = multiprocessing.Process(target=run_flask)
    bot_process = multiprocessing.Process(target=run_bot)

    # Запускаємо обидва процеси
    flask_process.start()
    bot_process.start()

    # Очікуємо завершення процесів
    flask_process.join()
    bot_process.join()
