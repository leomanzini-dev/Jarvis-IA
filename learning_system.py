# learning_system.py - Sistema de Aprendizagem e Personalização do Jarvis
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from collections import Counter

class LearningSystem:
    """Sistema de aprendizagem ativa do Jarvis baseado em feedback"""
    
    def __init__(self, db_path: str = "jarvis.db"):
        self.db_path = db_path
    
    def analyze_negative_feedback(self, days_back: int = 7) -> Dict:
        """Analisa feedback negativo dos últimos dias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Data limite
            date_limit = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            # Buscar feedback negativo com correções
            cursor.execute('''
                SELECT user_query, bot_response, correction, timestamp
                FROM feedback 
                WHERE rating = -1 
                AND correction IS NOT NULL 
                AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (date_limit,))
            
            negative_feedback = cursor.fetchall()
            conn.close()
            
            if not negative_feedback:
                return {"message": "Nenhum feedback negativo com correções encontrado"}
            
            # Analisar padrões
            patterns = self._identify_error_patterns(negative_feedback)
            suggestions = self._generate_improvement_suggestions(patterns)
            
            return {
                "total_negative_feedback": len(negative_feedback),
                "patterns": patterns,
                "suggestions": suggestions,
                "period_days": days_back
            }
            
        except Exception as e:
            return {"error": f"Erro ao analisar feedback: {str(e)}"}
    
    def _identify_error_patterns(self, feedback_data: List[Tuple]) -> Dict:
        """Identifica padrões nos erros do Jarvis"""
        patterns = {
            "common_topics": [],
            "frequent_errors": [],
            "correction_examples": []
        }
        
        # Extrair tópicos das perguntas
        topics = []
        error_types = []
        
        for user_query, bot_response, correction, timestamp in feedback_data:
            # Extrair palavras-chave da pergunta
            query_words = re.findall(r'\b\w+\b', user_query.lower())
            topics.extend([word for word in query_words if len(word) > 3])
            
            # Classificar tipo de erro baseado na resposta e correção
            error_type = self._classify_error_type(bot_response, correction)
            if error_type:
                error_types.append(error_type)
            
            # Adicionar exemplo de correção
            patterns["correction_examples"].append({
                "query": user_query,
                "wrong_response": bot_response[:100] + "..." if len(bot_response) > 100 else bot_response,
                "correct_response": correction[:100] + "..." if len(correction) > 100 else correction,
                "timestamp": timestamp
            })
        
        # Contar tópicos mais frequentes
        topic_counts = Counter(topics)
        patterns["common_topics"] = topic_counts.most_common(10)
        
        # Contar tipos de erro mais frequentes
        error_counts = Counter(error_types)
        patterns["frequent_errors"] = error_counts.most_common(5)
        
        return patterns
    
    def _classify_error_type(self, bot_response: str, correction: str) -> str:
        """Classifica o tipo de erro baseado na resposta e correção"""
        bot_lower = bot_response.lower()
        correction_lower = correction.lower()
        
        # Padrões de classificação
        if "não sei" in bot_lower or "não encontrei" in bot_lower:
            return "Falta de conhecimento"
        elif "erro" in bot_lower or "desculpe" in bot_lower:
            return "Erro de processamento"
        elif len(correction) > len(bot_response) * 2:
            return "Resposta incompleta"
        elif any(word in correction_lower for word in ["ramal", "telefone", "contato"]):
            return "Informação de contato incorreta"
        elif any(word in correction_lower for word in ["prazo", "data", "quando"]):
            return "Informação temporal incorreta"
        else:
            return "Informação factual incorreta"
    
    def _generate_improvement_suggestions(self, patterns: Dict) -> List[str]:
        """Gera sugestões de melhoria baseadas nos padrões"""
        suggestions = []
        
        # Sugestões baseadas em tópicos frequentes
        if patterns["common_topics"]:
            top_topic = patterns["common_topics"][0][0]
            suggestions.append(
                f"Considere adicionar mais informações sobre '{top_topic}' à base de conhecimento, "
                f"pois aparece em {patterns['common_topics'][0][1]} feedbacks negativos."
            )
        
        # Sugestões baseadas em tipos de erro
        if patterns["frequent_errors"]:
            top_error = patterns["frequent_errors"][0][0]
            if top_error == "Falta de conhecimento":
                suggestions.append(
                    "Muitos erros são por falta de conhecimento. Considere expandir a base de conhecimento "
                    "ou melhorar a busca de informações relevantes."
                )
            elif top_error == "Informação de contato incorreta":
                suggestions.append(
                    "Há erros frequentes em informações de contato. Verifique e atualize os ramais "
                    "e informações de contato na base de conhecimento."
                )
            elif top_error == "Informação temporal incorreta":
                suggestions.append(
                    "Erros em informações de prazo/data são frequentes. Considere adicionar mais "
                    "informações sobre prazos e datas importantes."
                )
        
        # Sugestão geral se há muitos exemplos de correção
        if len(patterns["correction_examples"]) > 5:
            suggestions.append(
                f"Com {len(patterns['correction_examples'])} correções disponíveis, "
                "considere usar esses dados para fine-tuning do modelo ou atualização do prompt."
            )
        
        return suggestions
    
    def generate_prompt_improvements(self, patterns: Dict) -> str:
        """Gera melhorias para o system prompt baseadas nos padrões"""
        improvements = []
        
        # Adicionar instruções específicas baseadas nos erros
        if patterns.get("frequent_errors"):
            for error_type, count in patterns["frequent_errors"]:
                if error_type == "Falta de conhecimento":
                    improvements.append(
                        "- Quando não souber uma informação, seja específico sobre o que não sabe "
                        "e sugira onde o usuário pode encontrar a informação."
                    )
                elif error_type == "Informação de contato incorreta":
                    improvements.append(
                        "- Sempre verifique cuidadosamente as informações de contato antes de fornecê-las. "
                        "Se não tiver certeza, peça para o usuário confirmar."
                    )
        
        # Adicionar exemplos de correções como few-shot examples
        if patterns.get("correction_examples"):
            improvements.append("\nExemplos de respostas corretas baseadas em feedback:")
            for i, example in enumerate(patterns["correction_examples"][:3]):  # Apenas 3 exemplos
                improvements.append(
                    f"Pergunta: {example['query']}\n"
                    f"Resposta correta: {example['correct_response']}\n"
                )
        
        return "\n".join(improvements)


class PersonalizationSystem:
    """Sistema de personalização baseado em atalhos e histórico do usuário"""
    
    def __init__(self, db_path: str = "jarvis.db"):
        self.db_path = db_path
    
    def analyze_user_interests(self, user_id: int) -> Dict:
        """Analisa os interesses do usuário baseado em atalhos e histórico"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar atalhos do usuário
            cursor.execute('''
                SELECT text, timestamp FROM shortcuts 
                WHERE user_id = ? 
                ORDER BY timestamp DESC
            ''', (user_id,))
            shortcuts = cursor.fetchall()
            
            # Buscar histórico de perguntas (feedback positivo)
            cursor.execute('''
                SELECT user_query, timestamp FROM feedback 
                WHERE user_id = ? AND rating = 1
                ORDER BY timestamp DESC
                LIMIT 50
            ''', (user_id,))
            positive_queries = cursor.fetchall()
            
            conn.close()
            
            # Analisar tópicos de interesse
            interests = self._extract_topics_from_text([s[0] for s in shortcuts] + [q[0] for q in positive_queries])
            
            # Gerar perfil do usuário
            profile = {
                "user_id": user_id,
                "total_shortcuts": len(shortcuts),
                "total_positive_feedback": len(positive_queries),
                "top_interests": interests[:10],
                "last_activity": shortcuts[0][1] if shortcuts else None
            }
            
            return profile
            
        except Exception as e:
            return {"error": f"Erro ao analisar interesses: {str(e)}"}
    
    def _extract_topics_from_text(self, texts: List[str]) -> List[Tuple[str, int]]:
        """Extrai tópicos de interesse de uma lista de textos"""
        # Palavras-chave relevantes para contabilidade
        relevant_keywords = {
            'ferias', 'salario', 'folha', 'pagamento', 'rescisao', 'admissao',
            'nota', 'fiscal', 'imposto', 'icms', 'ipi', 'pis', 'cofins',
            'balanco', 'contabil', 'demonstracao', 'resultado', 'patrimonio',
            'cliente', 'fornecedor', 'ramal', 'contato', 'departamento',
            'prazo', 'vencimento', 'entrega', 'documento', 'certidao'
        }
        
        # Extrair palavras de todos os textos
        all_words = []
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            # Filtrar apenas palavras relevantes
            relevant_words = [word for word in words if word in relevant_keywords and len(word) > 3]
            all_words.extend(relevant_words)
        
        # Contar frequência
        word_counts = Counter(all_words)
        return word_counts.most_common()
    
    def generate_personalized_suggestions(self, user_id: int) -> List[str]:
        """Gera sugestões personalizadas para o usuário"""
        profile = self.analyze_user_interests(user_id)
        
        if "error" in profile:
            return ["Como posso ajudá-lo hoje?"]
        
        suggestions = []
        
        # Sugestões baseadas nos interesses principais
        if profile.get("top_interests"):
            for topic, count in profile["top_interests"][:3]:
                if topic == "ferias":
                    suggestions.append("Precisa de informações sobre férias?")
                elif topic == "fiscal":
                    suggestions.append("Tem dúvidas sobre questões fiscais?")
                elif topic == "salario":
                    suggestions.append("Quer saber sobre folha de pagamento?")
                elif topic == "cliente":
                    suggestions.append("Precisa consultar dados de algum cliente?")
                elif topic == "prazo":
                    suggestions.append("Quer verificar prazos importantes?")
        
        # Sugestões padrão se não há interesses específicos
        if not suggestions:
            suggestions = [
                "Como posso ajudá-lo hoje?",
                "Precisa de alguma informação específica?",
                "Tem alguma dúvida sobre processos da empresa?"
            ]
        
        return suggestions[:3]  # Máximo 3 sugestões
    
    def update_user_profile(self, user_id: int, new_data: Dict) -> bool:
        """Atualiza o perfil do usuário com novas informações"""
        try:
            # Por enquanto, apenas salva como um novo atalho se for relevante
            if "interest" in new_data:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO shortcuts (user_id, text, timestamp)
                    VALUES (?, ?, ?)
                ''', (user_id, f"Interesse: {new_data['interest']}", datetime.now().isoformat()))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            print(f"Erro ao atualizar perfil: {e}")
            return False


class FeedbackAnalyzer:
    """Analisador de feedback para relatórios administrativos"""
    
    def __init__(self, db_path: str = "jarvis.db"):
        self.db_path = db_path
    
    def generate_weekly_report(self) -> Dict:
        """Gera relatório semanal de feedback e aprendizagem"""
        try:
            learning_system = LearningSystem(self.db_path)
            
            # Analisar feedback da semana
            weekly_analysis = learning_system.analyze_negative_feedback(days_back=7)
            
            # Estatísticas gerais
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Feedback da semana
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('''
                SELECT rating, COUNT(*) as count 
                FROM feedback 
                WHERE timestamp >= ? 
                GROUP BY rating
            ''', (week_ago,))
            
            weekly_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Usuários mais ativos
            cursor.execute('''
                SELECT u.username, COUNT(f.id) as feedback_count
                FROM feedback f
                JOIN users u ON f.user_id = u.id
                WHERE f.timestamp >= ?
                GROUP BY f.user_id, u.username
                ORDER BY feedback_count DESC
                LIMIT 5
            ''', (week_ago,))
            
            active_users = [{"username": row[0], "feedback_count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            # Compilar relatório
            report = {
                "period": "Últimos 7 dias",
                "generated_at": datetime.now().isoformat(),
                "feedback_stats": {
                    "positive": weekly_stats.get(1, 0),
                    "negative": weekly_stats.get(-1, 0),
                    "total": sum(weekly_stats.values())
                },
                "learning_analysis": weekly_analysis,
                "active_users": active_users,
                "recommendations": self._generate_recommendations(weekly_analysis, weekly_stats)
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Erro ao gerar relatório: {str(e)}"}
    
    def _generate_recommendations(self, analysis: Dict, stats: Dict) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        total_feedback = sum(stats.values())
        negative_feedback = stats.get(-1, 0)
        
        if total_feedback == 0:
            recommendations.append("Incentive os usuários a fornecerem mais feedback para melhorar o sistema.")
        elif negative_feedback / total_feedback > 0.3:
            recommendations.append("Taxa de feedback negativo alta (>30%). Revise a base de conhecimento.")
        elif negative_feedback / total_feedback < 0.1:
            recommendations.append("Excelente taxa de satisfação! Continue monitorando a qualidade.")
        
        # Recomendações baseadas na análise de padrões
        if analysis.get("suggestions"):
            recommendations.extend(analysis["suggestions"][:2])  # Adicionar até 2 sugestões
        
        return recommendations

