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
import base_words as words
import voice


assistant_running = True
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
    
    def set_devices(self, input_index, output_index):
        try:
            self.input_device = int(input_index) if input_index else None
            self.output_device = int(output_index) if output_index else None
            
            current_settings['input_device'] = self.input_device
            current_settings['output_device'] = self.output_device
            
            if self.input_device is not None:
                sd.default.device = (self.input_device, self.output_device)
            
            return {'status': 'success', 'input': self.input_device, 'output': self.output_device}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

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

        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform(list(words.data_set.keys()))
    
        clf = LogisticRegression()
        clf.fit(vectors, list(words.data_set.values()))

        del words.data_set

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
                                    self.recognize(data, vectorizer, clf)
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

    
    def recognize(self, data, vectorizer, clf):

        trg = words.TRIGGERS.intersection(data.split())
        if not trg:
            return

        data.replace(list(trg)[0], '')

        text_vector = vectorizer.transform([data]).toarray()[0]
        answer = clf.predict([text_vector])[0]

        func_name = answer.split()[0]

        voice.speaker(answer.replace(func_name, ''))

        exec(func_name + '()')

    def stop_assistant(self):
        global assistant_running
        assistant_running = False
        
        while not q.empty():
            try:
                q.get_nowait()
            except queue.Empty:
                break
        
        return {'status': 'success', 'message': 'Ассистент остановлен'}
    
    def save_settings(self, settings):
        try:
            current_settings.update(settings)
            
            with open('assistant_settings.json', 'w', encoding='utf-8') as f:
                json.dump(current_settings, f, ensure_ascii=False, indent=2)
            
            if settings.get('input_device') and settings.get('output_device'):
                self.set_devices(settings['input_device'], settings['output_device'])
            
            if settings.get('volume'):
                self.set_volume(settings['volume'])
            
            self.load_settings()
            return {'status': 'success', 'message': 'Настройки сохранены'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        
    
    def load_settings(self):
        try:
            if os.path.exists('assistant_settings.json'):
                with open('assistant_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                if settings.get('input_device'):
                    self.input_device = int(settings['input_device'])
                if settings.get('output_device'):
                    self.output_device = int(settings['output_device'])
                if settings.get('volume'):
                    self.current_volume = settings['volume'] / 100.0
                    current_settings['volume'] = settings['volume']
                
                width, height = map(int, str(settings.get("window_size")).split("x"))
                webview.active_window().resize(width=width, height=height)
                return settings
            return {}
        except Exception as e:
            return {'error': str(e)}
    
    def get_assistant_status(self):
        global assistant_running
        return {
            'running': assistant_running,
            'input_device': self.input_device,
            'output_device': self.output_device,
            'volume': current_settings['volume']
        }
        
def main():
    api = VoiceAssistantAPI()
    
    window = webview.create_window(
        'Голосовой ассистент - Настройки',
        html=open("index.html", encoding="UTF-8").read(),
        js_api=api,
        width=600,
        height=700,
        resizable=True,
        fullscreen=False,
        min_size=(400, 500),
        confirm_close=True
    )
    api.load_settings()
    

    webview.start(debug=False, http_server=True)

    api.start_assistant()

if __name__ == '__main__':
    main()