from backend.database.models import SessionLocal, Box, Item

def suggest_box(items):
    total_volume = 0
    max_length = max_width = max_height = 0

    for item in items:
        total_volume += item["length"] * item["width"] * item["height"]
        max_length = max(max_length, item["length"])
        max_width = max(max_width, item["width"])
        max_height = max(max_height, item["height"])

    box_length = int(max_length * 1.1)
    box_width = int(max_width * 1.1)
    box_height = int(max_height * 1.1)

    box_type = "Custom Box"
    efficiency = 90.0
    co2_saved = round((total_volume / 100000.0), 3)

    db = SessionLocal()
    try:
        new_box = Box(
            box_type=box_type,
            efficiency=efficiency,
            co2_saved=co2_saved,
            length=box_length,
            width=box_width,
            height=box_height
        )
        db.add(new_box)
        db.commit()
        db.refresh(new_box)

        for item in items:
            new_item = Item(
                name=item["name"],
                length=item["length"],
                width=item["width"],
                height=item["height"],
                weight=item["weight"],
                fragile=item["fragile"],
                box_id=new_box.id
            )
            db.add(new_item)

        db.commit()

        return {
            "box_type": box_type,
            "efficiency": efficiency,
            "co2_saved": co2_saved,
            "length": box_length,
            "width": box_width,
            "height": box_height,
            "parcel_id": new_box.id
        }

    except Exception as e:
        db.rollback()
        print("❌ DB Error:", e)
        raise
    finally:
        db.close()
