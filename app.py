from flask import Flask, render_template, jsonify, request
import sqlite3
app = Flask(__name__)
@app.route("/")
def home():
    return render_template("index.html")  # Відображення шаблону
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
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        username = data.get("username", "Unknown")

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        print(f"[GET STATS] Received request with user_id: {user_id}, username: {username}")

        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()

        # Перевіряємо, чи існує користувач
        cursor.execute("SELECT balance, hp, damage FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            # Якщо користувача не знайдено, додаємо його
            cursor.execute('''
                INSERT INTO users (id, username, balance, energy, damage, hp, level, monsters_killed)
                VALUES (?, ?, 0, 10, 1, 100, 1, 0)
            ''', (user_id, username))
            conn.commit()
            cursor.execute("SELECT balance, hp, damage FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

        conn.close()

        # Повертаємо дані користувача
        return jsonify({
            "balance": user[0],
            "hp": user[1],
            "damage": user[2]
        })

    except Exception as e:
        print(f"[GET STATS ERROR] {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Обробити клік по монстру
@app.route("/api/hit", methods=["POST"])
def hit_monster():
    data = request.get_json()
    user_id = data.get("user_id")
    print(f"[HIT MONSTER] Received request with user_id: {user_id}")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    # Перевіряємо, чи існує користувач
    cursor.execute("SELECT damage, hp, balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    damage, hp, balance = result

    # Оновлюємо HP монстра
    hp -= damage
    if hp <= 0:
        hp = 100
        balance += 10
        cursor.execute("UPDATE users SET monsters_killed = monsters_killed + 1 WHERE id = ?", (user_id,))

    # Записуємо оновлення у базу
    cursor.execute("UPDATE users SET hp = ?, balance = ? WHERE id = ?", (hp, balance, user_id))
    conn.commit()  # НЕ ЗАБУВАЙТЕ ПРО commit()!
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
