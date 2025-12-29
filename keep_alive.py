from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Ultra Forward Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def start():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
