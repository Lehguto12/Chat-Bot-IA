from datetime import datetime
from typing import Dict, List
import json
import os
from pymongo import MongoClient

class AnalyticsService:
    def __init__(self):
        self.mongo_client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.mongo_client['chatbot_analytics']
        self.interactions = self.db['interactions']
        self.metrics = self.db['metrics']
    
    def log_interaction(self, user_id: str, message: str, response: str):
        """Registra uma interação do usuário"""
        interaction = {
            'user_id': user_id,
            'message': message,
            'response': response,
            'timestamp': datetime.utcnow(),
            'platform': 'web'  # Pode ser atualizado para outras plataformas
        }
        self.interactions.insert_one(interaction)
    
    def get_user_interactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Obtém histórico de interações de um usuário"""
        return list(self.interactions.find(
            {'user_id': user_id},
            {'_id': 0}
        ).sort('timestamp', -1).limit(limit))
    
    def calculate_metrics(self):
        """Calcula métricas gerais do chatbot"""
        total_interactions = self.interactions.count_documents({})
        unique_users = len(self.interactions.distinct('user_id'))
        
        # Calcula tempo médio de resposta
        interactions = list(self.interactions.find(
            {},
            {'timestamp': 1}
        ).sort('timestamp', -1).limit(1000))
        
        avg_response_time = 0
        if len(interactions) > 1:
            time_diffs = []
            for i in range(len(interactions) - 1):
                diff = (interactions[i]['timestamp'] - interactions[i+1]['timestamp']).total_seconds()
                time_diffs.append(diff)
            avg_response_time = sum(time_diffs) / len(time_diffs)
        
        metrics = {
            'total_interactions': total_interactions,
            'unique_users': unique_users,
            'avg_response_time': avg_response_time,
            'timestamp': datetime.utcnow()
        }
        
        self.metrics.insert_one(metrics)
        return metrics
    
    def get_platform_usage(self) -> Dict[str, int]:
        """Obtém estatísticas de uso por plataforma"""
        pipeline = [
            {'$group': {
                '_id': '$platform',
                'count': {'$sum': 1}
            }}
        ]
        results = list(self.interactions.aggregate(pipeline))
        return {r['_id']: r['count'] for r in results}
    
    def get_user_engagement(self, user_id: str) -> Dict:
        """Calcula métricas de engajamento do usuário"""
        user_interactions = list(self.interactions.find({'user_id': user_id}))
        
        if not user_interactions:
            return {
                'total_interactions': 0,
                'avg_response_time': 0,
                'last_interaction': None
            }
        
        # Calcula tempo médio entre interações
        time_diffs = []
        for i in range(len(user_interactions) - 1):
            diff = (user_interactions[i]['timestamp'] - user_interactions[i+1]['timestamp']).total_seconds()
            time_diffs.append(diff)
        
        avg_response_time = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        
        return {
            'total_interactions': len(user_interactions),
            'avg_response_time': avg_response_time,
            'last_interaction': user_interactions[0]['timestamp']
        } 