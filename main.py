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
    
    def engine_init(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)	
        self.engine.setProperty('volume', self.current_volume)
    
    def speak(self, text):
        self.engine_init()
        self.engine.say(text)
        self.engine.runAndWait()
        self.engine.stop()
        del self.engine

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

        self.speak(answer.replace(func_name, ''))
        print(answer.replace(func_name, ''))


        exec(func_name + '()')
    
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