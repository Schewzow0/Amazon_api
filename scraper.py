from playwright.sync_api import sync_playwright


def get_amazon_product_data(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            locale='en-US',
            timezone_id='America/New_York',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            geolocation={"longitude": -74.006, "latitude": 40.7128},  # Нью-Йорк
            permissions=["geolocation"],
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9"
            }
        )

        page = context.new_page()

        # Установка куки региона (США)
        page.goto("https://www.amazon.com", wait_until="domcontentloaded", timeout=20000)
        page.evaluate("""() => {
            document.cookie = 'lc-main=en_US; path=/;';
            document.cookie = 'i18n-prefs=USD; path=/;';
        }""")

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


def get_amazon_price(url: str) -> str | None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            locale='en-US',
            timezone_id='America/New_York',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            geolocation={"longitude": -74.006, "latitude": 40.7128},
            permissions=["geolocation"],
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9"
            }
        )

        page = context.new_page()

        page.goto("https://www.amazon.com", wait_until="domcontentloaded", timeout=20000)
        page.evaluate("""() => {
            document.cookie = 'lc-main=en_US; path=/;';
            document.cookie = 'i18n-prefs=USD; path=/;';
        }""")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_selector("#corePrice_feature_div .a-offscreen", timeout=10000)
            price_el = page.query_selector("#corePrice_feature_div .a-offscreen")
            price = price_el.inner_text().strip() if price_el else None
        except:
            price = None

        browser.close()
        return price
