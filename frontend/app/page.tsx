// // [SYSTEM_CHECK]: GODS_EYE COMMAND CENTER
// // [CLASSIFICATION]: MAIN DASHBOARD INTERFACE
// // [STATUS]: OPERATIONAL

"use client";

import { useEffect, useState, useCallback } from "react";

// // [TYPE]: Detection log entry structure
interface DetectionLog {
  timestamp: string;
  num_persons: number;
  confidence: number;
}

// // [TYPE]: Status response structure
interface SystemStatus {
  person_detected: boolean;
  frame_count: number;
  detections_count: number;
}

// // [CONFIG]: Backend API endpoints
const API_BASE = "https://capacity-spirits-donor-respiratory.trycloudflare.com";
const VIDEO_FEED_URL = `${API_BASE}/video_feed`;
const LOGS_URL = `${API_BASE}/logs`;
const STATUS_URL = `${API_BASE}/status`;

// // [POLL]: Refresh interval in milliseconds
const POLL_INTERVAL = 2000;

// // [COMPONENT]: Face Management Panel
function FaceManager() {
  const [faces, setFaces] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const fetchFaces = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/faces`);
      const data = await res.json();
      if (data.status === "success") {
        setFaces(data.faces);
      }
    } catch (e) {
      console.error("Failed to fetch faces", e);
    }
  }, []);

  useEffect(() => {
    fetchFaces();
  }, [fetchFaces]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    setIsUploading(true);
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      await fetch(`${API_BASE}/faces`, {
        method: "POST",
        body: formData,
      });
      await fetchFaces();
    } catch (e) {
      console.error("Upload failed", e);
    } finally {
      setIsUploading(false);
      // Reset input
      e.target.value = "";
    }
  };

  const handleDelete = async (name: string) => {
    if (!confirm(`Delete identity: ${name}?`)) return;
    try {
      await fetch(`${API_BASE}/faces/${name}`, {
        method: "DELETE",
      });
      await fetchFaces();
    } catch (e) {
      console.error("Delete failed", e);
    }
  };

  return (
    <aside className="tactical-border flex flex-col overflow-hidden h-2/5">
      <div className="p-3 border-b border-[#FF6300]/30 flex justify-between items-center bg-[#FF6300]/10">
        <h2 className="text-[#FF6300] text-xs uppercase tracking-widest">
          [DB] // KNOWN FACES
        </h2>
        <span className="text-xs text-gray-400">{faces.length} RECS</span>
      </div>

      <div className="flex-1 overflow-y-auto tactical-scroll p-2">
        {faces.length === 0 ? (
          <div className="text-center text-gray-600 text-xs py-4">
            NO RECORDS FOUND
          </div>
        ) : (
          <ul className="space-y-1">
            {faces.map((name) => (
              <li key={name} className="flex justify-between items-center text-xs p-2 bg-black border border-gray-800 hover:border-[#FF6300] group">
                <span className="text-gray-300 font-mono truncate max-w-[70%]">{name}</span>
                <button 
                  onClick={() => handleDelete(name)}
                  className="text-red-500 opacity-50 group-hover:opacity-100 hover:text-red-400 font-bold px-1"
                >
                  [DEL]
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="p-2 border-t border-[#FF6300]/30 bg-black">
        <label className={`block text-center text-xs p-2 border border-dashed border-[#FF6300] text-[#FF6300] cursor-pointer hover:bg-[#FF6300]/10 transition-colors ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}>
          {isUploading ? "UPLOADING..." : "+ UPLOAD IDENTITY"}
          <input 
            type="file" 
            accept="image/*" 
            className="hidden" 
            onChange={handleUpload}
            disabled={isUploading}
          />
        </label>
      </div>
    </aside>
  );
}

export default function CommandCenter() {
  // // [STATE]: Detection logs from backend
  const [logs, setLogs] = useState<DetectionLog[]>([]);
  
  // // [STATE]: System status
  const [status, setStatus] = useState<SystemStatus | null>(null);
  
  // // [STATE]: Connection status
  const [isConnected, setIsConnected] = useState(false);
  
  // // [STATE]: Current timestamp
  const [currentTime, setCurrentTime] = useState("");

  // // [FETCH]: Get detection logs from backend
  const fetchLogs = useCallback(async () => {
    try {
      const response = await fetch(`${LOGS_URL}?limit=50`);
      const data = await response.json();
      if (data.logs) {
        setLogs(data.logs.reverse()); // // [NOTE]: Newest first
      }
      setIsConnected(true);
    } catch {
      setIsConnected(false);
    }
  }, []);

  // // [FETCH]: Get current system status
  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(STATUS_URL);
      const data = await response.json();
      if (data.data) {
        setStatus(data.data);
      }
    } catch {
      setStatus(null);
    }
  }, []);

  // // [EFFECT]: Polling mechanism for real-time updates
  useEffect(() => {
    fetchLogs();
    fetchStatus();

    const logsInterval = setInterval(fetchLogs, POLL_INTERVAL);
    const statusInterval = setInterval(fetchStatus, POLL_INTERVAL);

    return () => {
      clearInterval(logsInterval);
      clearInterval(statusInterval);
    };
  }, [fetchLogs, fetchStatus]);

  // // [EFFECT]: Real-time clock
  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(new Date().toISOString().replace("T", " // ").slice(0, 22));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // // [FORMAT]: Convert ISO timestamp to display format
  const formatTimestamp = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleTimeString("en-US", { 
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  };

  return (
    <div className="min-h-screen bg-[#050505] p-4 scanlines">
      {/* // [HEADER]: System status bar */}
      <header className="mb-4 tactical-border p-3 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <h1 className="text-[#FF6300] text-lg uppercase tracking-wider font-bold">
            [GODS_EYE] // COMMAND CENTER
          </h1>
          <span className="text-xs text-gray-500">v1.0.0</span>
        </div>
        
        <div className="flex items-center gap-6 text-sm">
          {/* // [INDICATOR]: Connection status */}
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500 pulse" : "bg-red-500 blink"}`} />
            <span className={isConnected ? "text-green-500" : "text-red-500"}>
              {isConnected ? "LINKED" : "OFFLINE"}
            </span>
          </div>
          
          {/* // [CLOCK]: System time */}
          <span className="text-[#FF6300]">{currentTime}</span>
        </div>
      </header>

      {/* // [MAIN]: Grid layout - Viewport + Intel Panel */}
      <main className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-[calc(100vh-120px)]">
        
        {/* // [VIEWPORT]: Main video feed - 75% width */}
        <section className="lg:col-span-3 tactical-border viewfinder relative overflow-hidden bg-black">
          {/* // [LABEL]: Viewport header */}
          <div className="absolute top-0 left-0 right-0 z-30 bg-gradient-to-b from-black/80 to-transparent p-3">
            <div className="flex justify-between items-center">
              <span className="text-[#FF6300] text-xs uppercase tracking-widest">
                [MAIN_VIEWPORT] // LIVE FEED
              </span>
              <span className="text-xs text-gray-500">
                FRAME: {status?.frame_count?.toLocaleString() || "---"}
              </span>
            </div>
          </div>

          {/* // [STREAM]: Video feed from Python backend */}
          {/* // [CRITICAL]: Using standard <img> tag, NOT Next.js Image component */}
          <img
            src={VIDEO_FEED_URL}
            alt="Live Surveillance Feed"
            className="w-full h-full object-contain"
            style={{ imageRendering: "auto" }}
          />

          {/* // [STATUS]: Target acquisition indicator */}
          <div className="absolute bottom-0 left-0 right-0 z-30 bg-gradient-to-t from-black/80 to-transparent p-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 text-xs uppercase font-bold tracking-wider ${
                  status?.person_detected 
                    ? "bg-red-500/20 text-red-500 border border-red-500/50 blink" 
                    : "bg-cyan-500/20 text-cyan-500 border border-cyan-500/50"
                }`}>
                  {status?.person_detected ? "⚠ TARGET ACQUIRED" : "◎ SEARCHING..."}
                </span>
                {status?.person_detected && (
                  <span className="text-red-500 text-xs">
                    [{status.detections_count} TARGET{status.detections_count !== 1 ? "S" : ""}]
                  </span>
                )}
              </div>
              <span className="text-xs text-gray-500 uppercase">
                {isConnected ? "STREAM ACTIVE" : "NO SIGNAL"}
              </span>
            </div>
          </div>
        </section>

          {/* // [SIDEBAR]: Right column with stacked panels */}
        <div className="lg:col-span-1 flex flex-col gap-4 h-full"> 
          
          {/* // [PANEL 1]: Intel Logs (Top ~60%) */}
          <aside className="tactical-border flex flex-col overflow-hidden h-3/5">
            <div className="p-3 border-b border-[#FF6300]/30 flex-shrink-0">
              <h2 className="text-[#FF6300] text-xs uppercase tracking-widest">
                [INTEL_LOG] // DETECTIONS
              </h2>
              <p className="text-xs text-gray-500 mt-1">
                {logs.length} ENTRIES // POLLING: {POLL_INTERVAL / 1000}s
              </p>
            </div>

            <div className="flex-1 overflow-y-auto tactical-scroll p-2">
              {logs.length === 0 ? (
                <div className="text-center text-gray-600 text-xs py-8">
                  <p>NO DETECTIONS</p>
                  <p className="mt-1">AWAITING TARGETS...</p>
                </div>
              ) : (
                <ul className="space-y-1">
                  {logs.map((log, index) => (
                    <li
                      key={`${log.timestamp}-${index}`}
                      className="text-xs p-2 bg-[#FF6300]/5 border-l-2 border-[#FF6300]/50 hover:bg-[#FF6300]/10 transition-colors"
                    >
                      <div className="flex justify-between items-start">
                        <span className="text-[#FF6300]">
                          ▸ {formatTimestamp(log.timestamp)}
                        </span>
                        <span className="text-gray-500">
                          {Math.round(log.confidence * 100)}%
                        </span>
                      </div>
                      <p className="text-gray-400 mt-1">
                        DETECTED: {log.num_persons} PERSON{log.num_persons !== 1 ? "S" : ""}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {/* // [FOOTER]: Quick stats */}
            <div className="p-3 border-t border-[#FF6300]/30 flex-shrink-0 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div className="text-center p-2 bg-[#FF6300]/10">
                  <p className="text-gray-500">TOTAL</p>
                  <p className="text-[#FF6300] font-bold">{logs.length}</p>
                </div>
                <div className="text-center p-2 bg-[#FF6300]/10">
                  <p className="text-gray-500">STATUS</p>
                  <p className={status?.person_detected ? "text-red-500 font-bold" : "text-cyan-500"}>
                    {status?.person_detected ? "ACTIVE" : "CLEAR"}
                  </p>
                </div>
              </div>
            </div>
          </aside>

          {/* // [PANEL 2]: Face Database (Bottom ~40%) */}
          <FaceManager />
        </div>
      </main>

      {/* // [FOOTER]: System info bar */}
      <footer className="mt-4 tactical-border p-2 flex justify-between items-center text-xs text-gray-500">
        <span>SYSTEM: ONLINE // SURVEILLANCE ACTIVE</span>
        <span>BACKEND: {API_BASE}</span>
      </footer>
    </div>
  );
}
