from flask import Flask, render_template, request, jsonify
from core import get_bot_reply

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "")
    reply = get_bot_reply(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    # debug=True supaya mudah melihat error saat pengembangan
    app.run(debug=True)