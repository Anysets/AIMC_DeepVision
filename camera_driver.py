# -*- coding: utf-8 -*-
import sys
import struct
import requests
import cv2
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QGroupBox, QLabel
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# from PIL import Image

class CameraDriver(QThread):
    frame_processed_signal = pyqtSignal(list)
    camera_connected_signal = pyqtSignal(int)
    camera_disconnected_signal = pyqtSignal(int)
    process_result = []
    def __init__(self)  :
        # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        # 装载UI
        self.setUi()
        self.setSignal()
        

    def setUi(self):
        pass
    
    def setSignal(self):
        pass
    
    def run(self):
        while True:
            if self.post_encode_config(self.frame_config_encode(1, 1, 255, 0, 2, 7, 1, 0, 0)):
                p = self.get_frame_from_http()
                if p is not None:
                    depthPhoto, irPhoto, statusPhoto, rgbPhoto = self.process_frame(p)
                    self.process_result = [depthPhoto, irPhoto, statusPhoto, rgbPhoto]
                    # print(type(process_result))
                    self.frame_processed_signal.emit(self.process_result)
                else:
                    print("get_frame_from_http wrong")
    
    def giveProcessResult(self):
        return self.process_result

    HOST = '192.168.233.1'
    PORT = 80

    def frame_config_decode(self, frame_config):
        '''
            @frame_config bytes

            @return fields, tuple (trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)
        '''
        return struct.unpack("<BBBBBBBBi", frame_config)


    def frame_config_encode(self, trigger_mode=1, deep_mode=1, deep_shift=255, ir_mode=1, status_mode=2, status_mask=7, rgb_mode=1, rgb_res=0, expose_time=0):
        return struct.pack("<BBBBBBBBi",
                        trigger_mode, deep_mode, deep_shift, ir_mode, status_mode, status_mask, rgb_mode, rgb_res, expose_time)


    def frame_payload_decode(self, frame_data: bytes, with_config: tuple):
        try:
            deep_data_size, rgb_data_size = struct.unpack("<ii", frame_data[:8])
            frame_payload = frame_data[8:]
            # 0:16bit 1:8bit, resolution: 320*240
            deepth_size = (320*240*2) >> with_config[1]
            deepth_img = struct.unpack("<%us" % deepth_size, frame_payload[:deepth_size])[
                0] if 0 != deepth_size else None
            frame_payload = frame_payload[deepth_size:]

            # 0:16bit 1:8bit, resolution: 320*240
            ir_size = (320*240*2) >> with_config[3]
            ir_img = struct.unpack("<%us" % ir_size, frame_payload[:ir_size])[
                0] if 0 != ir_size else None
            frame_payload = frame_payload[ir_size:]

            status_size = (320*240//8) * (16 if 0 == with_config[4] else
                                        2 if 1 == with_config[4] else 8 if 2 == with_config[4] else 1)
            status_img = struct.unpack("<%us" % status_size, frame_payload[:status_size])[
                0] if 0 != status_size else None
            frame_payload = frame_payload[status_size:]

            assert(deep_data_size == deepth_size+ir_size+status_size)

            rgb_size = len(frame_payload)
            assert(rgb_data_size == rgb_size)
            rgb_img = struct.unpack("<%us" % rgb_size, frame_payload[:rgb_size])[
                0] if 0 != rgb_size else None

            if (not rgb_img is None) and (1 == with_config[6]):
                jpeg = cv2.imdecode(np.frombuffer(
                    rgb_img, 'uint8', rgb_size), cv2.IMREAD_COLOR)
                if not jpeg is None:
                    rgb = cv2.cvtColor(jpeg, cv2.COLOR_BGR2RGB)
                    rgb_img = rgb.tobytes()
                else:
                    rgb_img = None

            return (deepth_img, ir_img, status_img, rgb_img)
        except Exception as e:
            print("An error occurred:", e)
            return (None, None, None, None)


    # def post_encode_config(self, config=None, host=HOST, port=PORT):
    #     if config is None:
    #         config = self.frame_config_encode()
    #     r = requests.post('http://{}:{}/set_cfg'.format(host, port), config)
    #     if(r.status_code == requests.codes.ok):
    #         return True
    #     return False
    def post_encode_config(self, config=None, host=HOST, port=PORT, retry_count=3):
        if config is None:
            config = self.frame_config_encode()
        session = requests.Session()
        retries = Retry(total=retry_count, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        try:
            r = session.post('http://{}:{}/set_cfg'.format(host, port), config, timeout=5)
            if r.status_code == requests.codes.ok:
                self.camera_connected_signal.emit(1)
                return True
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            self.camera_disconnected_signal.emit(0)
        return False


    # def get_frame_from_http(self, host=HOST, port=PORT):
    #     r = requests.get('http://{}:{}/getdeep'.format(host, port))
    #     if(r.status_code == requests.codes.ok):
    #         # print('Get deep image')
    #         deepimg = r.content
    #         # print('Length={}'.format(len(deepimg)))
    #         (frameid, stamp_msec) = struct.unpack('<QQ', deepimg[0:8+8])
    #         # print((frameid, stamp_msec/1000))
    #         return deepimg

    def get_frame_from_http(self, host=HOST, port=PORT, retry_count=3):
        session = requests.Session()
        retries = Retry(total=retry_count, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        try:
            r = session.get('http://{}:{}/getdeep'.format(host, port), timeout=5)
            if r.status_code == requests.codes.ok:
                deepimg = r.content
                (frameid, stamp_msec) = struct.unpack('<QQ', deepimg[0:8+8])
                return deepimg
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            self.camera_disconnected_signal.emit(0)
        return None


    def apply_custom_colormap(self, depth_image):
        # 将深度值映射到0-255范围内
        depth_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        # 创建自定义的彩色映射
        colormap = cv2.applyColorMap(255 - depth_normalized, cv2.COLORMAP_JET)
        
        return colormap

    def process_frame(self, frame_data: bytes):
        config = self.frame_config_decode(frame_data[16:16+12])
        frame_bytes = self.frame_payload_decode(frame_data[16+12:], config)

        depthPhoto = np.frombuffer(frame_bytes[0], 'uint16' if 0 == config[1] else 'uint8').reshape(
            240, 320) if frame_bytes[0] else None

        irPhoto = np.frombuffer(frame_bytes[1], 'uint16' if 0 == config[3] else 'uint8').reshape(
            240, 320) if frame_bytes[1] else None

        statusPhoto = np.frombuffer(frame_bytes[2], 'uint16' if 0 == config[4] else 'uint8').reshape(
            240, 320) if frame_bytes[2] else None

        rgbPhoto = np.frombuffer(frame_bytes[3], 'uint8').reshape(
            (480, 640, 3)) if frame_bytes[3] else None
        
        if depthPhoto is not None:
            # 将深度图像应用自定义的彩色映射
            # depthPhoto = self.apply_custom_colormap(depthPhoto)
            depthPhoto = cv2.applyColorMap(depthPhoto, cv2.COLORMAP_JET)
            # cv2.imshow("Depth", depth_colormap)

        if irPhoto is not None:
            if irPhoto.dtype == 'uint16':
                irPhoto = cv2.convertScaleAbs(irPhoto, alpha=(255.0/2500.0))
            # cv2.imshow("IR", ir)
            pass

        if statusPhoto is not None:
            pass
            color_map = np.array([
                    [68, 1, 84],    # #440154
                    [48, 103, 141], # #30678d
                    [53, 183, 120], # #35b778
                    [81, 181, 105]  # #51b569
                ], dtype=np.uint8)
            statusPhoto = color_map[statusPhoto]
            # statusPhoto = QImage(colored_image.data, colored_image.shape[1], colored_image.shape[0], colored_image.shape[1] * 3, QImage.Format_RGB888)
            # print(statusPhoto)
            # status_colormap = cv2.applyColorMap(status, cv2.COLORMAP_JET)
            # cv2.imshow("Status", status)

        if rgbPhoto is not None:
            pass
            # rgbPhoto = cv2.cvtColor(rgbPhoto, cv2.COLOR_RGB2BGR)
            # height, width, channel = rgb.shape
            # bytesPerLine = width * 3
            # bgr_show = QImage(rgb.data, width, height, bytesPerLine,
            #                QImage.Format_RGB888).rgbSwapped()
            # self.testlabel.setPixmap(QPixmap.fromImage(bgr_show))

        return depthPhoto, irPhoto, statusPhoto, rgbPhoto
    
    def check_connection(self, url):
        try:
            response = requests.head(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        return False
    
    '''url = 'http://{}:{}/set_cfg'.format(HOST, PORT)
        if self.check_connection(url):
            print("Connection to {} is active.".format(url))
        else:
            print("Failed to establish connection to {}.".format(url))'''

    
class CameraStatus(QWidget):
    fontType_normal = QFont("微软雅黑", 16)
    def __init__(self, changeStartButton):
    # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        # 装载UI
        self.changeStartButton = changeStartButton
        self.setUi()
        self.setSignal()
        
    def setUi(self):
        MainLayout = QHBoxLayout()

        camera_status_label = QLabel("摄像头状态：")
        camera_status_label.setFont(self.fontType_normal)
        MainLayout.addWidget(camera_status_label)
        self.camera_status_label = QLabel("未连接")
        self.camera_status_label.setFont(self.fontType_normal)
        self.camera_status_label.setStyleSheet("QLabel { color : red; }")
        self.changeStartButton(False)
        MainLayout.addWidget(self.camera_status_label)

        self.setLayout(MainLayout)

    def setSignal(self):
        pass

    def changeStatus(self, status):
        if status:
            self.camera_status_label.setText("已连接")
            self.camera_status_label.setStyleSheet("QLabel { color : green; }")
            self.changeStartButton(True)
        else:
            self.camera_status_label.setText("未连接")
            self.camera_status_label.setStyleSheet("QLabel { color : red; }")
            self.changeStartButton(False)