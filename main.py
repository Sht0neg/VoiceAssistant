import subprocess
import threading

import vosk
import queue
import json
import sounddevice as sd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import asyncio
from skills import *
import os
import pyttsx3
import base_words as words

q = queue.Queue()

model = vosk.Model("model")

class VoiceAssistantAPI:
    def __init__(self):
        self.samplerate = None
        self.current_volume = 0.7
        self.is_streaming = False
        self.input_device = None
        self.vosk_model = None
        self.engine = None

        self.load_vosk_model()

    def load_vosk_model(self):
        try:
            model_path = "model"
            if os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
        except Exception as e:
            print("Ошибка загрузки звуковой модели!")
    
    def get_input_device(self):
        try:
            self.input_device = sd.default.device[0]
            self.get_samplerate()
        except Exception as e:
            print("Не удалось найти устройства ввода!")
    
    def get_samplerate(self):
        try:
            self.samplerate = int(sd.query_devices(self.input_device, "input")["default_samplerate"])
        except Exception as e:
            print("Ошибка в подключении к устройству ввода!")
    
    def get_weather(self):
            with open("data.json") as f:
                data = json.load(f)
                return f"Сейчас на улице {data["days"][0]["description"]}, {data["days"][0]["temp"]} градусов, ощущается как {data["days"][0]["feelslike"]} градусов, скорость ветра {data["days"][0]["windspeed"]} метров в секунду"
    
    def speak(self, text):
        cmd = f'spd-say -o rhvoice -y "Arina" -i {self.current_volume * 100} "{text}"'
        os.system(cmd)

    def callback(self, indata, frames, time, status):
        q.put(bytes(indata))

    def recognize(self, data, vectorizer, clf):
        trg = words.TRIGGERS.intersection(data.split())
        if not trg:
            return

        data.replace(list(trg)[0], '')

        text_vector = vectorizer.transform([data]).toarray()[0]
        answer = clf.predict([text_vector])[0]
        func_name = answer.split()[0]

        self.speak(answer.replace(func_name + " ", ''))

        if func_name == "search":
            exec(func_name + f"('{re.sub(r"(искра|искорка) найди", "", data)}')")
            return
        if func_name == "video_search":
            exec(func_name + f"('{re.sub(r"(искра|искорка) открой в ютубе", "", data)}')")
            return
        exec(func_name + '()')
        if func_name == "weather":
            self.speak(self.get_weather())
    
    def start_voice_assistant(self):
        self.get_input_device()

        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform(list(words.data_set.keys()))
    
        clf = LogisticRegression()
        clf.fit(vectors, list(words.data_set.values()))

        del words.data_set

        with sd.RawInputStream(samplerate=self.samplerate, blocksize = 48000, device=self.input_device,dtype="int16", channels=1, callback=self.callback):
            rec = vosk.KaldiRecognizer(model, self.samplerate)
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    data = json.loads(rec.Result())["text"]
                    self.recognize(data, vectorizer, clf)
    
if __name__ == "__main__":
    api = VoiceAssistantAPI()

    api.start_voice_assistant()