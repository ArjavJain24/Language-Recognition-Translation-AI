from flask import Flask, render_template, request, jsonify, send_from_directory
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import os
from datetime import datetime

app = Flask(__name__)

os.makedirs("static", exist_ok=True)
translator = Translator()

def normalize_lang(code: str) -> str:
    if not code:
        return "en"
    code = code.lower()
    aliases = {"jp":"ja","he":"iw","fil":"tl","zh":"zh-cn","zh-cn":"zh-cn","zh-tw":"zh-tw","pt-br":"pt"}
    return aliases.get(code, code)

@app.route("/")
def index():
    return render_template("index-futuristic.html", languages=LANGUAGES)

@app.route("/translate", methods=["POST"])
def translate_text():
    try:
        text = (request.form.get("text") or "").strip()
        src = (request.form.get("src_lang") or "auto").lower()
        dest = normalize_lang(request.form.get("tgt_lang") or "en")
        if not text:
            return jsonify({"error": "No text provided."}), 400
        res = translator.translate(text, src=("auto" if src == "auto" else src), dest=dest)
        detected = getattr(res, "src", src if src != "auto" else "")
        return jsonify({
            "original": text,
            "translated": res.text,
            "detected_code": detected,
            "detected_lang": LANGUAGES.get(detected, detected) if detected else "auto"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/tts", methods=["POST"])
def tts():
    try:
        text = (request.form.get("text") or "").strip()
        lang = normalize_lang(request.form.get("lang") or "en")
        if not text:
            return jsonify({"error":"Nothing to speak."}), 400
        try:
            tts = gTTS(text=text, lang=lang)
        except Exception:
            tts = gTTS(text=text, lang="en")
        fname = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.mp3"
        path = os.path.join("static", fname)
        tts.save(path)
        return jsonify({"audio_url": f"/static/{fname}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
