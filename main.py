import vosk
import queue
import json
import sounddevice as sd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


q = queue.Queue()

model = vosk.Model("model")

device = sd.default.device
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