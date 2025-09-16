from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import mimetypes
import logging
from datetime import datetime
from pathlib import Path

from route.user import user_bp
from route.welcome import welcome_bp
from predict import predict

def create_app():
    app = Flask(__name__)
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs('run', exist_ok=True)
    os.makedirs('run/predict', exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def hello_world():
        return 'predict!!!'
    
    @app.route('/predict_image', methods=['POST'])
    def predict_image():
        try:
            # 检查是否有文件上传
            if 'file' not in request.files:
                logger.warning("No file part in request")
                return jsonify({'error': 'No file part'}), 400
            
            file = request.files['file']
            
            # 检查是否选择了文件
            if file.filename == '':
                logger.warning("No file selected")
                return jsonify({'error': 'No selected file'}), 400
            
            # 检查文件大小
            file.seek(0, 2)  # 移动到文件末尾
            file_size = file.tell()
            file.seek(0)  # 重置到文件开头
            
            if file_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {file_size} bytes")
                return jsonify({'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
            
            # 检查文件类型是否允许
            if not allowed_file(file.filename):
                logger.warning(f"File type not allowed: {file.filename}")
                return jsonify({'error': 'File type not allowed. Supported formats: PNG, JPG, JPEG, GIF'}), 400
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            temp_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            logger.info(f"Processing file: {file.filename} -> {unique_filename}")
            
            # 保存文件
            file.save(temp_path)
            
            try:
                # 进行预测
                result = predict(temp_path)
                
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info(f"Cleaned up temp file: {temp_path}")

                if not result['success']:
                    logger.error(f"Prediction failed: {result.get('error', 'Unknown error')}")
                    return jsonify({'error': result['error']}), 500
                
                # 构建响应数据
                response_data = {
                    'success': True,
                    'json_result': result['json_result'],
                    'message': result.get('message', 'Prediction completed'),
                    'output_image_url': f'/get_result_image/{os.path.basename(result["output_image_path"])}' if result['output_image_path'] else None
                }
                
                logger.info(f"Prediction successful: {result.get('message', '')}")
                return jsonify(response_data)
                
            except Exception as e:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.info(f"Cleaned up temp file after error: {temp_path}")
                
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({'error': f'Error processing image: {str(e)}'}), 500
        
        except Exception as e:
            logger.error(f"Unexpected error in predict_image: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/get_result_image/<filename>')
    def get_result_image(filename):
        """获取识别结果图片"""
        try:
            # 确保文件名安全
            safe_filename = secure_filename(filename)
            
            # 在run目录及其子目录中查找图片
            run_dir = Path('run')
            image_path = None
            
            # 首先在run目录直接查找
            direct_path = run_dir / safe_filename
            if direct_path.exists():
                image_path = direct_path
            else:
                # 在predict子目录中查找
                predict_dir = run_dir / 'predict'
                if predict_dir.exists():
                    for subdir in predict_dir.iterdir():
                        if subdir.is_dir() and subdir.name.startswith('predict'):
                            potential_path = subdir / safe_filename
                            if potential_path.exists():
                                image_path = potential_path
                                break
            
            if not image_path or not image_path.exists():
                logger.warning(f"Image not found: {safe_filename}")
                return jsonify({'error': 'Image not found'}), 404
            
            # 获取文件的MIME类型
            mime_type, _ = mimetypes.guess_type(str(image_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            logger.info(f"Serving image: {image_path}")
            return send_file(str(image_path), mimetype=mime_type)
            
        except Exception as e:
            logger.error(f"Error serving image: {str(e)}")
            return jsonify({'error': f'Error serving image: {str(e)}'}), 500


    with app.app_context():
        # 注册路由
        app.register_blueprint(welcome_bp)
        app.register_blueprint(user_bp)

    return app
