from fastapi import APIRouter, HTTPException
from backend.modules.data_manager import DataManager
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/jumphosts",
    tags=["jumphosts"]
)

data_manager = DataManager()

class JumpHost(BaseModel):
    name: str
    host: str
    username: str
    password: str
    port: int = 22

@router.get("")
async def get_jumphosts():
    return data_manager.jumphosts

@router.post("")
async def add_jumphost(jumphost: JumpHost):
    data_manager.save_jumphost(
        jumphost.name,
        jumphost.host,
        jumphost.username,
        jumphost.password,
        jumphost.port
    )
    return {"message": f"Jump host {jumphost.name} added successfully", "jumphost": jumphost}

@router.delete("/{name}")
async def delete_jumphost(name: str):
    if name in data_manager.jumphosts:
        data_manager.delete_jumphost(name)
        return {"message": f"Jump host {name} deleted"}
    raise HTTPException(status_code=404, detail="Jump host not found")
