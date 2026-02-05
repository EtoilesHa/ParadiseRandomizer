const form = document.getElementById("wish-form");
const statusText = document.getElementById("status-text");
const resultCard = document.getElementById("result-card");
const sceneValue = document.getElementById("scene-value");
const foodValue = document.getElementById("food-value");
const missValue = document.getElementById("miss-value");
const machineCards = Array.from(document.querySelectorAll(".machine-card"));
let selectedMachine = null;

machineCards.forEach((card) => {
    card.addEventListener("click", () => {
        selectedMachine = card.dataset.machine;
        machineCards.forEach((el) => el.classList.remove("active"));
        card.classList.add("active");
        statusText.textContent = `已选择：${selectedMachine}`;
        statusText.classList.remove("error");
    });
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const wishInput = document.getElementById("wish-input");
    const payload = {
        machine: selectedMachine,
        message: wishInput.value.trim(),
    };

    if (!payload.machine) {
        showStatus("请先选择机型。", true);
        return;
    }

    if (!payload.message) {
        showStatus("请填写一段留言，哪怕几个字也好。", true);
        return;
    }

    showStatus("正在掷骰子…");

    try {
        const response = await fetch("/api/random", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: "请求失败" }));
            throw new Error(error.message || "请求失败");
        }

        const data = await response.json();
        renderResult(data);
        showStatus("已完成！");
    } catch (error) {
        console.error(error);
        showStatus(error.message || "出现未知错误", true);
    }
});

function showStatus(message, isError = false) {
    statusText.textContent = message;
    statusText.classList.toggle("error", Boolean(isError));
}

function renderResult(data) {
    sceneValue.textContent = data.scene?.label || data.scene?.id || "-";
    foodValue.textContent = data.food || "-";
    missValue.textContent = data.miss || "-";
    resultCard.classList.remove("hidden");
}
