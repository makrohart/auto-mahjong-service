from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from route.user import user_bp
from route.welcome import welcome_bp
from predict import predict
import os

def create_app():
    app = Flask(__name__)
    
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def hello_world():
        return 'predict!!!'
    
    @app.route('/predict_image', methods=['POST'])
    def predict_image():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
    
        # 检查是否选择了文件
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # 检查文件类型是否允许
        if file and allowed_file(file.filename):
            # 安全保存文件名
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)
            
            try:
                result = predict(temp_path)

                if os.path.exists(temp_path):
                    os.remove(temp_path)

                return jsonify(result)
                
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    
        return jsonify({'error': 'File type not allowed'}), 400


    with app.app_context():
        # 注册路由
        app.register_blueprint(welcome_bp)
        app.register_blueprint(user_bp)

    return app
