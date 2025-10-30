# from flask import Flask, render_template, request
# import requests
# from gtts import gTTS
# import os
# import uuid
#
# app = Flask(__name__)
#
# LIBRE_URL = "https://libretranslate.de/translate"  # asosiy bepul server
#
# @app.route("/", methods=["GET", "POST"])
# def index():
#     translated_text = ""
#     audio_file = None
#
#     if request.method == "POST":
#         text = request.form["text"]
#         from_lang = request.form["from_lang"]
#         to_lang = request.form["to_lang"]
#
#         # LibreTranslate API'ga so‘rov
#         payload = {
#             "q": text,
#             "source": from_lang,
#             "target": to_lang,
#             "format": "text"
#         }
#
#         try:
#             response = requests.post(LIBRE_URL, data=payload)
#             result = response.json()
#             translated_text = result.get("translatedText", "Tarjima topilmadi.")
#         except Exception as e:
#             translated_text = f"Xato: {e}"
#
#         # Ovozli fayl yaratish (agar tarjima muvaffaqiyatli bo‘lsa)
#         try:
#             os.makedirs("static", exist_ok=True)
#             audio_file = f"static/voice_{uuid.uuid4().hex}.mp3"
#             tts = gTTS(translated_text, lang=to_lang)
#             tts.save(audio_file)
#         except Exception as e:
#             print("Ovoz yaratishda xato:", e)
#             audio_file = None
#
#     return render_template("index.html", translated_text=translated_text, audio_file=audio_file)
#
#
# if __name__ == "__main__":
#     from os import environ
#     port = int(environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)

from flask import Flask, render_template, request
import requests
from gtts import gTTS
import os
import uuid
import time
import logging
from requests.exceptions import RequestException

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Asosiy LibreTranslate endpointlari (agar biri ishlamasa, boshqasiga o‘tiladi)
LIBRE_ENDPOINTS = [
    "https://libretranslate.de/translate",
    "https://libretranslate.com/translate",
    "https://translate.argosopentech.com/translate"
]

HEADERS = {"Content-Type": "application/json"}

def libre_translate(text, source_lang, target_lang, retries=2, timeout=10):
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    last_err = None
    for endpoint in LIBRE_ENDPOINTS:
        for attempt in range(retries + 1):
            try:
                logging.info(f"Request to {endpoint} attempt {attempt+1}")
                resp = requests.post(endpoint, json=payload, headers=HEADERS, timeout=timeout)
                logging.info(f"Status code: {resp.status_code}")
                logging.debug(f"Response text: {resp.text[:1000]}")  # qisqacha log
                if resp.status_code != 200:
                    last_err = f"HTTP {resp.status_code}: {resp.text}"
                    # kichik kutish va qayta urinish
                    time.sleep(1 + attempt)
                    continue
                # JSON parse qilishni sinab ko'ramiz
                try:
                    data = resp.json()
                except ValueError as e:
                    last_err = f"JSON decode error: {e}; body: {resp.text[:1000]}"
                    logging.error(last_err)
                    time.sleep(1 + attempt)
                    continue

                # normal ishlash - translatedText olamiz
                if isinstance(data, dict) and "translatedText" in data:
                    return data.get("translatedText", "")
                # Ba'zi endpointlar boshqacha struktura qaytarishi mumkin
                if isinstance(data, dict) and "data" in data and "translations" in data["data"]:
                    return data["data"]["translations"][0].get("translatedText", "")
                # agar struktura boshqacha bo'lsa, uni string sifatida qaytarish
                if isinstance(data, str):
                    return data
                last_err = f"Unexpected response structure: {data}"
            except RequestException as e:
                last_err = f"RequestException: {e}"
                logging.error(last_err)
                time.sleep(1 + attempt)
        logging.warning(f"Endpoint {endpoint} failed: {last_err}")
    # Agar hammasi muvaffaqiyatsiz bo'lsa, xatolik matnini qaytaramiz
    return f"Xato: tarjima bajarilmadi. Tafsilotlar server logida."

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    audio_file = None
    error_message = None

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        from_lang = request.form.get("from_lang", "auto")
        to_lang = request.form.get("to_lang", "en")

        if not text:
            error_message = "Iltimos, tarjima qilish uchun matn kiriting."
        else:
            translated_text = libre_translate(text, from_lang, to_lang)
            # Agar javob "Xato:" bilan boshlansa, uni error sifatida ko'rsatamiz
            if translated_text.startswith("Xato:"):
                error_message = translated_text
                translated_text = ""
            else:
                # Ovozli fayl yaratish
                try:
                    os.makedirs("static", exist_ok=True)
                    audio_file = f"static/voice_{uuid.uuid4().hex}.mp3"
                    tts = gTTS(translated_text, lang=to_lang)
                    tts.save(audio_file)
                except Exception as e:
                    logging.error("Ovoz yaratishda xato: %s", e)
                    audio_file = None
                    error_message = "Tarjima bajarildi, ammo audio yaratib bo'lmadi."

    return render_template("index.html",
                           translated_text=translated_text,
                           audio_file=audio_file,
                           error_message=error_message)

if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

