from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_amazon_product_data, get_amazon_price

import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from pydantic import BaseModel, EmailStr

# Поддержка Windows для работы Playwright
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()

# --- FastAPI app ---
app = FastAPI(title="Amazon Scraper API", version="1.0")

# --- CORS для взаимодействия с фронтендом ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Структура email-сообщения для отправки ---
class EmailRequest(BaseModel):
    email: EmailStr
    subject: str
    message: str


# --- Отправка email через SMTP Gmail ---
def send_email(to_email: str, subject: str, message: str):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = gmail_user
    msg.set_content(message, subtype='plain', charset='utf-8')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_password)
        smtp.send_message(msg)


# --- Healthcheck: базовая проверка доступности API ---
@app.get("/", tags=["Health"])
def root():
    """
    Проверка доступности API.
    """
    return {"message": "API is running!"}


# --- GET /product ---
@app.get("/product/", tags=["Product Info"])
def product(uri: str = Query(..., description="Amazon product URL")):
    """
    Получить полную информацию о товаре Amazon:
    - Название
    - Изображение
    - Цена
    """
    result = get_amazon_product_data(uri)
    return result


# --- GET /price ---
@app.get("/price/", tags=["Product Info"])
def price(uri: str = Query(..., description="Amazon product URL")):
    """
    Получить только цену товара Amazon.
    Если цена не найдена — возвращается сообщение об ошибке.
    """
    result = get_amazon_price(uri)
    if result:
        return {"price": result}
    return {"error": "Price not found"}


# --- POST /send-email ---
@app.post("/send-email", tags=["Email"])
def send_email_handler(data: EmailRequest = Body(...)):
    """
        Отправить email-сообщение.
        Принимает тело запроса с email-адресом, темой и текстом письма.
        Возвращает статус отправки или сообщение об ошибке.
        """
    try:
        send_email(data.email, data.subject, data.message)
        return {"status": "success", "message": "Email sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
