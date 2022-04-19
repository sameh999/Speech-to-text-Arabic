from flask import Flask, render_template, request, redirect
import speech_recognition as sr
import transcribe_basics as tr
import time
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
           audio_path = f'Audio\demo-{time.time_ns()}.wav'
           audio_name =f'demo-{time.time_ns()}'
           recognizer = sr.Recognizer()
           audioFile = sr.AudioFile(file)

           with audioFile as source:
               data = recognizer.record(source)
            
           with open(audio_path, "wb") as f:
               f.write(data.get_wav_data())

           transcript = tr.Transcribe(audio_path , audio_name)
    return render_template('index.html', transcript=transcript)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
