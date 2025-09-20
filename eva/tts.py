from datetime import datetime
import logging
import os
import sounddevice as sd
import soundfile as sf
import wave
import threading

from piper import PiperVoice


class TextToSpeechConfiguration:
    enabled: bool
    onnx_model_path: str

    def __init__(self, enabled: bool, onnx_model_path: str):
        self.enabled = enabled
        self.onnx_model_path = onnx_model_path


class TextToSpeech:

    def __init__(self, config: TextToSpeechConfiguration):
        self.enabled = config.enabled
        self._voice = self._load_voice(config.onnx_model_path)
        self._logger = logging.getLogger(self.__class__.__name__)

    def _load_voice(self, model_path: str):
        if not model_path.strip() and self.enabled:
            raise ValueError('TTS_ONNX_MODEL_PATH can\'t be empty when TTS is enabled')
        if not self.enabled:
            return None
        return PiperVoice.load(model_path)
    
    def _synthesize_wav_file(self, text: str) -> str:
        timestamp = int(datetime.now().timestamp())
        wav_file_path = f'{timestamp}.wav'
        with wave.open(wav_file_path, 'wb') as wav:
            self._voice.synthesize_wav(text, wav)
        return wav_file_path 
    
    def _play_sound(self, wav_file_path: str):
        data, fs = sf.read(wav_file_path, dtype='float32')
        sd.play(data, fs)
        sd.wait()
        os.unlink(wav_file_path)

    def play(self, text: str):
        try:
            wav_file_path = self._synthesize_wav_file(text)
            play_thread = threading.Thread(target=self._play_sound, args=(wav_file_path,))
            play_thread.start()
        except Exception as err:
            self.enabled = False
            self._logger.error('Text to speech error %s', err, exc_info=True)
