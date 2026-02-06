# 🎯 Mini God's Eye

> **Tactical Surveillance System** - Real-time human detection POC using YOLOv8 + FastAPI + Next.js

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple)

## 📋 Overview

A proof-of-concept surveillance system that:
- Captures live webcam feed
- Detects humans using YOLOv8n neural network
- Streams processed video with tactical HUD overlays
- Logs detection timestamps to CSV
- Displays real-time dashboard via web interface

## 🏗️ Architecture

```
┌─────────────────┐     MJPEG Stream      ┌─────────────────┐
│   Python        │ ──────────────────────▶│   Next.js       │
│   Backend       │                        │   Frontend      │
│   (FastAPI)     │ ◀──────────────────────│   (React)       │
│                 │     REST API           │                 │
└─────────────────┘                        └─────────────────┘
        │
        ▼
┌─────────────────┐
│   YOLOv8n       │
│   Detection     │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Webcam

### Backend Setup
```bash
cd Backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Dashboard:** http://localhost:3000
- **Video Stream:** http://localhost:8000/video_feed
- **Detection Logs:** http://localhost:8000/logs
- **System Status:** http://localhost:8000/status

## 📁 Project Structure

```
Gods eye/
├── Backend/
│   ├── main.py              # FastAPI server
│   ├── vision_engine.py     # YOLOv8 detection module
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    └── app/
        ├── page.tsx         # Command Center dashboard
        ├── layout.tsx       # Root layout
        └── globals.css      # Tactical styling
```

## ⚙️ Features

| Feature | Description |
|---------|-------------|
| **Frame Skipping** | YOLO runs every 5th frame for performance |
| **Tactical HUD** | Orange bounding boxes with "TARGET ACQUIRED" labels |
| **CSV Logging** | Persistent detection history |
| **Real-time Polling** | Dashboard updates every 2 seconds |
| **Status Indicators** | Visual feedback for target detection |

## 📜 License

MIT License - Use responsibly.

---

**[GODS_EYE] // SYSTEM ONLINE**
