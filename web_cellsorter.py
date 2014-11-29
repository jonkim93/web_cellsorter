import os
from flask import Flask, request, redirect, url_for, send_from_directory, make_response, send_file, render_template
from werkzeug import secure_filename
from backend import process
from flask_bootstrap import Bootstrap
import cv2

UPLOAD_FOLDER = '/Users/Jon/Documents/College/Research/HealyLab/web_cellsorter/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'JPG', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)

results = None
 #"../uploads/0.jpg"
imgsource = 'http://127.0.0.1:5000/uploads/0.jpg'
image_names = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def splash_page():
    return render_template('base.html', homepage=True, processpage=False)

@app.route('/about')
def about_page():
    return render_template('about.html', homepage=False, processpage=False, aboutpage=True)

@app.route('/process', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files["files[]"]
        if allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cellCount, images = process(os.path.join(app.config['UPLOAD_FOLDER'], filename), DEBUG=False)
            #cellCount, images = process('uploads/' + filename, DEBUG=False)
            global results
            results = "There are %s cells in the image" % str(int(cellCount))
            global image_names
            for i in xrange(0,len(images)):
                print os.path.join(app.config['UPLOAD_FOLDER'], str(i)+".jpg")
                cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], str(i)+".jpg"), images[i]) #images[i].save(os.path.join(app.config['UPLOAD_FOLDER'], filename, str(i)))
                image_names.append("http://127.0.0.1:5000/uploads/" + str(i)+".jpg")
            print image_names
            return redirect(url_for('display_results'))
    return render_template('process.html', homepage=False, processpage=True)  

@app.route('/results', methods=['GET', 'POST'])
def display_results():
    return render_template('result_page.html',homepage=False, processpage=True, results=results, imgsource=imgsource, image_names=image_names[1:], first_image_name=image_names[0])

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
	app.run(debug=True)