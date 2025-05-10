document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const suggestionButtons = document.querySelectorAll('.suggestion-btn');
    
    // Set focus on input field
    userInput.focus();
    
    // Add a slight delay to the initial message to make it look like it's just arrived
    setTimeout(() => {
        const initialMessage = document.querySelector('.bot-message');
        initialMessage.classList.add('animated');
    }, 500);
    
    // Function to create and add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', isUser ? 'user-message' : 'bot-message');
        
        // Create avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar');
        
        const avatarIcon = document.createElement('i');
        avatarIcon.classList.add('fa-solid', isUser ? 'fa-user' : 'fa-robot');
        avatarDiv.appendChild(avatarIcon);
        
        // Create message bubble
        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('message-bubble');
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        bubbleDiv.appendChild(paragraph);
        
        // Assemble the message
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
        
        // Add to chat with animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        chatMessages.appendChild(messageDiv);
        
        // Force a reflow
        void messageDiv.offsetWidth;
        
        // Add animation
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
        
        // Scroll to the bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator-container');
        typingDiv.id = 'typing-indicator';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('message-avatar');
        
        const avatarIcon = document.createElement('i');
        avatarIcon.classList.add('fa-solid', 'fa-robot');
        avatarDiv.appendChild(avatarIcon);
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('message-bubble');
        
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('typing-indicator');
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingIndicator.appendChild(dot);
        }
        
        bubbleDiv.appendChild(typingIndicator);
        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(bubbleDiv);
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return typingDiv;
    }
    
    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Function to send user message and get bot response
    async function sendMessage(message) {
        if (!message.trim()) return;
        
        // Clear input
        userInput.value = '';
        
        // Add user message
        addMessage(message, true);
        
        // Show typing indicator
        showTypingIndicator();
        
        try {
            // Send message to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });
            
            // Get response data
            const data = await response.json();
            
            // Simulate a slight delay for more natural conversation flow
            setTimeout(() => {
                // Remove typing indicator
                removeTypingIndicator();
                
                // Add bot response
                if (data.status === 'success') {
                    addMessage(data.response);
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.');
                }
            }, 1000); // Adjust timing for more natural feel
            
        } catch (error) {
            console.error('Error:', error);
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Show error message
            addMessage('Sorry, I encountered a connection error. Please check your internet connection and try again.');
        }
    }
    
    // Event listeners for sending messages
    sendButton.addEventListener('click', () => {
        sendMessage(userInput.value);
    });
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(userInput.value);
        }
    });
    
    // Add click events for suggestion buttons
    suggestionButtons.forEach(button => {
        button.addEventListener('click', () => {
            sendMessage(button.textContent);
        });
    });
    
    // Animate suggestion buttons on load
    setTimeout(() => {
        suggestionButtons.forEach((btn, index) => {
            setTimeout(() => {
                btn.style.opacity = '0';
                btn.style.transform = 'translateY(10px)';
                btn.style.transition = 'all 0.3s ease';
                
                // Force reflow
                void btn.offsetWidth;
                
                btn.style.opacity = '1';
                btn.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }, 1000);
    
    // Add a hover effect to the send button
    sendButton.addEventListener('mouseover', () => {
        sendButton.style.transform = 'scale(1.1)';
    });
    
    sendButton.addEventListener('mouseout', () => {
        sendButton.style.transform = 'scale(1)';
    });
    
    // Add animation when input is focused
    userInput.addEventListener('focus', () => {
        document.querySelector('.input-wrapper').style.boxShadow = '0 0 0 2px rgba(139, 0, 0, 0.3)';
    });
    
    userInput.addEventListener('blur', () => {
        document.querySelector('.input-wrapper').style.boxShadow = 'none';
    });
});