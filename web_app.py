import os
from flask import Flask, render_template, request, jsonify
from core import get_bot_reply

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "")
        reply = get_bot_reply(user_message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)