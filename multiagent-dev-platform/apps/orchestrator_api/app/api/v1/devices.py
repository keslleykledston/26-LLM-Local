"""
Devices API - inventory and BGP peer queries
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from loguru import logger

from app.core.database import get_db
from app.models.device import Device
from app.services.crypto_service import CryptoService
from app.services.ssh_service import SSHService
from app.services.bgp_parsers import (
    parse_huawei_bgp_peer,
    parse_cisco_bgp_summary,
    parse_juniper_bgp_summary,
    parse_mikrotik_bgp,
)

router = APIRouter()


class DeviceCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=200)
    vendor: str = Field(..., min_length=2, max_length=50)
    platform: str = Field(..., min_length=2, max_length=50)
    host: str = Field(..., min_length=3, max_length=255)
    port: int = Field(default=22, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=100)
    password: Optional[str] = None
    enable_password: Optional[str] = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    vendor: str
    platform: str
    host: str
    port: int
    username: str
    has_password: bool
    has_enable_password: bool
    last_error: Optional[str]


class BgpQueryRequest(BaseModel):
    password: Optional[str] = None
    enable_password: Optional[str] = None
    port: Optional[int] = None


class BgpQueryResponse(BaseModel):
    device_id: int
    vendor: str
    platform: str
    raw: str
    peers: List[dict]


def _build_device_response(device: Device) -> DeviceResponse:
    return DeviceResponse(
        id=device.id,
        name=device.name,
        vendor=device.vendor,
        platform=device.platform,
        host=device.host,
        port=device.port,
        username=device.username,
        has_password=bool(device.password_encrypted),
        has_enable_password=bool(device.enable_password_encrypted),
        last_error=device.last_error,
    )


@router.post("/", response_model=DeviceResponse, status_code=201)
async def create_device(device_data: DeviceCreate, db: AsyncSession = Depends(get_db)):
    crypto = CryptoService()

    device = Device(
        name=device_data.name,
        vendor=device_data.vendor,
        platform=device_data.platform,
        host=device_data.host,
        port=device_data.port,
        username=device_data.username,
        password_encrypted=crypto.encrypt(device_data.password) if device_data.password else None,
        enable_password_encrypted=crypto.encrypt(device_data.enable_password)
        if device_data.enable_password
        else None,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)

    return _build_device_response(device)


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).order_by(Device.created_at.desc()))
    devices = result.scalars().all()
    return [_build_device_response(device) for device in devices]


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return _build_device_response(device)


@router.post("/{device_id}/bgp/peers", response_model=BgpQueryResponse)
async def query_bgp_peers(
    device_id: int,
    payload: BgpQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    crypto = CryptoService()
    password = payload.password or (crypto.decrypt(device.password_encrypted) if device.password_encrypted else "")
    enable_password = payload.enable_password or (
        crypto.decrypt(device.enable_password_encrypted) if device.enable_password_encrypted else ""
    )
    port = payload.port or device.port or 22

    if not password:
        raise HTTPException(status_code=400, detail="Password required for this device")

    ssh_service = SSHService()

    try:
        raw_output = await ssh_service.run_commands(
            platform=device.platform,
            host=device.host,
            port=port,
            username=device.username,
            password=password,
            enable_password=enable_password,
        )

        if device.password_encrypted is None and payload.password:
            device.password_encrypted = crypto.encrypt(payload.password)
        if device.enable_password_encrypted is None and payload.enable_password:
            device.enable_password_encrypted = crypto.encrypt(payload.enable_password)
        device.last_error = None
        await db.commit()

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f"Device query failed: {error_msg}")
        device.last_error = error_msg
        await db.commit()
        raise HTTPException(status_code=500, detail=error_msg)

    if device.platform == "huawei":
        peers = parse_huawei_bgp_peer(raw_output)
    elif device.platform in {"cisco_ios", "cisco_xe", "cisco_xr"}:
        peers = parse_cisco_bgp_summary(raw_output)
    elif device.platform == "juniper":
        peers = parse_juniper_bgp_summary(raw_output)
    elif device.platform in {"mikrotik_v6", "mikrotik_v7"}:
        peers = parse_mikrotik_bgp(raw_output)
    else:
        peers = []

    return BgpQueryResponse(
        device_id=device.id,
        vendor=device.vendor,
        platform=device.platform,
        raw=raw_output,
        peers=peers,
    )
