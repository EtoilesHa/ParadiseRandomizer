from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request, send_file

from random_tm import MACHINE_OPTIONS, pick_scene_and_food

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
INDEX_FILE = PROJECT_ROOT / "index.html"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


@app.route("/")
def serve_index():
    return send_file(INDEX_FILE)


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
