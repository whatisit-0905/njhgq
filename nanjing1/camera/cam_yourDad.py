import cv2
import json
import os
import sys
import numpy as np
from os import getcwd
import cv2
import msvcrt
from ctypes import *
import yaml
# # 获取当前脚本的绝对路径
# current_file_path = os.path.abspath(__file__)
# # 获取当前脚本所在的目录
# current_dir = os.path.dirname(current_file_path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # 将当前目录加入到 sys.path 中
# if current_dir not in sys.path:
#     sys.path.append(current_dir)

# sys.path.append(r"hk_utilt\Python\MvImport")
from MvImport.MvCameraControl_class import * # type: ignore
from camera.grabimage1 import enum_devices,identify_different_devices,input_num_camera
from camera.grabimage1 import creat_camera,open_device,one_shot_image
from camera.grabimage1 import decide_divice_on_line,create_byIP


class Camera:
    def __init__(self,serial:str, ip:str,local_ip:str):
        """
        初始化 Camera 类，默认使用第一个摄像头设备。

        :param 
        serial: 摄像头的序列号
        ip:     摄像头的ip
        local_ip:电脑网卡ip
        """
        MvCamera.MV_CC_Initialize()
            # ch:初始化SDK | en: initialize SDK
        self.stDevInfo = MV_CC_DEVICE_INFO()
        self.stGigEDev = MV_GIGE_DEVICE_INFO()

        self.serial=serial
        self.cam_ip=ip
        self.stDeviceList= None #设备登陆句柄
        self.cam=None
        
        self.localnet=local_ip#本地网卡ip
        self.cap = None
        self.parameters = {}
        self.deviceIpList = self.cam_ip.split('.')
        self.stGigEDev.nCurrentIp = (int(self.deviceIpList[0]) << 24) | (int(self.deviceIpList[1]) << 16) | (int(self.deviceIpList[2]) << 8) | int(self.deviceIpList[3])

        self.netIpList = self.localnet.split('.')
        self.stGigEDev.nNetExport =  (int(self.netIpList[0]) << 24) | (int(self.netIpList[1]) << 16) | (int(self.netIpList[2]) << 8) | int(self.netIpList[3])

        self.stDevInfo.nTLayerType = MV_GIGE_DEVICE
        self.stDevInfo.SpecialInfo.stGigEInfo = self.stGigEDev
        

    def camrea_create_byID(self,devicelist):
            self.devicelist=devicelist
            
            self.cam, self.stDeviceList = creat_camera(self.devicelist, self.id, log=False)
    def camera_create_byIP(self):
        
        self.cam=create_byIP(self.stDevInfo)
        if self.cam == None:
            # print ("open device fail! ret[0x%x]" % ret)
            print(f"open camera {self.cam_ip} failed!")
        
        
    def destory_handle(self):
        ret = self.cam.MV_CC_CloseDevice()
        if ret != 0:
            print ("close deivce fail! ret[0x%x]" % ret)
            



    def search_for_best_packetsize(self):
        # ch:探测网络最佳包大小(只对GigE相机有效) | en:Detection network optimal package size(It only works for the GigE camera)
        if self.stDevInfo.nTLayerType == MV_GIGE_DEVICE:
            nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
            if int(nPacketSize) > 0:
                ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
                if ret != 0:
                    print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
            else:
                print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)
        
          
    def open_camera(self):
        """
        打开摄像头设备。
       
        :return: 成功返回 True，失败返回 False。
        """
        ret = self.cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
        if  ret:
            print(f"Failed to open camera id is {self.cam_ip}.")
            return False
        print(f"Camera id {self.cam_ip} opened successfully.")
        return True

    def cam_start_grabbing(self):
        ret = self.cam.MV_CC_StartGrabbing()
        if ret != 0:
            print("开始取流失败! ret[0x%x]" % ret)
            return False
        return True
           
    def set_camera_parameters(self):
        """设置相机参数"""
        try:
            # 设置数据包大小
            if self.stDevInfo.nTLayerType in [MV_GIGE_DEVICE, MV_GENTL_GIGE_DEVICE]:
                nPacketSize = self.cam.MV_CC_GetOptimalPacketSize()
                print(f"nPacketSize: {nPacketSize}")
                if int(nPacketSize) > 0:
                    ret = self.cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize)
                    if ret != 0:
                        print(f"设置数据包大小失败! ret[0x{ret:x}]")
                    else:
                        print(f"设置数据包大小成功! ret[0x{ret:x}]")

            # 设置采集帧率使能
            stBool = c_bool(False)
            ret = self.cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)
            if ret != 0:
                print(f"获取采集帧率使能状态失败! ret[0x{ret:x}]")
            else:
                print(f"获取采集帧率使能状态成功! ret[0x{ret:x}]")

            # 设置触发模式为off
            ret = self.cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
            if ret != 0:
                print(f"设置触发模式失败! ret[0x{ret:x}]")
            else:
                print(f"设置触发模式成功! ret[0x{ret:x}]")

            return True
        except Exception as e:
            print(f"设置相机参数失败: {str(e)}")
            return False   
    def export_camera_parameters(self, file_path="FeatureFile.mfs"):
        """
        导出当前摄像头的参数到 mfs 文件中。
        
        :param file_path: 保存摄像头参数的文件路径，默认为 "camera_params.json"。
        :return: 成功返回 True，失败返回 False。
        """
        print ("start export the camera properties to the file",file_path)
        print ("wait......")

        #ch:将相机属性导出到文件中 | en:Export the camera properties to the file
        ret = self.cam.MV_CC_FeatureSave(file_path)
        if MV_OK != ret:#MV_OK可能是动态链接库里定义的变量
            print ("save feature fail! ret [0x%x]" % ret)
            return False
        print ("finish export the camera properties to the file")
        return True

    def import_camera_parameters(self, file_path="camera_params.mfs"):
        """
        从 mfs 文件中导入摄像头参数并应用到摄像头设备。
        
        :param file_path: 摄像头参数文件路径，默认为 "camera_params.json"。
        :return: 成功返回 True，失败返回 False。
        """
        ret = self.cam.MV_CC_FeatureLoad(file_path)
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

        ret=self.cam_start_grabbing()
        if ret:
            one_shot_image(self.cam,active_way="getImagebuffer",output_path= file_name)
            self.stop_Grabing()
            return True
        else:
            return False



        
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
        if(self.cam ==None):
            print(f"camera {self.cam_ip} is not firts initialize")
            return False

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


class Camera_father:
    def __init__(self, cam_dict):
        """
        初始化摄像头父类
        
        :param cam_dict: 字典，键为摄像头序列号，值为摄像头IP地址。
        """
        with open("config.yaml", 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        which_one=config['which_one']
        if(which_one):
            self.local_net_ip=config['local_net_ip']['outer']
        else:
            self.local_net_ip=config['local_net_ip']['inner'] 

        
        self.cam_dict = cam_dict  # 存储摄像头序列号和 IP 的字典
        self.cameras = []         # 用于保存初始化的摄像头实例

    def initialize_cameras(self):
        """
        初始化所有摄像头，将每个摄像头序列号对应的摄像头对象存入字典中。
        """
        for serial, ip in self.cam_dict.items():
            camera = Camera(serial, ip,self.local_net_ip)
            self.cameras.append(camera)


    def get_camera_by_serial(self, serial):
        """
        根据摄像头序列号获取摄像头实例。
        
        :param serial: 摄像头的序列号。
        :return: Camera 对象。
        """
        return self.cameras.get(serial, None)
    def export_config(self):
        if(self.cameras!=[]):
            for each_cam in self.cameras:
                each_cam.export_camera_parameters(str(each_cam.serial)+'.mfs')


def load_config(file_path='config.yaml'):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

# 示例用法
if __name__ == "__main__":
    # MvCamera.MV_CC_Initialize()
    # devicelist=enum_devices(device=0,device_way=False)
    # identify_different_devices(devicelist)
    # stDevInfo=MV_CC_DEVICE_INFO ()
    # gigeinfo=MV_GIGE_DEVICE_INFO()

    import time
        # 使用配置
    config = load_config()
    # print(config)
    which_one=config['which_one']
    if which_one==0:
        cam_dict = {cam_info['serial']: cam_info['ip'] for cam_name, cam_info in config['cameras']['inner'].items()}
        mycam=Camera_father(cam_dict=cam_dict)
        # tcp_server = TCPServer(host=config['tcpIp']['ip'], port=int(config['tcpIp']['port']))
    else:
        cam_dict = {cam_info['serial']: cam_info['ip'] for cam_name, cam_info in config['cameras']['outer'].items()}
        mycam=Camera_father(cam_dict=cam_dict)

        # mycam=Camera_father(cam_dict=cam_dict)
    # print(cam_dict)
    mycam.initialize_cameras()
    print(mycam.cameras)
    for _cam in mycam.cameras:
        _cam.camera_create_byIP()
        _cam.open_camera()
        _cam.export_camera_parameters("./MFS/"+str(_cam.serial)+'.mfs')
        # _cam.import_camera_parameters("./MFS/"+str(_cam.serial)+'.mfs')
        _cam.capture_image()

    # while(True):
    #     for _cam in mycam.cameras: 
    #         if(_cam.is_cam_online()):
    #             # print("here")
    #             _cam.capture_image()
    #         else:
    #             # _cam = Camera(_cam.serial, _cam.cam_ip,mycam.local_net_ip)
                
    #             _cam.camera_create_byIP()
    #             _cam.open_camera() 
    #             print(f"reopen ip {_cam.cam_ip}")
    #             time.sleep(1)
    #     time.sleep(1)
 