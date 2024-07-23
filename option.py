# -*- coding: utf-8 -*-
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QGroupBox, QLabel, QComboBox, \
    QTextEdit, QTextBrowser, QLineEdit, QLCDNumber, QMessageBox, QMainWindow, QTableWidgetItem, QSlider, QCheckBox, QGridLayout, QFileDialog, QButtonGroup
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from pathlib import Path


class option_photo(QWidget):
    startShot_signal = pyqtSignal(list)
    pathChanged_signal = pyqtSignal(str)
    stopShot_signal = pyqtSignal()
    fontType_normal = QFont("微软雅黑", 16)
    fontType_amount = QFont("微软雅黑", 20)
    fontType_small = QFont("微软雅黑", 12)
    def __init__(self):
        # 一定要首先调用init方法，进行初始化操作
        super().__init__()
        # 装载UI
        self.setUi()
        self.setSignal()
        
    def setUi(self):
        # 根据排版，整体的布局
        MainLayout = QGridLayout()
        MainLayout.setSpacing(25)
        MainLayout.setRowStretch(0, 0) 
        # 保存路径--------------------
        # 创建组件
        self.path_lable = QLabel("保存路径")  # 保存路径的文本
        self.path_lable.setFont(self.fontType_normal)
        SaveLayout = QHBoxLayout()
        self.path_text = QLineEdit()  # 选择路径的文本框
        self.path_text.setFont(self.fontType_small)
        SaveLayout.addWidget(self.path_text)
        self.pathView_button = QPushButton("浏览")  # 调用文件管理器的按钮
        self.pathView_button.setFont(self.fontType_small)
        SaveLayout.addWidget(self.pathView_button)
        # 添加组件进布局
        MainLayout.addWidget(self.path_lable, 1, 0, 1, 1)
        MainLayout.addWidget(self.path_text, 1, 1, 1, 2)
        MainLayout.addWidget(self.pathView_button, 1, 3, 1, 1)

        # 文件前缀--------------------
        FileFrontLayout = QHBoxLayout()
        # 创建组件
        self.fileFront_lable = QLabel("文件前缀")  # 提示文本
        self.fileFront_lable.setFont(self.fontType_normal)
        self.fileFront_text = QLineEdit()  # 前缀输入框
        self.fileFront_text.setFont(self.fontType_small)
        self.fileFront_text.setEnabled(False)
        FileFrontLayout.addWidget(self.fileFront_text)

        self.fileFront_checkbox = QCheckBox()  # 勾选框
        self.fileFront_checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        FileFrontLayout.addWidget(self.fileFront_checkbox)
        # 添加组件进布局
        MainLayout.addWidget(self.fileFront_lable, 2, 0, 1, 1)
        MainLayout.addWidget(self.fileFront_text, 2, 1, 1, 2)
        MainLayout.addWidget(self.fileFront_checkbox, 2, 3, 1, 1)

        # 文件后缀--------------------
        FileBackLayout = QHBoxLayout()
        # 创建组件
        self.fileBack_lable = QLabel("文件后缀")  # 提示文本
        self.fileBack_lable.setFont(self.fontType_normal)
        self.fileBack_combobox = QComboBox()  # 下拉选择框
        self.fileBack_combobox.setFont(self.fontType_small)
        FileBackLayout.addWidget(self.fileBack_combobox)
        self.fileBack_combobox.addItems(["Unix时间戳", "分段序号"])
        self.fileBack_combobox.setEnabled(True)
        # self.fileBack_checkbox = QCheckBox()  # 勾选框
        # FileBackLayout.addWidget(self.fileBack_checkbox)
        # 添加组件进布局
        MainLayout.addWidget(self.fileBack_lable, 3, 0, 1, 1)
        MainLayout.addWidget(self.fileBack_combobox, 3, 1, 1, 2)
        # MainLayout.addWidget(self.fileBack_checkbox, 3, 2)
        
        # # 分割线--------------------
        # divide_label = QLabel("----------------")
        # divide_label.setAlignment(Qt.AlignVCenter)
        # divide_label.setEnabled(False)
        # MainLayout.addWidget(divide_label, 4, 0, 4, 1)

        # 拍照模式--------------------
        PhotoModeLayout = QHBoxLayout()
        # 创建组件
        self.photoMode_lable = QLabel("拍照模式")  # 提示文本
        self.photoMode_lable.setFont(self.fontType_small)
        self.mode_button_group = QButtonGroup()
        self.manualMode_checkbox = QCheckBox("手动")  # 三个勾选框
        self.manualMode_checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        self.manualMode_checkbox.setFont(self.fontType_normal)
        self.manualMode_checkbox.setChecked(True)
        # self.manualMode_checkbox.setExclusive(True)  # 设置三选一
        PhotoModeLayout.addWidget(self.manualMode_checkbox)
        self.continuousMode_checkbox = QCheckBox("连续")
        self.continuousMode_checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        self.continuousMode_checkbox.setFont(self.fontType_normal)
        # self.continuousMode_checkbox.setExclusive(True)  # 设置三选一
        PhotoModeLayout.addWidget(self.continuousMode_checkbox)
        self.triggerMode_checkbox = QCheckBox("触发")
        self.triggerMode_checkbox.setEnabled(False)
        self.triggerMode_checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        self.triggerMode_checkbox.setFont(self.fontType_normal)
        # self.triggerMode_checkbox.setExclusive(True)  # 设置三选一
        PhotoModeLayout.addWidget(self.triggerMode_checkbox)
        # 添加单选框到单选框组
        self.mode_button_group.addButton(self.manualMode_checkbox)
        self.mode_button_group.addButton(self.continuousMode_checkbox)
        self.mode_button_group.addButton(self.triggerMode_checkbox)
        # 添加组件进布局
        MainLayout.addWidget(self.photoMode_lable, 5, 0, 1, 1)
        MainLayout.addLayout(PhotoModeLayout, 5, 1, 1, 2)

        # 数量--------------------
        QuantityLayout = QHBoxLayout()
        # 创建组件
        self.quantity_lable = QLabel("数量")
        self.quantity_lable.setFont(self.fontType_small)
        self.quantity_num = 0
        self.quantity_num_lable = QLabel(f"{self.quantity_num:05d}")
        self.quantity_num_lable.setFont(self.fontType_amount)
        QuantityLayout.addWidget(self.quantity_num_lable)
        # 添加组件进布局
        MainLayout.addWidget(self.quantity_lable, 6, 0)
        MainLayout.addWidget(self.quantity_num_lable, 6, 1)

        # 连拍间隔--------------------
        shootingIntervalLayout = QHBoxLayout()
        # 创建组件
        self.shootingInterval_lable = QLabel("连拍间隔")  # 提示文本
        self.shootingInterval_lable.setFont(self.fontType_small)
        self.shootingInterval_text = QLineEdit()  # 前缀输入框
        self.shootingInterval_text.setAlignment(Qt.AlignCenter)
        self.shootingInterval_text.setFixedWidth(80)
        self.shootingInterval_text.setValidator(QtGui.QIntValidator())
        self.shootingInterval_text.setFont(self.fontType_small)
        self.shootingInterval_text.setText("1")
        shootingIntervalLayout.addWidget(self.shootingInterval_text)
        # 添加组件进布局
        MainLayout.addWidget(self.shootingInterval_lable, 7, 0)
        MainLayout.addWidget(self.shootingInterval_text, 7, 1)

        # 数量上限--------------------
        amountLimitLayout = QHBoxLayout()
        # 创建组件
        self.amountLimit_lable = QLabel("数量上限")  # 提示文本
        self.amountLimit_lable.setFont(self.fontType_small)
        self.amountLimit_text = QLineEdit()  # 前缀输入框
        self.amountLimit_text.setAlignment(Qt.AlignCenter)
        self.amountLimit_text.setFixedWidth(80)
        self.amountLimit_text.setValidator(QtGui.QIntValidator())
        self.amountLimit_text.setFont(self.fontType_small)
        self.amountLimit_text.setText("1")
        amountLimitLayout.addWidget(self.amountLimit_text)
        # 添加组件进布局
        MainLayout.addWidget(self.amountLimit_lable, 8, 0)
        MainLayout.addWidget(self.amountLimit_text, 8, 1)

        # 开始拍照--------------------
        self.startShoot_button = QPushButton()
        # self.startShoot_button.setStyleSheet('''
        #     QPushButton {
        #         border: none; /* 移除边框 */
        #         background-image: url(/run/media/anysets/Files/Files/AIMC-Video/icons/start.png); /* 设置默认状态下的背景图片 */
        #     }
        #     QPushButton:pressed {
        #         border: none; /* 移除边框 */
        #         background-image: url(./icon/start_pressed.png); /* 设置按下状态下的背景图片 */
        #     }
        # ''')
        
        self.startShoot_button.setFixedSize(100, 100)  # 设置按钮的固定大小
        self.startShoot_button.setIconSize(self.startShoot_button.size())  # 设置图标大小与按钮大小相同
        # self.startShoot_button.setIcon(QIcon("/run/media/anysets/Files/Files/AIMC-Video/icons/start.png"))  # 设置按钮的图标为图片
        self.startShoot_button.setStyleSheet('''
            QPushButton {
                border: none; /* 移除边框 */
                image: url("icons/start.svg"); /* 设置默认状态下的背景图片 */
                background-repeat: no-repeat;
                background-position: center
            }
            QPushButton:pressed {
                border: none; /* 移除边框 */
                image: url("icons/start_pressed.svg"); /* 设置按下状态下的背景图片 */
            }
        ''')

        # self.startShoot_button.setStyleSheet('''
        #     QPushButton {
        #         border: none; /* 移除边框 */
        #     }
        #     QPushButton:pressed {
        #         background-color: rgba(0, 0, 0, 0.3); /* 设置按下时的半透明背景色 */
        #     }
        # ''')
        MainLayout.addWidget(self.startShoot_button, 7, 3, 2, 2)

        # 将MainLayout设置为该组件布局
        self.setLayout(MainLayout)
        

    def setSignal(self):
        # 选择保存文件夹
        self.pathView_button.clicked.connect(self.getStorageLocation)
        # 设置勾选框和组件的关系
        # self.fileBack_checkbox.stateChanged.connect(self.setBackComboboxWidget)
        self.fileFront_checkbox.stateChanged.connect(self.setFrontTextWidget)
        # 点击开始拍照，将拍照信息发送出去
        self.startShoot_button.clicked.connect(self.saveInfo)


    def getStorageLocation(self):
        dirName = QFileDialog.getExistingDirectory(self, "选择保存文件夹", "", QFileDialog.ShowDirsOnly)
        if dirName is not None:
            self.pathChanged_signal.emit(dirName)
            self.path_text.setText(dirName)

    def setFrontTextWidget(self):
        if self.fileFront_checkbox.isChecked():
            self.fileFront_text.setEnabled(True)
        else:
            self.fileFront_text.setEnabled(False)

    # def setBackComboboxWidget(self):
    #     if self.fileBack_checkbox.isChecked():
    #         self.fileBack_combobox.setEnabled(True)
    #     else:
    #         self.fileBack_combobox.setEnabled(False)

    # saveInfoFLAG 用于指示拍照按钮的状态
    # 0 代表空闲状态，可以进行拍照
    # 1 代表忙碌状态，再次点击会停止拍照
    saveInfoFLAG = 0
    def saveInfo(self):
        # [savePath, FrontIsChecked, Front, BackIsChecked, Back, checkboxStatus, shootingInterval, amountLimit]
        # 如果处于空闲状态，则开始拍照
        if (self.saveInfoFLAG == 0):
            savePath = self.path_text.text()
            if savePath == '':
                QMessageBox.information(self, "注意", "请选择保存路径", QMessageBox.Yes,QMessageBox.Yes)
                return
            FrontIsChecked = self.fileFront_checkbox.isChecked()
            Front = self.fileFront_text.text()
            # BackIsChecked = self.fileBack_checkbox.isChecked()
            Back = self.fileBack_combobox.currentText()
            if (self.manualMode_checkbox.isChecked()):
                checkboxStatus = 1
            elif (self.continuousMode_checkbox.isChecked()):
                checkboxStatus = 2
            elif (self.triggerMode_checkbox.isChecked()):
                checkboxStatus = 3
            else:
                checkboxStatus = 0
            shootingInterval = self.shootingInterval_text.text()
            amountLimit = self.amountLimit_text.text()
            saveInfo_list = [savePath, FrontIsChecked, Front, 1, Back, checkboxStatus, shootingInterval, amountLimit]
            print(saveInfo_list)
            self.saveInfoFLAG = 1  # 将按钮设置为忙碌状态
            self.startShoot_button.setStyleSheet('''
            QPushButton {
                border: none; /* 移除边框 */
                image: url("icons/stop.svg"); /* 设置默认状态下的背景图片 */
                background-repeat: no-repeat;
                background-position: center
            }
            QPushButton:pressed {
                border: none; /* 移除边框 */
                image: url("icons/stop_pressed.svg"); /* 设置按下状态下的背景图片 */
            }
        ''')
            self.startShot_signal.emit(saveInfo_list)

        #如果处于忙碌状态，则停止拍照
        elif (self.saveInfoFLAG == 1):
            self.saveInfoFLAG = 0  # 将按钮设置为空闲状态
            self.startShoot_button.setStyleSheet('''
            QPushButton {
                border: none; /* 移除边框 */
                image: url("icons/start.svg"); /* 设置默认状态下的背景图片 */
                background-repeat: no-repeat;
                background-position: center
            }
            QPushButton:pressed {
                border: none; /* 移除边框 */
                image: url("icons/start_pressed.svg"); /* 设置按下状态下的背景图片 */
            }
        ''')
            self.stopShot_signal.emit()

    def refreshAmount(self, amount):
        # self.quantity_num_lable = QLabel(f"{amount:05d}")
        # print(f"refreshAmount:{amount}")
        self.quantity_num_lable.setText(f"{amount:05d}")

    def refreshPath(self, path):
        # print(f"option_photo:{path}")
        self.path_text.setText(path)
    
    def changeStartButton(self, flag):
        self.startShoot_button.setEnabled(flag)
