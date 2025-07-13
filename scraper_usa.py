from playwright.sync_api import sync_playwright, Page
from typing import Optional
import time

# --- Настройки эмуляции браузера ---
context_args = dict(
    locale='en-US',
    timezone_id='America/New_York',
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    geolocation={"longitude": -74.006, "latitude": 40.7128},  # Нью-Йорк
    permissions=["geolocation"],
    extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
)


def handle_additional_prompts(page: Page):
    """
    Обработка дополнительных окон Amazon: капча, подтверждение региона и пр.
    - Эмулирует клик по кнопке при капче
    - Нажимает "Continue shopping", если появляется
    """
    try:
        if page.locator("form[action='/errors/validateCaptcha']").is_visible(timeout=3000):
            print("[INFO] CAPTCHA detected. Attempting JS-based confirmation...")
            page.evaluate("""
                () => {
                    const btn = document.querySelector("form[action='/errors/validateCaptcha'] button[type='submit']");
                    if (btn) {
                        const evt = new MouseEvent('click', {
                            bubbles: true, cancelable: true, view: window
                        });
                        btn.dispatchEvent(evt);
                    }
                }
            """)
            page.wait_for_timeout(2000)
    except:
        pass

    try:
        if page.is_visible('button:has-text("Continue shopping")', timeout=3000):
            page.click('button:has-text("Continue shopping")')
            page.wait_for_timeout(1000)
    except:
        pass


def get_amazon_product_data(url: str) -> dict:
    """
    Получает полные данные товара Amazon: название, изображение и цена.
    Возвращает словарь с ключами: link, title, img, price
    """
    start = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**context_args)
        page = context.new_page()
        result = {"link": url, "title": None, "img": None, "price": None}

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            handle_additional_prompts(page)

            # Название товара
            try:
                result["title"] = page.locator("#productTitle").text_content(timeout=10000).strip()
            except:
                pass

            # Главное изображение товара
            try:
                result["img"] = page.query_selector("#landingImage").get_attribute("src")
            except:
                pass

            # Цена товара — из основного блока
            try:
                container = page.query_selector("#corePriceDisplay_desktop_feature_div")
                if container:
                    price_el = container.query_selector("span.aok-offscreen")
                    if price_el:
                        result["price"] = price_el.inner_text().strip().replace("$", "")
            except:
                pass

            # Альтернативный способ поиска цены
            if not result["price"]:
                try:
                    alt_price = page.query_selector("span.a-offscreen")
                    if alt_price:
                        text = alt_price.inner_text().strip()
                        if "$" in text:
                            result["price"] = text.replace("$", "")
                except:
                    pass

        except Exception as e:
            print("[ERROR] Failed to parse product:", e)

        context.close()
        browser.close()

    print(f"[INFO] Product parsed in {round(time.time() - start, 2)} sec: {url}")
    return result


def get_amazon_price(url: str) -> Optional[str]:
    """
    Получает только цену товара Amazon.
    Возвращает строку с ценой или None при ошибке.
    """
    start = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**context_args)
        page = context.new_page()
        price = None

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            handle_additional_prompts(page)

            # Явное ожидание появления блока с ценой
            try:
                page.wait_for_selector("#corePriceDisplay_desktop_feature_div", timeout=5000)
                container = page.query_selector("#corePriceDisplay_desktop_feature_div")
                if container:
                    price_el = container.query_selector("span.aok-offscreen")
                    if price_el:
                        price = price_el.inner_text().strip().replace("$", "")
            except:
                pass

            # Альтернативный span для поиска цены
            if not price:
                try:
                    alt_price = page.query_selector("span.a-offscreen")
                    if alt_price:
                        text = alt_price.inner_text().strip()
                        if "$" in text:
                            price = text.replace("$", "")
                except:
                    pass

        except Exception as e:
            print(f"[ERROR] Price parsing failed: {e}")

        context.close()
        browser.close()

    print(f"[INFO] Price parsed in {round(time.time() - start, 2)} sec: {url}")
    return price
