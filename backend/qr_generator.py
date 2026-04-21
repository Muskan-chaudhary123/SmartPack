# generate_qr.py

import qrcode

# Example parcel ID
parcel_id = "BOX123"
url = f"http://localhost:5000/scan?id={parcel_id}"  # Replace with your ngrok/render URL if deployed

qr = qrcode.make(url)
qr.save(f"{parcel_id}.png")

print(f"QR code saved as {parcel_id}.png")
