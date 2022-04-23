import threading
from flask import Flask, render_template, request, redirect
import speech_recognition as sr
import transcribe_basics as tr
import time
# import os
# from redis import Redis
# from rq import Queue
# from worker import conn
# q = Queue(connection=conn)
from transcribe_basics import Transcribe

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        print("FORM DATA transcript funcrion ")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            audio_path = f'demo-{time.time_ns()}.wav'
            #audio_path = os.path.join(os.getcwd(),f'static/Audio/demo-{time.time_ns()}.wav')
            print(audio_path)
            print("-"*80)
            audio_name =f'demo-{time.time_ns()}'
            recognizer = sr.Recognizer()
            audioFile = sr.AudioFile(file)

            with audioFile as source:
               data = recognizer.record(source)
            
            with open(audio_path, "wb") as f:
               f.write(data.get_wav_data())
            MyWorker('param_value')
            # transcript = tr.Transcribe(audio_path , audio_name)
            transcript = q.enqueue(Transcribe,audio_path , audio_name)
    return render_template('index.html', transcript=transcript)

class MyWorker():

  def __init__(self, message):
    self.message = message

    thread = threading.Thread(target=self.run, args=())
    thread.daemon = True
    thread.start()

  def run(self):
    print(f'run MyWorker with parameter {self.message}')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)


