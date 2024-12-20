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
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()

    # Шукаємо username за user_id
    cursor.execute("SELECT username, balance, hp, damage FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        # Якщо користувач не існує, створюємо його
        username = "Unknown"
        cursor.execute('''
            INSERT INTO users (id, username, balance, energy, damage, hp, level, monsters_killed)
            VALUES (?, ?, 0, 10, 1, 100, 1, 0)
        ''', (user_id, username))
        conn.commit()
        balance, hp, damage = 0, 100, 1
    else:
        username, balance, hp, damage = user

    conn.close()
    return jsonify({"username": username, "balance": balance, "hp": hp, "damage": damage})
   
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
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        upgrade_type = data.get("type")

        if not user_id or not upgrade_type:
            return jsonify({"error": "User ID and upgrade type are required"}), 400

        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()

        # Отримуємо поточний баланс і урон користувача
        cursor.execute("SELECT balance, damage FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        balance, damage = user

        # Вартість апгрейду
        upgrade_cost = 10

        if balance < upgrade_cost:
            return jsonify({"success": False, "message": "Not enough balance!"}), 400

        # Знімаємо гроші, збільшуємо урон
        new_balance = balance - upgrade_cost
        new_damage = damage + 1

        cursor.execute("UPDATE users SET balance = ?, damage = ? WHERE id = ?", (new_balance, new_damage, user_id))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "balance": new_balance, "damage": new_damage})

    except Exception as e:
        print(f"[BUY UPGRADE ERROR] {e}")
        return jsonify({"error": "An internal error occurred"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
