# app.py
from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import pillow_heif
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'transformed_images'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files or 'format' not in request.form:
            return 'Missing file or format selection'
        file = request.files['file']
        output_format = request.form['format']
        if file.filename == '':
            return 'No selected file'
        if file and output_format:
            f, _ = os.path.splitext(file.filename)
            outfile = f + '.' + (output_format.lower() if output_format.lower() != 'heif' else 'heic')
            try:
                if file.filename.lower().endswith('.heic'):
                    heif_file = pillow_heif.read_heif(file)
                    im = Image.frombytes(
                        heif_file.mode, 
                        heif_file.size, 
                        heif_file.data,
                        "raw",
                        heif_file.mode,
                        heif_file.stride,
                    )
                else:
                    im = Image.open(file.stream)

                if output_format.lower() == 'heif':
                    heif_image = pillow_heif.from_pillow(im)
                    heif_image.save(os.path.join(app.config['UPLOAD_FOLDER'], outfile), quality=100)
                else:
                    if im.mode == 'RGBA' and output_format.lower() != 'png':
                        im = im.convert('RGB')
                    im.save(os.path.join(app.config['UPLOAD_FOLDER'], outfile))

                return render_template('index.html', filename=outfile)
            except Exception as e:
                return f'Error: {e}'
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
