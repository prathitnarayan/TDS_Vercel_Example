from fastapi import FastAPI, Response
from pydantic import BaseModel
import json
import numpy as np
from pathlib import Path

app = FastAPI()

class LatencyRequest(BaseModel):
    regions: list[str]
    threshold_ms: float

class RegionMetrics(BaseModel):
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int

def load_telemetry_data():
    data_path = Path(__file__).parent.parent / "q-vercel-latency.json"
    with open(data_path, 'r') as f:
        return json.load(f)

def add_cors_headers(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/")
async def root(response: Response):
    add_cors_headers(response)
    return {"status": "ok", "endpoint": "/api/latency"}

@app.options("/api/latency")
async def options_latency(response: Response):
    add_cors_headers(response)
    return {}

@app.post("/api/latency")
async def check_latency(request: LatencyRequest, response: Response) -> dict[str, RegionMetrics]:
    add_cors_headers(response)
    
    telemetry_data = load_telemetry_data()
    results = {}
    
    for region in request.regions:
        region_data = [r for r in telemetry_data if r["region"] == region]
        
        if not region_data:
            results[region] = RegionMetrics(
                avg_latency=0.0,
                p95_latency=0.0,
                avg_uptime=0.0,
                breaches=0
            )
            continue
        
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] / 100 for r in region_data]
        
        results[region] = RegionMetrics(
            avg_latency=round(float(np.mean(latencies)), 2),
            p95_latency=round(float(np.percentile(latencies, 95)), 2),
            avg_uptime=round(float(np.mean(uptimes)), 4),
            breaches=sum(1 for lat in latencies if lat > request.threshold_ms)
        )
    
    return results