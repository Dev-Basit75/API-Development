
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEYS = {
    "KEY123",
    "KEY456",
    "KEY789"
}

@app.route("/process", methods=["POST"])
def process_text():

    api_key = request.headers.get("X-API-Key")

    if api_key not in API_KEYS:
        return jsonify({"error": "Unauthorized: Invalid or missing API key"}), 401

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Text is required"}), 400

    text = data["text"]

    return jsonify({
        "original_text": text,
        "processed_text": text.upper(),
        "message": "Text processed successfully"
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
