from functools import wraps
from flask import request, jsonify
from jose import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'sua_chave_secreta')
        self.algorithm = 'HS256'
        self.token_expiration = timedelta(hours=24)
        self.socket_users = {}
    
    def generate_token(self, user_id: str) -> str:
        """Gera um token JWT para o usuário"""
        expiration = datetime.utcnow() + self.token_expiration
        payload = {
            'user_id': user_id,
            'exp': expiration
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verifica se o token é válido e retorna o payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.JWTError:
            return None
    
    def require_auth(self, f):
        """Decorator para proteger rotas que requerem autenticação"""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'Token não fornecido'}), 401
            
            try:
                token = auth_header.split(' ')[1]
                payload = self.verify_token(token)
                
                if not payload:
                    return jsonify({'error': 'Token inválido'}), 401
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': str(e)}), 401
                
        return decorated
    
    def validate_socket_connection(self, request):
        """Valida conexão WebSocket"""
        token = request.args.get('token')
        if not token:
            return False
            
        payload = self.verify_token(token)
        if not payload:
            return False
            
        self.socket_users[request.sid] = payload['user_id']
        return True
    
    def get_user_from_socket(self, sid: str) -> Optional[str]:
        """Obtém ID do usuário a partir do ID do socket"""
        return self.socket_users.get(sid)
    
    def remove_socket_user(self, sid: str):
        """Remove usuário quando socket é desconectado"""
        if sid in self.socket_users:
            del self.socket_users[sid] 