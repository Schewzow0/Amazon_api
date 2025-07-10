from fastapi import FastAPI, Query
from scraper import get_amazon_product_data, get_amazon_price

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
