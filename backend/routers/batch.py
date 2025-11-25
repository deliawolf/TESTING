from fastapi import APIRouter, HTTPException
from backend.modules.data_manager import DataManager
from backend.modules.device_manager import DeviceConnection
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/batch",
    tags=["batch"]
)

data_manager = DataManager()

class BatchCommand(BaseModel):
    device_names: List[str]
    command: str

class BatchResult(BaseModel):
    device: str
    status: str
    output: str

@router.post("/execute")
async def execute_batch_command(batch: BatchCommand):
    """Execute a command on multiple devices"""
    results = []
    
    # Get current gateway session dynamically
    from backend.routers.gateway import get_gateway_session
    gateway_session = get_gateway_session()
    
    # Reload DataManager to get latest inventory
    fresh_data_manager = DataManager()
    
    # Check if gateway is connected
    if not gateway_session or not gateway_session.is_active():
        return [{
            "device": "Gateway",
            "status": "error",
            "output": "Gateway session not connected. Please connect to gateway first."
        }]
    
    for device_name in batch.device_names:
        if device_name not in fresh_data_manager.inventory:
            results.append({
                "device": device_name,
                "status": "error",
                "output": f"Device {device_name} not found in inventory"
            })
            continue
        
        device_data = fresh_data_manager.inventory[device_name]
        
        # Resolve credentials
        cred_name = device_data.get("credential_name")
        username = ""
        password = ""
        secret = ""
        if cred_name and cred_name in fresh_data_manager.credentials:
            cred = fresh_data_manager.credentials[cred_name]
            username = cred['username']
            password = cred['password']
            secret = cred.get('secret', '')
        else:
            results.append({
                "device": device_name,
                "status": "error",
                "output": f"Credentials '{cred_name}' not found"
            })
            continue
        
        # Execute command through gateway
        try:
            # Open a channel through the gateway to the device
            sock = gateway_session.open_channel(device_data['host'], device_data['port'])
            
            # Connect to device using the gateway channel
            device_connection = DeviceConnection()
            device_connection.connect(
                device_type=device_data['device_type'],
                host=device_data['host'],  # This is used for reference only when sock is provided
                port=device_data['port'],
                username=username,
                password=password,
                secret=secret,
                sock=sock  # Pass the gateway channel
            )
            
            output = device_connection.send_command(batch.command)
            device_connection.disconnect()
            
            results.append({
                "device": device_name,
                "status": "success",
                "output": output
            })
        except Exception as e:
            results.append({
                "device": device_name,
                "status": "error",
                "output": f"Connection/execution failed: {str(e)}"
            })
    
    return results

from fastapi.responses import FileResponse
import os
import zipfile
from datetime import datetime

@router.post("/download")
async def download_results(results: List[dict]):
    """Create a zip file with all device outputs as separate .txt files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"batch_results_{timestamp}.zip"
    zip_path = f"/tmp/{zip_filename}"
    
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for result in results:
                device_name = result['device']
                status = result['status']
                output = result['output']
                
                # Create filename: device_name_status.txt
                txt_filename = f"{device_name}_{status}.txt"
                
                # Write to zip
                zipf.writestr(txt_filename, output)
        
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type='application/zip',
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create zip: {str(e)}")

