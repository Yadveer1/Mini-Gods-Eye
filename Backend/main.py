# // [SYSTEM_CHECK]: GODS_EYE COMMAND CENTER ONLINE
# // [CLASSIFICATION]: TACTICAL API SERVER
# // [STATUS]: AWAITING CONNECTIONS

"""
main.py - FastAPI Command Center for Mini God's Eye
Serves MJPEG video stream and detection logs via REST API.
"""

import atexit
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import shutil
import os
from pathlib import Path
from typing import List

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


@app.get("/faces")
async def get_faces():
    """
    // [ROUTE]: List Known Faces
    // [ACCESS]: GET /faces
    // [RETURNS]: List of registered identities
    """
    faces = list(vision_engine.face_db.known_faces.keys())
    return JSONResponse(content={
        "status": "success",
        "count": len(faces),
        "faces": faces
    })


@app.post("/faces")
async def upload_face(file: UploadFile = File(...)):
    """
    // [ROUTE]: Upload New Face
    // [ACCESS]: POST /faces
    // [PAYLOAD]: multipart/form-data (image file)
    """
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
            
        # Create known_faces directory if needed
        save_dir = Path("known_faces")
        save_dir.mkdir(exist_ok=True)
        
        # Save file
        file_path = save_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Reload database
        vision_engine.reload_faces()
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Registered face: {file.filename}",
            "filename": file.filename
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/faces/{name}")
async def delete_face(name: str):
    """
    // [ROUTE]: Delete Face
    // [ACCESS]: DELETE /faces/{name}
    """
    try:
        # Find the file associated with the name
        target_path = None
        if name in vision_engine.face_db.known_faces:
            target_path = vision_engine.face_db.known_faces[name]
        
        if not target_path or not os.path.exists(target_path):
            raise HTTPException(status_code=404, detail="Face not found")
            
        # Delete file
        os.remove(target_path)
        
        # Reload database
        vision_engine.reload_faces()
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Deleted identity: {name}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
