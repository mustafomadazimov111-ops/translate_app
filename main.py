from flask import Flask, render_template, request
import requests
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

LIBRE_URL = "https://libretranslate.de/translate"  # asosiy bepul server

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    audio_file = None

    if request.method == "POST":
        text = request.form["text"]
        from_lang = request.form["from_lang"]
        to_lang = request.form["to_lang"]

        # LibreTranslate API'ga so‘rov
        payload = {
            "q": text,
            "source": from_lang,
            "target": to_lang,
            "format": "text"
        }

        try:
            response = requests.post(LIBRE_URL, data=payload)
            result = response.json()
            translated_text = result.get("translatedText", "Tarjima topilmadi.")
        except Exception as e:
            translated_text = f"Xato: {e}"

        # Ovozli fayl yaratish (agar tarjima muvaffaqiyatli bo‘lsa)
        try:
            os.makedirs("static", exist_ok=True)
            audio_file = f"static/voice_{uuid.uuid4().hex}.mp3"
            tts = gTTS(translated_text, lang=to_lang)
            tts.save(audio_file)
        except Exception as e:
            print("Ovoz yaratishda xato:", e)
            audio_file = None

    return render_template("index.html", translated_text=translated_text, audio_file=audio_file)


if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
