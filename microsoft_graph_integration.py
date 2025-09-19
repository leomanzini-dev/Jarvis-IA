# microsoft_graph_integration.py - Módulo de Integração com Microsoft 365
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class MicrosoftGraphClient:
    """Cliente para interagir com a Microsoft Graph API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Faz uma requisição para a Microsoft Graph API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para Microsoft Graph: {e}")
            return {"error": str(e)}
    
    # === FUNCIONALIDADES DE E-MAIL ===
    
    def get_unread_emails(self, sender_email: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Obtém e-mails não lidos, opcionalmente filtrados por remetente"""
        endpoint = "/me/messages"
        
        # Construir filtros
        filters = ["isRead eq false"]
        if sender_email:
            filters.append(f"from/emailAddress/address eq '{sender_email}'")
        
        filter_query = " and ".join(filters)
        params = f"?$filter={filter_query}&$top={limit}&$orderby=receivedDateTime desc"
        
        result = self._make_request("GET", endpoint + params)
        return result.get("value", [])
    
    def get_emails_summary(self, days_back: int = 7) -> str:
        """Gera um resumo dos e-mails recentes"""
        # Calcular data de início
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        endpoint = "/me/messages"
        params = f"?$filter=receivedDateTime ge {start_date}&$top=20&$orderby=receivedDateTime desc"
        
        result = self._make_request("GET", endpoint + params)
        emails = result.get("value", [])
        
        if not emails:
            return f"Não há e-mails nos últimos {days_back} dias."
        
        # Gerar resumo
        unread_count = sum(1 for email in emails if not email.get("isRead", True))
        total_count = len(emails)
        
        summary = f"Resumo dos últimos {days_back} dias:\n"
        summary += f"- Total de e-mails: {total_count}\n"
        summary += f"- E-mails não lidos: {unread_count}\n\n"
        
        if unread_count > 0:
            summary += "E-mails não lidos recentes:\n"
            for email in emails[:5]:  # Mostrar apenas os 5 mais recentes
                if not email.get("isRead", True):
                    sender = email.get("from", {}).get("emailAddress", {}).get("name", "Desconhecido")
                    subject = email.get("subject", "Sem assunto")
                    received = email.get("receivedDateTime", "")
                    summary += f"- {sender}: {subject} ({received[:10]})\n"
        
        return summary
    
    def send_email(self, to_email: str, subject: str, body: str, cc_emails: Optional[List[str]] = None) -> Dict:
        """Envia um e-mail"""
        endpoint = "/me/sendMail"
        
        # Construir lista de destinatários
        to_recipients = [{"emailAddress": {"address": to_email}}]
        
        cc_recipients = []
        if cc_emails:
            cc_recipients = [{"emailAddress": {"address": email}} for email in cc_emails]
        
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": to_recipients,
                "ccRecipients": cc_recipients
            }
        }
        
        return self._make_request("POST", endpoint, email_data)
    
    # === FUNCIONALIDADES DE CALENDÁRIO ===
    
    def get_upcoming_events(self, days_ahead: int = 7, limit: int = 10) -> List[Dict]:
        """Obtém eventos futuros do calendário"""
        start_time = datetime.now().isoformat()
        end_time = (datetime.now() + timedelta(days=days_ahead)).isoformat()
        
        endpoint = "/me/calendar/events"
        params = f"?$filter=start/dateTime ge '{start_time}' and end/dateTime le '{end_time}'&$top={limit}&$orderby=start/dateTime"
        
        result = self._make_request("GET", endpoint + params)
        return result.get("value", [])
    
    def check_availability(self, date_str: str, start_hour: int = 9, end_hour: int = 17) -> Dict:
        """Verifica disponibilidade em uma data específica"""
        try:
            # Converter string de data para datetime
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            start_time = target_date.replace(hour=start_hour, minute=0).isoformat()
            end_time = target_date.replace(hour=end_hour, minute=0).isoformat()
            
            endpoint = "/me/calendar/events"
            params = f"?$filter=start/dateTime ge '{start_time}' and end/dateTime le '{end_time}'"
            
            result = self._make_request("GET", endpoint + params)
            events = result.get("value", [])
            
            # Calcular horários livres
            busy_periods = []
            for event in events:
                event_start = event.get("start", {}).get("dateTime", "")
                event_end = event.get("end", {}).get("dateTime", "")
                if event_start and event_end:
                    busy_periods.append({
                        "start": event_start,
                        "end": event_end,
                        "subject": event.get("subject", "Evento sem título")
                    })
            
            return {
                "date": date_str,
                "total_events": len(events),
                "busy_periods": busy_periods,
                "is_free": len(events) == 0
            }
            
        except ValueError:
            return {"error": "Formato de data inválido. Use YYYY-MM-DD"}
    
    def create_meeting(self, subject: str, start_time: str, end_time: str, 
                      attendees: List[str], body: Optional[str] = None) -> Dict:
        """Cria uma reunião no calendário"""
        endpoint = "/me/calendar/events"
        
        # Construir lista de participantes
        attendee_list = []
        for email in attendees:
            attendee_list.append({
                "emailAddress": {
                    "address": email,
                    "name": email.split("@")[0]  # Usar parte antes do @ como nome
                },
                "type": "required"
            })
        
        event_data = {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body or f"Reunião: {subject}"
            },
            "start": {
                "dateTime": start_time,
                "timeZone": "America/Sao_Paulo"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "America/Sao_Paulo"
            },
            "attendees": attendee_list,
            "allowNewTimeProposals": True
        }
        
        return self._make_request("POST", endpoint, event_data)
    
    # === FUNCIONALIDADES DE TEAMS (FUTURO) ===
    
    def get_teams_channels(self) -> List[Dict]:
        """Obtém lista de canais do Teams (funcionalidade futura)"""
        # Esta funcionalidade requer permissões específicas do Teams
        # e pode ser implementada em versões futuras
        return [{"message": "Funcionalidade de Teams em desenvolvimento"}]
    
    def send_teams_message(self, channel_id: str, message: str) -> Dict:
        """Envia mensagem para um canal do Teams (funcionalidade futura)"""
        # Esta funcionalidade requer permissões específicas do Teams
        # e pode ser implementada em versões futuras
        return {"message": "Funcionalidade de Teams em desenvolvimento"}


class MockMicrosoftGraphClient:
    """Cliente mock para testes sem autenticação real"""
    
    def __init__(self):
        self.mock_data = {
            "emails": [
                {
                    "id": "1",
                    "subject": "Relatório Mensal - Setembro",
                    "from": {"emailAddress": {"name": "João Silva", "address": "joao@contec.com.br"}},
                    "receivedDateTime": "2024-09-10T09:30:00Z",
                    "isRead": False,
                    "bodyPreview": "Segue o relatório mensal de setembro com os principais indicadores..."
                },
                {
                    "id": "2", 
                    "subject": "Reunião de Planejamento",
                    "from": {"emailAddress": {"name": "Maria Santos", "address": "maria@contec.com.br"}},
                    "receivedDateTime": "2024-09-10T08:15:00Z",
                    "isRead": True,
                    "bodyPreview": "Confirmo a reunião de planejamento para amanhã às 14h..."
                }
            ],
            "events": [
                {
                    "id": "1",
                    "subject": "Reunião de Equipe",
                    "start": {"dateTime": "2024-09-11T14:00:00"},
                    "end": {"dateTime": "2024-09-11T15:00:00"},
                    "attendees": [{"emailAddress": {"name": "Felipe", "address": "felipe@contec.com.br"}}]
                },
                {
                    "id": "2",
                    "subject": "Apresentação Trimestral", 
                    "start": {"dateTime": "2024-09-12T10:00:00"},
                    "end": {"dateTime": "2024-09-12T11:30:00"},
                    "attendees": [{"emailAddress": {"name": "Diretoria", "address": "diretoria@contec.com.br"}}]
                }
            ]
        }
    
    def get_unread_emails(self, sender_email: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Retorna e-mails não lidos mock"""
        unread_emails = [email for email in self.mock_data["emails"] if not email["isRead"]]
        if sender_email:
            unread_emails = [email for email in unread_emails 
                           if email["from"]["emailAddress"]["address"] == sender_email]
        return unread_emails[:limit]
    
    def get_emails_summary(self, days_back: int = 7) -> str:
        """Gera resumo mock dos e-mails"""
        total = len(self.mock_data["emails"])
        unread = len([e for e in self.mock_data["emails"] if not e["isRead"]])
        
        summary = f"Resumo dos últimos {days_back} dias (DEMO):\n"
        summary += f"- Total de e-mails: {total}\n"
        summary += f"- E-mails não lidos: {unread}\n\n"
        
        if unread > 0:
            summary += "E-mails não lidos:\n"
            for email in self.mock_data["emails"]:
                if not email["isRead"]:
                    sender = email["from"]["emailAddress"]["name"]
                    subject = email["subject"]
                    summary += f"- {sender}: {subject}\n"
        
        return summary
    
    def send_email(self, to_email: str, subject: str, body: str, cc_emails: Optional[List[str]] = None) -> Dict:
        """Simula envio de e-mail"""
        return {
            "success": True,
            "message": f"E-mail enviado com sucesso para {to_email} (DEMO MODE)",
            "subject": subject
        }
    
    def get_upcoming_events(self, days_ahead: int = 7, limit: int = 10) -> List[Dict]:
        """Retorna eventos futuros mock"""
        return self.mock_data["events"][:limit]
    
    def check_availability(self, date_str: str, start_hour: int = 9, end_hour: int = 17) -> Dict:
        """Verifica disponibilidade mock"""
        # Simular alguns horários ocupados
        if date_str == "2024-09-11":
            return {
                "date": date_str,
                "total_events": 1,
                "busy_periods": [
                    {
                        "start": "2024-09-11T14:00:00",
                        "end": "2024-09-11T15:00:00", 
                        "subject": "Reunião de Equipe"
                    }
                ],
                "is_free": False
            }
        else:
            return {
                "date": date_str,
                "total_events": 0,
                "busy_periods": [],
                "is_free": True
            }
    
    def create_meeting(self, subject: str, start_time: str, end_time: str,
                      attendees: List[str], body: Optional[str] = None) -> Dict:
        """Simula criação de reunião"""
        return {
            "success": True,
            "message": f"Reunião '{subject}' criada com sucesso (DEMO MODE)",
            "id": "mock_event_123",
            "attendees": attendees
        }

