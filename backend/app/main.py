from fastapi import FastAPI, WebSocket

app = FastAPI(title="Kubernetes Cluster Clash Online")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    await ws.send_text("Welcome to Kubernetes Cluster Clash!")
    await ws.close()
