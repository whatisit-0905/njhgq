from flask import Flask, request, jsonify, send_from_directory,render_template,Response
from flask_cors import CORS
import os
from PIL import Image
import webview
import cv2
# from ultralytics import YOLO
import uuid

from threading import Thread,Event
import numpy as np
import time
from camera.ocr_cam import Camera
from MvImport.MvCameraControl_class import *
# MvCameraControl_class import * # type: ignore
import time
from camera.grabimage1 import enum_devices,identify_different_devices,input_num_camera
from camera.grabimage1 import creat_camera,open_device,one_shot_image
from camera.grabimage1 import decide_divice_on_line
from config import *
from camera.cam_yourDad import Camera_father
import yaml

# current_directory = os.getcwd().replace("\\", "/")

import socket

def send_udp_message(message, ip, port):
    # 创建一个UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (ip, port)
    try:
        # 发送数据
        print(f'Sending "{message}" to {ip}:{port}')
        sent = sock.sendto(message.encode(), server_address)
    finally:
        sock.close()
# 读取配置文件，显式指定 UTF-8 编码
def load_config(file_path='config.yaml'):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config
# 使用配置
config = load_config()
produce = config['produce']

global camera
global camera2
global camera3
global camera4

cam_dict = {cam_info['serial']: cam_info['ip'] for cam_name, cam_info in config['cameras'].items()}
mycam=Camera_father(cam_dict=cam_dict)

if produce:
    # 读取摄像头配置并动态创建字典

    mycam.initialize_cameras()
        # 创建 Camera 类实例
    camera = mycam.cameras[0]
    camera2 = mycam.cameras[1]
    camera3 = mycam.cameras[2]
    camera4 = mycam.cameras[3]

# Camera reconnection logic
def reconnect_cameras(stop_event):
    # print("断线重连进程执行")
    while not stop_event.is_set():
        # print("11111") 
        for _cam in mycam.cameras: 
            if _cam!=None:
                if(_cam.is_cam_online()):
                    # print("here")
                    pass
                else:
                    # _cam = Camera(_cam.serial, _cam.cam_ip,mycam.local_net_ip)
                    
                    _cam.camera_create_byIP()
                    _cam.open_camera() 
                    print(f"reopen ip {_cam.cam_ip}")
                    time.sleep(3)
    
        time.sleep(1)

app = Flask(__name__, static_folder='static')  # 设置静态文件夹为 'statics'
CORS(app)
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename,mimetype='application/javascript')

# yoloDefect = YOLOV10_run(weight=r"utils\weights\bestDefect2.pt")
# yoloS1S2  = YOLOV10_run(weight=r"utils\weights\bestS1S2.pt")
# calLength = CalLength(fname=r"test_data\testCal\826chess.jpg")


# Folder to store uploaded images
UPLOAD_FOLDER = upload_folder
app.config['UPLOAD_FOLDER'] = upload_folder



@app.route('/testPhoto', methods=['POST'])
def testPhoto():
    time.sleep(0.5)
    return jsonify({"image_url": f"/uploads/test244995924176a3bb27b7ee5c00c6a6a.png"})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




@app.route('/handleSnap', methods=['POST','GET'])
def handleSnap():

    
    send_udp_message("WA0999T", "192.168.0.110", 3205)
    photo_flag = "1727074541_ai"
    image_path1=f"uploads/result_cam1In{photo_flag}.jpg"
    image_path2=f"uploads/result_cam2In{photo_flag}.jpg"
    image_path3=f"uploads/result_cam3In{photo_flag}.jpg"
    image_path4=f"uploads/result_cam4In{photo_flag}.jpg"
    if produce:
        photo_flag = time.time()
        image_path1=f"uploads/result_cam1In{photo_flag}.jpg"
        image_path2=f"uploads/result_cam2In{photo_flag}.jpg"
        image_path3=f"uploads/result_cam3In{photo_flag}.jpg"
        image_path3=f"uploads/result_cam4In{photo_flag}.jpg"
        camera.capture_image(image_path1)  # 捕获单张照片
        camera2.capture_image(image_path2)  # 捕获单张照片
        camera3.capture_image(image_path3)  # 捕获单张照片
        camera4.capture_image(image_path4)  # 捕获单张照片
        
    result = {'code':1,'data':[{"id": 1,"url":image_path1},{"id": 2,"url":image_path2},{"id": 3,"url":image_path3},{"id": 4,"url":image_path4}]}
    
    logger.info({"handleSnap:":result})
    send_udp_message("WA0999F", "192.168.0.110", 3205)
    return jsonify(result)


@app.route('/handleTest', methods=['POST','GET'])
def handleTest():
    send_udp_message("WA0999T", "192.168.0.110", 3205)
    if not produce:
        print('goto handleTest')
    for filename in os.listdir(upload_folder):
        if filename.startswith('result') and filename.endswith('.jpg'):
            file_path = os.path.join(upload_folder, filename)
            
    photo_flag = "1727074541_ai"
    image_path1=f"uploads/result_cam1In{photo_flag}.jpg"
    image_path2=f"uploads/result_cam2In{photo_flag}.jpg"
    image_path3=f"uploads/result_cam3In{photo_flag}.jpg"
    image_path4=f"uploads/result_cam4In{photo_flag}.jpg"
    if produce:
        photo_flag = time.time()
        image_path1=f"uploads/result_cam1In{photo_flag}.jpg"
        image_path2=f"uploads/result_cam2In{photo_flag}.jpg"
        image_path3=f"uploads/result_cam3In{photo_flag}.jpg"
        image_path4=f"uploads/result_cam4In{photo_flag}.jpg"
        camera.capture_image(image_path1)  # 捕获单张照片
        camera2.capture_image(image_path2)  # 捕获单张照片
        camera3.capture_image(image_path3)  # 捕获单张照片
        camera4.capture_image(image_path4)  # 捕获单张照片
    res1 = yolo_arrow.run_arrow(image_path1)
    res2 = yolo_arrow.run_arrow(image_path2)
    res3,newpath3,confidence3 = yolo_type.run_type(image_path3)
    res4,newpath4,confidence4 = yolo_type.run_type(image_path4)
    if(confidence4>confidence3):
        restype = res4
    else:
        restype = res3
    res = "@@@DIR"+str(res1)+str(res2)+str(restype)
    result = {'code':1,'res':res,'data':[{"id": 1,"url":image_path1},{"id": 2,"url":image_path2},{"id": 3,"url":newpath3},{"id": 4,"url":newpath4}]}
    if(res2=="E" or res1=="E"):
        logger.error(result)
    else:
        logger.info(result)
    send_udp_message("WA0999F", "192.168.0.110", 3205)
    return jsonify(result)
@app.route('/stream')
def stream():
    def event_stream():
        while True:
            yield f"data: {{'message': 'Hello from Python!', 'time': '{time.ctime()}'}}\n\n"
            time.sleep(10)  # 每3秒发送一次

    return Response(event_stream(), content_type='text/event-stream')


def run_flask_app():
    app.run(host='127.0.0.1', port=5000, debug=False)

def start_webview():
    # 使用 pywebview 启动一个 Web 浏览器窗口
    # window = webview.create_window('·互感器缺陷检测软件 -上海大学', 'http://localhost:5000/page1')
    window = webview.create_window('·互感器缺陷检测软件 -上海大学', 'http://localhost:3000/')
    webview.start()

if __name__ == '__main__':
    # if not produce:
    #     app.run(debug=True)
    # flask_thread = Thread(target=run_flask_app)
    # flask_thread.daemon = True
    # flask_thread.start()
    # start_webview()

    stop_reconnect_event = Event()
    if not produce:
        stop_reconnect_event.set() 
    reconnect_thread = Thread(target=reconnect_cameras, args=(stop_reconnect_event,))
    reconnect_thread.daemon = True
    reconnect_thread.start()

    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    start_webview()

    # Stop camera reconnection thread when the app exits
    stop_reconnect_event.set()
    reconnect_thread.join()
