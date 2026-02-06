# // [SYSTEM_CHECK]: GODS_EYE COMMAND CENTER ONLINE
# // [CLASSIFICATION]: TACTICAL API SERVER
# // [STATUS]: AWAITING CONNECTIONS

"""
main.py - FastAPI Command Center for Mini God's Eye
Serves MJPEG video stream and detection logs via REST API.
"""

import atexit
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from vision_engine import VisionEngine


# // [GLOBAL]: Vision Engine instance
vision_engine: VisionEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    // [LIFECYCLE]: Application startup/shutdown handler
    Ensures proper resource management
    """
    global vision_engine
    
    # // [STARTUP]: Initialize Vision Engine
    print("[GODS_EYE] Initializing Vision Engine...")
    vision_engine = VisionEngine(
        camera_index=0,
        log_file="detection_history.csv"
    )
    print("[GODS_EYE] System Online - Awaiting Targets")
    
    yield  # // [RUNTIME]: Application is running
    
    # // [SHUTDOWN]: Cleanup resources
    print("[GODS_EYE] Initiating shutdown sequence...")
    if vision_engine:
        vision_engine.cleanup()
    print("[GODS_EYE] System Offline")


# // [INIT]: FastAPI Application
app = FastAPI(
    title="Mini God's Eye",
    description="Tactical Surveillance System - Real-time Human Detection",
    version="1.0.0",
    lifespan=lifespan
)

# // [CONFIG]: CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # // [NOTE]: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# // ============================================================
# // [ENDPOINTS]: API Routes
# // ============================================================

@app.get("/")
async def root():
    """
    // [ROUTE]: Health check endpoint
    """
    return {
        "system": "GODS_EYE",
        "status": "ONLINE",
        "message": "Tactical Surveillance System Active"
    }


@app.get("/video_feed")
async def video_feed():
    """
    // [ROUTE]: MJPEG Video Stream
    // [ACCESS]: GET /video_feed
    // [RETURNS]: Multipart JPEG stream of processed frames
    """
    return StreamingResponse(
        vision_engine.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/logs")
async def get_logs(limit: int = 50):
    """
    // [ROUTE]: Detection Logs
    // [ACCESS]: GET /logs?limit=50
    // [RETURNS]: JSON array of recent detection timestamps
    """
    logs = vision_engine.get_logs(limit=limit)
    return JSONResponse(content={
        "status": "success",
        "count": len(logs),
        "logs": logs
    })


@app.get("/status")
async def get_status():
    """
    // [ROUTE]: Current Detection Status
    // [ACCESS]: GET /status
    // [RETURNS]: Current detection state
    """
    status = vision_engine.get_status()
    return JSONResponse(content={
        "status": "success",
        "data": status
    })


# // ============================================================
# // [ENTRY]: Direct execution handler
# // ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║            M I N I   G O D ' S   E Y E                    ║
    ║         Tactical Surveillance System v1.0                 ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  [ENDPOINTS]                                              ║
    ║    • Video Feed:  http://localhost:8000/video_feed        ║
    ║    • Logs:        http://localhost:8000/logs              ║
    ║    • Status:      http://localhost:8000/status            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
