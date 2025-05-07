import os
import requests
from core.chatbot import Chatbot

class WhatsAppBot:
    def __init__(self, chatbot: Chatbot):
        self.chatbot = chatbot
        self.token = os.getenv('WHATSAPP_TOKEN')
        self.api_url = f"https://graph.facebook.com/v17.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def handle_webhook(self, request):
        """Processa webhooks do WhatsApp"""
        data = request.get_json()
        
        try:
            # Extrai informações da mensagem
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            user_id = message['from']
            message_text = message['text']['body']
            
            # Processa mensagem com o chatbot
            response = self.chatbot.process_message(user_id, message_text)
            
            # Envia resposta
            self.send_message(user_id, response)
            
            return {'status': 'ok'}
            
        except Exception as e:
            print(f"Erro ao processar webhook do WhatsApp: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def send_message(self, to: str, message: str):
        """Envia mensagem para um número do WhatsApp"""
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {
                'body': message
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
            return None
    
    def send_template(self, to: str, template_name: str, components: list):
        """Envia mensagem de template para um número do WhatsApp"""
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {
                    'code': 'pt_BR'
                },
                'components': components
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Erro ao enviar template WhatsApp: {str(e)}")
            return None 