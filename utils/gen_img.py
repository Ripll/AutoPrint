from PIL import ImageFont, Image, ImageDraw
from io import BytesIO


def get_image(msg):
    W, H = (300, 200)
    msg = str(msg)
    font = ImageFont.truetype('./utils/font.ttf', 50)
    im = Image.new("RGBA", (W, H), "white")
    draw = ImageDraw.Draw(im)
    w, h = font.getsize(msg)
    draw.text(((W-w)/2, (H-h)/2), msg, fill="black", font=font)
    imgByteArr = BytesIO()
    im.save(imgByteArr, format='PNG')

    return imgByteArr.getvalue()
