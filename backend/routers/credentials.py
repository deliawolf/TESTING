from fastapi import APIRouter, HTTPException
from backend.modules.data_manager import DataManager
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/credentials",
    tags=["credentials"]
)

data_manager = DataManager()

class Credential(BaseModel):
    name: str
    username: str
    password: str
    secret: Optional[str] = ""

@router.get("")
async def get_credentials():
    return data_manager.credentials

@router.post("")
async def add_credential(credential: Credential):
    data_manager.save_credential(
        credential.name,
        credential.username,
        credential.password,
        credential.secret
    )
    return {"message": f"Credential {credential.name} added successfully", "credential": credential}

@router.delete("/{name}")
async def delete_credential(name: str):
    if name in data_manager.credentials:
        data_manager.delete_credential(name)
        return {"message": f"Credential {name} deleted"}
    raise HTTPException(status_code=404, detail="Credential not found")
