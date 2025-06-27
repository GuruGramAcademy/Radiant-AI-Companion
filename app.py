# app.py - Radiant AI Companion Backend (Phase 1 MVP)

from flask import Flask, request, jsonify, render_template
from textblob import TextBlob
import random
import os
import json # For loading content from a JSON file, simulating DB for MVP
import uuid # For generating user_id (pseudonym)

app = Flask(__name__)

# --- In-memory data storage for MVP (simulating SQLite) ---
# For a real MVP, this would connect to SQLite as discussed.
# Using a dict to easily store user sessions in memory for this demo.
# In production, this would be a proper database.
user_sessions = {} # Stores {user_id: {sparkle_points, awaiting_validation, validation_type}}

# --- Content Library (Hardcoded for quick MVP, will load from Happier.in/DB later) ---
# In a real MVP, these would come from SQLite, populated from Happier.in
# For now, a few curated examples for immediate demo
radiant_content = {
    "happiness_tips": [
        {"tip": "Be Curious: Embrace new experiences and never stop learning.", "source": "Happier.in"},
        {"tip": "Be Open: Openness to new ideas and people sparks growth.", "source": "Happier.in"},
        {"tip": "Be Positive: Focus on the good, even in challenges.", "source": "Happier.in"},
        {"tip": "Be Trustworthy: Building strong relationships brings joy.", "source": "Happier.in"}
    ],
    "radiant_anecdotes": [
        "Do you know, when I was getting built, even Gemini and Guru tried 180 times to get some things just right, and now see how easily I'm chatting with you!",
        "My developers say my 'CAN DO' spirit came from all the tiny adjustments they made, one happy thought at a time!",
        "Sometimes even the smartest algorithms need a moment to 'pause, think, feel, and act' before getting it just right!"
    ],
    "default_responses": [
        "That's an interesting thought! Tell me more about it, or would you like me to share a little dose of positivity from Happier.in?",
        "I'm still learning to understand everything, but I'm all ears! What else is on your mind today?",
        "That's a new one for me! How about we try talking about something else? Perhaps what makes you smile?",
        "Hmm, I might need a little more clarity on that. But hey, how about we explore a happy memory together?",
        "Every conversation helps me grow! While I ponder that, would you like a quick tip for a brighter moment?"
    ]
}

# Define keyword lists for better detection (more comprehensive for better linkage)
LONELY_KEYWORDS = ['lonely', 'alone', 'sad', 'by myself', 'isolated', 'down', 'bummed', 'quiet', 'no one', 'unhappy', 'miss', 'solitary', 'depressed', 'blue']
FRUSTRATED_KEYWORDS = ['frustrated', 'stuck', 'app', 'tech', 'annoyed', 'difficult', 'problem', 'confused', "can't do it", 'crazy', 'ugh', 'stressed', 'irritated', 'struggle', 'hard', 'impossible']
LOW_MOTIVATION_KEYWORDS = ['flat', 'motivation', 'tired', 'rut', 'uninspired', 'no energy', "can't be bothered", 'listless', 'bored', 'nothing to do', 'bad day', 'tough', 'slump', 'unproductive', 'dull']
HAPPY_KEYWORDS = ['happy', 'joy', 'good', 'great', 'awesome', 'wonderful', 'positive', 'excited', 'optimistic', 'cheerful', 'fantastic', 'want to be happy']
GREETING_KEYWORDS = ['hello', 'hi', 'hey', 'good morning', 'good evening', 'how are you', 'howdy']

# Function to check if any keyword from a list is present in the text
def contains_any_keyword(text, keywords):
    return any(keyword in text for keyword in keywords)

@app.route('/')
def index():
    """Renders the main chat interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles incoming chat messages and generates Radiant's response."""
    user_message = request.json.get('message', '').strip()
    user_id = request.json.get('user_id')

    # If no user_id, generate a new one (for new users)
    if not user_id or user_id not in user_sessions:
        user_id = str(uuid.uuid4())
        user_sessions[user_id] = {
            'sparkle_points': 0,
            'awaiting_validation': None,
            'validation_type': None
        }

    session = user_sessions[user_id]
    lower_message = user_message.lower()
    radiant_response = ""
    points_earned = 0

    # --- Step 1: Handle ongoing validation (if Radiant asked a 'Yes/No' question) ---
    if session['awaiting_validation']:
        validation_confirmed = 'yes' in lower_message or 'y' in lower_message
        validation_denied = 'no' in lower_message or 'n' in lower_message

        if validation_confirmed:
            response_type = session['validation_type']
            if response_type == 'lonely':
                radiant_response = (
                    "Thanks for letting me know. It's totally okay to feel that way sometimes. "
                    "But you know, even quiet evenings can hold a little spark! How about we find it together? We could...\n\n"
                    "🎧 Listen to a happy song? \n"
                    "📖 Start a story session? Want to hear something, or do you have a best moment from your life you'd love to share with me? I'm really eager to listen!"
                )
                points_earned = 5
                radiant_response += f"\n\nYou just earned {points_earned} 'Brightness Points' for opening up and being ready for a little fun!"
            elif response_type == 'frustrated':
                radiant_response = (
                    "Totally get it! New challenges can sometimes feel like they're speaking a different language. "
                    f"({random.choice(radiant_content['radiant_anecdotes'])}) So, your 'CAN DO' spirit is definitely stronger than any hurdle! "
                    "Let's pause for a moment and take a deep breath. You've got this!\n\n"
                    "Now, let's think: What exactly were you hoping to achieve with this? What's the main thing you want to do? "
                    "Once we know that, we can figure out the best way forward. Would you like me to try and help you figure it out step-by-step, "
                    "or should we call in a friendly expert for backup, like a tech-savvy family member or a friend? We can explore options!"
                )
                points_earned = 10
                radiant_response += f"\n\nYou just earned {points_earned} 'Problem-Solver Points' for not giving up and being ready to tackle this! Let's conquer this digital dragon together, one step at a time!"
            elif response_type == 'low_motivation':
                chosen_anecdote = random.choice(radiant_content['radiant_anecdotes'])
                radiant_response = (
                    "Totally understandable! Even the brightest sun needs a cloud break sometimes. "
                    "But you know what always brings a little sunshine back? Recalling a moment when you were bursting with energy and happiness! "
                    "Can you remember a time when you felt really active and joyful? What was happening then? I bet we can find a spark from that memory!\n\n"
                    f"Or, speaking of finding sparks, {chosen_anecdote}\n\n"
                    "So, what feels right for you right now? Maybe we just need a quick 'reset' button. How about taking a short break first? We could:\n"
                    "🚶‍♂️ Do some light activity, like stretching or a quick walk.\n"
                    "🎬 Watch a short inspirational video on YouTube.\n"
                    "🎧 Listen to an uplifting story or podcast.\n"
                    "Or just pause and let me know what feels possible for you right now."
                )
                points_earned = 15
                radiant_response += f"\n\nYou just earned {points_earned} 'Momentum Sparks'! Even small steps create big waves. Let's find your rhythm again!"
            elif response_type == 'happy_goal': # For "I want to be happy now" confirmation
                chosen_tip = random.choice(radiant_content['happiness_tips'])
                chosen_anecdote = random.choice(radiant_content['radiant_anecdotes'])
                radiant_response = (
                    "Oh, that's a brilliant goal! I love your 'CAN DO' spirit! Let's find some happy sparkles together, right now!\n\n"
                    "How about a quick dose of immediate joy? You could try: \n"
                    "✨ Think of three things you're super grateful for right this moment. \n"
                    "💃 Stand up and do a quick stretch, or dance to your favorite upbeat song! \n"
                    "👀 Take a minute to just notice one beautiful thing around you.\n\n"
                    f"Remember what they say on Happier.in: \"{chosen_tip['tip']}\" - sometimes a tiny shift makes all the difference!\n\n"
                    f"({chosen_anecdote})"
                )
                points_earned = 20 # Higher points for a direct positive goal
                radiant_response += f"\n\nYou just earned {points_earned} 'Joy Seeker Points' for expressing such a wonderful intention! Let's make it happen!"


            session['awaiting_validation'] = None
            session['validation_type'] = None
        elif validation_denied:
            radiant_response = "My apologies! Thank you for clarifying. It's important to me to understand you correctly. What is on your mind?"
            session['awaiting_validation'] = None
            session['validation_type'] = None
        else:
            radiant_response = f"I'm still trying to understand. Can you confirm if you're feeling {session['validation_type']}? (Yes/No)"
    else:
        # --- Step 2: Initial message processing using sentiment and keywords ---
        blob = TextBlob(user_message)
        sentiment_polarity = blob.sentiment.polarity # -1 (negative) to +1 (positive)

        # Check for specific emotional scenarios (more robust keyword matching)
        if contains_any_keyword(lower_message, LONELY_KEYWORDS):
            radiant_response = responses['lonely']['validation']
            session['awaiting_validation'] = "lonely"
            session['validation_type'] = 'lonely'
        elif contains_any_keyword(lower_message, FRUSTRATED_KEYWORDS):
            radiant_response = responses['frustrated']['validation']
            session['awaiting_validation'] = "frustrated"
            session['validation_type'] = 'frustrated';
        elif contains_any_keyword(lower_message, LOW_MOTIVATION_KEYWORDS):
            radiant_response = responses['low_motivation']['validation']
            session['awaiting_validation'] = "low on energy or motivation" # Human-friendly phrase
            session['validation_type'] = 'low_motivation';
        elif contains_any_keyword(lower_message, HAPPY_KEYWORDS) and sentiment_polarity > 0.1: # Catch positive expressions or direct 'want to be happy'
            radiant_response = (
                "Oh, that's a brilliant goal! I love your 'CAN DO' spirit! Let's find some happy sparkles together, right now!\n\n"
                "How about a quick dose of immediate joy? You could try: \n"
                "✨ Think of three things you're super grateful for right this moment. \n"
                "💃 Stand up and do a quick stretch, or dance to your favorite upbeat song! \n"
                "👀 Take a minute to just notice one beautiful thing around you.\n\n"
                f"Remember what they say on Happier.in: \"{random.choice(radiant_content['happiness_tips'])['tip']}\" - sometimes a tiny shift makes all the difference!\n\n"
                f"({random.choice(radiant_content['radiant_anecdotes'])})"
            )
            points_earned = 20
            radiant_response += f"\n\nYou just earned {points_earned} 'Joy Seeker Points' for expressing such a wonderful intention! Let's make it happen!"
            session['awaiting_validation'] = None # No validation needed if already positive/clear
            session['validation_type'] = None
        elif contains_any_keyword(lower_message, GREETING_KEYWORDS):
            radiant_response = random.choice(responses['greetings'])
            session['awaiting_validation'] = None
            session['validation_type'] = None
        else:
            # Default response for inputs not matching specific scenarios
            radiant_response = random.choice(radiant_content['default_responses'])
            session['awaiting_validation'] = None
            session['validation_type'] = None

    # Update sparkle points
    session['sparkle_points'] += points_earned
    user_sessions[user_id] = session # Save updated session (important for persistence)

    return jsonify({
        'radiant_response': radiant_response,
        'sparkle_points': session['sparkle_points'],
        'user_id': user_id # Send user_id back to frontend to maintain session
    })

if __name__ == '__main__':
    # Ensure templates directory exists for render_template
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True) # debug=True for development, turn off for production
