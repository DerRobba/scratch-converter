        const chatForm = document.getElementById('chat-form');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');
        const chatContainer = document.getElementById('chat-container');

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userMessage = messageInput.value.trim();
            if (!userMessage) return;

            addMessage(userMessage, 'user');
            messageInput.value = '';
            sendButton.disabled = true;

            try {
                const response = await fetch('chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                addMessage(data.reply, 'ai');

            } catch (error) {
                console.error('Fehler beim Senden der Nachricht:', error);
                addMessage('Entschuldigung, es ist ein Fehler aufgetreten.', 'ai');
            } finally {
                sendButton.disabled = false;
                messageInput.focus();
            }
        });

        function addMessage(text, sender) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', `${sender}-message`);
            messageElement.textContent = text;
            chatContainer.appendChild(messageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight; // Auto-scroll to bottom
        }