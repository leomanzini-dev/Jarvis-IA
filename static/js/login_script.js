// static/js/login_script.js - VERSÃO 10.0 - "Análise da Rede Global"
document.addEventListener('DOMContentLoaded', () => {
    const titleElement = document.getElementById('login-title');
    const loginContainer = document.querySelector('.login-container');
    const loginForm = document.getElementById('login-form');
    const animationContainer = document.getElementById('animation-container');
    const errorMessageContainer = document.getElementById('error-message-container');
    const logText = document.getElementById('log-text');

    // Efeito de digitação no título
    const textToType = "INICIANDO JARVIS...";
    let i = 0;
    const typeWriter = () => {
        if (titleElement && i < textToType.length) {
            titleElement.innerHTML += textToType.charAt(i);
            i++;
            setTimeout(typeWriter, 100);
        } else if (titleElement) {
            titleElement.innerHTML += '<span class="typing-cursor">_</span>';
        }
    };
    if (titleElement) {
        setTimeout(typeWriter, 500);
    }

    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            if (errorMessageContainer) errorMessageContainer.style.display = 'none';
            if (loginContainer) loginContainer.style.animation = 'fadeOut 0.5s ease-out forwards';
            if (animationContainer) animationContainer.classList.add('active');

            // Sequência de animação RÁPIDA E OTIMIZADA
            const steps = [
                { text: "[AUTENTICANDO]...", duration: 1000 },
                { text: "[CONECTANDO À REDE]...", duration: 1000 },
                { text: "[NÚCLEO DE IA ONLINE]", duration: 1000 },
                { text: "BEM-VINDO AO JARVIS", isWelcome: true, duration: 1500 }
            ];
            let cumulativeTime = 500; // Delay inicial

            function showStep(index) {
                if (!steps[index]) return;
                const step = steps[index];
                setTimeout(() => {
                    logText.textContent = step.text;
                    logText.classList.add('visible');
                    if (step.isWelcome) {
                        logText.classList.add('final');
                    }
                    setTimeout(() => {
                        if (!step.isWelcome) logText.classList.remove('visible');
                    }, step.duration - 200);
                }, cumulativeTime);
                cumulativeTime += step.duration;
            }
            
            fetch(loginForm.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: new FormData(loginForm)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStep(0);
                    showStep(1);
                    showStep(2);
                    showStep(3);
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, cumulativeTime + 500); // Redireciona 0.5s após a última mensagem

                } else {
                    setTimeout(() => {
                        if (animationContainer) animationContainer.classList.remove('active');
                        if (loginContainer) loginContainer.style.animation = 'fadeIn 0.5s ease-out forwards';
                        if (errorMessageContainer) {
                            errorMessageContainer.textContent = data.message;
                            errorMessageContainer.style.display = 'block';
                        }
                    }, 500);
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                setTimeout(() => {
                    if (animationContainer) animationContainer.classList.remove('active');
                    if (loginContainer) loginContainer.style.animation = 'fadeIn 0.5s ease-out forwards';
                    if (errorMessageContainer) {
                        errorMessageContainer.textContent = 'Erro de conexão. Tente novamente.';
                        errorMessageContainer.style.display = 'block';
                    }
                }, 500);
            });
        });
    }
});