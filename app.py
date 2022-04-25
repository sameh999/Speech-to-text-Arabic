from flask import Flask, render_template, request, redirect
import speech_recognition as sr
import transcribe_basics as tr
import time
import os
from threading import Thread
from transcribe_basics import Transcribe

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            audio_path = f'demo-{time.time_ns()}.wav'
            print(audio_path)
            print("-"*80)
            audio_name =f'demo-{time.time_ns()}'
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)

            with audioFile as source:
               data = recognizer.record(source)
            
            with open(audio_path, "wb") as f:
               f.write(data.get_wav_data())
               
            task(audio_path , audio_name)
            transcript = " your audio under processing please wait...."
            print("transcript : ", transcript)
    return render_template('index.html', transcript=transcript)

def task(audio_path , audio_name):
    thread = Thread(target=Transcribe, args=(audio_path , audio_name,))
    thread.daemon = True
    thread.start()
    return thread
if __name__ == "__main__":
    app.run(debug=True, threaded=True)

