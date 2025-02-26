import cv2
import json
import os
import sys
import numpy as np
from os import getcwd
import cv2
import msvcrt
from ctypes import *
# sys.path.append(r"hk_utilt\Python\MvImport")
from MvImport.MvCameraControl_class import * # type: ignore
from camera.grabimage1 import enum_devices,identify_different_devices,input_num_camera
from camera.grabimage1 import creat_camera,open_device,one_shot_image
from camera.grabimage1 import decide_divice_on_line

class Camera:
    def __init__(self):
        """
        初始化 Camera 类，默认使用第一个摄像头设备。

        :param camera_id: 摄像头的ID，通常为0表示默认摄像头。
        """
            # ch:初始化SDK | en: initialize SDK
        

        self.stDeviceList= None #设备登陆句柄
        self.cam=None
        

        self.cap = None
        self.parameters = {}

    def camrea_create_byID(self,id,devicelist):
            self.devicelist=devicelist
            self.cam, self.stDeviceList = creat_camera(self.devicelist, id, log=False)

          
    def open_camera(self):
        """
        打开摄像头设备。
       
        :return: 成功返回 True，失败返回 False。
        """
        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if  ret:
            print("Failed to open camera.")
            return False
        print(f"Camera opened successfully.")
        return True

    def cam_start_grabbing(self):
        ret = self.cam.MV_CC_StartGrabbing()
        if ret != 0:
            print("开始取流失败! ret[0x%x]" % ret)
           

    def export_camera_parameters(self, file_path="FeatureFile.mfs"):
        """
        导出当前摄像头的参数到 mfs 文件中。
        
        :param file_path: 保存摄像头参数的文件路径，默认为 "camera_params.json"。
        :return: 成功返回 True，失败返回 False。
        """
        print ("start export the camera properties to the file")
        print ("wait......")

        #ch:将相机属性导出到文件中 | en:Export the camera properties to the file
        ret = self.cam.MV_CC_FeatureSave(file_path)
        if MV_OK != ret:#MV_OK可能是动态链接库里定义的变量
            print ("save feature fail! ret [0x%x]" % ret)
            return False
        print ("finish export the camera properties to the file")
        return True

    def import_camera_parameters(self, file_path="camera_params.json"):
        """
        从 mfs 文件中导入摄像头参数并应用到摄像头设备。
        
        :param file_path: 摄像头参数文件路径，默认为 "camera_params.json"。
        :return: 成功返回 True，失败返回 False。
        """
        ret = self.cam.MV_CC_FeatureLoad("FeatureFile.mfs")
        if MV_OK != ret:
            print ("load feature fail! ret [0x%x]" % ret)
            return False
        print ("finish import the camera properties from the file")
        return True

    def capture_image(self, file_name="captured_image.jpg"):
        """
        使用摄像头捕捉一张照片并保存为文件。
        
        :param file_name: 保存图像的文件名，默认为 "captured_image.jpg"。
        :return: 成功返回 True，失败返回 False。
        """
        self.cam_start_grabbing()
        one_shot_image(self.cam,active_way="getImagebuffer",output_path= file_name)
        self.stop_Grabing()
    def close_camera(self):
        """
        关闭摄像头设备。
        """
        ret = self.cam.MV_CC_CloseDevice()
        if ret != 0:
            print ("close deivce fail! ret[0x%x]" % ret)
            return False

        # ch:销毁句柄 | Destroy handle
        ret = self.cam.MV_CC_DestroyHandle()
        if ret != 0:
            print ("destroy handle fail! ret[0x%x]" % ret)
            return True
        return True

    def is_cam_online(self):
        ret=decide_divice_on_line(cam=self.cam)
        return ret

    def stop_Grabing(self):
        ret = self.cam.MV_CC_StopGrabbing()
        if ret != 0:
            print("stop grabbing fail! ret[0x%x]" % ret)
            # sys.exit()
            return False
        else:
            return True


# 示例用法
if __name__ == "__main__":
    # MvCamera.MV_CC_Initialize()
    # devicelist=enum_devices(device=0,device_way=False)
    # identify_different_devices(devicelist)
    MvCamera.MV_CC_Initialize()

    devicelist=enum_devices(device=0,device_way=False)
    print("deviceList type",type(devicelist))

    dev_info_dict=identify_different_devices(devicelist)
    # camera_dict={"G15926345":0,"DA3826510":1}
    camera = Camera()  # 创建 Camera 类实例
    camera2=Camera()
    camera3=Camera()
    import time

    # id=input("输入你要打开的相机1编号 ")
    camera.camrea_create_byID(dev_info_dict['G15926345'])
    status1=camera.open_camera()
    # camera.cam_start_grabbing()
    # statu2=camera.is_cam_online()
    # i=0
    # while(True):
    #     statu2=camera.is_cam_online()
    #     i+=1
    #     time.sleep(1)
    #     if not statu2:
    #         camera.close_camera()
    #         time.sleep(3)
    #         try:
    #             camera.camrea_create_byID(id)
    #             camera.open_camera()
    #             statu2=camera.is_cam_online()
    #         except Exception as e:
    #             print (e)
    #             statu2=False
    #             print("retry")
    #     else:
    #         camera.cam_start_grabbing()#必须要在导入导出函数之后
        
    #         camera.capture_image(f"0920dxy/output{i}.jpg")  # 捕获单张照片 
    #         camera.stop_Grabing()
            

    time.sleep(1)

    # id=input("输入你要打开的相机2编号 ")
    camera2.camrea_create_byID(dev_info_dict['DA3826510'])
    camera2.open_camera()
    # camera2.cam_start_grabbing()


    i=0
    while True:
        
        camera.capture_image(f"uploads/output1{i}.jpg")
        

        
        camera2.capture_image(f"uploads/output2{i}.jpg")
      
        i+=1
    # id=input("输入你要打开的相机3编号 ")
    # camera3.camrea_create_byID(id)
    # camera3.open_camera()


    
    
        
    # camera.export_camera_parameters("19gm1.mfs")  # 导出摄像头参数
    # camera.import_camera_parameters("19gm1.mfs")  # 导入摄像头参数
    # camera.cam_start_grabbing()#必须要在导入导出函数之后
    
    # camera.capture_image(f"0920dxy/output1.jpg")  # 捕获单张照片
    # camera.close_camera()  





# camera.export_camera_parameters("19gc.mfs")  # 导出摄像头参数
#     camera.import_camera_parameters("19gc.mfs")  # 导入摄像头参数
#     camera2.export_camera_parameters("19gm2.mfs")  # 导出摄像头参数
#     camera2.import_camera_parameters("19gm2.mfs")  # 导入摄像头参数
#     camera2.cam_start_grabbing()#必须要在导入导出函数之后
        
#     camera2.capture_image(f"0920dxy/output2.jpg")  # 捕获单张照片
#     camera2.close_camera()               



#     # camera3.export_camera_parameters("19gm3.mfs")  # 导出摄像头参数
#     # camera.import_camera_parameters("19gm3.mfs")  # 导入摄像头参数
#     camera3.cam_start_grabbing()#必须要在导入导出函数之后

#     camera3.capture_image(f"0920dxy/output3.jpg")  # 捕获单张照片  
#     camera3.close_camera()
