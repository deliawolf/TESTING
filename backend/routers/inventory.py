from fastapi import APIRouter, HTTPException
from backend.modules.data_manager import DataManager
from pydantic import BaseModel
from typing import List, Optional, Dict

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

data_manager = DataManager()

class Device(BaseModel):
    name: str
    host: str
    device_type: str
    port: int = 22
    username: Optional[str] = None
    password: Optional[str] = None
    secret: Optional[str] = None
    credential_name: Optional[str] = None
    jumphost_profile: Optional[str] = None
    jumphost2_profile: Optional[str] = None
    tags: List[str] = []

@router.get("/devices")
async def get_devices():
    return data_manager.inventory

@router.post("/devices")
async def add_device(device: Device):
    # Convert Pydantic model to dict
    device_data = device.dict()
    name = device_data.pop('name')
    
    # Save to DataManager (correct parameter order)
    data_manager.save_device(
        name, 
        device_data['device_type'], 
        device_data['host'], 
        device_data['port'],
        device_data['credential_name'],
        device_data['jumphost_profile'],
        device_data['jumphost2_profile'],
        device_data['tags']
    )
    return {"message": f"Device {name} added successfully", "device": device}

@router.put("/devices/{name}")
async def update_device(name: str, device: Device):
    """Update an existing device"""
    if name not in data_manager.inventory:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Convert Pydantic model to dict
    device_data = device.dict()
    device_data.pop('name')  # Remove name from data since it's in the URL
    
    # Save updated device (overwrites existing) - correct parameter order
    data_manager.save_device(
        name, 
        device_data['device_type'], 
        device_data['host'], 
        device_data['port'],
        device_data['credential_name'],
        device_data['jumphost_profile'],
        device_data['jumphost2_profile'],
        device_data['tags']
    )
    return {"message": f"Device {name} updated successfully", "device": device}

@router.delete("/devices/{name}")
async def delete_device(name: str):
    if name in data_manager.inventory:
        data_manager.delete_device(name)
        return {"message": f"Device {name} deleted"}
    raise HTTPException(status_code=404, detail="Device not found")

from fastapi.responses import StreamingResponse
from fastapi import UploadFile, File
import csv
import io

@router.get("/export/csv")
async def export_inventory_csv():
    """Export inventory to CSV file"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'name', 'host', 'device_type', 'port', 
        'credential_name', 'jumphost_profile', 'jumphost2_profile', 'tags'
    ])
    
    # Write device data
    for name, device in data_manager.inventory.items():
        tags_str = ','.join(device.get('tags', []))
        writer.writerow([
            name,
            device.get('host', ''),
            device.get('device_type', ''),
            device.get('port', 22),
            device.get('credential_name', ''),
            device.get('jumphost_profile', ''),
            device.get('jumphost2_profile', ''),
            tags_str
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=inventory_export.csv"}
    )

@router.post("/import/csv")
async def import_inventory_csv(file: UploadFile = File(...)):
    """Import devices from CSV file"""
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        imported_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                name = row.get('name', '').strip()
                if not name:
                    continue
                
                # Parse tags
                tags_str = row.get('tags', '').strip()
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                
                # Save device
                data_manager.save_device(
                    name,
                    row.get('device_type', 'cisco_nxos').strip(),
                    row.get('host', '').strip(),
                    int(row.get('port', 22)),
                    row.get('credential_name', '').strip(),
                    row.get('jumphost_profile', '').strip() or None,
                    row.get('jumphost2_profile', '').strip() or None,
                    tags
                )
                imported_count += 1
            except Exception as e:
                errors.append(f"Row {imported_count + 1}: {str(e)}")
        
        return {
            "message": f"Imported {imported_count} device(s)",
            "imported": imported_count,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {str(e)}")
