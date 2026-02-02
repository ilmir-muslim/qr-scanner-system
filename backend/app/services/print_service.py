import asyncio
from typing import Dict, Optional
import json
from app.schemas.scan import PrintCommand
from app.services.qr_service import QRService


class PrintService:
    """Сервис управления печатью"""

    def __init__(self):
        self.print_clients: Dict[str, any] = {}  # client_id -> websocket
        self.default_printer: Optional[str] = None

    def register_client(self, client_id: str, websocket):
        """Регистрирует клиент для печати"""
        self.print_clients[client_id] = websocket
        print(f"Клиент зарегистрирован: {client_id}")

    def unregister_client(self, client_id: str):
        """Удаляет клиент"""
        if client_id in self.print_clients:
            del self.print_clients[client_id]
            print(f"Клиент удален: {client_id}")

    def set_default_printer(self, client_id: str):
        """Устанавливает клиент как принтер по умолчанию"""
        self.default_printer = client_id
        print(f"Принтер по умолчанию установлен: {client_id}")

    async def send_print_command(self, print_cmd: PrintCommand):
        """Отправляет команду на печать указанному клиенту"""
        client_id = print_cmd.client_id or self.default_printer

        if not client_id:
            raise ValueError("Не указан клиент для печати и нет принтера по умолчанию")

        if client_id not in self.print_clients:
            raise ValueError(f"Клиент {client_id} не подключен")

        websocket = self.print_clients[client_id]

        # Генерируем QR код
        qr_image_data = QRService.get_qr_code_base64(print_cmd.qr_data)

        # Создаем команду для печати
        print_data = {
            "type": "print",
            "qr_data": print_cmd.qr_data,
            "qr_image": qr_image_data,
            "printer_id": print_cmd.printer_id,
        }

        try:
            await websocket.send_text(json.dumps(print_data))
            print(f"Команда печати отправлена клиенту {client_id}")
            return True
        except Exception as e:
            print(f"Ошибка при отправке команды печати: {e}")
            return False


# Глобальный экземпляр сервиса печати
print_service = PrintService()
