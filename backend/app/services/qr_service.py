import qrcode
from io import BytesIO
import base64
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
from pathlib import Path
from datetime import datetime
from app.config import settings


class QRService:
    @staticmethod
    def generate_qr_code(data: str, size: int = None) -> bytes:
        """Генерирует QR код из данных"""
        if size is None:
            size = settings.QR_CODE_SIZE

        qr = qrcode.QRCode(
            version=settings.QR_CODE_VERSION,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    @staticmethod
    def decode_qr_from_image(image_data: bytes) -> str:
        """Декодирует QR код из изображения"""
        # Преобразуем bytes в numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        # Декодируем QR код
        decoded_objects = decode(img)

        if decoded_objects:
            return decoded_objects[0].data.decode("utf-8")
        raise ValueError("QR код не найден на изображении")

    @staticmethod
    def save_uploaded_image(image_data: str) -> str:
        """Сохраняет загруженное изображение (base64) на диск"""
        # Создаем директорию если не существует
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"qr_scan_{timestamp}.png"
        filepath = upload_dir / filename

        # Декодируем base64 и сохраняем
        if "," in image_data:
            image_data = image_data.split(",")[1]

        img_data = base64.b64decode(image_data)

        with open(filepath, "wb") as f:
            f.write(img_data)

        return str(filepath)

    @staticmethod
    def get_qr_code_base64(data: str) -> str:
        """Возвращает QR код в формате base64"""
        qr_image = QRService.generate_qr_code(data)
        return base64.b64encode(qr_image).decode("utf-8")
