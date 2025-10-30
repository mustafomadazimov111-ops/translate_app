frfrom flask import Flask, render_template, request
from googletrans import Translator
from gtts import gTTS
import os

app = Flask(__name__)
translator = Translator()

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    audio_file = None

    if request.method == "POST":
        text = request.form["text"]
        from_lang = request.form["from_lang"]
        to_lang = request.form["to_lang"]

        # Tarjima qilish
        translated = translator.translate(text, src=from_lang, dest=to_lang)
        translated_text = translated.text

        # Ovoz faylini yaratish (faqat to_lang = 'en' yoki boshqa gTTS qo‘llaydigan tilda)
        try:
            tts = gTTS(translated_text, lang=to_lang)
            audio_file = "static/voice.mp3"
            os.makedirs("static", exist_ok=True)
            tts.save(audio_file)
        except Exception as e:
            print("Audio yaratishda xato:", e)
            audio_file = None

    return render_template("index.html", translated_text=translated_text, audio_file=audio_file)

if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
