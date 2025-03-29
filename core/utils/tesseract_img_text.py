from datetime import datetime
import re
from PIL import Image
import pytesseract
import cv2  # Для предобработки изображения (если нужно)
import numpy as np
# pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

months_rus_int = {"Дек": 12, "Ноя": 11, "Окт": 10, "Сен": 9, "Авг": 8, "Июл": 7, 
                "Июн": 6, "Май": 5, "Апр": 4, "Мар": 3, "Фев": 2, "Янв": 1}

RU_EN_timetravel = {"1Д":"1D", "4Ч":"4H", "1Ч":"1H", "30 минут":"30m", "5 минут":"5m", "15 минут":"15m"}
timetravel_seconds_int = {"1D":24*3600, "4H":4*3600, "1H":3600, "5m":5*60, "15m":15*60}

def preprocess_image(img: Image) -> Image:
    """
    BETA 
    Улучшает качество изображения для распознавания.

    Args:
        img (Image): Исходное изображение.

    Returns:
        Image: Обработанное изображение.
    """
    # Конвертация в grayscale
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Увеличение контраста
    img = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
    return Image.fromarray(img)

def image_to_text(img: Image) -> str:
        # bbox = img.getbbox()
        # img = img.crop(bbox).convert('L')
        # img = Image.eval(img, lambda x: 255 - x)
        # threshold = 150        # Пороговое значение для бинаризации (настройте по необходимости)
        # img = img.point(lambda p: p > threshold and 255)  # Бинаризация

        # Распознавание текста с указанием параметров
        # text = pytesseract.image_to_string(img, config='--psm 6 --oem 3 -l rus')
        # text = pytesseract.image_to_string(img, lang='rus')
        text = pytesseract.image_to_string(img, config='--psm 6', lang='rus')
        text = text.strip()
        return text

def first_format_date(date_str):
    # Первый формат: 26 Дек '23 20:19 или 26 Дек '23
    russian_date_pattern = r"(\d{1,2})\s+([А-Яа-я]{3})\s+'?(\d{2})\s*(\d{2}:\d{2})?"

    # Проверка первого формата
    match_russian = re.match(russian_date_pattern, date_str)
    if match_russian:
        day = match_russian.group(1)
        month_str = match_russian.group(2)
        year = match_russian.group(3)
        time_str = match_russian.group(4)

        month = months_rus_int[month_str]

        # Формирование даты
        if time_str:
            return datetime.strptime(f"{day} {month} 20{int(year)} {time_str}", "%d %m %Y %H:%M")
        else:
            return datetime.strptime(f"{day} {month} 20{int(year)}", "%d %m %Y")

def second_format_date(date_str: str) -> datetime:
    # Второй формат: 2024/02/11 или 2024/07/02 09:30:00
    date_str = date_str.replace("_", " ")
    date_str = date_str.strip()
    iso_date_pattern = r'(\d{4})/(\d{2})/(\d{2})(\s+(\d{2}:\d{2}:\d{2}))?'

    # Проверка второго формата
    match_iso = re.match(iso_date_pattern, date_str)

    if match_iso:
        year = match_iso.group(1)
        month = match_iso.group(2)
        day = match_iso.group(3)
        time_str = match_iso.group(5)

        if int(day) > 31:
            day = 31
        elif int(day) < 1:
            day = 1

        if int(month) > 12:
            month = 12
        elif int(month) < 1:
            month = 1

        # Формирование даты
        if time_str:
            return datetime.strptime(f"{year}-{month}-{day} {time_str}", "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")

def str_to_datatime(date_str):
    fist_format = first_format_date(date_str)
    if fist_format:
        return fist_format

    second_format = second_format_date(date_str)
    if second_format:
        return second_format
    
