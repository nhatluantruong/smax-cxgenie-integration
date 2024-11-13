from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import httpx
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/webhook/smax")
async def handle_webhook(request: Dict[str, Any]):
    try:
        # Log incoming request
        logger.info(f"Received request: {request}")

        # Extract the message text
        message_text = request["messages"][0]["text"]
        bot_id = request["bot_id"]
        workspace_token = request["workspace_token"]

        # Create CX Genie request
        cxgenie_request = {
            "bot_id": bot_id,
            "content": message_text,
            "workspace_token": workspace_token
        }

        # Send request to CX Genie
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://gateway.cxgenie.ai/api/v1/messages",
                json=cxgenie_request
            )
            
            logger.info(f"CX Genie response: {response.text}")
            
            if response.status_code == 200:
                genie_data = response.json()
                return {
                    "messages": [
                        {"text": genie_data.get("data", "No response content")}
                    ]
                }
            else:
                logger.error(f"CX Genie error: {response.status_code} - {response.text}")
                return {
                    "messages": [
                        {"text": "Không thể kết nối với CX Genie. Vui lòng thử lại."}
                    ]
                }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        # Return a more specific error message
        return {
            "messages": [
                {"text": f"Có lỗi xảy ra: {str(e)}"}
            ]
        }

@app.get("/")
async def root():
    return {"message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
