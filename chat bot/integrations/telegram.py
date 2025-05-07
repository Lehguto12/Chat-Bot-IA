from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from core.chatbot import Chatbot

class TelegramBot:
    def __init__(self, chatbot: Chatbot):
        self.chatbot = chatbot
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.app = Application.builder().token(self.token).build()
        
        # Configura handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para o comando /start"""
        welcome_message = (
            "Olá! Eu sou seu assistente virtual. "
            "Como posso ajudar você hoje?"
        )
        await update.message.reply_text(welcome_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para mensagens de texto"""
        user_id = str(update.effective_user.id)
        message = update.message.text
        
        # Processa mensagem com o chatbot
        response = self.chatbot.process_message(user_id, message)
        
        # Envia resposta
        await update.message.reply_text(response)
    
    def run(self):
        """Inicia o bot"""
        self.app.run_polling()
    
    def handle_webhook(self, request):
        """Handler para webhooks do Telegram"""
        update = Update.de_json(request.get_json(), self.app.bot)
        self.app.process_update(update)
        return {'status': 'ok'} 