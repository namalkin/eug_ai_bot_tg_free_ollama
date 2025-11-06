from PIL import Image, ImageDraw, ImageFont
import datetime
from config import MSK
import os

def add_text_to_image(background, texts, text_color=(255, 255, 255)):
    draw = ImageDraw.Draw(background)
    for text, font_file, font_size, position in texts:
        font = ImageFont.truetype(font_file, font_size)
        draw.text(position, text, font=font, fill=text_color)
    return background

def add_rounded_overlay(background, overlay_image, position):
    default_avatar_path = "app/photo/default_avatar.jpg"
    if not os.path.exists(overlay_image):
        overlay_image = default_avatar_path
    try:
        overlay = Image.open(overlay_image).convert("RGBA")
        overlay = overlay.resize((80, 80))
        overlay = overlay.rotate(15, expand=True)
        background.paste(overlay, position, overlay)
    except Exception as e:
        pass
    return background

def get_time_and_date_info():
    current_time = datetime.datetime.now(MSK)
    hour = current_time.strftime("%H")
    minute = current_time.strftime("%M")
    day = current_time.strftime("%d")
    if day[0] == "0":
        day = day[1:]
    month = current_time.strftime("%B")
    day_of_week = current_time.strftime("%A")

    if int(hour) < 6:
        time_of_day = "ночь"
    elif int(hour) < 11:
        time_of_day = "утро"
    elif int(hour) < 18:
        time_of_day = "день"
    else:
        time_of_day = "вечер"

    months = {
        "January": "января",
        "February": "февраля",
        "March": "марта",
        "April": "апреля",
        "May": "мая",
        "June": "июня",
        "July": "июля",
        "August": "августа",
        "September": "сентября",
        "October": "октября",
        "November": "ноября",
        "December": "декабря"
    }

    days_of_week = {
        "Monday": "понедельник",
        "Tuesday": "вторник",
        "Wednesday": "среда",
        "Thursday": "четверг",
        "Friday": "пятница",
        "Saturday": "суббота",
        "Sunday": "воскресенье"
    }

    month_ru = months[month]
    day_of_week_ru = days_of_week[day_of_week]

    return {
        "hour": hour,
        "minute": minute,
        "day": day,
        "month_ru": month_ru,
        "day_of_week_ru": day_of_week_ru,
        "time_of_day": time_of_day
    }

def create_composite_image(background_image, texts, overlay_images, overlay_positions, add_time_info=False, coloric=(255,255,255)):
    background = Image.open(background_image)

    background = add_text_to_image(background, texts, text_color=coloric)

    for overlay_image, position in zip(overlay_images, overlay_positions):
        background = add_rounded_overlay(background, overlay_image, position)

    if add_time_info:
        time_info = get_time_and_date_info()
        texts_time = [
            (f"{time_info['hour']}:{time_info['minute']}", "app/photo/DSEraserCyr.ttf", 24, (20, 250)),
            (f"{time_info['day']} {time_info['month_ru']}", "app/photo/DSEraserCyr.ttf", 24, (20, 280)),
            (time_info['day_of_week_ru'], "app/photo/DSEraserCyr.ttf", 24, (20, 310)),
            (f"{time_info['time_of_day']}", "app/photo/DSEraserCyr.ttf", 24, (20, 340))
        ]
        background = add_text_to_image(background, texts_time)

    return background

def info_img_draw(txt, uname, overimg, ok, snum):
    background_image = "app/photo/background_info.jpg"
    texts = [
        (f"@{txt} ", "app/photo/Goose.ttf", 13, (200, 50)),
        (f"{uname}", "app/photo/Goose.ttf", 13, (220, 65)),
        (f"{ok}", "app/photo/Goose.ttf", 16, (230, 105)),
        (f"осталось", "app/photo/Goose.ttf", 16, (170, 150)),
        (f"запросов: ", "app/photo/Goose.ttf", 16, (190, 160)),
        (f"{snum}", "app/photo/Goose.ttf", 32, (280, 150))
    ]
    # Check if overlay image exists, else use default
    default_avatar_path = "app/photo/default_avatar.jpg"
    if not os.path.exists(overimg):
        overimg = default_avatar_path
    overlay_images = [
        f"{overimg}"
    ]
    overlay_positions = [
        (35, 80)
    ]
    result_image = create_composite_image(background_image, texts, overlay_images, overlay_positions, add_time_info=False, coloric=(87,49,29))
    result_image.save("app/result.jpg")
    return "app/result.jpg"

def passport_img_draw(one,two,frnd, ign, chts):
    background_image = "app/photo/background.jpg"
    texts = [
        ("Настроение: ", "app/photo/DSEraserCyr.ttf", 38, (20, 20)),
        (f"{one}", "app/photo/EmojiOne.ttf", 30, (300, 20)),
        (f"{two}", "app/photo/EmojiOne.ttf", 30, (330, 20)),
        (f"Друзей: {frnd}", "app/photo/DSEraserCyr.ttf", 63, (20, 50)),
        (f"Игнорит: {ign}", "app/photo/DSEraserCyr.ttf", 55, (20, 100)),
        (f"Частота общаемости: {chts}", "app/photo/DSEraserCyr.ttf", 24, (20, 145))
    ]

    overlay_images = []
    overlay_positions = []

    result_image = create_composite_image(background_image, texts, overlay_images, overlay_positions, add_time_info=True)
    result_image.save("app/result.jpg")
    return "app/result.jpg"
