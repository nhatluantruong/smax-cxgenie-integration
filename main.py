from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
import os

app = FastAPI()

class Message(BaseModel):
    text: Optional[str]

class WebhookRequest(BaseModel):
    messages: List[Dict]
    bot_id: str
    workspace_token: str

@app.get("/")
async def root():
    return {"message": "Service is running"}

@app.post("/webhook/smax")
async def handle_webhook(request: WebhookRequest):
    try:
        # Extract message text
        message_text = request.messages[0].get("text", "") if request.messages else ""
        
        # Prepare request for CX Genie
        cxgenie_request = {
            "bot_id": request.bot_id,
            "content": message_text,
            "workspace_token": request.workspace_token
        }
        
        # Send to CX Genie
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.getenv('CXGENIE_API_URL')}/api/v1/messages",
                json=cxgenie_request
            )
            response.raise_for_status()
            
            # Format response for Smax
            return {
                "messages": [
                    {"text": response.json().get("data", "No response from CX Genie")}
                ]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
