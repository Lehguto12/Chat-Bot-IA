import openai
from typing import Dict, Any
import json
import os
from datetime import datetime

class Chatbot:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = {}
        self.user_preferences = {}
        
    def process_message(self, user_id: str, message: str) -> str:
        # Carrega histórico de conversa do usuário
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            
        # Adiciona mensagem ao histórico
        self.conversation_history[user_id].append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Prepara contexto para o modelo
        context = self._prepare_context(user_id, message)
        
        try:
            # Gera resposta usando OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=context,
                temperature=0.7,
                max_tokens=150
            )
            
            # Extrai resposta
            bot_response = response.choices[0].message.content
            
            # Atualiza histórico
            self.conversation_history[user_id].append({
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Mantém histórico limitado
            self._trim_history(user_id)
            
            return bot_response
            
        except Exception as e:
            print(f"Erro ao processar mensagem: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."
    
    def _prepare_context(self, user_id: str, message: str) -> list:
        # Prepara contexto com histórico e preferências do usuário
        context = [
            {"role": "system", "content": "Você é um assistente virtual amigável e prestativo."}
        ]
        
        # Adiciona preferências do usuário se existirem
        if user_id in self.user_preferences:
            context.append({
                "role": "system",
                "content": f"Preferências do usuário: {json.dumps(self.user_preferences[user_id])}"
            })
        
        # Adiciona histórico recente
        for msg in self.conversation_history[user_id][-5:]:
            context.append({
                "role": msg['role'],
                "content": msg['content']
            })
            
        return context
    
    def _trim_history(self, user_id: str, max_history: int = 10):
        # Mantém apenas as últimas N mensagens no histórico
        if len(self.conversation_history[user_id]) > max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][-max_history:]
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        # Atualiza preferências do usuário
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        self.user_preferences[user_id].update(preferences)
    
    def get_conversation_history(self, user_id: str) -> list:
        # Retorna histórico de conversa do usuário
        return self.conversation_history.get(user_id, []) 