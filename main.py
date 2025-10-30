from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    audio_file = None

    if request.method == "POST":
        text = request.form["text"]
        from_lang = request.form["from_lang"]
        to_lang = request.form["to_lang"]

        # Tarjima qilish
        translated_text = GoogleTranslator(source=from_lang, target=to_lang).translate(text)

        # Ovozli fayl yaratish
        try:
            os.makedirs("static", exist_ok=True)
            audio_file = "static/voice.mp3"
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
