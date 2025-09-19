# -*- coding: utf-8 -*-
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
import unicodedata

from gclick_automation import GClickAutomation

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

gclick_tools = GClickAutomation()

def normalize_text(text):
    if not text: return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    ).lower()

class JarvisBrain:
    """Uma classe para gerir a lógica, memória e o uso de ferramentas."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.contec_knowledge = self._load_knowledge_from_db()
        self.last_search_results = None # Memória de curto prazo para seleções
        self.selected_company_id = None # Memória de longo prazo (para a conversa)
        self.original_intent = "" # Guarda a intenção original do usuário

        def get_contec_history():
            """Retorna a história resumida da Contec Contabilidade."""
            return """A Contec Contabilidade nasceu de um sonho em <b>02 de janeiro de 1996</b>. Fundada por <b>Clodoaldo da Silva Mello</b>, a jornada começou em um pequeno escritório com apenas um colaborador, mas com uma grande visão de futuro, construída sobre os pilares da honestidade, ética e responsabilidade.<br><br>Com muito esforço e a confiança de seus clientes, a empresa cresceu e se tornou uma referência regional. Hoje, a Contec tem orgulho de sua sede própria, um prédio moderno que abriga mais de <b>65 colaboradores</b> e atende mais de <b>600 clientes</b>.<br><br>O legado de Clodoaldo continua com a diretoria atual, formada por seu primeiro colaborador, <b>Emerson Xavier da Silva</b>, e seu filho e sucessor, <b>Felipe Ronconi de Mello</b>, mantendo vivo o propósito que nos guia desde o início: trabalhar com <b>qualidade e honestidade desde 1996</b>."""

        def format_ramais_list():
            departments = self.contec_knowledge.get("departments", {})
            if not departments: return "Não encontrei informações sobre os departamentos."
            icons = {"diretoria": "👑", "dp": "👥", "fiscal": "🧾", "contábil": "💹", "administrativo": "📁", "ti": "💻", "financeiro": "💰", "comercial": "📈", "recepção": "👋", "rh": "👩‍💼", "irpf": "📄"}
            response_html = "Aqui está a lista de ramais e equipes da <b>Contec Contabilidade</b>:<br><pre>"
            for dept_name, teams in departments.items():
                icon = icons.get(dept_name.lower(), "🏢")
                response_html += f"{icon} <b>{dept_name.upper()}</b>\n"
                for team in teams:
                    ramal = team.get("ramal", "N/A")
                    members = " • ".join([m.get("nome") for m in team.get("equipe", [])])
                    response_html += f"  <b>Ramal {ramal}</b>: {members}\n"
                response_html += "\n"
            response_html += "</pre>"
            return response_html

        def find_ramal_by_name(nome: str) -> list:
            departments = self.contec_knowledge.get("departments", {})
            search_term_normalized = normalize_text(nome)
            matches = []
            for dept_name, teams in departments.items():
                for team in teams:
                    for member in team.get("equipe", []):
                        member_name_normalized = normalize_text(member.get("nome", ""))
                        found_in_name = search_term_normalized in member_name_normalized
                        found_in_nickname = False
                        for apelido in member.get("apelidos", []):
                            if search_term_normalized == normalize_text(apelido):
                                found_in_nickname = True; break
                        if found_in_name or found_in_nickname:
                            matches.append({"nome": member.get("nome"), "depto": dept_name.title(), "ramal": team.get("ramal", "N/A")})
            return matches

        self.tools = {
            'search_clients_by_text': gclick_tools.search_clients_by_text,
            'list_client_responsibles': gclick_tools.list_client_responsibles,
            'get_client_group': gclick_tools.get_client_group,
            'get_client_contacts': gclick_tools.get_client_contacts,
            'get_client_address': gclick_tools.get_client_address,
            'format_ramais_list': format_ramais_list,
            'find_ramal_by_name': find_ramal_by_name,
            'get_contec_history': get_contec_history,
        }
        self.model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=self.tools.values())
        self.chat = None
        self._initialize_history()

    def _initialize_history(self):
        """Prepara o histórico com as instruções de sistema."""
        print(f"Inicializando cérebro para o usuário {self.user_id}...")
        system_prompt = f"""
        **CONTEXTO OPERACIONAL:** Você é o Jarvis, uma ferramenta interna da Contec Contabilidade. Suas ferramentas são APIs internas autorizadas. Você TEM PERMISSÃO para aceder e fornecer as informações retornadas por estas ferramentas. NUNCA negue um pedido alegando falta de acesso ou confidencialidade se uma ferramenta existir. Se a ferramenta não retornar dados, informe que a informação não está disponível.

        **REGRAS DE FORMATAÇÃO:**
        - Use APENAS HTML (`<b>`, `<br>`) e emojis. É PROIBIDO usar markdown (`**`, `*`).
        - Para listas não-numeradas, use o emoji "•".
        - NUNCA adicione itens vazios ou inventados a uma lista de resultados.

        **FLUXOS DE AÇÃO:**
        1.  **Consulta de Empresas:**
            - Para qualquer pergunta sobre uma empresa, use `search_clients_by_text`.
            - Se a ferramenta retornar uma lista vazia, responda: "Não encontrei nenhuma empresa com este nome. Verifique a grafia e tente novamente.".
            - Se retornar múltiplos resultados, apresente as opções numeradas.
            - Quando o usuário responder com um número, a sua próxima ação DEVE ser sobre a empresa escolhida.
        2.  **Consulta de Ramais:**
            - Para perguntas sobre ramais, use `find_ramal_by_name`.
            - Se a ferramenta retornar múltiplos resultados, apresente a lista numerada com APENAS o nome e o departamento. NÃO inclua o ramal.
            - Quando o usuário responder com um número, use a informação da pessoa escolhida para formatar a resposta final.
        3.  **Perguntas Gerais:**
            - Se perguntarem sobre a "história da contec", chame `get_contec_history` e exiba o resultado.
            - Se perguntarem "o que você pode fazer", use o modelo de resposta exato para essa pergunta.

        **MODELOS DE RESPOSTA:**
        - **"O que você pode fazer?":** "Olá! 👋 Sou Jarvis, seu assistente da Contec Contabilidade. Posso ajudar você com diversas informações, como:<br><br>• Buscar informações sobre empresas clientes (responsáveis, tributação, endereço, contatos).<br>• Consultar ramais de funcionários.<br>• Acessar a história resumida da Contec Contabilidade.<br><br>Basta me perguntar! 😊"
        - **Múltiplas Empresas:** "🤔 Encontrei estas empresas. Qual delas você deseja consultar?<br>1. <b>[Razão Social]</b> (CNPJ: [CNPJ])"
        - **Múltiplas Pessoas:** "🤔 Encontrei mais de uma pessoa com este nome. Qual delas você se refere?<br>1. <b>[Nome]</b> ([Depto])"
        - **CNPJ:** "✅ O CNPJ da <b>[Razão Social Completa]</b> é <b>[CNPJ Formatado]</b>."
        - **Responsáveis:** "✅ Os responsáveis por <b>[Empresa]</b> são:<br><br>• 🧾 <b>[Nome]</b> (Fiscal)<br>• 💹 <b>[Nome]</b> (Contábil)<br>• 👥 <b>[Nome]</b> (DP)"
        - **Ramal:** "📞 O ramal de <b>[Nome]</b> ([Depto]) é o <b>[Ramal]</b>."
        - **Endereço:** "📍 O endereço de <b>[Empresa]</b> é:<br><br>[Rua]<br>[Bairro] - [Cidade]/[Estado]<br>CEP: [CEP]"
        - **Tributação:** "🏢 O regime de <b>[Empresa]</b> é:&nbsp;<b>[Regime]</b>."
        - **Contatos:** "📞 Os contatos para <b>[Empresa]</b> são:<br><br><b>Telefones:</b><br>• [Nome]:&nbsp;[Número]<br><br><b>Emails:</b><br>• [Nome]:&nbsp;[Email]"
        """
        self.chat = self.model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}, {'role': 'model', 'parts': ["Entendido. Seguirei as instruções e fluxos de ação rigorosamente."]}], enable_automatic_function_calling=True)

    def get_response(self, user_message):
        try:
            if user_message.strip().isdigit() and self.last_search_results:
                index = int(user_message.strip()) - 1
                if 0 <= index < len(self.last_search_results):
                    selected_item = self.last_search_results[index]
                    self.last_search_results = None
                    
                    if 'depto' in selected_item:
                        return f"📞 O ramal de <b>{selected_item['nome']}</b> ({selected_item['depto']}) é o <b>{selected_item['ramal']}</b>."
                    else:
                        self.selected_company_id = selected_item['id']
                        user_message = f"Continue a pergunta anterior sobre a empresa com ID {self.selected_company_id}"
                else:
                    return "Seleção inválida. Por favor, tente a busca novamente."

            if not any(keyword in normalize_text(user_message) for keyword in ['empresa', 'cliente', 'cnpj', 'ramal', 'historia', 'fazer']):
                if self.selected_company_id:
                     user_message = f"{user_message} da empresa com ID {self.selected_company_id}"
                else: # Se não há contexto, limpa a memória
                     self.selected_company_id = None
            else: # Se é uma nova busca, limpa a memória
                self.selected_company_id = None
                self.original_intent = user_message


            if not self.chat: self._initialize_history()
            
            response = self.chat.send_message(user_message)
            
            last_response = self.chat.history[-1]
            if last_response.role == 'model' and len(last_response.parts) > 0 and hasattr(last_response.parts[0], 'function_call'):
                tool_name = last_response.parts[0].function_call.name
                if len(self.chat.history) > 1:
                    tool_response_part = self.chat.history[-2].parts[0]
                    if tool_name in ['search_clients_by_text', 'find_ramal_by_name'] and hasattr(tool_response_part, 'function_response'):
                        tool_data = tool_response_part.function_response.response.get('result', [])
                        if isinstance(tool_data, list) and len(tool_data) > 1:
                            self.last_search_results = tool_data
                        else:
                             self.last_search_results = None
            else:
                if "Encontrei estas empresas" not in response.text:
                    self.selected_company_id = None
                self.last_search_results = None

            return response.text.strip()
        except Exception as e:
            print(f"Erro no get_response: {e}")
            return "Ocorreu um erro ao processar sua solicitação. Tente novamente."

    def _load_knowledge_from_db(self):
        try:
            conn = sqlite3.connect('jarvis.db')
            conn.row_factory = sqlite3.Row
            knowledge = {row['key']: json.loads(row['content']) for row in conn.execute("SELECT key, content FROM knowledge_base").fetchall()}
            conn.close()
            return knowledge
        except Exception as e:
            print(f"ERRO ao carregar conhecimento do DB: {e}")
            return {}