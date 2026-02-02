from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanUpdate


def create_scan(db: Session, scan: ScanCreate) -> Scan:
    db_scan = Scan(
        qr_data=scan.qr_data, scan_type=scan.scan_type, printer_id=scan.printer_id
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan


def get_scan(db: Session, scan_id: int) -> Optional[Scan]:
    return db.query(Scan).filter(Scan.id == scan_id).first()


def get_scans(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Scan]:
    query = db.query(Scan)

    if start_date:
        query = query.filter(Scan.scanned_at >= start_date)
    if end_date:
        query = query.filter(Scan.scanned_at <= end_date)

    return query.order_by(desc(Scan.scanned_at)).offset(skip).limit(limit).all()


def update_scan(db: Session, scan_id: int, scan_update: ScanUpdate) -> Optional[Scan]:
    db_scan = get_scan(db, scan_id)
    if db_scan:
        for field, value in scan_update.dict(exclude_unset=True).items():
            if field == "printed" and value:
                setattr(db_scan, "printed_at", datetime.utcnow())
            setattr(db_scan, field, value)
        db.commit()
        db.refresh(db_scan)
    return db_scan


def delete_scan(db: Session, scan_id: int) -> bool:
    db_scan = get_scan(db, scan_id)
    if db_scan:
        db.delete(db_scan)
        db.commit()
        return True
    return False
