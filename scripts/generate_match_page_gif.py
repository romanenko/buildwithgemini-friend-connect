"""Generate an animated demo GIF showing the Match Connection Page and Contact Sharing flow."""

import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# Canvas dimensions
WIDTH = 800
HEIGHT = 580
BG_COLOR = (15, 23, 42)         # #0f172a
PANEL_COLOR = (30, 41, 59)      # #1e293b
BORDER_COLOR = (51, 65, 85)     # #334155
TEXT_WHITE = (248, 250, 252)    # #f8fafc
TEXT_MUTED = (148, 163, 184)    # #94a3b8
TEXT_BLUE = (56, 189, 248)      # #38bdf8
TEXT_PURPLE = (168, 85, 247)    # #a855f7
TEXT_GREEN = (34, 197, 94)      # #22c55e
ACCENT_GRAD_1 = (236, 72, 153)  # #ec4899
ACCENT_GRAD_2 = (139, 92, 246)  # #8b5cf6

REAL_IMG_PATH = "kawaii_real.jpg"


def get_font(size=14, bold=False):
    """Load default PIL font or DejaVuSans."""
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def draw_container_base():
    """Draw the outer container card for /match/link-e1347ee."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Card background
    cx1, cy1, cx2, cy2 = 120, 30, WIDTH - 120, HEIGHT - 30
    draw.rectangle([(cx1, cy1), (cx2, cy2)], fill=PANEL_COLOR, outline=BORDER_COLOR, width=1)

    # Badge
    draw.rectangle([(280, 45), (520, 72)], fill=ACCENT_GRAD_1)
    draw.text((295, 51), "MATCH CONFIRMED ✨", fill=TEXT_WHITE, font=get_font(11, bold=True))

    # Title & Names
    draw.text((230, 82), "You both love Pickleball!", fill=TEXT_WHITE, font=get_font(18, bold=True))
    draw.text((310, 110), "Alex & Sam", fill=TEXT_BLUE, font=get_font(14, bold=True))

    # Embedded Artwork
    img_w, img_h = 280, 150
    img_x, img_y = (WIDTH - img_w) // 2, 138

    if os.path.exists(REAL_IMG_PATH):
        try:
            k_img = Image.open(REAL_IMG_PATH).convert("RGB")
            k_img = k_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
            img.paste(k_img, (img_x, img_y))
            draw.rectangle([(img_x, img_y), (img_x + img_w, img_y + img_h)], outline=BORDER_COLOR, width=1)
        except Exception:
            draw.rectangle([(img_x, img_y), (img_x + img_w, img_y + img_h)], fill=(51, 65, 85))

    # Icebreaker box
    bx1, by1, bx2, by2 = 150, 300, WIDTH - 150, 355
    draw.rectangle([(bx1, by1), (bx2, by2)], fill=(15, 23, 42), outline=TEXT_BLUE, width=1)
    draw.text((bx1 + 12, by1 + 8), "BY THE WAY, QUESTION...", fill=TEXT_MUTED, font=get_font(10, bold=True))
    draw.text((bx1 + 12, by1 + 26), '"What is your favorite court or outdoor spot for a game?"', fill=TEXT_WHITE, font=get_font(11, bold=True))

    return img, draw


def build_match_page_frames():
    """Build the frame sequence for match_page_demo.gif."""
    frames = []

    # Frame 1: Match Page initial view with empty contact list
    img1, d1 = draw_container_base()
    # Contact methods header
    d1.text((150, 370), "Shared Contact Methods", fill=TEXT_WHITE, font=get_font(13, bold=True))
    d1.text((150, 395), "No contact details shared yet. Be the first below!", fill=TEXT_MUTED, font=get_font(11))

    # Form box
    d1.rectangle([(150, 425), (WIDTH - 150, 520)], fill=(15, 23, 42), outline=BORDER_COLOR, width=1)
    d1.text((165, 435), "Your Handle: Alex", fill=TEXT_WHITE, font=get_font(11))
    d1.text((165, 460), "Contact: e.g. IG: @alex_pickleball", fill=TEXT_MUTED, font=get_font(11))
    d1.rectangle([(165, 485), (WIDTH - 165, 510)], fill=ACCENT_GRAD_2)
    d1.text((280, 492), "Share Contact Details 🚀", fill=TEXT_WHITE, font=get_font(11, bold=True))
    frames.append(img1)

    # Frame 2: User fills out form
    img2, d2 = draw_container_base()
    d2.text((150, 370), "Shared Contact Methods", fill=TEXT_WHITE, font=get_font(13, bold=True))
    d2.text((150, 395), "No contact details shared yet. Be the first below!", fill=TEXT_MUTED, font=get_font(11))

    d2.rectangle([(150, 425), (WIDTH - 150, 520)], fill=(15, 23, 42), outline=TEXT_PURPLE, width=1)
    d2.text((165, 435), "Your Handle: Alex", fill=TEXT_WHITE, font=get_font(11, bold=True))
    d2.text((165, 460), "Contact: IG: @alex_pickleball_fan", fill=TEXT_BLUE, font=get_font(11, bold=True))
    d2.rectangle([(165, 485), (WIDTH - 165, 510)], fill=ACCENT_GRAD_1)
    d2.text((280, 492), "Submitting Contact Details...", fill=TEXT_WHITE, font=get_font(11, bold=True))
    frames.append(img2)

    # Frame 3: Contact shared successfully & visible in real time
    img3, d3 = draw_container_base()
    d3.text((150, 370), "Shared Contact Methods", fill=TEXT_WHITE, font=get_font(13, bold=True))
    
    # Shared contact pill
    d3.rectangle([(150, 392), (WIDTH - 150, 432)], fill=(51, 65, 85))
    d3.text((165, 402), "Alex:", fill=TEXT_PURPLE, font=get_font(12, bold=True))
    d3.text((220, 402), "IG: @alex_pickleball_fan", fill=TEXT_BLUE, font=get_font(12, bold=True))
    d3.text((WIDTH - 250, 402), "✓ Shared Live", fill=TEXT_GREEN, font=get_font(11, bold=True))

    d3.rectangle([(150, 445), (WIDTH - 150, 520)], fill=(15, 23, 42), outline=TEXT_GREEN, width=1)
    d3.text((165, 465), "🎉 Your contact info has been shared with Sam!", fill=TEXT_GREEN, font=get_font(13, bold=True))
    d3.text((165, 490), "Sam can now see your handle and reach out on Instagram!", fill=TEXT_MUTED, font=get_font(11))
    frames.append(img3)

    out_path = "/home/user/build-with-gemini/friend-connect/match_demo.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=2500,  # 2.5 seconds per frame
        loop=0
    )
    print(f"Generated match_demo.gif at: {out_path}")


if __name__ == "__main__":
    build_match_page_frames()
