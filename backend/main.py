"""
India Stock Market Analyzer - Flask Backend
Main application entry point
"""

from flask import Flask
from flask_cors import CORS
from routes.api import api_bp
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def health():
    return {"status": "healthy", "message": "India Stock Market Analyzer API"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
