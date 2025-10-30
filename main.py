from flask import Flask, render_template, request
from googletrans import Translator
from gtts import gTTS
import os, time

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
        result = translator.translate(text, src=from_lang, dest=to_lang)
        translated_text = result.text

        # Tovush fayl yaratish (yangi nom bilan)
        safe_lang = to_lang if to_lang in ['en', 'ru', 'fr', 'de', 'es'] else 'en'
        tts = gTTS(text=translated_text, lang=safe_lang)

        if not os.path.exists("static"):
            os.makedirs("static")

        filename = f"translate_{int(time.time())}.mp3"
        audio_path = os.path.join("static", filename)
        tts.save(audio_path)

        audio_file = f"static/{filename}"

    return render_template("index.html", translated_text=translated_text, audio_file=audio_file)

if __name__ == "__main__":
    app.run(debug=True)
