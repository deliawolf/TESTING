from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.modules.data_manager import DataManager

app = FastAPI(
    title="Network Automation API",
    description="Backend API for Network Automation Tool",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3003",  # Next.js Frontend (dynamic port)
    "http://localhost:3000",  # Next.js Frontend (fallback)
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Data Manager
data_manager = DataManager()

@app.get("/")
async def root():
    return {"message": "Network Automation API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Import and Include Routers
from backend.routers import inventory, jumphosts, credentials, batch, gateway
app.include_router(inventory.router)
app.include_router(jumphosts.router)
app.include_router(credentials.router)
app.include_router(batch.router)
app.include_router(gateway.router)
