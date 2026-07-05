from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Device
from app.schemas import DeviceRegisterRequest, HeartbeatRequest
from app.security import get_current_user
from app.models import User

router = APIRouter(
    prefix="/device",
    tags=["Device"]
)


@router.post("/register")
def register_device(
    data: DeviceRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    device = db.query(Device).filter(
        Device.device_uuid == data.device_uuid,
        Device.user_id == current_user.id
    ).first()

    if device:

        device.device_name = data.device_name
        device.os = data.os
        device.version = data.version
        device.status = "Online"
        device.last_login = datetime.utcnow()

        db.commit()

        return {
            "message": "Device Updated",
            "device_id": device.id
        }

    new_device = Device(
        user_id=current_user.id,
        device_uuid=data.device_uuid,
        device_name=data.device_name,
        os=data.os,
        version=data.version,
        status="Online",
        last_login=datetime.utcnow()
    )

    db.add(new_device)

    db.commit()

    db.refresh(new_device)

    return {
        "message": "Device Registered",
        "device_id": new_device.id
    }
@router.post("/heartbeat")
def heartbeat(
    data: HeartbeatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    device = db.query(Device).filter(
        Device.id == data.device_id,
        Device.user_id == current_user.id
    ).first()

    if not device:
        return {
            "success": False,
            "message": "Device Not Found"
        }

    device.status = "Online"
    device.protection = data.protection
    device.realtime = data.realtime
    device.files_scanned = data.files_scanned
    device.threats_blocked = data.threats_blocked
    device.threat_level = data.threat_level
    device.last_scan = datetime.utcnow()
    

    db.commit()

    return {
        "success": True
    }