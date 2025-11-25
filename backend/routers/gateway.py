from fastapi import APIRouter, HTTPException
from backend.modules.ssh_manager import GatewaySession
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/gateway",
    tags=["gateway"]
)

# Global gateway session (in a real app, this would be user-specific)
gateway_session: Optional[GatewaySession] = None

class GatewayConnect(BaseModel):
    jumphost1_profile: str
    jumphost2_profile: Optional[str] = None

@router.post("/connect")
async def connect_gateway(connection: GatewayConnect):
    """Establish a gateway session through jump hosts"""
    global gateway_session
    
    from backend.modules.data_manager import DataManager
    data_manager = DataManager()
    
    # Get jumphost1 config
    if connection.jumphost1_profile not in data_manager.jumphosts:
        raise HTTPException(status_code=404, detail=f"Jump host '{connection.jumphost1_profile}' not found")
    
    jh1 = data_manager.jumphosts[connection.jumphost1_profile]
    gw_config = {
        'host': jh1['host'],
        'port': jh1['port'],
        'username': jh1['username'],
        'password': jh1['password']
    }
    
    # Get jumphost2 config if provided
    jh2_config = None
    if connection.jumphost2_profile:
        if connection.jumphost2_profile not in data_manager.jumphosts:
            raise HTTPException(status_code=404, detail=f"Jump host '{connection.jumphost2_profile}' not found")
        jh2 = data_manager.jumphosts[connection.jumphost2_profile]
        jh2_config = {
            'host': jh2['host'],
            'port': jh2['port'],
            'username': jh2['username'],
            'password': jh2['password']
        }
    
    try:
        gateway_session = GatewaySession()
        gateway_session.connect(
            gw_config['host'],
            gw_config['port'],
            gw_config['username'],
            gw_config['password'],
            jumphost2_config=jh2_config
        )
        
        return {
            "status": "connected",
            "jumphost1": connection.jumphost1_profile,
            "jumphost2": connection.jumphost2_profile
        }
    except Exception as e:
        gateway_session = None
        raise HTTPException(status_code=500, detail=f"Failed to connect: {str(e)}")

@router.get("/status")
async def get_gateway_status():
    """Check if gateway session is active"""
    global gateway_session
    
    if gateway_session and gateway_session.is_active():
        return {
            "connected": True,
            "status": "active"
        }
    return {
        "connected": False,
        "status": "disconnected"
    }

@router.post("/disconnect")
async def disconnect_gateway():
    """Disconnect the gateway session"""
    global gateway_session
    
    if gateway_session:
        try:
            gateway_session.close()
            gateway_session = None
            return {"status": "disconnected"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")
    
    return {"status": "already disconnected"}

@router.get("/session")
async def get_session():
    """Get the current gateway session object for device connections"""
    global gateway_session
    return gateway_session

def get_gateway_session():
    """Get the current gateway session (for use by other routers)"""
    global gateway_session
    return gateway_session
