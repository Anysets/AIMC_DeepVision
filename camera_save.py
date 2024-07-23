# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QGroupBox, QLabel, QComboBox, \
    QTextEdit, QTextBrowser, QLineEdit, QLCDNumber, QMessageBox, QMainWindow, QTableWidgetItem, QSlider
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QImage
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal, QThread
import time

# from mediator import Mediator

# os.path.exists('/run/media/anysets/Files/Files/AIMC-Video')
# os.makedirs()
class savePhotos(QThread):
    # 记录总拍摄张数
    photo_amount = 0
    amount_changed_signal = pyqtSignal(int)
    saveFinished_signal = pyqtSignal()
    def __init__(self, getProcessResult):
        # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        # self.mediator = Mediator()
        # 装载UI
        self.setUi()
        self.setSignal()
        self.getProcessResult = getProcessResult
    
    def setUi(self):
        pass

    def setSignal(self):
        pass
    
    timer = QTimer()
    timerCount = 0
    def savePhoto(self, saveInfo_list):
        # ['/home/anysets/Desktop', False, '', False, 'Unix时间戳', 1, '1', '1']
        if self.timer.isActive():
            print("STOP!!!")
            self.timer.stop()
        if (saveInfo_list[5] == 1):
            # # 这里的原方案是点击开始拍照，再次点击停止拍照
            # self.timerCount = -1
            # self.timer.timeout.connect(lambda: self.saveSinglePhoto(saveInfo_list))
            # self.timer.setInterval(1)
            # self.timer.start()
            # 这里是新方案，点击一次只执行一次拍照
            self.timerCount = 1
            self.timer.timeout.connect(lambda: self.saveSinglePhoto(saveInfo_list))
            print(int(saveInfo_list[6]))
            self.timer.setInterval(1)
            self.timer.start()
        elif (saveInfo_list[5] == 2):
            self.timerCount = int(saveInfo_list[7])
            self.timer.timeout.connect(lambda: self.saveSinglePhoto(saveInfo_list))
            print(int(saveInfo_list[6]))
            self.timer.setInterval(int(saveInfo_list[6]))
            self.timer.start()
            # for i in range(count):
            #     self.saveSinglePhoto(saveInfo_list)
            #     # print(i)
            #     self.amount_changed_signal.emit(self.photo_amount)
            #     # time.sleep()
        elif (saveInfo_list[5] == 3):
            self.stopSavePhoto()
#---------------------------------------------------------------------------------------------------------------------------------------------
    def stopSavePhoto(self):
        if self.timer.isActive():
            self.timer.stop()
        # if self.timer.timeout.hasConnections():
            self.timer.timeout.disconnect()
#---------------------------------------------------------------------------------------------------------------------------------------------
    
    def saveSinglePhoto(self, saveInfo_list):
        if (self.timerCount == 0):
            # self.timer.stop()
            # self.timer.timeout.disconnect()
            self.saveFinished_signal.emit()
            return
        
        process_result = self.getProcessResult()  # 获取图像
        if len(process_result) == 0:
            return
            
        # <图像处理>-----------------------------------------------------------------------
        depthPhoto = process_result[0]
        depth_height, depth_width, depth_channel = depthPhoto.shape
        depth_save = QImage(depthPhoto.data, depth_width, depth_height, depth_width*3,
                        QImage.Format_RGB888)
        
        irPhoto = process_result[1]
        ir_height, ir_width = irPhoto.shape
        ir_save = QImage(irPhoto.data, ir_width, ir_height, ir_width,
                        QImage.Format_Grayscale8)
        
        statusPhoto = process_result[2]
        status_height, status_width, status_channel = statusPhoto.shape
        status_save = QImage(statusPhoto.data, status_width, status_height, status_width*3,
                        QImage.Format_RGB888)

        rgbPhoto = process_result[3]
        rgb_height, rgb_width, rgb_channel = rgbPhoto.shape
        rgb_save = QImage(rgbPhoto.data, rgb_width, rgb_height, rgb_width*3,
                        QImage.Format_RGB888)
        # </图像处理>----------------------------------------------------------------------
        
        # <路径处理>-----------------------------------------------------------------------
        deep_path = saveInfo_list[0] + '/Deep'
        ir_path = saveInfo_list[0] + '/IR'
        status_path = saveInfo_list[0] + '/Status'
        rgb_path = saveInfo_list[0] + '/RGB'
        
        # </路径处理>----------------------------------------------------------------------

        
        # <文件名处理>---------------------------------------------------------------------
        # deep_name = '/Deep.bmp'
        # ir_name = '/IR.bmp'
        # status_name = '/Status.bmp'
        # rgb_name = '/Deep.bmp'
        deep_name = '/'
        ir_name = '/'
        status_name = '/'
        rgb_name = '/'
        if (saveInfo_list[1]):
            deep_name = deep_name + saveInfo_list[2]
            ir_name = ir_name + saveInfo_list[2]
            status_name = status_name + saveInfo_list[2]
            rgb_name = rgb_name + saveInfo_list[2]
        if (saveInfo_list[3]):
            if (saveInfo_list[4] == 'Unix时间戳'):
                time_now = time.time()*1000
                deep_name = deep_name + f"{int(time_now)}"
                ir_name = ir_name + f"{int(time_now)}"
                status_name = status_name + f"{int(time_now)}"
                rgb_name = rgb_name + f"{int(time_now)}"
            elif (saveInfo_list[4] == '分段序号'):
                deep_name = deep_name + f"{int(self.photo_amount)}"
                ir_name = ir_name + f"{int(self.photo_amount)}"
                status_name = status_name + f"{int(self.photo_amount)}"
                rgb_name = rgb_name + f"{int(self.photo_amount)}"
        if (deep_name == '/'):
            deep_name = deep_name + 'Deep'
            ir_name = ir_name + 'IR'
            status_name = status_name + 'Status'
            rgb_name = rgb_name + 'RGB'
        deep_name = deep_name + '.bmp'
        ir_name = ir_name + '.bmp'
        status_name = status_name + '.bmp'
        rgb_name = rgb_name + '.bmp'
        
        # </文件名处理>--------------------------------------------------------------------

        # <文件保存>-----------------------------------------------------------------------
        self.savePhotoToDisk(depth_save, deep_path, deep_name)
        self.savePhotoToDisk(ir_save, ir_path, ir_name)
        self.savePhotoToDisk(status_save, status_path, status_name)
        self.savePhotoToDisk(rgb_save, rgb_path, rgb_name)
        # </文件保存>----------------------------------------------------------------------

        if (self.timerCount > 0):
            self.photo_amount += 1
            self.amount_changed_signal.emit(self.photo_amount)
            self.timerCount -= 1
        else:
            self.photo_amount += 1
            self.amount_changed_signal.emit(self.photo_amount)
        
        

    def savePhotoToDisk(self, photo, path, name):
        if os.path.exists(path) == False:
            os.makedirs(path)
        photo.save(path+name)

    def givePhotoAmount(self):
        return self.photo_amount
    
    def refreshAmount(self, amount):
        self.photo_amount = amount
        print(f"refresh amount:{self.photo_amount}")
