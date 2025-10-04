from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import pandas as pd

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data
df = pd.read_json("q-vercel-latency.json")
# Convert uptime_pct to decimal (0-1 range)
df["uptime"] = df["uptime_pct"] / 100

@app.post("/api/latency")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    
    response = {}
    for region in regions:
        data = df[df["region"] == region]
        avg_latency = data["latency_ms"].mean()
        p95_latency = np.percentile(data["latency_ms"], 95)
        avg_uptime = data["uptime"].mean()
        breaches = (data["latency_ms"] > threshold_ms).sum()
        
        response[region] = {
            "avg_latency": round(float(avg_latency), 2),
            "p95_latency": round(float(p95_latency), 2),
            "avg_uptime": round(float(avg_uptime), 4),
            "breaches": int(breaches)
        }
    
    return JSONResponse(content=response)