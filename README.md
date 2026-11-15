# CYNOCOR founder contact cards

Static site served at **https://cards.cynocor.com** (GitHub Pages).

## Edit a person
1. Edit `founders.json` (name, title, role, bio, phone, email, links, photo).
2. Put a new photo in `photos-src/` if needed.
3. Run `python3 build.py` (needs Python 3 and Pillow: `pip install pillow`).
4. Commit and push. Pages redeploys in about a minute.

`build.py` regenerates every card page, `.vcf` contact file, QR code, the directory page and `sitemap.xml`.

## Hosting
- `CNAME` contains `cards.cynocor.com`.
- DNS: `cards` CNAME record pointing to `cynocor.github.io`.
