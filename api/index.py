import time
import uuid

from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()

ALLOWED_ORIGINS = ["https://dash-s4pou1.example.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start

        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        return response


app.add_middleware(RequestIdMiddleware)


@app.get("/stats")
async def stats(values:str = Query(...)):
    nums = [int(x) for x in values.split(",") if x.strip().isdigit()]

    count = len(nums)
    total = sum(nums)

    return {
        "email": "25ds2000019@ds.study.iitm.ac.in",
        "count": count,
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / count,
    }

