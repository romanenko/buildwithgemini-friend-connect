"""Generate an animated demo GIF showing FriendConnect Chat UI, A2UI cards, and real generated kawaii artwork."""

import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Download real generated image if not present
REAL_IMG_PATH = "kawaii_real.jpg"
if not os.path.exists(REAL_IMG_PATH):
    try:
        url = "https://storage.googleapis.com/friend-connect-media-qwiklabs-gcp-03-75b4c3d63ad8/kawaii_pickleball_bf1af2.jpg"
        urllib.request.urlretrieve(url, REAL_IMG_PATH)
    except Exception as e:
        print(f"Warning: could not download image: {e}")

# Canvas dimensions
WIDTH = 800
HEIGHT = 560
BG_COLOR = (15, 23, 42)        # #0f172a
PANEL_COLOR = (30, 41, 59)     # #1e293b
BORDER_COLOR = (51, 65, 85)    # #334155
TEXT_WHITE = (248, 250, 252)   # #f8fafc
TEXT_MUTED = (148, 163, 184)   # #94a3b8
TEXT_BLUE = (56, 189, 248)     # #38bdf8
TEXT_PURPLE = (168, 85, 247)   # #a855f7
ACCENT_GRAD_1 = (236, 72, 153) # #ec4899
ACCENT_GRAD_2 = (139, 92, 246) # #8b5cf6


def get_font(size=14, bold=False):
    """Load default PIL font or DejaVuSans."""
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def create_base_canvas():
    """Create the base header and background container."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([(0, 0), (WIDTH, 50)], fill=PANEL_COLOR)
    draw.line([(0, 50), (WIDTH, 50)], fill=BORDER_COLOR, width=1)

    # Brand Title
    f_title = get_font(18, bold=True)
    draw.text((20, 14), "FriendConnect ✨", fill=ACCENT_GRAD_1, font=f_title)

    # Nav link
    f_nav = get_font(12)
    draw.text((WIDTH - 130, 16), "← Back to Home", fill=TEXT_MUTED, font=f_nav)

    # Input bar at bottom
    draw.rectangle([(0, HEIGHT - 60), (WIDTH, HEIGHT)], fill=PANEL_COLOR)
    draw.line([(0, HEIGHT - 60), (WIDTH, HEIGHT - 60)], fill=BORDER_COLOR, width=1)

    # Input field
    draw.rectangle([(20, HEIGHT - 48), (WIDTH - 120, HEIGHT - 12)], fill=BG_COLOR, outline=BORDER_COLOR, width=1)
    f_input = get_font(13)
    draw.text((32, HEIGHT - 35), "Say hi or tell FriendConnect what you love...", fill=TEXT_MUTED, font=f_input)

    # Send button
    draw.rectangle([(WIDTH - 105, HEIGHT - 48), (WIDTH - 20, HEIGHT - 12)], fill=ACCENT_GRAD_2)
    f_btn = get_font(13, bold=True)
    draw.text((WIDTH - 82, HEIGHT - 35), "Send", fill=TEXT_WHITE, font=f_btn)

    return img


def draw_chat_bubble(img, draw, x, y, text, is_user=False):
    """Draw a chat bubble."""
    f_msg = get_font(13)
    bbox = draw.textbbox((0, 0), text, font=f_msg)
    tw = bbox[2] - bbox[1]
    padding = 12
    h = 38

    if is_user:
        rect = [(WIDTH - 20 - tw - padding * 2, y), (WIDTH - 20, y + h)]
        draw.rectangle(rect, fill=ACCENT_GRAD_2)
        draw.text((WIDTH - 20 - tw - padding, y + 10), text, fill=TEXT_WHITE, font=f_msg)
    else:
        rect = [(x, y), (x + tw + padding * 2, y + h)]
        draw.rectangle(rect, fill=PANEL_COLOR, outline=BORDER_COLOR, width=1)
        draw.text((x + padding, y + 10), text, fill=TEXT_WHITE, font=f_msg)
    
    return y + h + 12


def draw_a2ui_profile_card(draw, x, y):
    """Draw the A2UI Profile Card after intake."""
    w = 420
    h = 130
    rect = [(x, y), (x + w, y + h)]
    draw.rectangle(rect, fill=PANEL_COLOR, outline=BORDER_COLOR, width=1)

    f_h1 = get_font(15, bold=True)
    f_body = get_font(12)
    f_badge = get_font(11, bold=True)

    draw.text((x + 16, y + 14), "YOUR INTEREST PROFILE", fill=TEXT_BLUE, font=f_h1)
    
    # Interests
    draw.text((x + 16, y + 42), "• Pickleball & Racket Sports", fill=TEXT_WHITE, font=f_body)
    draw.text((x + 16, y + 62), "• Cooking & Culinary Arts", fill=TEXT_WHITE, font=f_body)
    draw.text((x + 16, y + 82), "• Outdoor Recreation & Hiking", fill=TEXT_WHITE, font=f_body)

    # Score Badge
    draw.rectangle([(x + 220, y + 40), (x + 400, y + 70)], fill=(124, 58, 237))
    draw.text((x + 230, y + 48), "Highlight Score: 98%", fill=TEXT_WHITE, font=f_badge)

    return y + h + 16


def draw_a2ui_match_card(img, draw, x, y):
    """Draw the A2UI Match Found Card featuring real generated kawaii artwork."""
    w = 460
    h = 195
    rect = [(x, y), (x + w, y + h)]
    draw.rectangle(rect, fill=PANEL_COLOR, outline=ACCENT_GRAD_2, width=1)

    f_h1 = get_font(15, bold=True)
    f_body = get_font(12)
    f_link = get_font(13, bold=True)

    draw.text((x + 16, y + 14), "🎉 MATCH FOUND: SAM", fill=TEXT_PURPLE, font=f_h1)
    draw.text((x + 16, y + 38), "Shared Passion: Pickleball & Racket Sports", fill=TEXT_WHITE, font=f_body)

    # Embed real generated image
    img_w, img_h = 180, 115
    img_x, img_y = x + 16, y + 62
    
    if os.path.exists(REAL_IMG_PATH):
        try:
            k_img = Image.open(REAL_IMG_PATH).convert("RGB")
            k_img = k_img.resize((img_w, img_h), Image.Resampling.LANCZOS)
            img.paste(k_img, (img_x, img_y))
            # Border around image
            draw.rectangle([(img_x, img_y), (img_x + img_w, img_y + img_h)], outline=BORDER_COLOR, width=1)
        except Exception:
            draw.rectangle([(img_x, img_y), (img_x + img_w, img_y + img_h)], fill=(51, 65, 85))
    else:
        draw.rectangle([(img_x, img_y), (img_x + img_w, img_y + img_h)], fill=(51, 65, 85))

    # Pair link invitation
    draw.text((x + 210, y + 65), "Pair Link:", fill=TEXT_MUTED, font=f_body)
    draw.text((x + 210, y + 85), "/match/link-e1347ee", fill=TEXT_BLUE, font=f_link)

    draw.rectangle([(x + 210, y + 125), (x + 430, y + 158)], fill=ACCENT_GRAD_1)
    draw.text((x + 225, y + 134), "Open Live Chat UI →", fill=TEXT_WHITE, font=get_font(12, bold=True))

    return y + h + 16


def draw_match_header_banner(draw):
    """Draw the top celebratory banner."""
    rect = [(80, 60), (WIDTH - 80, 110)]
    draw.rectangle(rect, fill=(30, 41, 59), outline=ACCENT_GRAD_2, width=1)

    # Badge
    draw.rectangle([(95, 72), (210, 98)], fill=ACCENT_GRAD_1)
    draw.text((105, 78), "🎉 Match Found!", fill=TEXT_WHITE, font=get_font(11, bold=True))

    f_text = get_font(12)
    draw.text((225, 78), "Pair Link: /match/link-e1347ee", fill=TEXT_BLUE, font=f_text)

    # Rematch button
    draw.rectangle([(WIDTH - 260, 70), (WIDTH - 95, 100)], fill=ACCENT_GRAD_2)
    draw.text((WIDTH - 250, 78), "Find me another match 🔄", fill=TEXT_WHITE, font=get_font(10, bold=True))


def build_frames():
    """Generate the sequence of demo frames."""
    frames = []

    # Frame 1: User intake prompt
    img1 = create_base_canvas()
    d1 = ImageDraw.Draw(img1)
    draw_chat_bubble(img1, d1, 20, 75, "Hi! I love playing pickleball and cooking gourmet meals!", is_user=True)
    frames.append(img1)

    # Frame 2: Agent intake reply + A2UI Profile Card
    img2 = create_base_canvas()
    d2 = ImageDraw.Draw(img2)
    y2 = draw_chat_bubble(img2, d2, 20, 75, "Hi! I love playing pickleball and cooking gourmet meals!", is_user=True)
    y2 = draw_chat_bubble(img2, d2, 20, y2, "I love it! It sounds like your main vibe is Pickleball & Culinary Arts!", is_user=False)
    draw_a2ui_profile_card(d2, 20, y2)
    frames.append(img2)

    # Frame 3: User says "Find me friends"
    img3 = create_base_canvas()
    d3 = ImageDraw.Draw(img3)
    y3 = draw_chat_bubble(img3, d3, 20, 75, "I love it! It sounds like your main vibe is Pickleball & Culinary Arts!", is_user=False)
    y3 = draw_chat_bubble(img3, d3, 20, y3, "Find me friends", is_user=True)
    frames.append(img3)

    # Frame 4: Agent finds match + A2UI Match Card with real generated kawaii image + Celebratory Banner
    img4 = create_base_canvas()
    d4 = ImageDraw.Draw(img4)
    draw_match_header_banner(d4)
    y4 = draw_chat_bubble(img4, d4, 20, 125, "OK, let me find a new match for you!", is_user=False)
    draw_a2ui_match_card(img4, d4, 20, y4)
    frames.append(img4)

    # Save animated GIF
    out_path = "/home/user/build-with-gemini/friend-connect/demo.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=2200,  # 2.2 seconds per frame
        loop=0
    )
    print(f"Generated optimized demo GIF with real generated artwork at: {out_path}")


if __name__ == "__main__":
    build_frames()
