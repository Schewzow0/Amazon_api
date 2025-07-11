from fastapi import FastAPI, Query
from scraper import get_amazon_product_data, get_amazon_price

# для работы под виндовс
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running!"}


@app.get("/product/")
def product(uri: str = Query(..., description="Amazon product URL")):
    result = get_amazon_product_data(uri)
    return result


@app.get("/price/")
def price(uri: str = Query(..., description="Amazon product URL")):
    price = get_amazon_price(uri)
    if price:
        return {"price": price}
    return {"error": "Price not found"}
