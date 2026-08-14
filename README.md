# 🤖 Leandro AI — Chat Bot com Inteligência Artificial

Aplicação web desenvolvida em **Python + Flask + SQLite + OpenAI**, com login, histórico persistente e interface inspirada em assistentes de IA modernos.

## ✅ O que funciona agora

- Cadastro e login de usuários
- Senhas armazenadas com hash
- Sessões de usuário
- Criação de múltiplas conversas
- Histórico salvo em SQLite
- Exclusão de conversas
- Continuidade de contexto usando mensagens anteriores
- Interface responsiva com barra lateral
- Integração com a API da OpenAI
- Endpoint `/health`
- Banco e credenciais ignorados pelo Git

## 🚀 Tecnologias

- Python
- Flask
- SQLite
- HTML/CSS/JavaScript
- OpenAI API
- Werkzeug Security

## ▶️ Como executar no Windows

### 1. Clone o projeto

```bash
git clone https://github.com/Lehguto12/Chat-Bot-IA.git
cd Chat-Bot-IA
cd "chat bot"
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências principais

```bash
pip install -r requirements.txt
```

### 4. Configure o ambiente

Crie um arquivo `.env` na pasta `chat bot` usando `.env.example` como modelo:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
SECRET_KEY=troque-por-uma-chave-longa-e-aleatoria
PORT=5000
FLASK_DEBUG=false
```

Nunca publique sua chave real da API nem sua `SECRET_KEY`.

### 5. Execute

```bash
python app.py
```

Abra:

```text
http://127.0.0.1:5000
```

Na primeira vez, clique em **Criar conta**, faça seu cadastro e comece uma conversa.

## 💾 Banco de dados

O arquivo `chatbot.db` é criado automaticamente na primeira execução. Ele armazena usuários, conversas e mensagens localmente e está incluído no `.gitignore`.

## 📂 Estrutura principal

```text
chat bot/
├── app.py
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-optional.txt
├── core/
│   └── chatbot.py
└── templates/
    ├── login.html
    └── chat.html
```

## 🔌 Integrações opcionais

O repositório ainda contém estruturas para Telegram, WhatsApp, voz e analytics. As dependências dessas funcionalidades foram separadas para não complicar a instalação do chatbot principal.

Para instalá-las futuramente:

```bash
pip install -r requirements-optional.txt
```

## 🔜 Próximas evoluções

- Publicar em um servidor na nuvem
- Recuperação de senha
- Renomear conversas
- Streaming de respostas
- Upload de arquivos
- Reativar WhatsApp e Telegram
- Dashboard de uso

## 👨‍💻 Autor

Desenvolvido por **Leandro Augusto**.

[GitHub](https://github.com/Lehguto12)
