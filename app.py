from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from transformers import pipeline
import datetime
import threading
import time
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_change_me_in_production')  # Use environment variable or default
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for development

emotion_analyzer = None
LOADED_MODEL_ID = None

# Prefer robust, widely used models. Try primary then fallback.
_MODEL_CANDIDATES = [
    "j-hartmann/emotion-english-distilroberta-base",          # 7-class emotions
    "bhadresh-savani/distilbert-base-uncased-emotion",        # 6-class emotions (love -> joy)
]

for candidate in _MODEL_CANDIDATES:
    try:
        print(f"Attempting to load emotion model: {candidate} ...")
        # Force CPU unless GPU is explicitly configured in the environment
        emotion_analyzer = pipeline(
            task="text-classification",
            model=candidate,
            device=-1,
        )
        LOADED_MODEL_ID = candidate
        print(f"Emotion model loaded successfully: {candidate}")
        break
    except Exception as e:
        print(f"Could not load model '{candidate}': {e}")
        emotion_analyzer = None

if not emotion_analyzer:
    print("No emotion model could be loaded. Falling back to mock analyzer.")

# --- Data Structures ---
# Store recent messages and their emotions
chat_history = []
MAX_CHAT_HISTORY = 50 # Keep a reasonable history

# Emotion mapping for colors and emojis (you can expand this)
emotion_map = {
    'joy': {'color': '#FFD700', 'emoji': '😊', 'word_color': '#DAA520'}, # Gold, DarkGoldenrod
    'sadness': {'color': '#6495ED', 'emoji': '😔', 'word_color': '#4682B4'}, # CornflowerBlue, SteelBlue
    'anger': {'color': '#DC143C', 'emoji': '😡', 'word_color': '#B22222'}, # Crimson, FireBrick
    'fear': {'color': '#8B008B', 'emoji': '😨', 'word_color': '#4B0082'}, # DarkMagenta, Indigo
    'disgust': {'color': '#228B22', 'emoji': '🤢', 'word_color': '#006400'}, # ForestGreen, DarkGreen
    'surprise': {'color': '#FFA500', 'emoji': '😮', 'word_color': '#FF8C00'}, # Orange, DarkOrange
    'neutral': {'color': '#D3D3D3', 'emoji': '😐', 'word_color': '#A9A9A9'}, # LightGray, DarkGray
    'positive': {'color': '#90EE90', 'emoji': '😃', 'word_color': '#3CB371'}, # LightGreen, MediumSeaGreen
    'negative': {'color': '#FF6347', 'emoji': '😞', 'word_color': '#CD5C5C'}, # Tomato, IndianRed
}

# --- Label Normalization and Helper Functions ---
def _normalize_label(raw_label: str) -> str:
    label = (raw_label or '').strip().lower()
    # Unify common variants from different models
    alias_to_label = {
        'happy': 'joy',
        'happiness': 'joy',
        'love': 'joy',
        'amusement': 'joy',
        'excitement': 'joy',
        'optimism': 'positive',
        'admiration': 'positive',
        'approval': 'positive',
        'gratitude': 'positive',
        'pride': 'positive',
        'relief': 'positive',
        'realization': 'neutral',
        'curiosity': 'neutral',
        'confusion': 'neutral',
        'annoyance': 'anger',
        'nervousness': 'fear',
        'disappointment': 'sadness',
        'grief': 'sadness',
        'shock': 'surprise',
    }

    if label in emotion_map:
        return label
    if label in alias_to_label:
        return alias_to_label[label]
    return 'neutral'

# --- Helper Function for Emotion Analysis ---
def get_emotion(text):
    if emotion_analyzer:
        try:
            result = emotion_analyzer(text, truncation=True)[0]
            label = _normalize_label(result['label'])
            score = float(result.get('score', 0.0))
            return label, score
        except Exception as e:
            print(f"Error during LLM emotion analysis: {e}. Falling back to mock.")
            # If LLM analysis fails for a specific input, use mock
            pass # Continue to mock emotion below
    
    # Mock emotion for demonstration if model failed to load or analysis failed
    mock_emotions = list(emotion_map.keys())
    chosen_emotion = random.choice(mock_emotions)
    return chosen_emotion, random.random() # Random score

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# --- SocketIO Event Handlers ---
@socketio.on('connect')
def test_connect():
    print('Client connected')
    # When a new client connects, send them the current chat history
    emit('current_chat_history', chat_history)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    user = data.get('user', 'Anonymous')
    message = data['message']
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')

    emotion_label, emotion_score = get_emotion(message)
    emotion_data = emotion_map.get(emotion_label, emotion_map['neutral']) # Get color and emoji

    chat_entry = {
        'user': user,
        'message': message,
        'timestamp': timestamp,
        'emotion_label': emotion_label,
        'emotion_score': emotion_score,
        'color': emotion_data['color'],
        'emoji': emotion_data['emoji'],
        'word_color': emotion_data.get('word_color', '#FFFFFF') # Ensure word_color is present
    }
    chat_history.append(chat_entry)
    if len(chat_history) > MAX_CHAT_HISTORY:
        chat_history.pop(0) # Remove oldest entry

    print(f"[{timestamp}] {user}: {message} (Emotion: {emotion_label}, Score: {emotion_score:.2f})")

    # Emit the new message to all connected clients
    socketio.emit('new_message', chat_entry)

# --- Optional: Simulate incoming messages for testing ---
def simulate_messages_thread():
    users = ["Alice", "Bob", "Charlie", "Diana"]
    messages = [
        "I'm so happy today!", "This is really frustrating.", "That's an interesting point.",
        "I'm completely thrilled with the results!", "Ugh, what a terrible day.",
        "I'm feeling a bit down.", "Haha, that's hilarious!", "I'm genuinely surprised by that outcome.",
        "I'm filled with joy and excitement!", "This makes me angry!", "I'm very sad to hear that.",
        "Fear not, we shall overcome!", "I'm disgusted by their actions.", "What a pleasant surprise!"
    ]
    print("Starting message simulation...")
    with app.app_context(): # Essential for emitting from a background thread
        while True:
            user = random.choice(users)
            message = random.choice(messages)

            emotion_label, emotion_score = get_emotion(message)
            emotion_data = emotion_map.get(emotion_label, emotion_map['neutral'])

            chat_entry = {
                'user': user,
                'message': message,
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S'),
                'emotion_label': emotion_label,
                'emotion_score': emotion_score,
                'color': emotion_data['color'],
                'emoji': emotion_data['emoji'],
                'word_color': emotion_data.get('word_color', '#FFFFFF')
            }
            
            chat_history.append(chat_entry)
            if len(chat_history) > MAX_CHAT_HISTORY:
                chat_history.pop(0)

            print(f"[Simulated] {chat_entry['user']}: {chat_entry['message']} (Emotion: {chat_entry['emotion_label']}, Score: {chat_entry['emotion_score']:.2f})")
            socketio.emit('new_message', chat_entry) # Emit from the simulation thread

            time.sleep(random.uniform(2, 5)) # Simulate messages every 2-5 seconds


if __name__ == '__main__':
    # Start the message simulation in a separate thread only if the real model failed to load
    if not emotion_analyzer:
        print("Emotion model not loaded. Starting message simulation.")
        thread = threading.Thread(target=simulate_messages_thread)
        thread.daemon = True # Allows the main program to exit even if this thread is still running
        thread.start()
    else:
        print("Emotion model loaded successfully. Simulation will not run.")

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)