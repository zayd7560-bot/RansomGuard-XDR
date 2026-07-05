from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str
    duress_password: str


class LoginRequest(BaseModel):

    username: str
    password: str


class TokenResponse(BaseModel):

    access_token: str
    token_type: str
class DeviceRegisterRequest(BaseModel):
    device_uuid: str
    device_name: str
    os: str
    version: str


class HeartbeatRequest(BaseModel):
    device_id: int
    protection: bool
    realtime: bool
    threats_blocked: int
    files_scanned: int
    threat_level: str