# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import realistic_wordlist

app = Flask(__name__)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
@limiter.limit("5 per minute")
def generate():
    try:
        data = request.get_json()
        print("\n=== RECEIVED PAYLOAD ===")
        print(data)
        print("=== END PAYLOAD ===\n")
        
        result = realistic_wordlist.generate_web(data)
        return jsonify(result)
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 400

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)