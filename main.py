from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from scraper import get_amazon_product_data, get_amazon_price

import smtplib
from email.message import EmailMessage
from pydantic import BaseModel, EmailStr

# Поддержка Windows для корректной работы Playwright
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- FastAPI app ---
app = FastAPI(title="Amazon Scraper API", version="1.0")

# --- Включаем CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Модель тела запроса для email ---
class EmailRequest(BaseModel):
    email: EmailStr
    subject: str
    message: str


# --- Функция отправки письма через Gmail ---
def send_email(to_email: str, subject: str, message: str):
    gmail_user = "your_email@gmail.com"              # <- сюда свой ящик
    gmail_password = "your_app_password_here"        # <- сюда пароль приложения

    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_password)
        smtp.send_message(msg)


# --- Healthcheck ---
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
    try:
        send_email(data.email, data.subject, data.message)
        return {"status": "success", "message": "Email sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
