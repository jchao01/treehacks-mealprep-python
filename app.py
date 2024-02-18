from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from autocart import AutoCart

AUTOCART = AutoCart()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/clear_history', methods=['DELETE'])
def clear_history():
    AUTOCART.chat_history = []
    return jsonify({'message': 'Chat history cleared'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    print(f'Received message: {message}')
    response = AUTOCART.chat(message)
    return jsonify({'response': response})
    
    # try:
        # Using subprocess.run instead of exec for better handling in Python
        # Ensure the Python script does not have untrusted input directly inserted into command line
        # result = subprocess.run(['python', 'autocart.py', message], capture_output=True, text=True)
        # if result.returncode != 0 or result.stderr:
        #     print(f"stderr: {result.stderr}")
        #     return jsonify({'error': 'Internal Server Error'}), 500
        # print(f"stdout: {result.stdout}")
        # return jsonify({'response': result.stdout.strip()})
    # except Exception as e:
    #     print(f'exec error: {e}')
    #     return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
