// enhanced_chat.js - JavaScript aprimorado para o Jarvis com streaming e voz

class EnhancedJarvisChat {
    constructor() {
        this.isStreaming = false;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.streamingEnabled = true;
        this.voiceEnabled = false;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.checkBrowserSupport();
    }
    
    initializeElements() {
        // Elementos existentes
        this.chatContainer = document.getElementById('chat-container');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        
        // Novos elementos para funcionalidades avançadas
        this.createAdvancedControls();
    }
    
    createAdvancedControls() {
        // Criar controles avançados se não existirem
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'advanced-controls';
        controlsContainer.innerHTML = `
            <div class="control-group">
                <button id="voice-button" class="control-btn" title="Gravar mensagem por voz">
                    🎤
                </button>
                <button id="streaming-toggle" class="control-btn active" title="Ativar/Desativar streaming">
                    ⚡
                </button>
                <button id="clear-chat" class="control-btn" title="Limpar conversa">
                    🗑️
                </button>
            </div>
        `;
        
        // Inserir antes do input
        const inputContainer = this.messageInput.parentElement;
        inputContainer.parentElement.insertBefore(controlsContainer, inputContainer);
        
        // Atualizar referências
        this.voiceButton = document.getElementById('voice-button');
        this.streamingToggle = document.getElementById('streaming-toggle');
        this.clearButton = document.getElementById('clear-chat');
    }
    
    initializeEventListeners() {
        // Eventos existentes
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Novos eventos
        this.voiceButton.addEventListener('click', () => this.toggleVoiceRecording());
        this.streamingToggle.addEventListener('click', () => this.toggleStreaming());
        this.clearButton.addEventListener('click', () => this.clearChat());
    }
    
    checkBrowserSupport() {
        // Verificar suporte para gravação de áudio
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.voiceButton.disabled = true;
            this.voiceButton.title = 'Gravação de voz não suportada neste navegador';
            console.warn('Gravação de voz não suportada');
        }
        
        // Verificar suporte para Web Speech API
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.voiceEnabled = true;
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isStreaming) return;
        
        // Adicionar mensagem do usuário
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        
        // Desabilitar input durante processamento
        this.setInputState(false);
        
        try {
            if (this.streamingEnabled) {
                await this.sendStreamingMessage(message);
            } else {
                await this.sendRegularMessage(message);
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.addMessage('Desculpe, ocorreu um erro. Tente novamente.', 'bot');
        } finally {
            this.setInputState(true);
        }
    }
    
    async sendStreamingMessage(message) {
        this.isStreaming = true;
        
        // Criar elemento de resposta para streaming
        const responseElement = this.addMessage('', 'bot', true);
        const textElement = responseElement.querySelector('.message-text');
        
        try {
            const response = await fetch('/ask_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = '';
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                fullResponse += chunk;
                textElement.textContent = fullResponse;
                
                // Auto-scroll
                this.scrollToBottom();
            }
            
            // Adicionar controles de feedback
            this.addFeedbackControls(responseElement, message, fullResponse);
            
        } catch (error) {
            textElement.textContent = 'Erro ao receber resposta em streaming.';
            console.error('Erro no streaming:', error);
        } finally {
            this.isStreaming = false;
        }
    }
    
    async sendRegularMessage(message) {
        // Adicionar indicador de digitação
        const typingElement = this.addMessage('Jarvis está digitando...', 'bot', true);
        
        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remover indicador de digitação
            typingElement.remove();
            
            // Adicionar resposta real
            const responseElement = this.addMessage(data.response, 'bot');
            this.addFeedbackControls(responseElement, message, data.response);
            
        } catch (error) {
            typingElement.querySelector('.message-text').textContent = 'Erro ao processar mensagem.';
            console.error('Erro na mensagem regular:', error);
        }
    }
    
    addMessage(text, sender, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const timestamp = new Date().toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addFeedbackControls(messageElement, userQuery, botResponse) {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'feedback-controls';
        feedbackDiv.innerHTML = `
            <button class="feedback-btn like-btn" data-rating="1" title="Gostei">👍</button>
            <button class="feedback-btn dislike-btn" data-rating="-1" title="Não gostei">👎</button>
            <button class="feedback-btn save-btn" title="Salvar como atalho">💾</button>
        `;
        
        messageElement.querySelector('.message-content').appendChild(feedbackDiv);
        
        // Event listeners para feedback
        feedbackDiv.addEventListener('click', (e) => {
            if (e.target.classList.contains('feedback-btn')) {
                this.handleFeedback(e.target, userQuery, botResponse);
            }
        });
    }
    
    async handleFeedback(button, userQuery, botResponse) {
        const rating = button.dataset.rating;
        
        if (rating) {
            // Feedback de like/dislike
            let correction = null;
            
            if (rating === '-1') {
                correction = prompt('Como eu deveria ter respondido?');
                if (!correction) return;
            }
            
            try {
                await fetch('/feedback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_query: userQuery,
                        bot_response: botResponse,
                        rating: parseInt(rating),
                        correction: correction
                    })
                });
                
                // Feedback visual
                button.style.opacity = '0.5';
                button.disabled = true;
                
                // Mostrar mensagem de agradecimento
                this.showToast(rating === '1' ? 'Obrigado pelo feedback!' : 'Obrigado! Vou aprender com isso.');
                
            } catch (error) {
                console.error('Erro ao enviar feedback:', error);
                this.showToast('Erro ao enviar feedback');
            }
        } else if (button.classList.contains('save-btn')) {
            // Salvar como atalho
            try {
                await fetch('/save_shortcut', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: userQuery })
                });
                
                button.style.opacity = '0.5';
                button.disabled = true;
                this.showToast('Atalho salvo!');
                
            } catch (error) {
                console.error('Erro ao salvar atalho:', error);
                this.showToast('Erro ao salvar atalho');
            }
        }
    }
    
    async toggleVoiceRecording() {
        if (!this.voiceEnabled) {
            this.showToast('Gravação de voz não suportada neste navegador');
            return;
        }
        
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        try {
            // Usar Web Speech API se disponível
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                this.startSpeechRecognition();
            } else {
                // Fallback para gravação de áudio
                await this.startAudioRecording();
            }
        } catch (error) {
            console.error('Erro ao iniciar gravação:', error);
            this.showToast('Erro ao acessar microfone');
        }
    }
    
    startSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'pt-BR';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            this.isRecording = true;
            this.voiceButton.classList.add('recording');
            this.voiceButton.textContent = '🔴';
            this.showToast('Fale agora...');
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            this.showToast('Texto reconhecido!');
        };
        
        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
            this.showToast('Erro no reconhecimento de voz');
        };
        
        recognition.onend = () => {
            this.isRecording = false;
            this.voiceButton.classList.remove('recording');
            this.voiceButton.textContent = '🎤';
        };
        
        recognition.start();
    }
    
    async startAudioRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        
        this.mediaRecorder.ondataavailable = (event) => {
            this.audioChunks.push(event.data);
        };
        
        this.mediaRecorder.onstop = () => {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            // Aqui você poderia enviar o áudio para transcrição
            this.showToast('Gravação finalizada (transcrição não implementada)');
        };
        
        this.mediaRecorder.start();
        this.isRecording = true;
        this.voiceButton.classList.add('recording');
        this.voiceButton.textContent = '🔴';
        this.showToast('Gravando...');
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
        
        this.isRecording = false;
        this.voiceButton.classList.remove('recording');
        this.voiceButton.textContent = '🎤';
    }
    
    toggleStreaming() {
        this.streamingEnabled = !this.streamingEnabled;
        this.streamingToggle.classList.toggle('active', this.streamingEnabled);
        this.streamingToggle.title = this.streamingEnabled ? 
            'Desativar streaming' : 'Ativar streaming';
        
        this.showToast(this.streamingEnabled ? 
            'Streaming ativado' : 'Streaming desativado');
    }
    
    clearChat() {
        if (confirm('Tem certeza que deseja limpar a conversa?')) {
            this.chatContainer.innerHTML = '';
            this.showToast('Conversa limpa');
        }
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        
        if (enabled) {
            this.messageInput.focus();
        }
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    showToast(message) {
        // Criar toast notification
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Animar entrada
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remover após 3 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisChat = new EnhancedJarvisChat();
});

// CSS adicional para os novos elementos
const additionalStyles = `
<style>
.advanced-controls {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
    gap: 10px;
}

.control-group {
    display: flex;
    gap: 5px;
}

.control-btn {
    background: #2c3e50;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    color: white;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s ease;
}

.control-btn:hover {
    background: #34495e;
    transform: scale(1.1);
}

.control-btn.active {
    background: #3498db;
}

.control-btn.recording {
    background: #e74c3c;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}

.feedback-controls {
    display: flex;
    gap: 5px;
    margin-top: 10px;
    justify-content: flex-end;
}

.feedback-btn {
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    padding: 5px;
    border-radius: 3px;
    transition: background 0.3s ease;
}

.feedback-btn:hover {
    background: rgba(0,0,0,0.1);
}

.feedback-btn:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #2c3e50;
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 1000;
}

.toast.show {
    transform: translateX(0);
}

.message.bot-message .message-text {
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Melhorias visuais para streaming */
.streaming-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #3498db;
    border-radius: 50%;
    margin-left: 5px;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
</style>
`;

// Adicionar estilos ao head
document.head.insertAdjacentHTML('beforeend', additionalStyles);

