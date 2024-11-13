from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import os

app = FastAPI()

class Message(BaseModel):
    text: str

class WebhookRequest(BaseModel):
    messages: List[Dict[str, Any]]
    bot_id: str
    workspace_token: str

@app.get("/")
async def root():
    return {"message": "Service is running"}

@app.post("/webhook/smax")
async def handle_webhook(request: dict):
    try:
        # Print received request for debugging
        print("Received request:", request)
        
        # Extract message text
        message_text = request.get("messages", [{}])[0].get("text", "")
        
        # Prepare request for CX Genie
        cxgenie_request = {
            "bot_id": os.getenv("CXGENIE_BOT_ID"),
            "content": message_text,
            "workspace_token": os.getenv("CXGENIE_WORKSPACE_TOKEN")
        }
        
        # Send to CX Genie
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.getenv('CXGENIE_API_URL')}/api/v1/messages",
                json=cxgenie_request
            )
            response.raise_for_status()
            cxgenie_response = response.json()
            
            # Format response for Smax
            return {
                "messages": [
                    {"text": cxgenie_response.get("data", "No response from CX Genie")}
                ]
            }
            
    except Exception as e:
        print("Error:", str(e))
        return {
            "messages": [
                {"text": "Sorry, there was an error processing your request."}
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
