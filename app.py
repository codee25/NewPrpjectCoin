from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    # Отримуємо user_id з параметра запиту
    user_id = request.args.get("user_id")
    if not user_id:
        return "Error: User ID is missing in the URL."

    # Додаткова логіка, якщо потрібно
    return render_template("index.html")

# Ініціалізація бази даних
def setup_database():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
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

setup_database()

# Отримати статистику користувача
@app.route("/api/stats", methods=["GET", "POST"])
def get_stats():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    try:
        if request.method == "POST":
            # Читаємо дані з тіла запиту (JSON)
            data = request.get_json()
            user_id = data.get("user_id")
            username = data.get("username", "Unknown")  # Ім'я користувача за замовчуванням
        elif request.method == "GET":
            # Читаємо user_id з параметра URL
            user_id = request.args.get("user_id")
            username = "Unknown"  # Якщо GET, ім'я користувача невідоме

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Перевіряємо існування користувача у базі даних
        cursor.execute("SELECT balance, hp, damage FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        # Якщо користувача немає - створюємо нового
        if not user:
            cursor.execute('''
                INSERT INTO users (id, username, balance, energy, damage, hp, level, monsters_killed)
                VALUES (?, ?, 0, 10, 1, 100, 1, 0)
            ''', (user_id, username))
            conn.commit()
            cursor.execute("SELECT balance, hp, damage FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

        # Повертаємо дані користувача у форматі JSON
        return jsonify({
            "balance": user[0],
            "hp": user[1],
            "damage": user[2]
        })

    except Exception as e:
        # Обробка помилок сервера
        return jsonify({"error": str(e)}), 500

    finally:
        # Закриваємо з'єднання з базою
        conn.close()


# Обробити клік по монстру
@app.route("/api/hit", methods=["POST"])
def hit_monster():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    # Перевіряємо, чи існує користувач, і створюємо його, якщо немає
    cursor.execute('''
        INSERT OR IGNORE INTO users (id, username, balance, energy, damage, hp, level, monsters_killed)
        VALUES (?, ?, 0, 10, 1, 100, 1, 0)
    ''', (user_id, "Unknown"))

    # Отримуємо HP і урон користувача
    cursor.execute("SELECT damage, hp FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    damage, hp = result

    # Зменшуємо HP монстра
    hp -= damage
    if hp <= 0:
        hp = 100
        cursor.execute("UPDATE users SET balance = balance + 10, monsters_killed = monsters_killed + 1 WHERE id = ?", (user_id,))

    # Оновлюємо HP у базі даних
    cursor.execute("UPDATE users SET hp = ? WHERE id = ?", (hp, user_id))
    conn.commit()

    # Повертаємо оновлені дані
    cursor.execute("SELECT balance, hp FROM users WHERE id = ?", (user_id,))
    balance, hp = cursor.fetchone()
    conn.close()

    return jsonify({"balance": balance, "hp": hp})

@app.route("/api/buy", methods=["POST"])
def buy_upgrade():
    data = request.get_json()
    user_id = data.get("user_id")
    upgrade_type = data.get("type")

    if not user_id or not upgrade_type:
        return jsonify({"success": False, "message": "Missing user_id or upgrade type"}), 400

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    # Перевіряємо, чи існує користувач
    cursor.execute("SELECT balance, damage FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:  # Користувач не знайдений
        conn.close()
        return jsonify({"success": False, "message": "User not found"}), 404

    # Отримуємо дані користувача
    balance, damage = user

    # Логіка покупки покращення
    if upgrade_type == "damage" and balance >= 10:
        balance -= 10
        damage += 1
        cursor.execute("UPDATE users SET balance = ?, damage = ? WHERE id = ?", (balance, damage, user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "balance": balance, "damage": damage})

    conn.close()
    return jsonify({"success": False, "message": "Not enough balance or invalid upgrade type"})

if __name__ == "__main__":
    app.run(debug=True)
