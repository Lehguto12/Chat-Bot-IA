from flask import render_template
from flask_socketio import emit
from core.chatbot import Chatbot
import json

class WebChat:
    def __init__(self, chatbot: Chatbot):
        self.chatbot = chatbot
    
    def render_chat_interface(self):
        """Renderiza a interface do chat"""
        return render_template('chat.html')
    
    def handle_message(self, data, socket):
        """Processa mensagens do WebSocket"""
        try:
            user_id = data.get('user_id')
            message = data.get('message')
            
            if not user_id or not message:
                emit('error', {'message': 'Dados inválidos'}, room=socket.sid)
                return
            
            # Processa mensagem com o chatbot
            response = self.chatbot.process_message(user_id, message)
            
            # Envia resposta
            emit('response', {
                'message': response,
                'timestamp': datetime.now().isoformat()
            }, room=socket.sid)
            
        except Exception as e:
            emit('error', {
                'message': f'Erro ao processar mensagem: {str(e)}'
            }, room=socket.sid)
    
    def handle_voice_message(self, data, socket):
        """Processa mensagens de voz"""
        try:
            user_id = data.get('user_id')
            audio_data = data.get('audio')
            
            if not user_id or not audio_data:
                emit('error', {'message': 'Dados inválidos'}, room=socket.sid)
                return
            
            # Transcreve áudio para texto
            from services.voice import VoiceService
            voice_service = VoiceService()
            text = voice_service.transcribe_audio(audio_data)
            
            if not text:
                emit('error', {'message': 'Não foi possível transcrever o áudio'}, room=socket.sid)
                return
            
            # Processa texto com o chatbot
            response = self.chatbot.process_message(user_id, text)
            
            # Envia resposta
            emit('response', {
                'message': response,
                'timestamp': datetime.now().isoformat()
            }, room=socket.sid)
            
        except Exception as e:
            emit('error', {
                'message': f'Erro ao processar mensagem de voz: {str(e)}'
            }, room=socket.sid)
    
    def handle_user_typing(self, data, socket):
        """Notifica quando usuário está digitando"""
        try:
            user_id = data.get('user_id')
            is_typing = data.get('is_typing')
            
            if not user_id:
                return
            
            # Emite evento de digitação
            emit('user_typing', {
                'user_id': user_id,
                'is_typing': is_typing
            }, broadcast=True, skip_sid=socket.sid)
            
        except Exception as e:
            print(f"Erro ao processar evento de digitação: {str(e)}") 