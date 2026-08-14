from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os

from core.chatbot import Chatbot

load_dotenv()

app = Flask(__name__)
chatbot = Chatbot()


@app.route('/')
def home():
    return render_template('chat.html')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_id = str(data.get('user_id') or 'web-user')
    message = str(data.get('message') or '').strip()

    if not message:
        return jsonify({'error': 'Digite uma mensagem antes de enviar.'}), 400

    response = chatbot.process_message(user_id, message)
    return jsonify({'response': response})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
