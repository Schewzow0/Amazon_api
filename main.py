from fastapi import FastAPI, Query
from scraper import get_amazon_product_data

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running!"}

@app.get("/product/")
def product(uri: str = Query(..., description="Amazon product URL")):
    result = get_amazon_product_data(uri)
    return result
