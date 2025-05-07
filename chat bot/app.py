from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from core.chatbot import Chatbot
from integrations.telegram import TelegramBot
from integrations.whatsapp import WhatsAppBot
from integrations.webchat import WebChat
from services.auth import AuthService
from services.voice import VoiceService
from services.analytics import AnalyticsService

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Inicializa serviços
chatbot = Chatbot()
auth_service = AuthService()
voice_service = VoiceService()
analytics_service = AnalyticsService()

# Inicializa integrações
telegram_bot = TelegramBot(chatbot)
whatsapp_bot = WhatsAppBot(chatbot)
webchat = WebChat(chatbot)

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    return telegram_bot.handle_webhook(request)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    return whatsapp_bot.handle_webhook(request)

@app.route('/api/chat', methods=['POST'])
@auth_service.require_auth
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    # Processa mensagem de voz se necessário
    if data.get('is_voice'):
        message = voice_service.transcribe_audio(message)
    
    # Obtém resposta do chatbot
    response = chatbot.process_message(user_id, message)
    
    # Registra interação para análise
    analytics_service.log_interaction(user_id, message, response)
    
    return jsonify({'response': response})

@socketio.on('connect')
def handle_connect():
    auth_service.validate_socket_connection(request)

@socketio.on('message')
def handle_message(data):
    user_id = auth_service.get_user_from_socket(request.sid)
    response = chatbot.process_message(user_id, data['message'])
    socketio.emit('response', {'message': response}, room=request.sid)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True) 