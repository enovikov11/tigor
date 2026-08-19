import qrcode

with open("snake.html") as f:
    html = f.read().strip()

# Minimal encoding: only < and > need escaping in data:text/html
payload = f"data:text/html,{html.replace('<', '%3C').replace('>', '%3E')}"

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
qr.add_data(payload)
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save("qrcode.png")

print(f"HTML: {len(html)} bytes -> encoded: {len(payload)} bytes")
print(f"QR: v{qr.version} ({qr.modules_count}x{qr.modules_count})")
