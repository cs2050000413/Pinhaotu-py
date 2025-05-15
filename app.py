from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
import os
import io
import numpy as np

app = Flask(__name__)

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_black_background(image):
    # 转换为numpy数组
    img_array = np.array(image)
    # 计算平均像素值
    mean_value = np.mean(img_array)
    # 如果平均值小于50（接近黑色），返回True
    return mean_value < 50

def process_images(image_files, invert_mode=False):
    if not 5 <= len(image_files) <= 9:
        return None, "请上传5-9张图片"
    
    # 处理第一张图片
    first_image = Image.open(image_files[0])
    result = np.array(first_image).astype(float)
    # 在反相模式下，对所有图片进行反相处理
    # 在正常模式下，只对黑色背景的图片进行反相处理
    if invert_mode or is_black_background(first_image):
        result = 255 - result
    
    # 处理剩余图片
    for image_file in image_files[1:]:
        img = Image.open(image_file)
        img_array = np.array(img).astype(float)
        
        # 在反相模式下，对所有图片进行反相处理
        # 在正常模式下，只对黑色背景的图片进行反相处理
        if invert_mode or is_black_background(img):
            img_array = 255 - img_array
        
        # 正片叠底运算
        result = (result * img_array) / 255.0
    
    # 将结果转换回0-255范围
    result = np.clip(result, 0, 255).astype(np.uint8)

    final_image = Image.fromarray(result)
    return final_image, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/invert', methods=['POST'])
def invert_image():
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify({'error': '无效的请求'}), 400
    
    try:
        # 从data URL中提取图片数据
        image_data = data['image_data'].split(',')[1] if ',' in data['image_data'] else data['image_data']
        image_data = image_data.split('base64,')[-1] if 'base64,' in image_data else image_data
        
        # 将base64解码为图片
        import base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # 进行反相处理
        img_array = np.array(image)
        inverted_array = 255 - img_array
        inverted_image = Image.fromarray(inverted_array.astype('uint8'))
        
        # 将处理后的图片转换为字节流
        output = io.BytesIO()
        inverted_image.save(output, format='PNG')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/png',
            as_attachment=True,
            download_name='inverted.png'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': '没有选择文件'})
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': '没有选择文件'})
    
    # 验证文件数量
    if not (5 <= len(files) <= 9):
        return jsonify({'error': '请上传5-9张图片'})
    
    # 验证文件类型
    for file in files:
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'})
    
    # 获取处理模式
    invert_mode = request.form.get('mode') == 'invert'
    
    # 处理图片
    result_image, error = process_images(files, invert_mode)
    if error:
        return jsonify({'error': error})
    
    # 保存结果
    output = io.BytesIO()
    result_image.save(output, format='PNG')
    output.seek(0)
    
    # 返回处理后的图片
    return send_file(
        output,
        mimetype='image/png',
        as_attachment=True,
        download_name='result.png'
    )

if __name__ == '__main__':
    app.run(debug=True)