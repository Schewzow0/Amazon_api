from playwright.sync_api import sync_playwright

def get_amazon_product_data(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        result = {"link": url}

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)

            # Цена
            try:
                page.wait_for_selector("#corePrice_feature_div .a-offscreen", timeout=10000)
                price_el = page.query_selector("#corePrice_feature_div .a-offscreen")
                result["price"] = price_el.inner_text().strip() if price_el else None
            except:
                result["price"] = None

            # Картинка
            try:
                img_el = page.query_selector("#landingImage")
                result["img"] = img_el.get_attribute("src") if img_el else None
            except:
                result["img"] = None

            # Название
            try:
                title_el = page.query_selector("#productTitle")
                result["title"] = title_el.inner_text().strip() if title_el else None
            except:
                result["title"] = None

        except:
            result.update({"price": None, "img": None, "title": None})

        browser.close()
        return result
