let hp = 100; // Локальна змінна для HP
const userId = new URLSearchParams(window.location.search).get("user_id"); // Отримуємо user_id з URL

if (!userId) {
    alert("Error: User ID is missing in the URL!");
    throw new Error("User ID is missing");
}
console.log("User ID:", userId); // Лог user_id для перевірки

// Функція для оновлення елементів на сторінці
function updateUI(balance, currentHp, damage) {
    document.getElementById("balance").innerText = balance;
    document.getElementById("hp").innerText = currentHp;
    document.getElementById("hp-progress").style.width = (currentHp / 100) * 100 + "%";
    hp = currentHp;
    localStorage.setItem("damage", damage); // Зберігаємо урон локально
}

// Завантаження статистики з сервера
async function loadStats() {
    try {
        console.log("Sending POST request to /api/stats...");
        const response = await fetch("/api/stats", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();
        console.log("Server response:", data);

        document.getElementById("balance").innerText = data.balance;
        document.getElementById("hp").innerText = data.hp;
        document.getElementById("hp-progress").style.width = (data.hp / 100) * 100 + "%";
    } catch (error) {
        console.error("Failed to load stats:", error);
        document.getElementById("balance").innerText = "Error";
        document.getElementById("hp").innerText = "Error";
    }
}

// Обробка кліків по монстру
async function hitMonster() {
    try {
        const response = await fetch("/api/hit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId }) // Передаємо user_id на сервер
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        // Оновлюємо баланс і HP на сторінці
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
            body: JSON.stringify({ user_id: userId, type: type }) // Передаємо user_id і тип покращення
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

// Прив'язка функцій до елементів
document.getElementById("monster").addEventListener("click", hitMonster);
document.getElementById("buy-damage").addEventListener("click", () => buyUpgrade("damage"));
window.onload = loadStats;
