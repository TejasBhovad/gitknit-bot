from flask import Flask
from threading import Thread
import os
app = Flask('')
@app.route('/')
def home():
    return "Discord Bot is online!"
def run():
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT is not set
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    server = Thread(target=run)
    server.start()