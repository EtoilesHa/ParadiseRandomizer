from __future__ import annotations

import hashlib
import os
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


PARADISE_FILE = Path(__file__).with_name("paradise.yaml")
MACHINE_OPTIONS = ["天空机", "陆地机", "海洋机", "翠林机"]


@lru_cache(maxsize=1)
def load_config() -> Dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - import guard
        raise SystemExit("需要 PyYAML 支持，请先运行 pip install pyyaml") from exc

    raw_data = yaml.safe_load(PARADISE_FILE.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        raise ValueError("paradise.yaml 的根节点必须是字典")
    return raw_data


def load_scenes() -> List[Dict[str, Any]]:
    scenes = load_config().get("scenes")
    if not isinstance(scenes, list):
        raise ValueError("paradise.yaml 中 scenes 的定义不正确")
    return scenes


def load_miss_options() -> List[str]:
    miss_config = load_config().get("miss_num") or {}
    counts = miss_config.get("count") if isinstance(miss_config, dict) else None
    if not isinstance(counts, list) or not counts:
        raise ValueError("paradise.yaml 中缺少 miss_num.count 配置")
    return counts


def apply_machine_prerequisite(machine_type: str, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = machine_type.strip().lower()
    is_emerald_machine = ("翠林" in machine_type) or ("emerald" in normalized)
    excluded_id = "sky" if is_emerald_machine else "emerald_forest"
    filtered = [scene for scene in scenes if scene.get("id") != excluded_id]
    if not filtered:
        raise ValueError("筛选后没有可用的场景，请检查机型或配置。")
    return filtered


def prompt_machine_choice() -> str:
    print("请选择机型：")
    for idx, label in enumerate(MACHINE_OPTIONS, start=1):
        print(f"{idx}. {label}")

    while True:
        selection = input("输入机型编号：").strip()
        if selection.isdigit():
            idx = int(selection)
            if 1 <= idx <= len(MACHINE_OPTIONS):
                return MACHINE_OPTIONS[idx - 1]
        print("无效输入，请重新输入 1-4 之间的数字。")


def derive_seed(user_entropy: str) -> int:
    digest = hashlib.sha256(user_entropy.encode("utf-8")).digest()
    base_seed = int.from_bytes(digest, "big")
    extra_entropy = int.from_bytes(os.urandom(16), "big")
    return base_seed ^ extra_entropy


def pick_scene_and_food(machine_type: str, user_entropy: str) -> Dict[str, Any]:
    scenes = load_scenes()
    available_scenes = apply_machine_prerequisite(machine_type, scenes)
    rng = random.Random(derive_seed(user_entropy))
    miss_choice = rng.choice(load_miss_options())
    chosen_scene = rng.choice(available_scenes)
    food_categories = chosen_scene.get("food_categories") or []
    if not food_categories:
        raise ValueError(f"场景 {chosen_scene.get('id')} 缺少 food_categories 配置。")
    return {
        "scene": chosen_scene,
        "food": rng.choice(food_categories),
        "miss": miss_choice,
    }


def main() -> None:
    machine_type = prompt_machine_choice()

    user_entropy = input("请输入任意内容以生成随机种子：").strip()
    if not user_entropy:
        raise SystemExit("随机内容不能为空")

    result = pick_scene_and_food(machine_type, user_entropy)
    scene_label = result["scene"].get("label", result["scene"].get("id"))

    print("=== 随机结果 ===")
    print(f"场景：{scene_label}")
    print(f"食物：{result['food']}")
    print(f"miss 档位：{result['miss']}")


if __name__ == "__main__":
    main()
