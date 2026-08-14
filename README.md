# 🤖 Chat Bot com Inteligência Artificial

Chatbot desenvolvido em **Python + Flask**, com interface web e integração com a API da OpenAI.

A versão atual foi simplificada para funcionar primeiro como um **chatbot web local**. As integrações com Telegram, WhatsApp, voz, autenticação e MongoDB continuam no projeto como base para evoluções futuras, mas não são necessárias para testar o chat principal.

## 🚀 Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

## ✅ O que funciona agora

- Interface web de chat
- Envio de mensagens pelo navegador
- Respostas geradas pela OpenAI
- Histórico curto de conversa por usuário
- Modelo configurável por variável de ambiente
- Endpoint `/health` para verificar o servidor
- Mensagem amigável quando a chave da API não está configurada

## ▶️ Como executar no Windows

### 1. Clone o projeto

```bash
git clone https://github.com/Lehguto12/Chat-Bot-IA.git
cd Chat-Bot-IA
cd "chat bot"
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

Ative:

```bash
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a chave da OpenAI

Na pasta `chat bot`, copie o arquivo `.env.example` e crie um arquivo chamado `.env`.

Exemplo:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
PORT=5000
FLASK_DEBUG=false
```

> Nunca publique sua chave real no GitHub.

### 5. Inicie o chatbot

```bash
python app.py
```

Abra no navegador:

```text
http://127.0.0.1:5000
```

Pronto: você já poderá conversar com o chatbot pela interface web.

## 🩺 Teste rápido

Com o servidor ligado, acesse:

```text
http://127.0.0.1:5000/health
```

O servidor informa se está ativo e se encontrou a variável `OPENAI_API_KEY`.

## 📂 Estrutura principal

```text
chat bot/
├── app.py
├── .env.example
├── requirements.txt
├── core/
│   └── chatbot.py
├── integrations/
├── services/
└── templates/
    └── chat.html
```

## 🔜 Próximas evoluções

- Reativar WhatsApp Cloud API
- Ajustar integração do Telegram
- Persistir histórico no banco de dados
- Implementar autenticação de usuários
- Melhorar suporte a voz
- Publicar o chatbot em um servidor na nuvem

## 👨‍💻 Autor

Desenvolvido por **Leandro Augusto**.

[GitHub](https://github.com/Lehguto12)