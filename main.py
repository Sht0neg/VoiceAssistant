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
    
    def set_volume(self, volume):
        try:
            self.current_volume = float(volume) / 100.0
            current_settings['volume'] = float(volume)
            return {'status': 'success', 'volume': self.current_volume}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def test_audio(self):
        try:
            if self.output_device is None:
                return {'status': 'error', 'message': 'Не выбрано устройство вывода'}
            
            duration = 0.5
            frequency = 440
            t = np.linspace(0, duration, int(16000 * duration))
            test_signal = np.sin(2 * np.pi * frequency * t) * self.current_volume
            
            def play():
                sd.play(test_signal, 16000, device=self.output_device)
                sd.wait()
            
            threading.Thread(target=play, daemon=True).start()
            
            return {'status': 'success', 'message': 'Тестовый сигнал воспроизводится'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        
    def start_assistant(self):
        global assistant_running, assistant_thread

        if assistant_running:
            return {'status': 'error', 'message': 'Ассистент уже запущен'}
        
        if self.input_device is None:
            return {'status': 'error', 'message': 'Не выбрано устройство ввода'}
        
        if self.vosk_model is None:
            return {'status': 'error', 'message': 'Модель Vosk не загружена'}
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            q.put(bytes(indata))
        
        def run_assistant():
            global assistant_running
            try:
                rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
                
                with sd.RawInputStream(
                    samplerate=16000,
                    blocksize=8000,
                    device=self.input_device,
                    dtype='int16',
                    channels=1,
                    callback=audio_callback
                ):
                    print("✓ Ассистент запущен. Говорите...")
                    
                    while assistant_running:
                        try:
                            data = q.get(timeout=1)
                            
                            if rec.AcceptWaveform(data):
                                result = json.loads(rec.Result())
                                text = result["text"]
                                if text: 
                                    print(f"▶ Распознано: {text}")
                                    self.process_command(text)
                            else:
                                partial = json.loads(rec.PartialResult())
                                if partial.get("partial"):
                                    print(f"⚡ Частично: {partial['partial']}", end="\r")
                        except queue.Empty:
                            continue
                        except Exception as e:
                            print(f"Ошибка обработки: {e}")
                    
            except Exception as e:
                print(f"Ошибка в ассистенте: {e}")
            finally:
                print("✓ Ассистент остановлен")
        
        assistant_running = True
        assistant_thread = threading.Thread(target=run_assistant, daemon=True)
        assistant_thread.start()
        
        return {'status': 'success', 'message': 'Ассистент запущен'}

    def stop_assistant(self):
        global assistant_running
        assistant_running = False
        
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                break
        
        return {'status': 'success', 'message': 'Ассистент остановлен'}

