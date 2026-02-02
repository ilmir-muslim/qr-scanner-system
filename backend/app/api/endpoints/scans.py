from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import base64
from io import BytesIO

from app.database import get_db
from app.schemas.scan import ScanCreate, ScanResponse, QRScanRequest, PrintCommand
from app.crud import scan as crud_scan
from app.services.qr_service import QRService
from app.services.print_service import print_service
from app.utils.excel_export import ExcelExporter
from app.models.scan import Scan

router = APIRouter()


@router.post("/scan/", response_model=ScanResponse)
async def create_scan(
    scan: ScanCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Создает новое сканирование"""
    db_scan = crud_scan.create_scan(db=db, scan=scan)

    # Отправляем на печать в фоновом режиме
    if scan.printer_id:
        background_tasks.add_task(
            print_service.send_print_command,
            PrintCommand(qr_data=scan.qr_data, printer_id=scan.printer_id),
        )

    return db_scan


@router.post("/scan-from-image/", response_model=ScanResponse)
async def scan_from_image(
    request: QRScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Сканирует QR код из изображения"""
    try:
        # Сохраняем изображение
        file_path = QRService.save_uploaded_image(request.image_data)

        # Декодируем QR код
        with open(file_path, "rb") as f:
            image_data = f.read()

        qr_data = QRService.decode_qr_from_image(image_data)

        # Создаем запись
        db_scan = crud_scan.create_scan(
            db=db,
            scan=ScanCreate(
                qr_data=qr_data, scan_type="camera", printer_id=request.client_id
            ),
        )

        # Обновляем путь к файлу
        db_scan.file_path = file_path
        db.commit()

        # Отправляем на печать
        if request.client_id:
            background_tasks.add_task(
                print_service.send_print_command,
                PrintCommand(
                    qr_data=qr_data, printer_id="default", client_id=request.client_id
                ),
            )

        return db_scan

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Ошибка при обработке QR кода: {str(e)}"
        )


@router.post("/manual-scan/")
async def manual_scan(
    data: str, scan_type: str = "keyboard", db: Session = Depends(get_db)
):
    """Ручной ввод данных (для сканеров клавиатурного ввода)"""
    db_scan = crud_scan.create_scan(
        db=db, scan=ScanCreate(qr_data=data, scan_type=scan_type)
    )

    return {"message": "Скан сохранен", "scan": db_scan}


@router.get("/scans/", response_model=List[ScanResponse])
async def read_scans(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Получает список сканирований"""
    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    scans = crud_scan.get_scans(
        db=db, skip=skip, limit=limit, start_date=start_datetime, end_date=end_datetime
    )
    return scans


@router.get("/scans/{scan_id}", response_model=ScanResponse)
async def read_scan(scan_id: int, db: Session = Depends(get_db)):
    """Получает скан по ID"""
    db_scan = crud_scan.get_scan(db, scan_id=scan_id)
    if db_scan is None:
        raise HTTPException(status_code=404, detail="Скан не найден")
    return db_scan


@router.get("/export-excel/")
async def export_excel(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Экспортирует данные в Excel"""
    start_datetime = None
    end_datetime = None

    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    scans = crud_scan.get_scans(
        db=db,
        start_date=start_datetime,
        end_date=end_datetime,
        limit=10000,  # Максимальное количество записей
    )

    excel_data = ExcelExporter.export_scans_to_excel(scans)

    filename = f"qr_scans_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return {"filename": filename, "data": base64.b64encode(excel_data).decode("utf-8")}


@router.get("/generate-qr/{data}")
async def generate_qr(data: str, size: int = 10):
    """Генерирует QR код для данных"""
    qr_image = QRService.generate_qr_code(data, size)
    return {"qr_image": base64.b64encode(qr_image).decode("utf-8"), "data": data}
