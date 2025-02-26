import cv2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ultralytics import YOLOv10
# from config import *
from utils.Logger import logger
from utils.nmsYolov10 import nms
# import torch
# flag = torch.cuda.is_available()
# print(flag)
# input("wait") 


def hsv2bgr(h, s, v):
    h_i = int(h * 6)
    f = h * 6 - h_i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    r, g, b = 0, 0, 0

    if h_i == 0:
        r, g, b = v, t, p
    elif h_i == 1:
        r, g, b = q, v, p
    elif h_i == 2:
        r, g, b = p, v, t
    elif h_i == 3:
        r, g, b = p, q, v
    elif h_i == 4:
        r, g, b = t, p, v
    elif h_i == 5:
        r, g, b = v, p, q

    return int(b * 255), int(g * 255), int(r * 255)

def random_color(id):
    h_plane = (((id << 2) ^ 0x937151) % 100) / 100.0
    s_plane = (((id << 3) ^ 0x315793) % 100) / 100.0
    return hsv2bgr(h_plane, s_plane, 1)


def keep_highest_confidence_two_boxes(boxes,x = 3):
    # 根据置信度降序排序
    sorted_boxes = sorted(boxes, key=lambda x: float(x[4]), reverse=True)
    
    # 保留置信度最高的两个框
    highest_confidence_two_boxes = sorted_boxes[:x]
    
    return highest_confidence_two_boxes

def showIImg(img):
        window_name = "Predicted Image"
        desired_width = 1080

        # 计算新的高度以保持纵横比
        original_height, original_width = img.shape[:2]
        aspect_ratio = original_width / original_height
        new_height = int(desired_width / aspect_ratio)

        # 创建一个可调整大小的窗口并设置宽度为1080
        window_name = "Predicted Image"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, desired_width, new_height)
        cv2.imshow(window_name, img)

        # 等待用户按键后关闭窗口
        key = cv2.waitKey(0)

        # 关闭所有窗口
        cv2.destroyAllWindows()

class YOLOV10_run:
    def __init__(self,weight = r"utils\weights\bestS1S2.pt") -> None:
        self.model = YOLOv10(weight)
    def run_flask(self,path):
        img = cv2.imread(path)
        results = self.model(img)
        return results[0]
    
    def run_type(self,path,save = True,showImg = False):
        img = cv2.imread(path)
        results = self.model(img)[0]
        # results=self.model.predict(path,show=False,save=False,conf=0.1,iou=0.1,nms=True)[0]
        names   = results.names
        # names   = ["01","02","03","04","05","06","11","12","13","14","15","16"]
        names   = ["01","11","02","12","03","13","04","14","05","15","06","16","07","17"]
        boxes   = results.boxes.data.tolist()
        boxes = nms(boxes,IOU=0.8)
        logger.info({path:boxes})
        boxes = keep_highest_confidence_two_boxes(boxes,3)
        # if len(boxes)!=2 or int(boxes[0][5])+int(boxes[1][5])!=1:
        #     return "识别数量不对//识别种类不对"
        dir = 0
        type = 0
        count = 0
        confidence = 0
        try:
            for obj in boxes:
                left, top, right, bottom = int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3])
                confidence = max(obj[4],confidence)
                label = int(obj[5])
                caption = f"{names[label]} {confidence:.2f}"
                dir += int(names[label][0])
                
                if type == 0:
                    type = f"{int(names[label][1]):02d}" 
                color = random_color(label)
                cv2.rectangle(img, (left, top), (right, bottom), color=color ,thickness=3, lineType=cv2.LINE_AA)
                caption = f"{names[label]} {confidence:.2f}"
                print("caption---",caption)
                w, h = cv2.getTextSize(caption, 0, 1, 2)[0]
                # cv2.rectangle(img, (left - 3, top - 33), (left + w + 10, top), color, 20)
                cv2.putText(img, caption, (left, top), 0, 3, color, 3, 6)
                if(int(names[label][1])!=5 and int(names[label][1])!=6):
                    count = 1 
                    break
                else:
                    count += 1

            newpath = path.split(".")[0] + "_ai.jpg"
            newpath = path.split(".")[0] + f"_ai{count}.jpg"
            if save:
                cv2.imwrite(newpath, img)
            if showImg:
                showIImg(img)
                
            res = str(dir)+"Type"+str(type)+"0"+str(count)
            # 注释 1：【000： 第一个 0 代表周转箱方向正确，第二个 0 代表托盘方向正确，第三个
            # 0 代表互感器方向反向的数量】
            # 注释 2：【Type0103: 01 为 01-99 代表 1-99 种型号（这个靠外观检测来区分 13 种的
            # 哪一种）；03 为托盘里互感器的数量，01 代表 1 只，02 代表 2 只，03 代表三只】
            # 注释 3：【识别如果周转箱、托盘、互感器方向有任意一个不正确则，VPC 向 PLC 发送：
            # @@@DIRnnn;Type:XXYY!!!
            return res,newpath,confidence
        except:
            return "E"
    def run_arrow(self,path,save=True):
        img = cv2.imread(path)
        results = self.model(img)[0]
        names   = results.names
        names   = ["arrow","triangle"]
        boxes   = results.boxes.data.tolist()
        boxes = keep_highest_confidence_two_boxes(boxes,2)
        # if len(boxes)!=2 or int(boxes[0][5])+int(boxes[1][5])!=1:
        #     return "识别数量不对//识别种类不对"
        map = {}
        try:
            for obj in boxes:
                left, top, right, bottom = int(obj[0]), int(obj[1]), int(obj[2]), int(obj[3])
                confidence = obj[4]
                label = int(obj[5])
                caption = f"{names[label]} {confidence:.2f}"
                print("caption---",caption)
                
                if(label == 0):
                    map['first'] = [left, top, right, bottom,confidence]
                if(label == 1 ):
                    map['second'] = [left, top, right, bottom,confidence]
                
            newpath = path.split(".")[0] + "_ai.jpg"
            # newpath = path.split(".")[0] + f"_ai.jpg"
            if save:
                cv2.imwrite(newpath, img)
            if (abs(map['first'][0]-map['second'][0])) < (abs(map['first'][2]-map['second'][2])):
                return 0#代表反向正确
            else:
                return 1#代表方向不对
        except:
            return "E"

    def run(self,path):
        img = cv2.imread(path)
        results = self.model(img)[0]
        names   = results.names
        names   = ["arrow","triangle"]
        # names   = ["01","02","03","04","05","06","11","12","13","14","15","16"]
        boxes   = results.boxes.data.tolist()
        boxes = keep_highest_confidence_two_boxes(boxes,2)

        drawn_texts = []  # 用于存储已绘制文本的位置和大小
 
        for obj in boxes:
            left, top, right, bottom = map(int, obj[:4])
            confidence = obj[4]
            label = int(obj[5])
            color = random_color(label)
            
            # 绘制矩形框
            cv2.rectangle(img, (left, top), (right, bottom), color=color, thickness=3, lineType=cv2.LINE_AA)
            
            # 准备文本标签
            caption = f"{names[label]} {confidence:.2f}"
            w, h = cv2.getTextSize(caption, 0, 1, 2)[0]
            
            # 初始文本位置
            text_x = left
            text_y = top - h - 5
            
            # 检查重叠并调整位置
            for (txt_x, txt_y, txt_w, txt_h) in drawn_texts:
                # 如果新标签与已绘制标签重叠
                if (text_x < txt_x + txt_w and text_x + w > txt_x and
                    text_y < txt_y + txt_h and text_y + h > txt_y):
                    # 调整新标签的位置（例如，向下移动）
                    text_y += txt_h + 10  # 增加一个适当的偏移量
                    # 可以添加更多逻辑来处理垂直空间不足的情况
            
            # 更新已绘制文本的位置列表
            drawn_texts.append((text_x, text_y, w, h))
            
            # 绘制文本标签
            cv2.putText(img, caption, (text_x, text_y), 0, 1, color, 3, 6)  # 黑色文本，厚度为3
        # 展示图像
        window_name = "Predicted Image"
        desired_width = 1080

        # 计算新的高度以保持纵横比
        original_height, original_width = img.shape[:2]
        aspect_ratio = original_width / original_height
        new_height = int(desired_width / aspect_ratio)

        # 创建一个可调整大小的窗口并设置宽度为1080
        window_name = "Predicted Image"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, desired_width, new_height)
        cv2.imshow(window_name, img)

        # 等待用户按键后关闭窗口
        key = cv2.waitKey(0)

        # 关闭所有窗口
        cv2.destroyAllWindows()
        import time
        cv2.imwrite(f"logs/{time.time()}.jpg", img)
        print("save done")    



if __name__ == "__main__":
    yolo = YOLOV10_run(weight=r"utils\weights\best_arrow_1202.pt")
    import os
    dir = r"uploads\arrow"
    for file in os.listdir(dir):
        # yolo.run(os.path.join(dir,file))
        image_path = os.path.join(dir,file)
        # image_path = r"uploads\testerror1.jpg"
        # if(image_path.endswith("jpg") and file.startswith("result_cam3")):
            # image_path = "uploads\9ebbf5a1e1c643555cf877cd5819e6f.png"
        # res =  yolo.run_type(image_path,save=False)
        res =  yolo.run_arrow(image_path)
        # yolo.run(image_path)
        print(image_path,"的检测结果：：：",res)
       
