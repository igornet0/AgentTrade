from datetime import datetime
import os 
from PIL import Image

from core.utils.tesseract_img_text import (str_to_datatime, 
                                           image_to_text, 
                                           preprocess_image)
from tests.test_settings import SettingsTest

settings = SettingsTest()

def test_str_to_datetime():
    # Примеры использования
    dates = [
        "26 Дек '23 20:19",
        "26 Дек '23",
        "2024/02/11",
        "2024/07/02 09:30:00"
    ]

    for date in dates:
        parsed_date = str_to_datatime(date)
        assert isinstance(parsed_date, datetime)


def test_image_to_text():
    imgs = [file for file in os.listdir(settings.PATH_IMG_DATE_TEST) if file.endswith((".png", ".jpg"))]
    assert len(imgs) == 4

    for img in imgs:
        main_part = img.split('.')[0]
        date_part, time_part = main_part.split('-')

        # Разбираем компоненты даты и времени
        year, month, day = map(int, date_part.split(':'))
        hour, minute, second = map(int, time_part.split(','))

        # Создаем объект datetime
        date_correct = datetime(year, month, day, hour, minute, second)
        img = Image.open(settings.BASE_DIR / settings.PATH_IMG_DATE_TEST / img)

        date_result = str_to_datatime(image_to_text(img))
        assert isinstance(image_to_text(img), str)
        assert date_result == date_correct
