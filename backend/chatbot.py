from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    return render_template("chatbot.html")  # Make sure this file exists

@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.get_json()
    user_input = data.get("message")

    if user_input == "__start__":
        return jsonify({
            "reply": "Hi there! 👋 I'm your SmartPack AI assistant. What would you like to explore?",
            "options": ["📦 Optimize Packaging", "📍 Track My Shipment", "🌱 Sustainability Tips"]
        })

    elif user_input == "📦 Optimize Packaging":
        return jsonify({
            "reply": "What's your goal?",
            "options": ["💰 Reduce Costs", "📏 Minimize Size", "♻️ Eco-Friendly Materials"]
        })

    elif user_input == "🔙 Back to Menu":
        return jsonify({
            "reply": "Back to main menu!",
            "options": ["📦 Optimize Packaging", "📍 Track My Shipment"]
        })

    return jsonify({
        "reply": "I'm still learning!",
        "options": ["🔙 Back to Menu"]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5050)
