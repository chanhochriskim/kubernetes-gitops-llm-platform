"""Chat backend. Runs in "fake" mode by default so no API key or cost is needed.

To use a real model later, set MODEL_MODE=real and provide LLM_API_KEY, then fill in
call_real_model(). Nothing else in the app needs to change.
"""
import os
import socket

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="chat-backend")

MODEL_MODE = os.getenv("MODEL_MODE", "fake")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")  # comes from a Kubernetes Secret, never from Git


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


@app.post("/chat")
def chat(req: ChatRequest):
    return {
        "answer": generate_reply(req.question),
        "mode": MODEL_MODE,
        "served_by": socket.gethostname(),  # the pod name, so we can see load spreading
    }
