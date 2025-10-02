import requests
import os

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

def send_message(to, message, phone_number_id):
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send message to {to}. Response: {response.status_code} {response.text}")
    else:
        print(f"Message sent to {to}.")
    
    print("📤 Respuesta de Meta:", response.status_code, response.text)