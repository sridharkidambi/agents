"""
Sales and Marketing Email Module

Dependencies (install via: pip install -r requirements.txt):
- python-dotenv
- sendgrid
"""

from dotenv import load_dotenv
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import asyncio


load_dotenv(override=True)


def send_test_email(from_address: str, to_address: str) -> int:
    """Send a simple HTML test email via SendGrid. Returns HTTP status code."""
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        raise RuntimeError('SENDGRID_API_KEY not set in environment')

    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email(from_address)
    to_email = To(to_address)
    content = Content("text/html", _HTML_BODY)
    mail = Mail(from_email, to_email, "Chai Time at the Center!", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return response.status_code


_HTML_BODY = """
<html>
  <body style="font-family: Arial, sans-serif; background-color:#f4f4f4; padding:20px;">
    <div style="max-width:600px; margin:auto; background:#ffffff; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1); overflow:hidden;">
      <div style="background:#1a73e8; color:#ffffff; padding:24px; text-align:center;">
        <h1 style="margin:0; font-size:28px;">Chai Time at the Center!</h1>
      </div>
      <div style="padding:24px; color:#333333; line-height:1.6;">
        <p>Hi there,</p>
        <p>Let's meet up with Rohit, Vidyadhar, Avinash, Ram, and Ramalingam near the center for some chai!</p>
        <p style="text-align:center;">
          <a href="https://maps.google.com" style="display:inline-block; padding:12px 22px; background:#1a73e8; color:#ffffff; text-decoration:none; border-radius:6px;">Find the Location</a>
        </p>
        <p>Looking forward to catching up over chai in Chennai,<br/>See you soon!</p>
      </div>
    </div>
  </body>
</html>
"""


def main():
    from_addr = os.environ.get('EMAIL_FROM', 'sridharhere@gmail.com')
    to_addr = os.environ.get('EMAIL_TO', 'k.avinashca@gmail.com')
    status = send_test_email(from_addr, to_addr)
    print('Email send status:', status)


if __name__ == '__main__':
    main()