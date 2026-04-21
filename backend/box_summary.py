from flask import Blueprint, render_template_string
from backend.database.models import SessionLocal, Box, Item

summary_bp = Blueprint("summary", __name__)

@summary_bp.route("/summary/<string:box_id>")
def show_summary(box_id):
    db = SessionLocal()
    try:
        box = db.query(Box).filter_by(id=box_id).first()
        if not box:
            return "Box not found", 404

        items = db.query(Item).filter_by(box_id=box_id).all()

        item_details = ""
        for item in items:
            item_details += f"<li>{item.name} – {item.length}x{item.width}x{item.height}, {item.weight}g, Fragile: {item.fragile}</li>"

        summary_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Box Summary</title>
            <style>
                body {{ font-family: Arial; background: #f4f4f4; padding: 20px; }}
                .box {{ background: white; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; }}
                h1 {{ color: #1e40af; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h1>📦 Box Summary</h1>
                <p><strong>Box ID:</strong> {box.id}</p>
                <p><strong>Box Type:</strong> {box.box_type}</p>
                <p><strong>Efficiency:</strong> {box.efficiency}%</p>
                <p><strong>CO₂ Saved:</strong> {box.co2_saved}g</p>
                <p><strong>Items:</strong></p>
                <ul>{item_details}</ul>
            </div>
        </body>
        </html>
        """
        return render_template_string(summary_html)
    finally:
        db.close()
