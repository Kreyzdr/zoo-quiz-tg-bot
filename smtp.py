from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP
import asyncio

from sekret.key import email, EMAIL_KEY

EMAIL = email
PWD = EMAIL_KEY

async def send_mail(msg,to,  subject = "От телебота"):
    message = MIMEMultipart()
    message["From"] = EMAIL
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(f"<html><body>{msg}</body></html>", "html", "utf-8"))

    smtp_client = SMTP(hostname="smtp.yandex.ru", port=465, use_tls=True)
    async with smtp_client:
        await smtp_client.login(EMAIL, PWD)
        await smtp_client.send_message(message)

if __name__ == "__main__":
    asyncio.run(send_mail('<h1>Привет</h1>', 'kirill23476kuleshov@yandex.ru'))