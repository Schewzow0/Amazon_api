from playwright.sync_api import sync_playwright, Page
from typing import Optional
import time


# Настройки эмуляции пользователя из США
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
    Обрабатывает капчи и подтверждения (например, 'Continue shopping').
    В случае появления кнопки — вызывает принудительное нажатие через JS.
    """
    try:
        if page.locator("form[action='/errors/validateCaptcha']").is_visible(timeout=3000):
            print("[INFO] CAPTCHA detected. Attempting manual button press...")

            page.evaluate("""
                () => {
                    const btn = document.querySelector("form[action='/errors/validateCaptcha'] button[type='submit']");
                    if (btn) {
                        const evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        btn.dispatchEvent(evt);
                    }
                }
            """)
            page.wait_for_timeout(2000)
            return
    except Exception as e:
        print(f"[DEBUG] CAPTCHA handling failed: {e}")

    try:
        if page.is_visible('button:has-text("Continue shopping")', timeout=3000):
            page.click('button:has-text("Continue shopping")')
            page.wait_for_timeout(1000)
    except:
        pass


def set_region_zip(page: Page) -> bool:
    """
    Пытается сменить регион прямо на странице товара.
    Возвращает True, если регион был успешно установлен.
    """
    try:
        page.evaluate("""() => {
            document.cookie = 'lc-main=en_US; path=/;';
            document.cookie = 'i18n-prefs=USD; path=/;';
        }""")

        page.wait_for_selector('input[data-action-type="SELECT_LOCATION"]', timeout=5000)
        page.click('input[data-action-type="SELECT_LOCATION"]', force=True)
        page.wait_for_timeout(1000)

        page.fill("input#GLUXZipUpdateInput", "10001")
        page.press("input#GLUXZipUpdateInput", "Enter")
        page.wait_for_timeout(1500)

        try:
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)
        except:
            pass

        return True
    except Exception as e:
        print("[ERROR] Failed to set region:", e)
        return False


def get_amazon_product_data(url: str) -> dict:
    """
    Получает данные о товаре Amazon: цена, изображение и заголовок.
    """
    start = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(**context_args)
        page = context.new_page()

        result = {"link": url, "title": None, "img": None, "price": None}

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            handle_additional_prompts(page)

            # Меняем регион на странице товара
            if not set_region_zip(page):
                return {"error": "Region selection failed. Try again later."}

            handle_additional_prompts(page)

            # Заголовок
            try:
                page.wait_for_selector("#productTitle", timeout=10000)
                result["title"] = page.query_selector("#productTitle").inner_text().strip()
            except:
                result["title"] = None

            # Изображение
            try:
                page.wait_for_selector("#landingImage", timeout=10000)
                result["img"] = page.query_selector("#landingImage").get_attribute("src")
            except:
                result["img"] = None

            # Цена
            try:
                # Находим контейнер с основной ценой (всегда в карточке товара)
                container = page.query_selector("#corePriceDisplay_desktop_feature_div")
                if container:
                    price_el = container.query_selector("span.aok-offscreen")
                    if price_el:
                        result["price"] = price_el.inner_text().strip().replace("$", "")
                    else:
                        result["price"] = None
                else:
                    result["price"] = None
            except Exception as e:
                print(f"[DEBUG] Ошибка при извлечении цены: {e}")
                result["price"] = None







        except Exception as e:
            print("[ERROR] Failed to parse product:", e)

        context.close()
        browser.close()

    print(f"[INFO] Parsed in {round(time.time() - start, 2)} sec: {url}")
    return result


def get_amazon_price(url: str) -> Optional[str]:
    """
    Получает только цену товара Amazon.
    """
    start = time.time()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**context_args)
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            handle_additional_prompts(page)

            if not set_region_zip(page):
                return None

            handle_additional_prompts(page)

            page.wait_for_selector("#corePrice_feature_div .a-offscreen", timeout=10000)
            price_el = page.query_selector("#corePrice_feature_div .a-offscreen")
            price = price_el.inner_text().strip().replace("$", "") if price_el else None
        except:
            price = None

        context.close()
        browser.close()

    print(f"[INFO] Price parsed in {round(time.time() - start, 2)} sec: {url}")
    return price
