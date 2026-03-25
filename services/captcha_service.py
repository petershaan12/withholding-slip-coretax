import logging
import time

import openai
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from core.settings import settings
from utils.driver_utils import element_to_base64

log = logging.getLogger(__name__)


def qwen_ocr_from_url(image_url: str) -> str:
    """Kirim captcha ke Qwen VL OCR dan kembalikan teks hasil baca."""
    client = openai.OpenAI(
        api_key=settings.qwen_apikey,
        base_url=settings.dashscope_base_url,
    )
    preview = f"{image_url[:60]}..." if len(image_url) > 60 else image_url
    log.info("Mengirim captcha ke Qwen OCR: %s", preview)
    log.info("API Key: %s", "*" * 8 + settings.qwen_apikey[-4:])

    if image_url.startswith("data:image/") and ";base64," in image_url:
        base64_data = image_url.split(",", 1)[1]
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_data}"},
        }
    else:
        image_content = {
            "type": "image_url",
            "image_url": {"url": image_url},
        }

    completion = client.chat.completions.create(
        model=settings.dashscope_model,
        messages=[
            {
                "role": "user",
                "content": [
                    image_content,
                    {"type": "text", "text": "Output the text in the image only."},
                ],
            },
        ],
    )
    return completion.choices[0].message.content.strip()


def solve_captcha(driver, selector: str) -> str:
    image_url = element_to_base64(driver, selector)
    return qwen_ocr_from_url(image_url)


def refresh_captcha(driver) -> None:
    for sel in [
        "#dntCaptchaImg + a",
        "#dntCaptchaImg ~ a",
        "a[onclick*='captcha']",
    ]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(1)
            return
        except NoSuchElementException:
            continue
