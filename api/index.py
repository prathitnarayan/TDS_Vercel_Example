from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import pandas as pd

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins
    allow_methods=["POST"],     # allow POST requests
    allow_headers=["*"],        # allow all headers
)

# Load sample telemetry (replace with actual path)
df = pd.read_csv("telemetry.csv")  # assuming 'region', 'latency_ms', 'uptime' columns

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
            "avg_uptime": round(float(avg_uptime), 2),
            "breaches": int(breaches)
        }
    
    return JSONResponse(content=response)
