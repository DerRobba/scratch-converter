from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
app = Flask(__name__)
api_key = os.getenv("API_KEY")
base_url = os.getenv("API_BASE")
model = os.getenv("MODEL")
system_prompt = os.getenv("SYSTEM_PROMPT")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json.get('message')
    if not user_prompt:
        return jsonify({"error": "Keine Nachricht erhalten"}), 400

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    ai_message = response.choices[0].message.content
    return jsonify({'reply': ai_message})

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)