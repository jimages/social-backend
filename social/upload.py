import os
from datetime import datetime
from flask import Blueprint, request, current_app, jsonify
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = ('jpg', 'png', "jpeg")

bp = Blueprint('upload', __name__)


def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS


@bp.route('/img', methods=['POST'])
def upload_img():
    file_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext_name = filename.split('.')[-1]
        c_time = datetime.now().strftime('%Y-%m-%d-%H-%M')
        random_str = uuid.uuid4().hex
        filename = f'{c_time}_{random_str}.{ext_name}'
        file.save(os.path.join(file_dir, filename))
        return jsonify({
            'ret': True,
            'filename': filename
        })
    else:
        return jsonify({
            'ret': False,
            'error_message': '文件上传失败'
        })