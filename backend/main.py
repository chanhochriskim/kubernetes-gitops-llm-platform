"""Chat backend. Runs in "fake" mode by default so no API key or cost is needed.

To use a real model later, set MODEL_MODE=real and provide LLM_API_KEY, then fill in
call_real_model(). Nothing else in the app needs to change.

Metrics: every request is counted by method, route and status code, and timed. Prometheus
scrapes them from GET /metrics. That is what makes an HTTP error rate possible.
"""
import os
import socket
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel

app = FastAPI(title="chat-backend")

MODEL_MODE = os.getenv("MODEL_MODE", "fake")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")  # comes from a Kubernetes Secret, never from Git

REQUESTS = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency in seconds", ["method", "path"])


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = route.path if route else "unmatched"  # route template, not the raw URL (keeps labels few)
        if path != "/metrics":
            REQUESTS.labels(request.method, path, str(status)).inc()
            LATENCY.labels(request.method, path).observe(time.perf_counter() - start)


class ChatRequest(BaseModel):
    question: str


def call_real_model(question: str) -> str:
    # Placeholder for the real API call (added later, once there is an API key).
    raise NotImplementedError("real model mode is not implemented yet")


def generate_reply(question: str) -> str:
    if MODEL_MODE == "real":
        return call_real_model(question)
    return f"[fake model] You asked: {question!r}"


@app.get("/health")
def health():
    # Used by the Kubernetes readiness probe.
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/fail")
def fail():
    # Always returns 500. Only for testing the error-rate metric.
    return JSONResponse({"error": "deliberate failure"}, status_code=500)


@app.post("/chat")
def chat(req: ChatRequest):
    return {
        "answer": generate_reply(req.question),
        "mode": MODEL_MODE,
        "served_by": socket.gethostname(),  # the pod name, so we can see load spreading
    }
