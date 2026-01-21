from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from app.agent import SimpleAgent

app = FastAPI(title="Agent MVP", version="1.0.0")
agent = SimpleAgent()

class AgentRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class AgentResponse(BaseModel):
    response: str
    status: str

my_obj = {"key": "value" }

@app.get("/")
async def root():
    return {
        "service": "Agent MVP",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/agent/process", response_model=AgentResponse)
async def process_message(request: AgentRequest):
    try:
        response = await agent.process(request.message, request.context)
        return AgentResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)