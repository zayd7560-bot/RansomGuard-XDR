from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Device, User
from app.security import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    devices = db.query(Device).filter(
        Device.user_id == current_user.id
    ).all()

    result = []

    now = datetime.utcnow()

    for device in devices:

        online = False

        if device.last_scan:

            online = (
                now - device.last_scan
            ).total_seconds() <= 15

        result.append({

            "device_id": device.id,

            "device_name": device.device_name,

            "os": device.os,

            "version": device.version,

            "status": "Online" if online else "Offline",

            "protection": device.protection,

            "realtime": device.realtime,

            "files_scanned": device.files_scanned,

            "threats_blocked": device.threats_blocked,
            
            "threat_level": device.threat_level,

            "last_seen": device.last_scan,

        })

    return {

        "total_devices": len(result),

        "online_devices": sum(
            1 for d in result if d["status"] == "Online"
        ),

        "devices": result,
    }