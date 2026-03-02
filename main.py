import vosk
import queue
import json
import sounddevice as sd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import asyncio
import skills
import webview
import numpy as np
import threading
import os
import sys
from datetime import datetime


assistant_running = False
assistant_thread = None
current_settings = {
    'volume': 70,
    'input_device': None,
    'output_device': None,
    'window_size': '600x700'
}
q = queue.Queue()
model = vosk.Model("model")

class VoiceAssistantAPI:
    def __init__(self):
        self.sample_rate = 16000 
        self.current_volume = 0.7
        self.input_stream = None
        self.output_stream = None
        self.is_streaming = False
        self.input_device = None
        self.output_device = None
        self.vosk_model = None
        self.rec = None
        
        self.load_vosk_model()
        
        self.refresh_devices()

    def load_vosk_model(self):
        try:
            model_path = "model"
            if os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
        except Exception as e:
            pass

    def refresh_devices(self):
        try:
            self.devices = sd.query_devices()
            self.input_devices = []
            self.output_devices = []
            
            for i, device in enumerate(self.devices):
                if device['max_input_channels'] > 0:
                    self.input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'samplerate': device['default_samplerate']
                    })
                if device['max_output_channels'] > 0:
                    self.output_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_output_channels'],
                        'samplerate': device['default_samplerate']
                    })
        except Exception as e:
            self.input_devices = []
            self.output_devices = []
    
    def get_devices(self):
        self.refresh_devices()
        return {
            'input': self.input_devices,
            'output': self.output_devices
        }

samplerate = int(sd.query_devices(device[0], "input")["default_samplerate"])

def callback(indata, frames, time, status):
    q.put(bytes(indata))


def main():
    with sd.RawInputStream(samplerate=samplerate, blocksize = 48000, device=device[0],
        dtype="int16", channels=1, callback=callback):

        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                data = json.loads(rec.Result())["text"]
            else:
                print(rec.PartialResult())

if __name__ == "__main__":
    main()