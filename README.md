Live Group Chat Emotion Heatmap 😄🔥😢
📖 Overview

A real-time group chat app that detects emotions from messages using a 🤗 Hugging Face model and visualizes them as colorful chat bubbles and an emoji heatmap! Perfect to see the mood of your group at a glance.

🚀 Features

🎭 Real-time emotion detection with j-hartmann/emotion-english-distilroberta-base

🌈 Color-coded chat messages with expressive emojis

📊 Dynamic emoji heatmap showing recent emotional trends

💬 Interactive chat interface for live conversations

🔄 Uses WebSocket (Flask-SocketIO) for instant updates

🛠️ Tech Stack

Python, Flask, Flask-SocketIO 🐍

Hugging Face Transformers 🤗, PyTorch ⚡

HTML, CSS, JavaScript, Socket.IO client 🌐

⚙️ Setup & Run

Clone repo and prepare structure:

EmotionChatHeatmap/
├── app.py
├── templates/index.html
└── static/
    ├── style.css
    └── script.js


Create & activate virtual environment:

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


Install dependencies:

pip install Flask Flask-SocketIO transformers torch tf-keras


Run the app:

python app.py


Open browser at 👉 http://127.0.0.1:5000/

📝 Usage

👤 Enter your name

✍️ Type your message

📩 Send it and watch your message colored by emotion with an emoji 🌟

📈 See the heatmap update live showing overall chat mood

🔧 Customization

🔄 Change the emotion model in app.py for different analyses

🎨 Update colors and emojis in app.py emotion map

📐 Adjust heatmap size in static/script.js
