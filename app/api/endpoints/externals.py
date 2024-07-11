from fastapi import APIRouter, Request
from app.schemas.requests import RSAEncryptRequest, RSADecryptRequest, ChatBotRequest
import requests
from fastapi import HTTPException
from app.core.config import get_settings


router = APIRouter()

@router.post("/rsa/encrypt", description="Encrypt RSA keys")
async def generate_rsa_keys(request: RSAEncryptRequest):
    try:
        response = requests.post(
            "https://5a7udyuiimjx3rngjs7lp4dxee0phmbl.lambda-url.us-east-1.on.aws/rsa/encrypt",
            json=request.dict()
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "Request sent", "response": response.json()}


@router.post("/rsa/decrypt", description="decrypt RSA keys")
async def generate_rsa_keys(request: RSADecryptRequest):
    try:
        response = requests.post(
            "https://5a7udyuiimjx3rngjs7lp4dxee0phmbl.lambda-url.us-east-1.on.aws/rsa/decrypt",
            json=request.dict()
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "Request sent", "response": response.json()}


@router.post("/bot", description="Send message to bot")
async def send_message_to_bot(request: ChatBotRequest):
    apiKey = get_settings().security.external_api_key.get_secret_value()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}"
    } 
    payload = {
        "model": "gpt-3.5-turbo-instruct",
        "prompt": request.prompt,
        "max_tokens": 2048,
        "temperature": 0.5
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print (e)
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "Request sent", "response": response.json()}

@router.get("/stocks/stock-summary/{symbol}", description="Get stock data")
async def get_stock_data(request: Request, symbol: str):
    try:
        url = f"https://stock-api-f7tht.ondigitalocean.app/api/stocks/stock-summary/{symbol}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    return {"status": "Request sent", "response": response.json()}