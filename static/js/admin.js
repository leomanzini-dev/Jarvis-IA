document.addEventListener('DOMContentLoaded', () => {
    const editors = {
        'departments': document.getElementById('departments-editor'),
        'faq_dp': document.getElementById('faq_dp-editor'),
        'faq_fiscal': document.getElementById('faq_fiscal-editor'),
        'faq_contabil': document.getElementById('faq_contabil-editor')
    };
    const notification = document.getElementById('notification');

    // Função para mostrar notificações
    const showNotification = (message, type) => {
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        setTimeout(() => {
            notification.className = 'notification';
        }, 3000);
    };

    // Carrega os dados iniciais
    const loadKnowledge = async () => {
        for (const key in editors) {
            // Adicionado para garantir que só busquemos elementos que existem na página
            if (editors[key]) { 
                try {
                    const response = await fetch(`/api/knowledge/${key}`);
                    if (!response.ok) {
                        // Se a chave não for encontrada (404), o campo fica vazio, o que é esperado para novos FAQs
                        if (response.status === 404) {
                            editors[key].value = JSON.stringify({}, null, 4);
                            console.warn(`A chave '${key}' não foi encontrada na base de dados. Um objeto vazio foi carregado.`);
                            continue; // Pula para a próxima iteração
                        }
                        throw new Error(`Falha ao buscar ${key}`);
                    }
                    const data = await response.json();
                    editors[key].value = JSON.stringify(data, null, 4);
                } catch (error) {
                    console.error(`Erro ao carregar ${key}:`, error);
                    showNotification(`Erro ao carregar dados de ${key}.`, 'error');
                }
            }
        }
    };

    // Adiciona o evento de clique para os botões de salvar
    document.querySelectorAll('.save-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const key = button.dataset.key;
            const editor = editors[key];
            let content;

            // Valida se o conteúdo é um JSON válido
            try {
                content = JSON.parse(editor.value);
            } catch (error) {
                showNotification('Erro: O texto não é um JSON válido!', 'error');
                return;
            }

            // Envia para o backend
            try {
                const response = await fetch(`/api/knowledge/${key}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(content)
                });

                if (!response.ok) throw new Error(`Falha ao salvar ${key}`);
                
                const result = await response.json();
                showNotification(result.message, 'success');
            } catch (error) {
                console.error(`Erro ao salvar ${key}:`, error);
                showNotification(`Erro ao salvar dados de ${key}.`, 'error');
            }
        });
    });

    loadKnowledge();
});
