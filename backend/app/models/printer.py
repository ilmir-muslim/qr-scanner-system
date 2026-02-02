from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base


class Printer(Base):
    __tablename__ = "printers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    printer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    printer_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    client_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # WebSocket client ID
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self):
        return f"<Printer(id={self.id}, name={self.printer_name})>"
