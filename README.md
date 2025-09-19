# Jarvis - Assistente Inteligente da Contec Contabilidade (Versão Aprimorada)

## 📋 Visão Geral

O Jarvis foi concebido para ser muito mais do que um simples chatbot. Ele é uma plataforma central de inteligência e automação, criada sob medida para o ambiente da Contec Contabilidade.

Esta versão aprimorada inclui quatro novos módulos principais:

1. **Módulo 1: Assistente Proativo** - Integração com Microsoft 365 (Outlook e Teams)
2. **Módulo 2: Automação de Processos** - Capacidade de escrita na API G-Click
3. **Módulo 3: Inteligência Aprimorada** - Sistema de aprendizagem ativa e personalização
4. **Módulo 4: Experiência do Usuário Avançada** - Streaming em tempo real e interação por voz

## 🚀 Novas Funcionalidades

### 📧 Gestão de E-mail e Agenda (Microsoft 365)

- **Verificar e-mails não lidos**: "Tenho algum e-mail novo do cliente X?"
- **Resumir e-mails**: "Resume os meus e-mails não lidos"
- **Enviar e-mails**: "Jarvis, envia um e-mail para o cliente Y confirmando a reunião"
- **Verificar agenda**: "Quais são os meus próximos compromissos?"
- **Verificar disponibilidade**: "Estou livre na terça-feira à tarde?"
- **Agendar reuniões**: "Marca uma reunião com o Felipe para amanhã às 15h"

### 🔄 Automação G-Click

- **Criar chamados**: "Jarvis, abre um chamado no G-Click para o cliente Z com o assunto 'Problema na nota fiscal'"
- **Atualizar dados de clientes**: "Adiciona uma nota ao cliente com CNPJ X de que o pagamento foi confirmado"
- **Buscar informações de clientes**: Integração automática com a base de dados do G-Click

### 🧠 Inteligência Aprimorada

- **Aprendizagem ativa**: Sistema que analisa feedback negativo e gera melhorias automaticamente
- **Personalização**: Adaptação baseada nos atalhos e histórico de cada usuário
- **Relatórios de aprendizagem**: Análise semanal de padrões e sugestões de melhoria

### ⚡ Experiência Avançada

- **Respostas em streaming**: Texto aparece palavra por palavra em tempo real
- **Comando por voz**: Botão de microfone para fazer perguntas falando
- **Interface aprimorada**: Novos controles e feedback visual

## 🛠️ Arquitetura Técnica

### Estrutura de Arquivos

```
jarvis_enhanced/
├── app_simple.py                 # Aplicação Flask principal (versão simplificada)
├── jarvis_brain_simple.py        # Lógica principal do assistente
├── microsoft_graph_integration.py # Integração com Microsoft 365
├── gclick_automation.py          # Automação de processos G-Click
├── learning_system.py            # Sistema de aprendizagem e personalização
├── static/
│   ├── css/
│   │   ├── chat_style.css        # Estilos do chat
│   │   ├── admin_style.css       # Estilos do painel admin
│   │   └── login_style.css       # Estilos da página de login
│   ├── js/
│   │   ├── enhanced_chat.js      # JavaScript aprimorado com streaming e voz
│   │   ├── admin.js              # JavaScript do painel admin
│   │   └── script.js             # JavaScript original
│   └── img/
│       └── icon.png              # Ícone do Jarvis
├── templates/
│   ├── enhanced_index.html       # Interface aprimorada do chat
│   ├── index.html                # Interface original
│   ├── admin.html                # Painel administrativo
│   └── login.html                # Página de login
├── knowledge_base.json           # Base de conhecimento
├── jarvis.db                     # Banco de dados SQLite
└── README.md                     # Esta documentação
```

### Componentes Principais

#### 1. JarvisBrainEnhanced
- Classe principal que gerencia todas as funcionalidades
- Detecção de intenção para rotear comandos
- Integração com Microsoft Graph e G-Click
- Sistema de aprendizagem baseado em feedback

#### 2. MicrosoftGraphClient
- Integração com APIs do Microsoft 365
- Gestão de e-mails (Outlook)
- Gestão de calendário
- Autenticação OAuth (em desenvolvimento)

#### 3. GClickAutomation
- Cliente para automação de processos no G-Click
- Criação e gestão de tarefas/chamados
- Gestão de dados de clientes
- Parser de comandos em linguagem natural

#### 4. LearningSystem
- Análise de feedback negativo
- Identificação de padrões de erro
- Geração de sugestões de melhoria
- Sistema de personalização por usuário

## 📦 Instalação e Configuração

### Pré-requisitos

```bash
pip install flask flask-login bcrypt python-dotenv google-generativeai python-dateutil
```

### Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes configurações:

```env
# API do Google Gemini
GEMINI_API_KEY=sua_chave_gemini_aqui

# Credenciais G-Click (opcional para modo demo)
GCLICK_CLIENT_ID=seu_client_id_gclick
GCLICK_CLIENT_SECRET=seu_client_secret_gclick

# Microsoft Graph (futuro)
MICROSOFT_CLIENT_ID=seu_client_id_microsoft
MICROSOFT_CLIENT_SECRET=seu_client_secret_microsoft
```

### Execução

```bash
# Inicializar banco de dados (se necessário)
python init_db.py

# Executar aplicação
python app_simple.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🎯 Como Usar as Novas Funcionalidades

### Comandos de E-mail

```
"Tenho e-mails novos?"
"Resume meus e-mails não lidos"
"Envia e-mail para joao@contec.com.br com assunto Reunião"
```

### Comandos de Agenda

```
"Quais são meus próximos compromissos?"
"Estou livre amanhã?"
"Estou livre no dia 15/09?"
"Agenda reunião com felipe@contec.com.br para amanhã às 14h"
```

### Comandos G-Click

```
"Abre chamado para cliente CNPJ 12345678000100 com assunto Problema na nota fiscal"
"Adiciona nota ao cliente CNPJ 12345678000100: Pagamento confirmado"
```

### Funcionalidades de Voz

1. Clique no botão do microfone (🎤)
2. Fale sua pergunta
3. O texto será reconhecido automaticamente
4. Pressione Enter ou clique em Enviar

### Streaming em Tempo Real

- Ativado por padrão
- Toggle disponível no botão ⚡
- Respostas aparecem palavra por palavra

## 🔧 Configuração Avançada

### Integração Microsoft 365

Para ativar a integração real com Microsoft 365:

1. Registre uma aplicação no Azure AD
2. Configure as permissões necessárias:
   - `Mail.Read`
   - `Mail.Send`
   - `Calendars.Read`
   - `Calendars.ReadWrite`
3. Adicione as credenciais ao arquivo `.env`
4. Substitua `MockMicrosoftGraphClient` por `MicrosoftGraphClient` no código

### Integração G-Click

Para ativar a integração real com G-Click:

1. Obtenha credenciais de API do G-Click
2. Configure `GCLICK_CLIENT_ID` e `GCLICK_CLIENT_SECRET`
3. Substitua `MockGClickAutomation` por `GClickAutomation` no código

## 📊 Painel Administrativo

Acesse `/admin` com credenciais de administrador para:

- Gerenciar base de conhecimento
- Visualizar feedback dos usuários
- Analisar métricas de uso
- Gerar relatórios de aprendizagem

## 🔍 Monitoramento e Análise

### Métricas Disponíveis

- Taxa de satisfação dos usuários
- Tópicos mais consultados
- Padrões de erro identificados
- Sugestões de melhoria automáticas

### Relatórios Automáticos

O sistema gera relatórios semanais com:

- Análise de feedback negativo
- Identificação de lacunas na base de conhecimento
- Sugestões de melhorias no prompt
- Estatísticas de uso por usuário

## 🚧 Limitações Atuais

### Modo Demo

- Microsoft Graph: Usando dados simulados
- G-Click: Usando dados simulados
- Reconhecimento de voz: Depende do navegador

### Dependências Externas

- Requer conexão com internet para APIs
- Gemini API necessária para funcionamento
- Navegadores modernos para funcionalidades de voz

## 🔮 Roadmap Futuro

### Próximas Funcionalidades

1. **Integração Teams**: Envio de mensagens e resumos de conversas
2. **IA de Documentos**: Análise automática de PDFs e contratos
3. **Dashboards Personalizados**: Métricas específicas por departamento
4. **Automação Avançada**: Workflows complexos entre sistemas
5. **Mobile App**: Aplicativo nativo para iOS e Android

### Melhorias Técnicas

1. **Cache Inteligente**: Redução de chamadas às APIs
2. **Processamento Offline**: Funcionalidades básicas sem internet
3. **Segurança Aprimorada**: Criptografia end-to-end
4. **Performance**: Otimização de consultas e respostas
5. **Escalabilidade**: Suporte a múltiplas empresas

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste thoroughly
5. Submeta um pull request

## 📞 Suporte

Para suporte técnico ou dúvidas:

- **E-mail**: informatica@contec1996.com.br
- **Documentação**: Este README
- **Issues**: Use o sistema de issues do repositório

## 📄 Licença

Este projeto é propriedade da Contec Contabilidade. Todos os direitos reservados.

---

**Versão**: 2.0.0  
**Data**: Setembro 2024  
**Desenvolvido por**: Leonardo Emanuel Manzini

