from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import soundfile as sf
import librosa
import pytesseract
from PIL import Image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/upload/text', methods=['POST'])
def upload_text():
    data = request.json
    return jsonify({
        'message': 'Text received successfully!',
        'text': data.get("text", "")
    })

@app.route('/api/upload/audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        audio, sr = librosa.load(filepath, sr=None)
        duration = librosa.get_duration(y=audio, sr=sr)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Audio uploaded successfully",
        "filename": file.filename,
        "duration_sec": duration,
        "samplerate": sr
    })

@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Image uploaded successfully",
        "filename": file.filename,
        "extracted_text": text.strip()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
