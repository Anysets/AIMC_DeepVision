import json
import platform
import os
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QWidget

class AIMC_JSON(QObject):
    os_type = "Unknown"
    json_content = {
    "amount": 0,
    "save_location": ""
}
    config_dir = ""
    config_name = "config.json"
    config_path = ""

    JSON_loaded_signal = pyqtSignal()
    amount_loaded_signal = pyqtSignal(int)
    path_loaded_signal = pyqtSignal(str)

    def __init__(self, refreshOptionPhotoAmount, refreshCameraSaveAmount, refreshPhotoPath):
        super().__init__()
        self.refreshOptionPhotoAmount = refreshOptionPhotoAmount
        self.refreshCameraSaveAmount = refreshCameraSaveAmount
        self.refreshPhotoPath = refreshPhotoPath
        self.setJSONLocation()
        self.readJSONContent()
        
        

    # 根据不同的操作系统适配不同的存储目录
    def setJSONLocation(self):
        self.os_type = platform.system()
        if self.os_type == "Windows":
            self.config_dir = os.path.join(os.getenv('APPDATA'), "AIMC-Video")
        elif self.os_type == "Linux" or self.os_type == "Darwin":
            self.config_dir = os.path.join(os.path.expanduser("~"), ".config", "AIMC-Video")
        else:
            self.config_dir = os.path.join(os.getcwd(), ".config")
        # 最终的存储路径
        self.config_path = os.path.join(self.config_dir, self.config_name)
    
    def readJSONContent(self):
        # 检查文件是否存在
        if os.path.exists(self.config_path):
            try:
                # 如果文件存在，打开并读取 JSON 文件
                with open(self.config_path, 'r') as file:
                    data = json.load(file)
                self.json_content = data
                 # 将amount发送出去
                amount = int(self.json_content['amount'])
                # self.amount_loaded_signal.emit(amount)
                # 将path发送出去
                path = str(self.json_content['save_location'])
                # self.path_loaded_signal.emit(path)
                
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"if An error occurred: {e}")
        # 如果不存在，把默认空配置写入配置文件
        else:
            try:
                os.makedirs(self.config_dir, exist_ok=True)
                with open(self.config_path, 'w') as file:
                    json.dump(self.json_content, file, indent=4)
            except Exception as e:
                print(f"else An error occurred: {e}")
        self.amount_loaded_signal.emit(amount)
        self.refreshOptionPhotoAmount(amount)
        self.refreshCameraSaveAmount(amount)
        self.path_loaded_signal.emit(path)
        self.refreshPhotoPath(path)
    
    def sendJSONInfo(self):
        self.JSON_loaded_signal.emit(self.json_content)

    def changeAmount(self, amount):
        self.json_content['amount'] = amount

    def changePath(self, path):
        self.json_content['save_location'] = path

    def saveToJSON(self):
        print("close after saving!")
        with open(self.config_path, 'w') as file:
            json.dump(self.json_content, file, indent=4)
