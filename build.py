#!/usr/bin/env python3
"""Embed logo.png inside ipm-auth.html so the page is a single, self-contained file.

Captive-portal firewalls accept only the HTML page and cannot serve a separate
logo.png, so the logo is shrunk, reduced to a 64-colour palette and inlined as
a base64 data URI. The firewall caps the page at 60,000 characters, so the
build fails if the result is over that. Re-run after replacing logo.png:
    python3 build.py
"""
import base64
import io
import os
import re

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "ipm-auth.html")
LOGO = os.path.join(HERE, "logo.png")
LOGO_WIDTH = 440  # 2x the on-screen width (220px), sharp on retina phones
LOGO_COLORS = 64
MAX_CHARS = 60000  # firewall limit for the custom HTML page

img = Image.open(LOGO).convert("RGBA")
img = img.resize((LOGO_WIDTH, round(img.height * LOGO_WIDTH / img.width)), Image.LANCZOS)
img = img.quantize(colors=LOGO_COLORS, method=Image.FASTOCTREE)
buf = io.BytesIO()
img.save(buf, "PNG", optimize=True)
data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

html = open(PAGE, encoding="utf-8").read()
# Matches both the plain src="logo.png" and a previously embedded data URI
pattern = r'(<div id="company-logo"><img src=")[^"]*(")'
html, count = re.subn(pattern, lambda m: m.group(1) + data_uri + m.group(2), html)
if count != 1:
    raise SystemExit('Could not find <div id="company-logo"><img src="..."> in ipm-auth.html')

if len(html) > MAX_CHARS:
    raise SystemExit(f"Page would be {len(html)} characters, over the {MAX_CHARS} limit; "
                     "lower LOGO_WIDTH or LOGO_COLORS")

with open(PAGE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Embedded logo into {PAGE}: {len(html)} characters (limit {MAX_CHARS})")
