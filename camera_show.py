import os.path
import sys
import cv2
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QGroupBox, QLabel, QComboBox, \
    QTextEdit, QTextBrowser, QLineEdit, QLCDNumber, QMessageBox, QMainWindow, QTableWidgetItem, QSlider, QGridLayout
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QImage, QPixmap
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
import numpy as np
from lib.ImagePreprocessing import ImageAlignment

class showWidget(QWidget):
    fontType_normal = QFont("微软雅黑", 14)
    def __init__(self, name):
        # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        # 装载UI
        self.setUi(name)
        self.setSignal()

    def setUi(self, name):
        # 创建窗口主布局
        MainLayout = QVBoxLayout()

        # 创建组件
        self.name_label = QLabel(name)
        self.name_label.setFont(self.fontType_normal)
        self.photo_label = QLabel()

        # 创建空图像
        blackPixel = np.zeros((240, 320), dtype=np.uint8)
        blackPixel = QImage(blackPixel.data, 320, 240, 320, QImage.Format_Grayscale8)
        self.photo_label.setPixmap(QPixmap.fromImage(blackPixel))

        # 添加组件进布局
        MainLayout.addStretch()
        MainLayout.addWidget(self.name_label)
        MainLayout.addWidget(self.photo_label)
        MainLayout.addStretch()

        # 应用布局
        self.setLayout(MainLayout)

    
    def setSignal(self):
        pass


class showCamera(QWidget):
    def __init__(self):
        # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        # 装载UI
        self.setUi()
        self.setSignal()
        self.ia = ImageAlignment()
        self.ia.load_h_matrix("./cache")

    def setUi(self):
        # 创建窗口主布局
        MainLayout = QGridLayout()
        MainLayout.setSpacing(10)

        # 创建组件
        self.depthWidget = showWidget("深度图预览")
        self.irWidget = showWidget("红外图预览")
        self.statusWidget = showWidget("Status图预览")
        self.rgbWidget = showWidget("彩色图预览")
        self.RGBIWidget = showWidget("红外融合图像")
        self.RGBDWidget = showWidget("深度融合图像")

        # 添加组件进布局
        MainLayout.addWidget(self.depthWidget, 0, 0)
        MainLayout.addWidget(self.irWidget, 0, 1)
        MainLayout.addWidget(self.statusWidget, 1, 0)
        MainLayout.addWidget(self.rgbWidget, 1, 1)
        MainLayout.addWidget(self.RGBIWidget, 2, 0)
        MainLayout.addWidget(self.RGBDWidget, 2, 1)

        # 应用布局
        self.setLayout(MainLayout)
    
    def setSignal(self):
        pass

    def showFrame(self, process_result):
        # depth
        depthPhoto = process_result[0]
        depth_height, depth_width, depth_channel = depthPhoto.shape
        depth_show = QImage(depthPhoto.data, depth_width, depth_height, depth_width*3,
                           QImage.Format_RGB888)
        self.depthWidget.photo_label.setPixmap(QPixmap.fromImage(depth_show))

        # ir
        irPhoto = process_result[1]
        ir_height, ir_width = irPhoto.shape
        ir_show = QImage(irPhoto.data, ir_width, ir_height, ir_width,
                           QImage.Format_Grayscale8)
        self.irWidget.photo_label.setPixmap(QPixmap.fromImage(ir_show))

        # status
        statusPhoto = process_result[2]
        status_height, status_width, status_channel = statusPhoto.shape
        status_show = QImage(statusPhoto.data, status_width, status_height, status_width*3,
                           QImage.Format_RGB888)
        self.statusWidget.photo_label.setPixmap(QPixmap.fromImage(status_show))

        # rgb
        rgbPhoto = process_result[3]
        rgb_height, rgb_width, rgb_channel = rgbPhoto.shape
        rgb_show = QImage(rgbPhoto.data, rgb_width, rgb_height, rgb_width*3,
                           QImage.Format_RGB888)
        rgb_show_resized = rgb_show.scaled(320, 240)
        self.rgbWidget.photo_label.setPixmap(QPixmap.fromImage(rgb_show_resized))

        # RGBI & RGBD
        rgb_r = cv2.resize(cv2.cvtColor(process_result[3], cv2.COLOR_BGR2RGB), (320, 240),
                   interpolation=cv2.INTER_AREA)
        deep_r = process_result[0]
        ir_r = cv2.cvtColor(process_result[1], cv2.COLOR_GRAY2RGB)
        # self.ia.calculate_mapping_matrix(rgb_r, ir_r, "./img", False)
        rgbi = self.ia.img_mapping(ir_r, rgb_r)
        rgbi_qimage = QImage(rgbi.data, rgbi.shape[1], rgbi.shape[0], QImage.Format_RGB888)

        rgbd = self.ia.img_mapping(deep_r, rgb_r)
        rgbd_qimage = QImage(rgbd.data, rgbi.shape[1], rgbi.shape[0], QImage.Format_RGB888)
        self.RGBIWidget.photo_label.setPixmap(QPixmap.fromImage(rgbi_qimage))
        self.RGBDWidget.photo_label.setPixmap(QPixmap.fromImage(rgbd_qimage))
