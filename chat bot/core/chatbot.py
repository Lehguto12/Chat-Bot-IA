from typing import Dict, Any, List, Optional
import json
import os

from openai import OpenAI


class Chatbot:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.openai_client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.user_preferences: Dict[str, Dict[str, Any]] = {}

    def process_message(
        self,
        user_id: str,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if not self.openai_client:
            return (
                'O chatbot está rodando, mas falta configurar a variável '
                'OPENAI_API_KEY no arquivo .env.'
            )

        context = self._prepare_context(user_id, history or [], message)

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=context,
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content or ''
        except Exception as e:
            print(f'Erro ao processar mensagem: {e}')
            return (
                'Não consegui acessar a IA agora. Confira sua OPENAI_API_KEY, '
                'o modelo configurado e sua conexão com a internet.'
            )

    def _prepare_context(
        self,
        user_id: str,
        history: List[Dict[str, str]],
        message: str,
    ) -> List[Dict[str, str]]:
        context: List[Dict[str, str]] = [
            {
                'role': 'system',
                'content': (
                    'Você é um assistente virtual amigável, claro e prestativo. '
                    'Responda em português do Brasil, salvo quando o usuário pedir outro idioma.'
                ),
            }
        ]

        if user_id in self.user_preferences:
            context.append({
                'role': 'system',
                'content': (
                    'Preferências do usuário: '
                    + json.dumps(self.user_preferences[user_id], ensure_ascii=False)
                ),
            })

        for item in history[-16:]:
            role = item.get('role')
            content = item.get('content')
            if role in {'user', 'assistant'} and content:
                context.append({'role': role, 'content': content})

        context.append({'role': 'user', 'content': message})
        return context

    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        self.user_preferences[user_id].update(preferences)
