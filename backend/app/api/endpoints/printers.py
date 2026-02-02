from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import json
import uuid

from app.database import get_db
from app.models.printer import Printer
from app.services.print_service import print_service
from app.schemas.scan import PrintCommand

router = APIRouter()


@router.websocket("/ws/print/{client_id}")
async def websocket_print_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint для управления печатью"""
    await websocket.accept()

    # Регистрируем клиент
    print_service.register_client(client_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "register_printer":
                # Регистрируем принтер
                printer_name = message.get("printer_name", f"Printer_{client_id}")
                # Здесь можно сохранить в базу данных

            elif message.get("type") == "set_default":
                # Устанавливаем как принтер по умолчанию
                print_service.set_default_printer(client_id)
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "status",
                            "message": "Установлен как принтер по умолчанию",
                        }
                    )
                )

    except WebSocketDisconnect:
        print_service.unregister_client(client_id)


@router.get("/printers/")
async def get_available_printers():
    """Получает список доступных принтеров"""
    # В реальной системе здесь можно получить список принтеров из системы
    return {
        "printers": [
            {"id": "default", "name": "Принтер по умолчанию"},
            {"id": "label_printer", "name": "Принтер этикеток"},
        ]
    }


@router.post("/print/")
async def send_print_command(print_cmd: PrintCommand):
    """Отправляет команду на печать"""
    try:
        success = await print_service.send_print_command(print_cmd)
        if success:
            return {"message": "Команда печати отправлена"}
        else:
            raise HTTPException(
                status_code=400, detail="Не удалось отправить команду печати"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
