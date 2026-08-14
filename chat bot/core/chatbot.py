from typing import Dict, Any
from datetime import datetime
import json
import os

from openai import OpenAI


class Chatbot:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.conversation_history = {}
        self.user_preferences = {}

    def process_message(self, user_id: str, message: str) -> str:
        if not self.openai_client:
            return (
                'O chatbot está rodando, mas falta configurar a variável '
                'OPENAI_API_KEY no arquivo .env.'
            )

        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        self.conversation_history[user_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })

        context = self._prepare_context(user_id)

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=context,
                temperature=0.7,
                max_tokens=300
            )

            bot_response = response.choices[0].message.content or ''

            self.conversation_history[user_id].append({
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.now().isoformat()
            })
            self._trim_history(user_id)
            return bot_response

        except Exception as e:
            print(f'Erro ao processar mensagem: {e}')
            return (
                'Não consegui acessar a IA agora. Confira sua OPENAI_API_KEY, '
                'o modelo configurado e sua conexão com a internet.'
            )

    def _prepare_context(self, user_id: str) -> list:
        context = [
            {
                'role': 'system',
                'content': (
                    'Você é um assistente virtual amigável, claro e prestativo. '
                    'Responda em português do Brasil, salvo quando o usuário pedir outro idioma.'
                )
            }
        ]

        if user_id in self.user_preferences:
            context.append({
                'role': 'system',
                'content': f'Preferências do usuário: {json.dumps(self.user_preferences[user_id], ensure_ascii=False)}'
            })

        for msg in self.conversation_history[user_id][-8:]:
            context.append({
                'role': msg['role'],
                'content': msg['content']
            })

        return context

    def _trim_history(self, user_id: str, max_history: int = 12):
        if len(self.conversation_history[user_id]) > max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][-max_history:]

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        self.user_preferences[user_id].update(preferences)

    def get_conversation_history(self, user_id: str) -> list:
        return self.conversation_history.get(user_id, [])
