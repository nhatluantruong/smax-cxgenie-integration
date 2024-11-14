from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any
import httpx
import logging
import re
import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

def clean_html_response(text: str) -> str:
    """Clean HTML tags and format the text properly"""
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = html.unescape(clean_text)
    clean_text = ' '.join(clean_text.split())
    return clean_text

@app.post("/webhook/smax")
async def handle_webhook(request: Request):
    try:
        request_data = await request.json()
        logger.info(f"Parsed request: {request_data}")

        # Extract message and user info
        message_text = request_data["messages"][0]["text"]
        chat_user_info = request_data.get("chat_user_info", {})
        
        logger.info(f"Message from {chat_user_info.get('name', 'Unknown')}: {message_text}")

        async with httpx.AsyncClient() as client:
            cxgenie_request = {
                "bot_id": "106e68cc-bb92-4368-a647-f63399802641",
                "content": message_text,
                "chat_user_info": chat_user_info,
                "workspace_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3b3Jrc3BhY2VfaWQiOiJhMzQ5YzU0YS0yNTNmLTRiMWEtOTdhOC1kYjM3MjcxMzA1MjgiLCJpYXQiOjE3MzA3MDg0OTl9.WM99uh4EjHrgd1XJKhZwl-6nS_g8qJ35u-EGcWQVcRE"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = await client.post(
                "https://gateway.cxgenie.ai/api/v1/messages",
                json=cxgenie_request,
                headers=headers,
                timeout=30.0
            )
            
            # Log the complete request and response for debugging
            logger.info(f"CX Genie request: {cxgenie_request}")
            logger.info(f"CX Genie response status: {response.status_code}")
            logger.info(f"CX Genie response body: {response.text}")
            
            if response.status_code == 200:
                genie_data = response.json()
                clean_response = clean_html_response(genie_data.get("data", "No response content"))
                return {
                    "messages": [
                        {"text": clean_response}
                    ]
                }
            else:
                logger.error(f"CX Genie error response: {response.status_code} - {response.text}")
                return {
                    "messages": [
                        {"text": f"Error: {response.text}"}
                    ]
                }

    except Exception as e:
        logger.error(f"Error details: {str(e)}", exc_info=True)
        return {
            "messages": [
                {"text": f"Error: {str(e)}"}
            ]
        }

@app.get("/")
async def root():
    return {"message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
