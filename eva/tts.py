from datetime import datetime
import logging
import os
import sounddevice as sd
import soundfile as sf
import wave
import threading

from piper import PiperVoice


class TextToSpeech:

    def __init__(self):
        self.enabled = os.getenv('ENABLE_TTS', 'False').lower() in ('true', 'yes', '1')
        self._logger = logging.getLogger(self.__class__.__name__)
        self._voice = self._load_voice(os.getenv('TTS_ONNX_MODEL_PATH', ''))

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

    def _start_cleanup(self, wav_file_path: str):
        remove_tmp_file_thread = threading.Thread(target=os.remove, args=(wav_file_path,))
        remove_tmp_file_thread.start()

    def play(self, text: str):
        try:
            wav_file_path = self._synthesize_wav_file(text)
            self._play_sound(wav_file_path)
            self._start_cleanup(wav_file_path)
        except Exception as err:
            self.enabled = False
            self._logger.error('Text to speech error %s', err, exc_info=True)
