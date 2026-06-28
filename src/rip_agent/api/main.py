from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rip_agent.api.routes import router
from rip_agent.telemetry import setup_telemetry

setup_telemetry("rip-agent-api")

app = FastAPI(title="RIP-Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
