from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Blueprint
from flask_cors import CORS
from packaging_engine import suggest_box
from database.models import SessionLocal, Box, Item
import os
import qrcode
import time

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "your-secret-key"
CORS(app)

vendor_bp = Blueprint("vendor", __name__)

@app.route("/")
def landing_page():
    return render_template("landing.html")

@vendor_bp.route("/api/suggest_box", methods=["POST"])
def api_suggest_box():
    try:
        data = request.json
        items = data.get("items", [])
        result = suggest_box(items)

        session["suggested_box"] = result

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not name or not email or not password or not role:
            flash("Please fill in all fields.")
            return redirect(url_for('login'))

        if role == 'vendor':
            return redirect(url_for('vendor_dashboard'))
        elif role == 'delivery_agent':
            return redirect(url_for('delivery_dashboard'))

        flash("Invalid role selected.")
        return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/get-dimensions', methods=['POST'])
def get_dimensions():
    data = request.get_json()
    try:
        item_name = data.get('item_name', '').strip()
        length = float(data.get('length', 0))
        width = float(data.get('width', 0))
        height = float(data.get('height', 0))
        weight = float(data.get('weight', 0))
        fragile = bool(data.get('fragile', False))

        dimensions = {
            "item_name": item_name,
            "length_cm": length,
            "width_cm": width,
            "height_cm": height,
            "weight_g": weight,
            "fragile": fragile
        }

        return jsonify({"status": "success", "dimensions": dimensions}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


from flask import session
@app.route('/dashboard/vendor', methods=['GET', 'POST'])
def vendor_dashboard():
    suggested_box = session.get("suggested_box", {})
    parcel_id = None
    qr_path = None

    db = SessionLocal()

    if request.method == 'POST':
        result = suggested_box
        if not result:
            flash("No suggested box available.")
            return redirect(url_for("vendor_dashboard"))

        parcel_id = result.get("parcel_id")
        if not parcel_id:
            flash("Parcel ID missing.")
            return redirect(url_for("vendor_dashboard"))

        existing_box = db.query(Box).filter_by(id=parcel_id).first()
        if not existing_box:
            box = Box(
                box_id=parcel_id,
                box_type=result.get("box_type"),
                efficiency=result.get("efficiency"),
                co2_saved=result.get("co2_saved"),
            )
            db.add(box)
            db.commit()
            db.refresh(box)

            for item in result.get("items", []):
                db_item = Item(
                    name=item["name"],
                    length=item["length"],
                    width=item["width"],
                    height=item["height"],
                    weight=item["weight"],
                    fragile=item["fragile"],
                    box_id=box.id
                )
                db.add(db_item)
            db.commit()

        url = f"http://localhost:5000/scan?id={parcel_id}"
        qr = qrcode.make(url)
        save_dir = os.path.join("static", "assets", "qrcodes")
        os.makedirs(save_dir, exist_ok=True)
        qr_filename = f"{parcel_id}.png"
        qr.save(os.path.join(save_dir, qr_filename))
        qr_path = f"assets/qrcodes/{parcel_id}.png"

    return render_template(
        "vendor_dash.html",
        box_type=suggested_box.get("box_type"),
        efficiency=suggested_box.get("efficiency"),
        co2_saved=suggested_box.get("co2_saved"),
        parcel_id=parcel_id,
        qr_path=qr_path
    )


@app.route('/dashboard/delivery', methods=['GET', 'POST'])
def delivery_dashboard():
    db = SessionLocal()

    parcel_id = None
    latitude = None
    longitude = None
    box = None
    items = None
    qr_path = None

    if request.method == 'POST':
        parcel_id = request.form.get('parcel_id')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        box = db.query(Box).filter_by(id=parcel_id).first()

        items = box.items if box else []
        qr_path = f"assets/qrcodes/{parcel_id}.png"

    return render_template(
        "delivery_dash.html",
        parcel_id=parcel_id,
        latitude=latitude,
        longitude=longitude,
        box=box,
        items=items,
        qr_path=qr_path,
    )


@app.route("/scan")
def scan_qr():
    db = SessionLocal()
    box_id = request.args.get("id")
    box = db.query(Box).filter_by(box_id=box_id).first()  # ✅ not .get()
    items = box.items if box else []
    return render_template("scan_summary.html", box=box, items=items)


@app.route('/box-preview')
def box_preview():
    return render_template('3dbox.html')

app.register_blueprint(vendor_bp)

@app.route("/chatbot")
def chatbot_ui():
    return render_template("chatbot.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.get_json()
    user_input = data.get("message")

    if user_input == "__start__":
        return jsonify({
            "reply": "Hi there! 👋 I'm your SmartPack AI assistant. What would you like to explore?",
            "options": ["📦 Optimize Packaging", "📍 Track My Shipment", "🌱 Sustainability Tips", "📊 AI Insights", "💰 Pricing Info"]
        })

    elif user_input == "📦 Optimize Packaging":
        return jsonify({
            "reply": "What’s your main goal for optimizing?",
            "options": ["💰 Reduce Costs", "📏 Minimize Size", "♻️ Eco-Friendly Materials", "🚚 Improve Logistics"]
        })

    elif user_input == "📍 Track My Shipment":
        return jsonify({
            "reply": "To track your shipment, please provide your Parcel ID or scan the QR.",
            "options": ["🔍 Track by Parcel ID", "📱 Scan QR", "🔙 Back to Menu"]
        })

    elif user_input == "🌱 Sustainability Tips":
        return jsonify({
            "reply": "🌱 Use recyclable materials, minimize box size, and avoid over-packaging. Need more?",
            "options": ["♻️ More Tips", "📊 Carbon Calculator", "🔙 Back to Menu"]
        })

    elif user_input == "📊 AI Insights":
        return jsonify({
            "reply": "We offer insights on demand, cost, performance & logistics. Choose one:",
            "options": ["📈 Demand Forecast", "🎯 Cost Analysis", "📦 Box Performance", "🔙 Back to Menu"]
        })

    elif user_input == "💰 Pricing Info":
        return jsonify({
            "reply": "We offer flexible pricing:\n• Free Trial\n• Pay-per-Use\n• Custom Plans\nWould you like to connect with sales?",
            "options": ["📞 Talk to Sales", "📋 Get Quote", "🔙 Back to Menu"]
        })

    elif user_input == "🔙 Back to Menu":
        return jsonify({
            "reply": "Back to main menu. What would you like to explore?",
            "options": ["📦 Optimize Packaging", "📍 Track My Shipment", "🌱 Sustainability Tips", "📊 AI Insights", "💰 Pricing Info"]
        })

    else:
        return jsonify({
            "reply": "I’m still learning! Please choose an option from the menu.",
            "options": ["📦 Optimize Packaging", "📍 Track My Shipment", "🌱 Sustainability Tips", "📊 AI Insights", "💰 Pricing Info"]
        })


if __name__ == '__main__':
    app.run(debug=True)
