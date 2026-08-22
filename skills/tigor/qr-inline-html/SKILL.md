---
name: qr-inline-html
description: >
  Fit a fully functional HTML app into a scannable QR code using
  data:text/html URI scheme. Minimizes payload to keep QR version low
  enough for reliable phone-camera scanning.
---

# QR Code with Inline HTML

Fit a fully functional HTML app into a scannable QR code using `data:text/html,` URI scheme.

## Trigger
- "Put HTML in a QR code"
- "QR code game" / "QR code app"
- Any task requiring self-contained HTML delivered via QR scan

## Encoding Strategy (Critical)

**iOS Safari does NOT parse `%3C/%3E`-encoded data URIs.** It returns "no usable data found" / "no data available." You MUST use base64 for real-world phone scanning:

```python
import qrcode, base64
with open("app.html") as f:
    html = f.read().strip()

# Base64 — works on iOS Safari, Android Chrome, desktop
b64 = base64.b64encode(html.encode()).decode()
payload = f"data:text/html;base64,{b64}"

qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=6)
qr.add_data(payload)
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save("qrcode.png")
```

Base64 inflates ~1.37x and adds 22-byte prefix. `%3C/%3E` encoding is ~1.05x but **broken on iOS Safari** — do not use for production QR codes.

## QR Image Resolution

Generate at high resolution for reliable phone-camera scanning:
- `box_size=20, border=6` → ~2000×2000px image for v20 QR
- Low-res images (box_size=10, border=4) produce tiny pixels that phone cameras miss

## QR Version Targets

| Version | Size | Status |
|---------|------|--------|
| ≤v15 | ≤77×77 | Excellent — any phone camera |
| v16–v20 | 81–97 | Good — standard scannable |
| v21–v25 | 101–117 | Marginal — needs good lighting |
| ≥v26 | ≥121 | Poor — often unscannable |

Aim for ≤v20 for reliable scanning. Use EC=L to minimize version for a given payload.

## HTML Compression Rules

1. **Single line** — no newlines, no indentation
2. **Shortest variable names** — `b`, `d`, `f`, `x` not `snake`, `direction`
3. **No HTML tags that inflate** — prefer `canvas` over DOM elements (no CSS needed)
4. **Minimal attribute quotes** — `<canvas id=c>` not `<canvas id="c">`
5. **`x.fillStyle=0`** works instead of `"#000"` (1 byte vs 5)
6. **`x.fillStyle="0f0"`** works instead of `"#0f0"` (1 byte saved)
7. **No touch support** unless explicitly required — arrow keys save ~200 bytes
8. **No score display** unless explicitly required — `fillText()` costs ~20 bytes

## Common Pitfalls

- `data:text/html;charset=utf-8,` prefix adds 23 bytes for nothing — browsers default to UTF-8. Use `data:text/html;base64,` (22 bytes).
- **iOS Safari ignores `%3C/%3E` data URIs** — always use base64 encoding, not URL-encoding. Test on iPhone before shipping.
- Low-res QR images fail on phone cameras — use `box_size=20, border=6` for ~2000px output.
- Trailing newline in HTML file adds to payload — use `.strip()` when reading.
- `setInterval` with `()=>{}` saves vs `function(){}`.
- Modulo wrap-around (`%20`) for snake field edges saves wall-collision code.
- `x.fillStyle=0` works instead of `"#000"` (1 byte vs 5). `x.fillStyle="0f0"` saves vs `"#0f0"`.

## See Also

`references/qr-capacity-table.md` — full QR byte-mode capacity by version and EC level.
