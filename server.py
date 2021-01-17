import imghdr
import os
from flask import Flask,flash, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
import socket
import os.path
from os import path
from config import *


app = Flask(__name__)
app.static_folder = 'static'
app_key='encryption'
file_mb_max = 100
app.secret_key = app_key
app.config['MAX_CONTENT_LENGTH'] = file_mb_max*1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['PUBLIC_UPLOAD_PATH'] = 'uploads/public'
app.config['PRIVATE_UPLOAD_PATH'] = 'uploads/private'


def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    files = os.listdir(app.config['PUBLIC_UPLOAD_PATH'])
    privatefiles=[]
    if socket.gethostname()!='' and path.exists(app.config['PRIVATE_UPLOAD_PATH']+'/'+socket.gethostname()):
        privatefiles = os.listdir(app.config['PRIVATE_UPLOAD_PATH']+'/'+socket.gethostname())
    return render_template('index.html', files=files,privatefiles=privatefiles)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('files[]')
    print(uploaded_files)
    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_image(uploaded_file.stream):
                abort(400)
            if(request.form['privacy']=='private'):
                if not os.path.exists(os.path.join(app.config['PRIVATE_UPLOAD_PATH']+'/'+str(socket.gethostname()))):
                    os.makedirs(os.path.join(app.config['PRIVATE_UPLOAD_PATH']+'/'+str(socket.gethostname())))
                uploaded_file.save(os.path.join(app.config['PRIVATE_UPLOAD_PATH']+'/'+str(socket.gethostname()), filename))
            else:
                uploaded_file.save(os.path.join(app.config['PUBLIC_UPLOAD_PATH'], filename))
    flash('File(s) uploaded')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['PUBLIC_UPLOAD_PATH'], filename)

@app.route('/privateuploads/<filename>')
def private_upload(filename):
    return send_from_directory(app.config['PRIVATE_UPLOAD_PATH']+'/'+str(socket.gethostname()), filename)

if __name__ == '__main__':
    app.run()

#https://towardsdatascience.com/writing-a-multi-file-upload-python-web-app-with-user-authentication-8f75064b819a

	#https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
