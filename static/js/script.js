// static/js/script.js - VERSÃO COM ANIMAÇÃO DE DIGITAÇÃO
document.addEventListener('DOMContentLoaded', () => {
    // --- Seleção de Elementos ---
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const chatWindow = document.getElementById('chat-window');
    const welcomeScreen = document.getElementById('welcome-screen');
    const newConversationButton = document.querySelector('.sidebar-header .nav-link');
    const suggestionCards = document.querySelectorAll('.suggestion-card');
    const shortcutsList = document.getElementById('user-shortcuts-list');
    
    // Modal de correção
    const modal = document.getElementById('correction-modal');
    const closeButton = document.querySelector('.close-button');
    const submitCorrectionBtn = document.getElementById('submit-correction-btn');
    const correctionTextarea = document.getElementById('correction-textarea');
    let activeFeedbackData = null;

    // --- Função Principal do Chat ---
    const sendMessage = async (messageText) => {
        if (!messageText || messageText.trim() === '') return;

        displayUserMessage(messageText);
        userInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('/ask', { 
                method: 'POST', 
                headers: {'Content-Type': 'application/json'}, 
                body: JSON.stringify({ message: messageText }) 
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            
            removeTypingIndicator();
            displayBotResponse(data, messageText);

        } catch (error) {
            removeTypingIndicator(); 
            console.error('Fetch Error:', error);
            displayBotResponse({ text: 'Desculpe, ocorreu um erro de conexão.', timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }, messageText);
        }
    };

    const displayUserMessage = (text) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = 'chat-message user';
        
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.innerHTML = `<p style="margin:0;">${text}</p><div class="timestamp">${new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</div>`;
        
        const favoriteBtn = document.createElement('button');
        favoriteBtn.className = 'favorite-button';
        favoriteBtn.innerHTML = '<i class="fa-regular fa-star"></i>';
        favoriteBtn.title = 'Adicionar aos atalhos';
        favoriteBtn.onclick = () => addShortcut(text, favoriteBtn);

        messageWrapper.appendChild(messageBubble);
        messageWrapper.appendChild(favoriteBtn);
        chatWindow.appendChild(messageWrapper);

        if (welcomeScreen) welcomeScreen.style.display = 'none';
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };
    
    const displayBotResponse = (data, userQuery) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.className = 'chat-message bot';
        
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        
        const contentElement = document.createElement('div');
        
        messageBubble.appendChild(contentElement);
        messageWrapper.appendChild(messageBubble);
        chatWindow.appendChild(messageWrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        const textToType = data.text.replace(/\n/g, '<br>');
        const speed = 15;
        let i = 0;

        function typeWriter() {
            if (i < textToType.length) {
                if (textToType.charAt(i) === '<') {
                    const endTagIndex = textToType.indexOf('>', i);
                    if (endTagIndex !== -1) {
                        contentElement.innerHTML += textToType.substring(i, endTagIndex + 1);
                        i = endTagIndex;
                    }
                } else {
                    contentElement.innerHTML += textToType.charAt(i);
                }
                i++;
                chatWindow.scrollTop = chatWindow.scrollHeight;
                setTimeout(typeWriter, speed);
            } else {
                addTimestampAndFeedback(messageBubble, data, userQuery);
            }
        }

        typeWriter();
    };

    const addTimestampAndFeedback = (messageBubble, data, userQuery) => {
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.innerText = data.timestamp;

        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'feedback-buttons';
        const thumbUpBtn = document.createElement('button');
        thumbUpBtn.className = 'feedback-btn';
        thumbUpBtn.innerHTML = '<i class="fa-solid fa-thumbs-up"></i>';
        const thumbDownBtn = document.createElement('button');
        thumbDownBtn.className = 'feedback-btn';
        thumbDownBtn.innerHTML = '<i class="fa-solid fa-thumbs-down"></i>';
        
        thumbUpBtn.addEventListener('click', () => handleFeedback(1, userQuery, data.text, thumbUpBtn, thumbDownBtn));
        thumbDownBtn.addEventListener('click', () => handleFeedback(-1, userQuery, data.text, thumbUpBtn, thumbDownBtn));
        
        feedbackContainer.appendChild(thumbUpBtn);
        feedbackContainer.appendChild(thumbDownBtn);
        
        messageBubble.appendChild(timestamp);
        messageBubble.appendChild(feedbackContainer);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };
    
    const showTypingIndicator = () => {
        if (document.getElementById('typing-indicator')) return;
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'chat-message bot';
        indicator.innerHTML = `<div class="message-bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
        chatWindow.appendChild(indicator);
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const removeTypingIndicator = () => { 
        const indicator = document.getElementById('typing-indicator'); 
        if (indicator) indicator.remove(); 
    };

    const loadUserShortcuts = async () => {
        try {
            const response = await fetch('/get_shortcuts');
            const data = await response.json();
            shortcutsList.innerHTML = '';
            if (data.shortcuts) {
                data.shortcuts.forEach(shortcut => appendShortcutToList(shortcut));
            }
        } catch (error) {
            console.error("Erro ao carregar atalhos:", error);
        }
    };

    const appendShortcutToList = (shortcut) => {
        const listItem = document.createElement('li');
        listItem.dataset.id = shortcut.id;

        const link = document.createElement('a');
        link.href = '#';
        link.className = 'nav-link';
        link.onclick = (e) => {
            e.preventDefault();
            // CORREÇÃO: Atalhos favoritados agora também preenchem o input
            userInput.value = shortcut.text;
            userInput.focus();
        };

        const icon = document.createElement('i');
        icon.className = 'fa-regular fa-star';
        
        const textSpan = document.createElement('span');
        textSpan.className = 'link-text';
        textSpan.textContent = shortcut.text;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-shortcut-btn';
        deleteBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
        deleteBtn.title = 'Remover atalho';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteShortcut(shortcut.id);
        };

        link.appendChild(icon);
        link.appendChild(textSpan);
        link.appendChild(deleteBtn);
        listItem.appendChild(link);
        shortcutsList.appendChild(listItem);
    };

    const addShortcut = async (text, button) => {
        try {
            const response = await fetch('/add_shortcut', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            const data = await response.json();
            if (data.success) {
                appendShortcutToList({ id: data.id, text: data.text });
                button.innerHTML = '<i class="fa-solid fa-star"></i>';
                button.classList.add('favorited');
                button.disabled = true;
            }
        } catch (error) {
            console.error("Erro ao adicionar atalho:", error);
        }
    };

    const deleteShortcut = async (id) => {
        try {
            await fetch('/delete_shortcut', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            });
            const listItem = shortcutsList.querySelector(`li[data-id='${id}']`);
            if (listItem) listItem.remove();
        } catch (error) {
            console.error("Erro ao remover atalho:", error);
        }
    };

    const handleFeedback = async (rating, userQuery, botResponse, btnUp, btnDown) => {
        btnUp.disabled = true;
        btnDown.disabled = true;
        btnUp.classList.remove('selected-good', 'selected-bad');
        btnDown.classList.remove('selected-good', 'selected-bad');
        if (rating === 1) {
            btnUp.classList.add('selected-good');
            await sendFeedbackToServer({ rating, user_query: userQuery, bot_response: botResponse });
        } else {
            btnDown.classList.add('selected-bad');
            activeFeedbackData = { rating, user_query: userQuery, bot_response: botResponse };
            correctionTextarea.value = '';
            modal.style.display = 'block';
        }
    };
    const sendFeedbackToServer = async (feedbackData) => {
        try {
            await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(feedbackData)
            });
        } catch (error) { console.error("Erro ao enviar feedback:", error); }
    };
    closeButton.onclick = () => { modal.style.display = "none"; sendFeedbackToServer(activeFeedbackData); };
    window.onclick = (event) => { if (event.target == modal) { modal.style.display = "none"; sendFeedbackToServer(activeFeedbackData); } };
    submitCorrectionBtn.onclick = () => { activeFeedbackData.correction = correctionTextarea.value.trim(); sendFeedbackToServer(activeFeedbackData); modal.style.display = "none"; };
    
    sendButton.addEventListener('click', () => sendMessage(userInput.value));
    userInput.addEventListener('keydown', (event) => { if (event.key === 'Enter') sendMessage(userInput.value); });
    
    // CORREÇÃO: Lógica de clique dos cartões de sugestão
    suggestionCards.forEach(card => {
        card.addEventListener('click', () => {
            const message = card.dataset.message;
            const shouldAppend = card.dataset.append === 'true';

            if (shouldAppend) {
                userInput.value = message;
                userInput.focus();
            } else {
                sendMessage(message);
            }
        });
    });

    if (newConversationButton) {
        newConversationButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.reload();
        });
    }

    loadUserShortcuts();
});