from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from random_tm import MACHINE_OPTIONS, pick_scene_and_food

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/random", methods=["POST"])
def generate_random():
    payload = request.get_json(silent=True) or {}
    machine = payload.get("machine", "").strip()
    message = payload.get("message", "").strip()

    if machine not in MACHINE_OPTIONS:
        return jsonify({"message": "机型选择无效。"}), 400

    if not message:
        return jsonify({"message": "留言不能为空。"}), 400

    result = pick_scene_and_food(machine, message)
    return jsonify(
        {
            "scene": result["scene"],
            "food": result["food"],
            "miss": result["miss"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
