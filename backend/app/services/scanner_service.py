import serial
import serial.tools.list_ports
from typing import Optional, List
import time


class ScannerService:
    """Сервис для работы со сканером Bestson S20-B"""

    @staticmethod
    def find_scanner() -> Optional[str]:
        """Находит подключенный сканер"""
        ports = serial.tools.list_ports.comports()

        for port in ports:
            # Ищем сканер Bestson S20-B по VID/PID или описанию
            if "Bestson" in port.description or "S20" in port.description:
                return port.device

        return None

    @staticmethod
    def read_from_scanner(
        port: str, baudrate: int = 9600, timeout: int = 1
    ) -> Optional[str]:
        """Читает данные со сканера"""
        try:
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                if ser.is_open:
                    # Ждем данные
                    time.sleep(0.1)
                    if ser.in_waiting > 0:
                        data = ser.readline().decode("utf-8").strip()
                        return data
        except Exception as e:
            print(f"Ошибка при чтении со сканера: {e}")

        return None

    @staticmethod
    def get_available_ports() -> List[str]:
        """Возвращает список доступных COM портов"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
