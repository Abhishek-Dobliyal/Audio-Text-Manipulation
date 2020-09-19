from flask import Flask, render_template, request, redirect
import speech_recognition as sr
from googletrans import Translator
import urllib3
from gtts import gTTS
import os
from PIL import Image
import pytesseract as pytrt

app = Flask(__name__)

if not os.path.isdir("tts_files"):
    os.makedirs("tts_files")

language_dict = {
        'it': 'Italian',
        'ar': 'Arabic',
        'ja': 'Japanese',
        'ko': 'Korean',
        'la': 'Latin',
        'fa': 'Persian',
        'ro': 'Romanian',
        'ru': 'Russian',
        'fr': 'French',
        'sv': 'Swedish',
        'hi': 'Hindi',
        'ur': 'Urdu',
        'en': 'English'
    }

def check_connection():
    ''' Checks wheather an active connection is present or not '''
    try:
        http = urllib3.PoolManager()
        r = http.request('GET', 'https://www.google.co.in')
        return r.status == 200
    except Exception:
        return False

@app.route("/", methods=["POST", "GET"])
def index():
    ''' Home Page '''
    text =  ""
    if request.method == "POST":
        # print("Form Submitted")
        if "file" not in request.files:
            return redirect(request.url)

        files = request.files["file"]
        # translated_text = request.form['text']
        if files.filename == "":
            return redirect(request.url)

        if files:
            if check_connection():
                try:
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(files) as source:
                        audio = recognizer.record(source)
                    text = recognizer.recognize_google(audio)
                except ValueError:
                    text = "Unable to Process this File Format!"
            else:
                text = "No Internet Access :("

    return render_template("index.html", text=text)

@app.route("/translate", methods=["POST", "GET"])
def translate():
    ''' Translation '''
    translated_text, lng_to_translate = "", ""
    lang_code, language = "en", ""
    translator = Translator() # A translator object

    if request.method == "POST":
        text = request.form['text'] # Text from User
        lang_code = request.form['languages'] # Language selection
        if text:
            if check_connection():
                translated_text = translator.translate(text, dest=lang_code).text # Fetch the text using text attribute
                lang_code_detect = translator.detect(text).lang # Language of the text to translate
                language = language_dict[lang_code_detect]
            else:
                translated_text = "No Internet Access :("
        else:
            translated_text = "Unable to Process this Data!"

    return render_template("translate.html", translated_text=translated_text,
                          language_from=language, language_to=language_dict[lang_code])

@app.route("/text_to_speech", methods=["GET", "POST"])
def text_to_speech():
    ''' Text-To-Speech '''
    if request.method == "POST":
        text_to_speak = request.form['text']
        language = request.form['languages']

        if text_to_speak:
            if check_connection():
                tts = gTTS(text_to_speak, lang=language)
                if len(text_to_speak)>10:
                    path = "tts_files/" + text_to_speak[:10].replace(" ", "_") + ".mp3"
                    print(path)
                    tts.save(path)
                    os.system(f"mpg321 {path}")
                else:
                    path = "tts_files/" + text_to_speak.replace(" ", "_") + ".mp3"
                    print(path)
                    tts.save(path)
                    os.system(f"mpg321 {path}")
            else:
                os.system("mpg321 error.mp3")

    return render_template('tts.html')

@app.route("/image_text", methods=["GET", "POST"])
def extract_text():
    ''' Extract Text from Image '''
    extracted_text = ""
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)

        img_file = request.files["file"]
        # translated_text = request.form['text']
        if img_file.filename == "":
            return redirect(request.url)

        if img_file:
            try:
                final_img = Image.open(img_file)
                extracted_text = pytrt.image_to_string(final_img, timeout=5)
            except Exception:
                extracted_text = "Unable to retrieve text from given file :("

    return render_template("image_text.html", extracted_text=extracted_text)

if __name__ == "__main__":
    app.run(debug=True)
