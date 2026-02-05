// 嵌入原 YAML 配置，方便 GitHub Pages 静态部署
const MACHINE_OPTIONS = ["天空机", "陆地机", "海洋机", "翠林机"];
const SCENES = [
    {
        id: "sky",
        label: "天空",
        food_categories: ["鸡类", "玉米类", "糖浆类", "杂食类"],
    },
    {
        id: "land",
        label: "陆地",
        food_categories: ["肉类", "蔬果类", "虫类", "杂食类"],
    },
    {
        id: "ocean",
        label: "海洋",
        food_categories: ["海鲜类", "海藻类", "虾类", "杂食类"],
    },
    {
        id: "emerald_forest",
        label: "翠林",
        food_categories: ["烤鸭类", "竹草类", "石榴类", "杂食类"],
    },
];
const MISS_OPTIONS = ["0", "0~1", "2~5", "6+"];

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

form.addEventListener("submit", (event) => {
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
        const result = generateRandomResult(payload.machine, payload.message);
        renderResult(result);
        showStatus("已完成！");
    } catch (error) {
        console.error(error);
        showStatus(error.message || "出现未知错误", true);
    }
});

function generateRandomResult(machineType, message) {
    if (!MACHINE_OPTIONS.includes(machineType)) {
        throw new Error("机型选择无效。");
    }

    const scenes = applyMachinePrerequisite(machineType);
    const entropySource = `${machineType}-${message}-${Date.now()}-${getRandomUint32()}`;
    const rng = createRng(deriveSeed(entropySource));
    const chosenScene = randomChoice(scenes, rng);
    const miss = randomChoice(MISS_OPTIONS, rng);
    const food = randomChoice(chosenScene.food_categories, rng);

    return {
        scene: chosenScene,
        food,
        miss,
    };
}

function applyMachinePrerequisite(machineType) {
    const normalized = (machineType || "").trim().toLowerCase();
    const isEmeraldMachine = machineType.includes("翠林") || normalized.includes("emerald");
    const excludedId = isEmeraldMachine ? "sky" : "emerald_forest";
    const filtered = SCENES.filter((scene) => scene.id !== excludedId);
    if (!filtered.length) {
        throw new Error("没有可用的场景，请检查配置。");
    }
    return filtered;
}

function randomChoice(options, rng) {
    if (!Array.isArray(options) || options.length === 0) {
        throw new Error("配置缺少可用选项。");
    }
    const index = Math.floor(rng() * options.length);
    return options[index];
}

function deriveSeed(entropy) {
    let hash = 0;
    for (let i = 0; i < entropy.length; i += 1) {
        hash = (hash * 31 + entropy.charCodeAt(i)) >>> 0;
    }
    return hash ^ getRandomUint32();
}

function createRng(seed) {
    let state = seed >>> 0;
    return () => {
        state = (1664525 * state + 1013904223) >>> 0;
        return state / 0x100000000;
    };
}

function getRandomUint32() {
    if (window.crypto && window.crypto.getRandomValues) {
        const buffer = new Uint32Array(1);
        window.crypto.getRandomValues(buffer);
        return buffer[0];
    }
    return Math.floor(Math.random() * 0xffffffff);
}

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
