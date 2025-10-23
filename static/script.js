// This file should remain the same as provided in the earlier response.
// Just make sure it's present in static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const chatMessages = document.getElementById('chat-messages');
    const heatmapGrid = document.getElementById('heatmap-grid');
    const usernameInput = document.getElementById('username-input');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');

    const MAX_HEATMAP_CELLS = 50; 

    function addMessageToChat(msg) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');

        const userSpan = document.createElement('span');
        userSpan.classList.add('user');
        userSpan.textContent = msg.user;

        const timestampSpan = document.createElement('span');
        timestampSpan.classList.add('timestamp');
        timestampSpan.textContent = msg.timestamp;

        const messageText = document.createElement('p');
        messageText.textContent = msg.message;

        const emotionInfoDiv = document.createElement('div');
        emotionInfoDiv.classList.add('emotion-info');
        // Ensure msg.word_color is used if available, otherwise fallback
        emotionInfoDiv.innerHTML = `Emotion: ${msg.emoji} <span class="emotion-word" style="background-color: ${msg.color}; color: ${msg.word_color || 'white'};">${msg.emotion_label}</span> (Score: ${msg.emotion_score.toFixed(2)})`;


        messageDiv.appendChild(userSpan);
        messageDiv.appendChild(messageText);
        messageDiv.appendChild(emotionInfoDiv);
        messageDiv.appendChild(timestampSpan);

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addCellToHeatmap(msg) {
        const cell = document.createElement('div');
        cell.classList.add('heatmap-cell');
        cell.style.backgroundColor = msg.color; 
        cell.textContent = msg.emoji; 

        const cellDetails = document.createElement('div');
        cellDetails.classList.add('cell-details');
        cellDetails.textContent = `${msg.user}: ${msg.emotion_label} (${msg.emotion_score.toFixed(2)})`;
        cell.appendChild(cellDetails);

        heatmapGrid.appendChild(cell);

        while (heatmapGrid.children.length > MAX_HEATMAP_CELLS) {
            heatmapGrid.removeChild(heatmapGrid.children[0]);
        }
    }

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('current_chat_history', (history) => {
        chatMessages.innerHTML = ''; 
        heatmapGrid.innerHTML = ''; 
        history.forEach(msg => {
            addMessageToChat(msg);
            addCellToHeatmap(msg);
        });
    });

    socket.on('new_message', (msg) => {
        addMessageToChat(msg);
        addCellToHeatmap(msg);
    });

    sendButton.addEventListener('click', () => {
        sendMessage();
    });

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const user = usernameInput.value.trim();
        const message = messageInput.value.trim();

        if (message && user) {
            socket.emit('send_message', { user: user, message: message });
            messageInput.value = ''; 
        } else if (!user) {
            alert('Please enter your name!');
        } else {
            alert('Please enter a message!');
        }
    }
});