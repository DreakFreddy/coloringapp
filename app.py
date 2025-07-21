import os
import cv2
import numpy as np
from flask import Flask, render_template, request, send_from_directory, send_file
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'static/processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_to_coloring_page(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Use Canny edge detection for coloring effect
    edges = cv2.Canny(gray, 50, 150)
    # Invert colors (black lines on white background)
    inverted = cv2.bitwise_not(edges)
    return inverted

@app.route('/', methods=['GET', 'POST'])
def index():
    processed_files = []
    if request.method == 'POST':
        files = request.files.getlist('images')
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process image
            processed = convert_to_coloring_page(filepath)
            processed_filename = f"processed_{filename}"
            processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            cv2.imwrite(processed_path, processed)
            processed_files.append(processed_filename)

    return render_template('index.html', files=processed_files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download_all')
def download_all():
    memory_file = io.BytesIO()
    with ZipFile(memory_file, 'w') as zipf:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith('processed_'):
                zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], filename), arcname=filename)
    memory_file.seek(0)
    return send_file(memory_file, download_name='coloring_pages.zip', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)