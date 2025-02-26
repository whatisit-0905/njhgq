from flask import Flask, render_template, send_from_directory, request, jsonify
import os
from flask_cors import CORS
import webview
from threading import Thread
import sys

#------------------------------------------------------------------------------
#生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):               #是否打包的
        base_path = sys._MEIPASS                    #得到运行时的目录
    else:
        base_path = os.path.abspath(".")            #得到当前目录
    return os.path.join(base_path, relative_path)
    
#获得首页的绝对路径
indexPage = resource_path(os.path.join("templates","index.html"))
# print(indexPage)
#------------------------------------------------------------------------------

app = Flask(__name__)
CORS(app)  # 允许所有域名跨域访问

@app.route('/')
def index():
    return render_template('index.html')
# 添加静态文件路由
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/handleSnap', methods=['POST','GET'])
def handleSnap():
    image_paths = [
    "/uploads/image_handleTest_0_test.jpg",
    "/uploads/image_handleTest_1_test.jpg",
    "/uploads/image_handleTest_2_test.jpg",
    "/uploads/image_handleTest_3_test.jpg",
    "/uploads/image_handleTest_4_test.jpg",
    "/uploads/image_handleTest_5_test.jpg",
    "/uploads/image_handleTest_6_test.jpg"
]
    snapimages = []
    # 为每张图片创建数据字典
    for idx, img_path in enumerate(image_paths):
        snapimages.append({
            'id': idx + 1, 
            'imgpath': img_path,
            'res': None  
    }) 
    result = {
            'code': 1,
            'data': snapimages,
            'result': None
            }
    return jsonify(result)

# Modify the handleTest function to update TCP server with results
@app.route('/handleTest', methods=['POST','GET'])
def handleTest():
    image_paths = [
    "/uploads/image_handleTest_1_test.jpg",
    "/uploads/image_handleTest_0_test.jpg",
    "/uploads/image_handleTest_3_test.jpg",
    "/uploads/image_handleTest_4_test.jpg",
    "/uploads/image_handleTest_2_test.jpg",
    "/uploads/image_handleTest_6_test.jpg",
    "/uploads/image_handleTest_5_test.jpg"
]

    testimages = []
    # 为每张图片创建数据字典
    for idx, img_path in enumerate(image_paths):
        testimages.append({
            'id': idx + 1, 
            'imgpath': img_path,
            'res': None  
    }) 
    result = {
            'code': 1,
            'data': testimages,
            'result': detection_info
            }
    return jsonify(result)

#前端请求返回数据（手动抓拍和手动测试也是类似的）
# 图片的检测信息
detection_info = [
    {"key": "time", "text": "时间", "value": "2024-01-01 00:00:00"},
    {"key": "current_ratio", "text": "当前比例", "value": "0.95"},
    {"key": "secondary_load_ratio", "text": "次级负载比例", "value": "0.95"},
    {"key": "accuracy", "text": "准确率", "value": "98.5%"},
    {"key": "P1", "text": "主参数1", "value": "1"},
    {"key": "P2", "text": "主参数2", "value": "1"},
    {"key": "S1", "text": "次参数1", "value": "0"},
    {"key": "S2", "text": "次参数2", "value": "0"},
    {"key": "SM1", "text": "主模块1", "value": "1"},
    {"key": "SM2", "text": "主模块2", "value": "1"},
    {"key": "hole_diameter", "text": "孔径", "value": "18.9"},
]

# 模拟七张图片的路径
image_paths = [
    "/uploads/white_image.png",
    "/uploads/result_cam2In1733993678.3064287.jpg",
    "/uploads/result_cam2In1733993241_ai.jpg",
    "/uploads/result_cam2In1733642841.656972.jpg",
    "/uploads/result_cam1In1733992219_ai.jpg",
    "/uploads/result_cam1In1733989481.733086.jpg",
    "/uploads/result_cam1In1733989429_ai.jpg",
    "/uploads/result_cam1In1733989429_ai.jpg",
    "/uploads/result_cam1In1733989429_ai.jpg",
    
]

images_data = []
# 为每张图片创建数据字典
for idx, img_path in enumerate(image_paths):
    images_data.append({
        'id': idx + 1,  # 假设图片ID从1开始
        'imgpath': img_path,
        'res': None  # 每张图片使用相同的检测信息
    })

@app.route('/get_images')
def get_images():
    try:
       
        result = {
            'code': 1,
            'data': images_data,
            'result': detection_info
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'code': 0,
            'data': [],
            'result': str(e)
        })
    





# 模拟设备状态数据
# 1 绿色 0 红色
devices_status =[
    {"key": "camera1", "text": "相机1", "value": {"status": 1, "description": "已连接"}},
    {"key": "camera2", "text": "相机2", "value": {"status": 0, "description": "未连接"}},
    {"key": "camera3", "text": "相机3", "value": {"status": 1, "description": "已连接"}},
    {"key": "camera4", "text": "相机4", "value": {"status": 0, "description": "未连接"}},
    {"key": "camera5", "text": "相机5", "value": {"status": 1, "description": "已连接"}},
    {"key": "camera6", "text": "相机6", "value": {"status": 0, "description": "未连接"}},
    {"key": "camera7", "text": "相机7", "value": {"status": 1, "description": "已连接"}},
    {"key": "plc", "text": "plc", "value": {"status": 1, "description": "已连接"}}
]

# 前端请求获取设备状态（对应红绿状态灯）
@app.route('/get_status')
def get_status():
    result = {
            'code': 1,
            'result': None,
            'data': devices_status
        }
    return jsonify(result)


@app.route('/get_history')
def get_history():
    # data = request.json
    # starttime = data.get('starttime')
    # endtime = data.get('endtime')
    result = [
        {"status":True, "time":"2024-01-01", "detection_info":detection_info,"image_paths":image_paths},
        {"status":False,  "time":"2024-01-02", "detection_info":detection_info,"image_paths":image_paths},
        {"status":True, "time":"2024-01-03","detection_info":detection_info,"image_paths":image_paths}
    ]
    return jsonify({
        "data":result,
        "total":3
    })

def run_flask_app():
    app.run(host='127.0.0.1', port=5001, debug=False)

if __name__ == '__main__':
    # app.run(debug=True)
    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    # 创建 webview 窗口并加载 index 页面
    webview.create_window(title='检测', url=f"file://{indexPage}", width=1000, height=600)
    webview.start()