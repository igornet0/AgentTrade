// static/chat.js
async function handleSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const thinkingIndicator = document.getElementById('thinking-indicator');

    // Добавляем сообщение пользователя
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = input.value;
    chatMessages.appendChild(userMessage);
    
    // Показываем индикатор загрузки
    thinkingIndicator.style.display = 'block';
    input.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        // Отправляем запрос на сервер
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                news_text: userMessage.textContent
            })
        });

        if (!response.ok) throw new Error('Server error');
        
        const result = await response.text();
        
        // Добавляем ответ модели
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.innerHTML = result;
        chatMessages.appendChild(botMessage);

    } catch (error) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message bot-message error';
        errorMessage.textContent = `Error: ${error.message}`;
        chatMessages.appendChild(errorMessage);
    } finally {
        thinkingIndicator.style.display = 'none';
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}