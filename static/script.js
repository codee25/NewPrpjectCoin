let hp = 100; // Локальна змінна для HP
const userId = new URLSearchParams(window.location.search).get("user_id"); // Отримуємо user_id з URL

if (!userId) {
    alert("Error: User ID is missing in the URL!");
    throw new Error("User ID is missing");
}
console.log("User ID:", userId);


// Функція для оновлення елементів на сторінці
function updateUI(balance, currentHp, damage) {
    document.getElementById("balance").innerText = balance;
    document.getElementById("hp").innerText = currentHp;
    document.getElementById("hp-progress").style.width = Math.max(0, (currentHp / 100) * 100) + "%";
    hp = currentHp;
    if (damage !== null) {
        localStorage.setItem("damage", damage); // Зберігаємо урон локально
    }
}

// Завантаження статистики з сервера
async function loadStats() {
    try {
        const response = await fetch("/api/stats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, username: "YourUsername" }) // Передаємо ім'я
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();
        console.log("Server response:", data);

        updateUI(data.balance, data.hp, data.damage);
    } catch (error) {
        console.error("Failed to load stats:", error);
        updateUI("Error", "Error", null);
    }
}


// Обробка кліків по монстру
async function hitMonster() {
    try {
        const response = await fetch("/api/hit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();

        updateUI(data.balance, data.hp, localStorage.getItem("damage"));
    } catch (error) {
        console.error("Failed to hit monster:", error);
    }
}

// Обробка покупки покращень
async function buyUpgrade(type) {
    try {
        const response = await fetch("/api/buy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, type: type })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();

        if (data.success) {
            alert("🎉 Upgrade successful!");
            updateUI(data.balance, hp, data.damage); // Оновлюємо баланс і урон
        } else {
            alert("❌ " + data.message);
        }
    } catch (error) {
        console.error("Error during upgrade:", error);
    }
}

// Перевірка наявності елементів перед додаванням подій
if (document.getElementById("monster")) {
    document.getElementById("monster").addEventListener("click", hitMonster);
}
if (document.getElementById("buy-damage")) {
    document.getElementById("buy-damage").addEventListener("click", () => buyUpgrade("damage"));
}

// Завантажуємо статистику при завантаженні сторінки
window.onload = loadStats;
