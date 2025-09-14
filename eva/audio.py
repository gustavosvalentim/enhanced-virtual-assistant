from datetime import datetime
import logging
import os
import sounddevice as sd
import soundfile as sf
import wave
import threading

from piper import PiperVoice


logger = logging.getLogger(__name__)

_voice = PiperVoice.load('voices/en_US-amy-medium.onnx')
_block_tts = False


def is_tts_enabled() -> bool:
    return os.getenv('ENABLE_TTS', 'False').lower() in ('true', 'yes', '1')


def text_to_speech(text: str):
    global _block_tts
    try:
        if is_tts_enabled() and not _block_tts:
            timestamp = int(datetime.now().timestamp())
            filepath = f'{timestamp}.wav'
            with wave.open(filepath, 'wb') as wav:
                _voice.synthesize_wav(text, wav)
            data, fs = sf.read(filepath, dtype='float32')
            sd.play(data, fs)
            sd.wait()
            
            remove_tmp_file_thread = threading.Thread(target=remove_tmp_file, args=(filepath,))
            remove_tmp_file_thread.start()
    except Exception as err:
        _block_tts = True
        logger.error('Text to speech error %s', err, exc_info=True)


def remove_tmp_file(filepath: str):
    os.remove(filepath)
