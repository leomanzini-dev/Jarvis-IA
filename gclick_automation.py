# -*- coding: utf-8 -*-
import os
import requests
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
import re

load_dotenv()

def _format_cnpj(cnpj: str) -> str:
    """Formata uma string de CNPJ para o padrão 00.000.000/0000-00."""
    if not cnpj or not cnpj.isdigit() or len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

class GClickAutomation:
    """Cliente para automação de processos no G-Click."""
    
    def __init__(self):
        self.client_id = os.environ.get("GCLICK_CLIENT_ID")
        self.client_secret = os.environ.get("GCLICK_CLIENT_SECRET")
        self.base_url = "https://api.gclick.com.br"
        
        if not self.client_id or not self.client_secret:
            print("ERRO CRÍTICO: Credenciais G-Click não encontradas no arquivo .env")

    def _get_access_token(self) -> str:
        data = {'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'client_credentials'}
        response = requests.post(f"{self.base_url}/oauth/token", data=data, timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Any:
        try:
            token = self._get_access_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method.upper(), url, headers=headers, params=params, json=data, timeout=30)
            response.raise_for_status()
            return response.json() if response.content else {"success": True}
        except Exception as e:
            print(f"ERRO na chamada à API G-CLICK: {e}")
            return {"error": str(e)}

    def search_clients_by_text(self, search_text: str) -> List[Dict]:
        """Busca clientes de forma inteligente, tentando múltiplas variações e filtrando por relevância."""
        
        def _filter_and_format(results, query):
            if not isinstance(results, list):
                return []
            
            query_keywords = {word for word in re.split(r'[\s.-/]', query.lower()) if word}
            
            filtered = []
            for c in results:
                company_name_lower = c.get("nome", "").lower()
                if all(keyword in company_name_lower for keyword in query_keywords):
                    filtered.append({
                        "id": c.get("id"),
                        "nome": c.get("nome"),
                        "inscricao": _format_cnpj(c.get("inscricao"))
                    })
            return filtered

        search_variations = [
            search_text,
            search_text.replace(' ', '-'),
            re.sub(r'[.\s]', '', search_text),
            re.sub(r'[\s.-/]', '', search_text)
        ]
        search_variations = list(dict.fromkeys(search_variations))

        for term in search_variations:
            if not term: continue
            results = self._make_request("GET", "/clientes/search", params={'texto': term})
            filtered_results = _filter_and_format(results, search_text)
            if filtered_results:
                return filtered_results

        return []

    def list_client_responsibles(self, client_id: int) -> List[Dict]:
        endpoint = f"/clientes/{int(client_id)}/responsaveis"
        result = self._make_request("GET", endpoint)
        if not result or isinstance(result, dict) and "error" in result: return []
        data_list = result if isinstance(result, list) else next((v for v in result.values() if isinstance(v, list)), [])
        return [{"nome": r.get("nome"), "cargo": r.get("cargo", {}).get("nome", "N/A")} for r in data_list if isinstance(r, dict) and r.get("nome")]

    def get_client_group(self, client_id: int) -> str:
        endpoint = f"/clientes/{int(client_id)}"
        client_details = self._make_request("GET", endpoint)
        if not client_details or isinstance(client_details, dict) and "error" in client_details:
             return "Não foi possível obter os detalhes da empresa."
        if 'grupos' in client_details and isinstance(client_details['grupos'], list) and client_details['grupos']:
            group_names = [group.get('nome') for group in client_details['grupos'] if group.get('nome')]
            if group_names: return ", ".join(group_names)
        return "Não possui um regime tributário associado."

    def get_client_contacts(self, client_id: int) -> Dict:
        endpoint = f"/clientes/{int(client_id)}"
        client_details = self._make_request("GET", endpoint)
        if not client_details or isinstance(client_details, dict) and "error" in client_details:
            return {"error": "Não foi possível obter os detalhes da empresa."}
        return { "telefones": client_details.get("telefones", []), "emails": client_details.get("emails", []) }
    
    def get_client_address(self, client_id: int) -> Dict:
        endpoint = f"/clientes/{int(client_id)}"
        client_details = self._make_request("GET", endpoint)
        if not client_details or isinstance(client_details, dict) and "error" in client_details:
            return {"error": "Não foi possível obter os detalhes da empresa."}
        return client_details.get("endereco", {})