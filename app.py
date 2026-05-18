"""
SALSO WhatsApp Bot — Flask Web App
=====================================
Receives incoming WhatsApp messages via Twilio webhook,
processes them, and sends replies back.

Setup:
1. Install dependencies: pip install -r requirements.txt
2. Copy .env.example to .env and fill in your Twilio credentials
3. Run: python app.py
4. Expose with ngrok: ngrok http 5000
5. Configure Twilio WhatsApp sandbox webhook to your ngrok URL + /whatsapp
"""

import os
import re
import logging
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

from bot.handlers import handle_message

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")  # Twilio sandbox number

# Initialise Twilio client
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio."""
    try:
        # Extract message details from Twilio's POST
        wa_id = request.form.get("WaId", "").strip()
        profile_name = request.form.get("ProfileName", "").strip()
        message_body = request.form.get("Body", "").strip()

        if not wa_id:
            app.logger.warning("No WaId received")
            return str(MessagingResponse())

        app.logger.info(f"Message from {wa_id} ({profile_name}): {message_body[:80]}")

        # Process the message through our handler
        replies = handle_message(wa_id, profile_name, message_body)

        # Build TwiML response
        resp = MessagingResponse()
        for reply in replies:
            resp.message(reply)

        return str(resp)

    except Exception as e:
        app.logger.error(f"Webhook error: {e}", exc_info=True)
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again later.")
        return str(resp)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "SALSO WhatsApp Bot"})


@app.route("/", methods=["GET"])
def index():
    return (
        "<h1>SALSO WhatsApp Bot</h1>"
        "<p>Webhook endpoint: POST /whatsapp</p>"
        "<p>Health check: GET /health</p>"
        "<p>Configure this URL in your Twilio WhatsApp Sandbox settings.</p>"
    )


def send_whatsapp(to_number, message):
    """Send an outbound WhatsApp message (for proactive messaging)."""
    if not twilio_client:
        app.logger.warning("Twilio not configured. Cannot send message.")
        return False
    try:
        twilio_client.messages.create(
            body=message,
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{to_number}",
        )
        return True
    except Exception as e:
        app.logger.error(f"Failed to send message: {e}")
        return False


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.logger.info(f"Starting SALSO WhatsApp Bot on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
