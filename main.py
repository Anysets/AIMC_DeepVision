# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QGroupBox, QLabel, QComboBox, \
    QTextEdit, QTextBrowser, QLineEdit, QLCDNumber, QMessageBox, QMainWindow, QTableWidgetItem, QSlider, QGridLayout
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from option import option_photo
from camera_show import showCamera
from camera_driver import CameraDriver, CameraStatus
from camera_save import savePhotos
from AIMC_json import AIMC_JSON
from lib.ImagePreprocessing import ImageAlignment

class MainWindow(QWidget):
    def __init__(self):
        # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        self.setWindowIcon(QIcon('icons/logo.png'))
        # 设置标题
        self.setWindowTitle('AIMC深度视觉采集')
        # 加载摄像头驱动
        self.CameraDriver = CameraDriver()
        # 装载UI
        self.setUi()
        # 使摄像头开始工作
        self.CameraDriver.start()
        # 加载摄像头保存模块
        self.camera_save = savePhotos(self.CameraDriver.giveProcessResult)
        self.camera_save.start()
        # 加载JSON模块
        self.AIMC_json = AIMC_JSON(self.option_photo.refreshAmount, self.camera_save.refreshAmount, self.option_photo.refreshPath)
        # 设置信号
        self.setSignal()
        # # 从配置文件加载amount
        # self.AIMC_json.amount_loaded_signal.connect(self.option_photo.refreshAmount)
        # self.AIMC_json.amount_loaded_signal.connect(self.camera_save.refreshAmount)
        # self.AIMC_json.amount_loaded_signal.connect(self.test)
        # # 从配置文件加载path
        # self.AIMC_json.path_loaded_signal.connect(self.option_photo.refreshPath)
        

        
    def setUi(self): 
        # 根据排版，整体的布局是一个横向布局
        MainLayout = QHBoxLayout()
        
        # 相机预览
        self.showCamera = showCamera()

        # 图片选项
        optionLayout = QGridLayout()
        # 创建组件
        self.option_photo = option_photo()  # 摄像头选项
        self.cameraStatus = CameraStatus(self.option_photo.changeStartButton)  # 摄像头状态
        # 添加组件进布局
        optionLayout.setRowStretch(0, 0) 
        optionLayout.addWidget(self.cameraStatus, 1, 0)
        optionLayout.addWidget(self.option_photo, 2, 0, 10, 0)


        # 添加局部布局进MainLayout
        # MainLayout.setGeometry()
        MainLayout.addWidget(self.showCamera)
        MainLayout.addLayout(optionLayout)
        # 将MainLayout设置为该组件布局
        self.setLayout(MainLayout)
        

    def setSignal(self):
        self.CameraDriver.frame_processed_signal.connect(self.showCamera.showFrame)
        # 点击照相按钮后给camera_save发送信息
        self.option_photo.startShot_signal.connect(self.camera_save.savePhoto)  # 开始拍照
        self.option_photo.stopShot_signal.connect(self.camera_save.stopSavePhoto)  # 停止拍照
        # amount变动后触发刷新数量值
        self.camera_save.amount_changed_signal.connect(self.option_photo.refreshAmount)
        # 连接成功触发界面显示
        self.CameraDriver.camera_connected_signal.connect(self.cameraStatus.changeStatus)
        # 连接失败触发界面显示
        self.CameraDriver.camera_disconnected_signal.connect(self.cameraStatus.changeStatus)
        # 拍照完成后刷新按钮
        self.camera_save.saveFinished_signal.connect(self.option_photo.saveInfo)
        
        # 更新JSON文件中的amount
        self.camera_save.amount_changed_signal.connect(self.AIMC_json.changeAmount)
        # 更新JSON文件中的path
        self.option_photo.pathChanged_signal.connect(self.AIMC_json.changePath)

    # 重写关闭事件
    def closeEvent(self, event):
        # 在这里写入配置文件
        self.AIMC_json.saveToJSON()  # 在关闭前写入配置文件
        event.accept()

    def test(self, amount):
        print("Amount loaded in MainWindow:", amount)


if __name__ == '__main__':
    # 1、创建一个程序 有且只能有一个
    app = QApplication(sys.argv)

    # 3、创建一个窗口
    w = MainWindow()

    # 4、显示出来
    w.show()

    # 2、进入消息循环
    app.exec_()
