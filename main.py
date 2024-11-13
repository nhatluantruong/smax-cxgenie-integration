from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any
import httpx
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhook/smax")
async def handle_webhook(request: Request):
    try:
        # Get raw request body
        body = await request.body()
        logger.info(f"Raw request body: {body}")
        
        # Parse request body
        request_data = await request.json()
        logger.info(f"Parsed request: {request_data}")

        # Extract the message text
        message_text = request_data["messages"][0]["text"]
        logger.info(f"Extracted message: {message_text}")

        # Make request to CX Genie
        async with httpx.AsyncClient() as client:
            cxgenie_request = {
                "bot_id": "106e68cc-bb92-4368-a647-f63399802641",
                "content": message_text,
                "workspace_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3Jrc3BhY2VfaWQiOiJhMzQ5YzU0YS0yNTNmLTRiMWEtOTdhOC1kYjM3MjcxMzA1MjgiLCJpYXQiOjE3MzA3MDg0OTl9.WM99uh4EjHrgd1XJKhZwl-6nS_g8qJ35u-EGcWQVcRE"
            }
            
            logger.info(f"Sending to CX Genie: {cxgenie_request}")
            
            response = await client.post(
                "https://gateway.cxgenie.ai/api/v1/messages",
                json=cxgenie_request,
                timeout=30.0
            )
            
            logger.info(f"CX Genie response status: {response.status_code}")
            logger.info(f"CX Genie response body: {response.text}")
            
            if response.status_code == 200:
                genie_data = response.json()
                return {
                    "messages": [
                        {"text": genie_data.get("data", "No response content")}
                    ]
                }
            else:
                return {
                    "messages": [
                        {"text": "CX Genie connection error. Please try again."}
                    ]
                }

    except Exception as e:
        logger.error(f"Error details: {str(e)}", exc_info=True)
        return {
            "messages": [
                {"text": "Processing error. Please try again."}
            ]
        }

@app.get("/")
async def root():
    return {"message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
