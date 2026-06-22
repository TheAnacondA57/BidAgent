from fastapi import FastAPI

from rip_agent.api.routes import router
from rip_agent.telemetry import setup_telemetry

setup_telemetry("rip-agent-api")

app = FastAPI(title="RIP-Agent API")
app.include_router(router)
