from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ScanBase(BaseModel):
    qr_data: str
    scan_type: str = "camera"
    printer_id: Optional[str] = None


class ScanCreate(ScanBase):
    pass


class ScanUpdate(BaseModel):
    printed: Optional[bool] = None
    printer_id: Optional[str] = None


class ScanInDB(ScanBase):
    id: int
    scanned_at: datetime
    printed: bool = False
    printed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScanResponse(ScanInDB):
    pass


class PrintCommand(BaseModel):
    qr_data: str
    printer_id: str
    client_id: Optional[str] = None


class QRScanRequest(BaseModel):
    image_data: str  # base64 encoded image
    client_id: Optional[str] = None
