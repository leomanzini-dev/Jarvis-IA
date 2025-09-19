# Guia de Implementação - Jarvis Aprimorado

## 🎯 Objetivo

Este guia fornece instruções detalhadas para implementar as novas funcionalidades do Jarvis na Contec Contabilidade, incluindo integração com Microsoft 365, automação G-Click, e melhorias na experiência do usuário.

## 📋 Pré-requisitos

### Técnicos
- Python 3.8+
- Flask e dependências
- Acesso às APIs do Google Gemini
- Credenciais Microsoft 365 (opcional)
- Credenciais G-Click (opcional)

### Organizacionais
- Aprovação da diretoria para integrações
- Treinamento da equipe de TI
- Plano de migração dos usuários

## 🚀 Fases de Implementação

### Fase 1: Preparação e Testes (Semana 1-2)

#### 1.1 Configuração do Ambiente de Desenvolvimento

```bash
# 1. Clonar o projeto aprimorado
git clone <repositorio-jarvis-enhanced>
cd jarvis-enhanced

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com as credenciais necessárias

# 4. Inicializar banco de dados
python init_db.py

# 5. Testar aplicação
python app_simple.py
```

#### 1.2 Testes das Funcionalidades

**Teste 1: Funcionalidades Básicas**
- [ ] Login e autenticação
- [ ] Chat básico funcionando
- [ ] Painel administrativo acessível
- [ ] Base de conhecimento carregando

**Teste 2: Novas Funcionalidades (Modo Demo)**
- [ ] Comandos de e-mail simulados
- [ ] Comandos de agenda simulados
- [ ] Comandos G-Click simulados
- [ ] Streaming de respostas
- [ ] Reconhecimento de voz (se suportado pelo navegador)

#### 1.3 Validação com Usuários Piloto

- Selecionar 3-5 usuários para testes
- Coletar feedback sobre usabilidade
- Identificar bugs e melhorias necessárias

### Fase 2: Integração Microsoft 365 (Semana 3-4)

#### 2.1 Configuração Azure AD

```bash
# 1. Registrar aplicação no Azure Portal
# - Nome: Jarvis Contec
# - Tipo: Web app
# - Redirect URI: https://jarvis.contec.com.br/auth/callback

# 2. Configurar permissões
# - Mail.Read
# - Mail.Send  
# - Calendars.Read
# - Calendars.ReadWrite
# - User.Read

# 3. Gerar client secret
# 4. Adicionar ao .env
```

#### 2.2 Implementação da Autenticação OAuth

```python
# Adicionar ao app_simple.py
from msal import ConfidentialClientApplication

@app.route('/auth/login')
def auth_login():
    # Implementar fluxo OAuth
    pass

@app.route('/auth/callback')
def auth_callback():
    # Processar callback do Azure
    pass
```

#### 2.3 Ativação da Integração Real

```python
# Em jarvis_brain_simple.py, substituir:
# self.graph_client = MockMicrosoftGraphClient()
# Por:
# self.graph_client = MicrosoftGraphClient(access_token)
```

#### 2.4 Testes de Integração

- [ ] Autenticação OAuth funcionando
- [ ] Leitura de e-mails reais
- [ ] Envio de e-mails de teste
- [ ] Consulta de calendário
- [ ] Agendamento de reuniões

### Fase 3: Integração G-Click (Semana 5-6)

#### 3.1 Obtenção de Credenciais

- Contatar suporte G-Click para credenciais de API
- Solicitar documentação atualizada
- Configurar ambiente de testes

#### 3.2 Configuração da Integração

```python
# Atualizar .env
GCLICK_CLIENT_ID=seu_client_id_real
GCLICK_CLIENT_SECRET=seu_client_secret_real

# Em jarvis_brain_simple.py, substituir:
# self.gclick_client = MockGClickAutomation()
# Por:
# self.gclick_client = GClickAutomation()
```

#### 3.3 Testes com Dados Reais

- [ ] Busca de clientes por CNPJ
- [ ] Criação de tarefas/chamados
- [ ] Adição de notas a clientes
- [ ] Listagem de departamentos

#### 3.4 Validação de Segurança

- Revisar permissões de acesso
- Implementar logs de auditoria
- Testar cenários de erro

### Fase 4: Deploy em Produção (Semana 7-8)

#### 4.1 Preparação do Servidor

```bash
# 1. Configurar servidor de produção
# - Ubuntu 20.04+ ou CentOS 8+
# - Python 3.8+
# - Nginx como proxy reverso
# - SSL/TLS configurado

# 2. Instalar dependências
sudo apt update
sudo apt install python3-pip nginx certbot
pip3 install -r requirements.txt

# 3. Configurar banco de dados
# - Migrar para PostgreSQL (recomendado)
# - Ou manter SQLite para pequeno volume

# 4. Configurar variáveis de ambiente de produção
```

#### 4.2 Configuração do Nginx

```nginx
# /etc/nginx/sites-available/jarvis
server {
    listen 80;
    server_name jarvis.contec.com.br;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4.3 Configuração SSL

```bash
# Obter certificado SSL
sudo certbot --nginx -d jarvis.contec.com.br

# Configurar renovação automática
sudo crontab -e
# Adicionar: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 4.4 Deploy da Aplicação

```bash
# 1. Clonar código no servidor
git clone <repositorio> /opt/jarvis
cd /opt/jarvis

# 2. Configurar ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar variáveis de produção
cp .env.production .env
# Editar com credenciais reais

# 4. Inicializar banco
python init_db.py

# 5. Configurar systemd service
sudo cp jarvis.service /etc/systemd/system/
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

### Fase 5: Treinamento e Rollout (Semana 9-10)

#### 5.1 Treinamento da Equipe

**Sessão 1: Administradores (2 horas)**
- Configuração do painel administrativo
- Gestão da base de conhecimento
- Análise de métricas e feedback
- Resolução de problemas comuns

**Sessão 2: Usuários Finais (1 hora)**
- Novas funcionalidades disponíveis
- Comandos de e-mail e agenda
- Comandos G-Click
- Uso do reconhecimento de voz
- Como fornecer feedback

#### 5.2 Rollout Gradual

**Semana 1**: Departamento de TI (5 usuários)
**Semana 2**: Departamento Pessoal (10 usuários)
**Semana 3**: Departamento Fiscal (15 usuários)
**Semana 4**: Departamento Contábil (20 usuários)
**Semana 5**: Todos os usuários (50+ usuários)

#### 5.3 Monitoramento Intensivo

- Monitorar logs de erro diariamente
- Coletar feedback dos usuários
- Ajustar base de conhecimento conforme necessário
- Otimizar performance baseado no uso real

## 🔧 Configurações Específicas

### Microsoft 365 - Configuração Detalhada

#### Permissões Necessárias

```json
{
  "requiredResourceAccess": [
    {
      "resourceAppId": "00000003-0000-0000-c000-000000000000",
      "resourceAccess": [
        {
          "id": "570282fd-fa5c-430d-a7fd-fc8dc98a9dca",
          "type": "Scope"
        },
        {
          "id": "024d486e-b451-40bb-833d-3e66d98c5c73",
          "type": "Scope"
        },
        {
          "id": "465a38f9-76ea-45b9-9f34-9e8b0d4b0b42",
          "type": "Scope"
        }
      ]
    }
  ]
}
```

#### Configuração de Redirect URIs

```
https://jarvis.contec.com.br/auth/callback
http://localhost:5000/auth/callback (apenas desenvolvimento)
```

### G-Click - Endpoints Principais

```python
# Configuração de endpoints
GCLICK_ENDPOINTS = {
    'token': 'https://api.gclick.com.br/oauth/token',
    'clientes': 'https://api.gclick.com.br/clientes',
    'tarefas': 'https://api.gclick.com.br/tarefas',
    'departamentos': 'https://api.gclick.com.br/departamentos'
}
```

## 📊 Monitoramento e Métricas

### Métricas Essenciais

1. **Performance**
   - Tempo de resposta médio
   - Taxa de erro das APIs
   - Uso de CPU/memória

2. **Uso**
   - Número de mensagens por dia
   - Comandos mais utilizados
   - Usuários ativos

3. **Qualidade**
   - Taxa de feedback positivo
   - Número de correções recebidas
   - Tópicos com mais erros

### Dashboards Recomendados

```python
# Exemplo de métricas para dashboard
{
    "daily_messages": 150,
    "satisfaction_rate": 85.5,
    "top_commands": [
        "verificar e-mails",
        "consultar ramais",
        "criar chamado"
    ],
    "error_rate": 2.1
}
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação Microsoft

```
Erro: AADSTS50011: The reply URL specified in the request does not match
Solução: Verificar redirect URIs no Azure AD
```

#### 2. Timeout na API G-Click

```
Erro: requests.exceptions.Timeout
Solução: Aumentar timeout ou implementar retry
```

#### 3. Reconhecimento de Voz Não Funciona

```
Problema: Navegador não suporta Web Speech API
Solução: Usar Chrome/Edge ou implementar fallback
```

### Logs Importantes

```bash
# Logs da aplicação
tail -f /var/log/jarvis/app.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs do sistema
journalctl -u jarvis -f
```

## 📋 Checklist de Go-Live

### Pré-Deploy
- [ ] Todos os testes passando
- [ ] Credenciais de produção configuradas
- [ ] Backup do banco de dados atual
- [ ] Plano de rollback definido
- [ ] Equipe de suporte notificada

### Deploy
- [ ] Aplicação deployada
- [ ] SSL configurado
- [ ] DNS apontando corretamente
- [ ] Monitoramento ativo
- [ ] Logs sendo coletados

### Pós-Deploy
- [ ] Testes de fumaça executados
- [ ] Usuários piloto validaram
- [ ] Métricas sendo coletadas
- [ ] Documentação atualizada
- [ ] Equipe treinada

## 🔄 Manutenção Contínua

### Tarefas Semanais
- Revisar logs de erro
- Analisar feedback dos usuários
- Atualizar base de conhecimento
- Verificar performance das APIs

### Tarefas Mensais
- Gerar relatório de uso
- Revisar e otimizar prompts
- Atualizar dependências
- Backup completo do sistema

### Tarefas Trimestrais
- Avaliar novas funcionalidades
- Revisar arquitetura
- Planejar melhorias
- Treinamento de reciclagem

---

**Documento**: Guia de Implementação Jarvis v2.0  
**Versão**: 1.0  
**Data**: Setembro 2024  
**Responsável**: Equipe de TI Contec

