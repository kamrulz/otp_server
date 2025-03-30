from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
otp_store: Dict[str, str] = {}

class SMSPayload(BaseModel):
    sender: str
    message: str
    timestamp: str
    sim: str
    mobile: str  # Your phone number
    device: str

@app.post("/sms-webhook")
async def receive_sms(sms: SMSPayload):
    # Extract OTP from message
    message = sms.message
    mobile = sms.mobile.strip()

    # Simple logic: pick first 6-digit number
    import re
    otp_match = re.search(r"\b\d{4,8}\b", message)
    if otp_match:
        otp = otp_match.group()
        otp_store[mobile] = otp
        return {"status": "success", "otp": otp}
    return JSONResponse(content={"error": "OTP not found in message"}, status_code=400)

@app.get("/get-otp")
def get_otp(mobile: str):
    otp = otp_store.get(mobile)
    if otp:
        return {"mobile": mobile, "otp": otp}
    return JSONResponse(content={"error": "OTP not found for this number"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
