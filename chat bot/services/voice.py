import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile
import base64

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def transcribe_audio(self, audio_data: str) -> str:
        """
        Transcreve áudio para texto
        audio_data: string base64 do áudio
        """
        try:
            # Decodifica áudio base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Salva temporariamente
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Converte para formato WAV se necessário
            if not temp_audio_path.endswith('.wav'):
                audio = AudioSegment.from_file(temp_audio_path)
                wav_path = temp_audio_path + '.wav'
                audio.export(wav_path, format='wav')
                os.remove(temp_audio_path)
                temp_audio_path = wav_path
            
            # Transcreve áudio
            with sr.AudioFile(temp_audio_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language='pt-BR')
            
            # Limpa arquivo temporário
            os.remove(temp_audio_path)
            
            return text
            
        except Exception as e:
            print(f"Erro ao transcrever áudio: {str(e)}")
            return ""
    
    def text_to_speech(self, text: str) -> str:
        """
        Converte texto para áudio (implementação futura)
        """
        # TODO: Implementar conversão de texto para áudio
        pass 