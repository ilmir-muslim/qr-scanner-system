from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    qr_data: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    scan_type: Mapped[str] = mapped_column(
        String(50), default="camera"
    )  # camera/scanner
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    printed: Mapped[bool] = mapped_column(Boolean, default=False)
    printed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    printer_id: Mapped[str] = mapped_column(String(100), nullable=True)

    def __repr__(self):
        return f"<Scan(id={self.id}, data={self.qr_data[:50]})>"
