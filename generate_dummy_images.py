from PIL import Image, ImageDraw, ImageFont
import time
import os
import uuid
import random

IMAGE_HEIGHT = 720
IMAGE_WIDTH = 1280


IMAGE_FORMAT = "png"
IMAGE_FOLDER = "test_data/"
IMAGE_COUNT = 100
FPS = 12

FONT = "/usr/share/fonts/truetype/ubuntu/UbuntuMono-RI.ttf"
DELTA_HEIGHT_POS = 250
DELTA_WIDTH_POS = 550
DISPLAY_POSITION = (
    IMAGE_WIDTH // 2 - DELTA_WIDTH_POS,
    IMAGE_HEIGHT // 2 - DELTA_HEIGHT_POS,
)
FONT_SIZE = 30

STAGE = ["PreFlop", "Flop", "Turn", "River"]

CARD_VALUES = "23456789TJQKA"
CARD_SUITES = "CDHS"
CARDS = ["QS", "KS", "AS", "AH"]
DECK = [x + y for x in CARD_VALUES for y in CARD_SUITES]
ACTION = ["raise", "bet", "call", "check", "fold"]
BIG_BLIND = ["0.05", "0.02", "0.1"]
PLAYER_COUNT = list(range(7))

# --------------------------------------------------------------------------
# Generate time images
unix_timestamp = time.time()

# Create directories
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Generate camera images
for im in range(IMAGE_COUNT):

    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=(73, 109, 137))
    d = ImageDraw.Draw(img)

    display_text = f"""{unix_timestamp}: DUMMY IMAGE """

    font = ImageFont.truetype(FONT, FONT_SIZE)
    d.text(DISPLAY_POSITION, display_text, fill=(255, 255, 0), font=font)
    image_path = os.path.join(
        IMAGE_FOLDER,
        f"{uuid.uuid1()}_{im}_real_6_{random.choice(BIG_BLIND)}_{random.choice(DECK)}{random.choice(DECK)}_{random.choice(STAGE)}_{random.choice(DECK)}{random.choice(DECK)}{random.choice(DECK)}_{random.choice(PLAYER_COUNT)}_{random.uniform(0.01, 5.0)}_{random.choice(ACTION)}_{random.uniform(0.01, 5.0)}_.{IMAGE_FORMAT}",
    )
    img.save(image_path)

    # Increment time
    unix_timestamp += 1 / FPS
    print(f"Generated: {image_path}")
