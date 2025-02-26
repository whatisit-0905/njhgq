
from utils.predict import YOLOV10_run
import os
import yaml

# produce = False #是否正式使用
# produce = True #是否debug

upload_folder = 'uploads'#uploads图片存储文件
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

#log
from utils.Logger import LogUtils
logger = LogUtils().get_log()

with open("config.yaml", 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)


yolo_arrow = YOLOV10_run(weight=config["yolo_arrow_weight"])
yolo_type = YOLOV10_run(weight=config["yolo_type_weight"])