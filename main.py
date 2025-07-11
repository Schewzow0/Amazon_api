from fastapi import FastAPI, Query
from scraper import get_amazon_product_data, get_amazon_price

# Поддержка Windows для корректной работы Playwright
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Инициализация FastAPI-приложения
app = FastAPI(title="Amazon Scraper API", version="1.0")


@app.get("/", tags=["Health"])
def root():
    """
    Проверка доступности API.
    """
    return {"message": "API is running!"}


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
