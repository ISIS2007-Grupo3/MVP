import os
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from requests import request as http_request
from app.models.whatsapp_webhook import WebhookPayload
from app.logic.send_message import send_message
from app.logic.whatsapp import handle_message

VERIFY_TOKEN = "ClaveSuperSecreta123NoNosRoben"  
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

router = APIRouter(prefix="/webhook")


@router.get("/")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        return PlainTextResponse(content="Error: token inválido", status_code=403)


@router.post("/")
async def obtener_mensaje(payload: WebhookPayload):
    print("LLEGÓ UN MENSAJE NUEVO")
    handle_message(payload, PHONE_NUMBER_ID)
    # mensaje = payload.get_mensaje()  
    # print(mensaje)
    # if mensaje:
    #     to = mensaje.from_
    #     print(mensaje.text.body)
    #     send_message(to, "holii", PHONE_NUMBER_ID)
    # data = {
    #     "messaging_product": "whatsapp",
    #     "to": to,
    #     "type": "text",
    #     "text": {
    #         "body": mensaje.__str__()
    #     }
    # }
    # url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    # headers = {
    #     "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    #     "Content-Type": "application/json"
    # }
    # resp = http_request("POST", url, headers=headers, json=data)
    # print("📤 Respuesta de Meta:", resp.status_code, resp.text)
    
    

    return {"status": "received"}
