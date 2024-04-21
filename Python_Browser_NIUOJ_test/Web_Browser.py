import sys
import os
import time
import threading
import requests
from datetime import datetime
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QSplitter, QDialog, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

class LogUploader:
    def __init__(self):
        self.stop_event = threading.Event()
        self.upload_thread = threading.Thread(target=self.upload_logs)
        self.upload_thread.start()

    def upload_logs(self):
        while not self.stop_event.is_set():
            time.sleep(5)
            new_logs = self.get_new_logs()
            if new_logs:
                self.upload_to_server(new_logs)

    def get_new_logs(self):
        # 檢查log文件是否有新增內容
        if os.path.exists('status.log'):
            with open('status.log', 'r') as f:
                logs = f.readlines()
                last_index = self.get_last_index()
                new_logs = logs[last_index:]
                if new_logs:
                    self.set_last_index(len(logs))
                    return new_logs

    def get_last_index(self):
        # 讀取上次上傳的log索引
        try:
            with open('last_index.txt', 'r') as f:
                last_index = int(f.read().strip())
                return last_index
        except FileNotFoundError:
            return 0

    def set_last_index(self, index):
        # 寫入上次上傳的log索引
        with open('last_index.txt', 'w') as f:
            f.write(str(index))

    def upload_to_server(self, logs):
        # 將新增部分上傳到指定的服務器
        local_ip = self.get_local_ip()
        data = {'logs': logs, 'local_ip': local_ip}
        response = requests.post('http://192.168.6.2:8000/', json=data)
        if response.status_code == 200:
            print(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},logs_uploaded')
            with open('status.log', 'a') as f:
                f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},logs_uploaded\n')
            # 接收合併後的日誌數據
            merged_logs = response.json()
            # 處理合併後的日誌數據...
        else:
            print(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},logs_upload_failed')
            with open('status.log', 'a') as f:
                f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},logs_upload_failed\n')

    def get_local_ip(self):
        # 獲取本機電腦的內網IP地址
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))  # 使用 Google 的公共 DNS 服務器
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


    def stop(self):
        self.stop_event.set()
        self.upload_thread.join()

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(PasswordDialog, self).__init__(parent)

        self.setWindowTitle('Password Input')

        self.layout = QVBoxLayout(self)

        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_edit)

        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        # 禁止右上角的關閉和提問選項
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        # Start logging 'entering_password'
        self.start_logging()

    def password(self):
        return self.password_edit.text()

    def start_logging(self):
        with open('status.log', 'a') as f:
            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},entering_password\n')
        QTimer.singleShot(1000, self.start_logging)



class MainWindow(QMainWindow):
    def __init__(self):
        # Add a new attribute to track the password dialog status
        self.password_dialog_open = False
        
        super(MainWindow, self).__init__()
        self.left_browser = QWebEngineView()
        self.left_browser.setUrl(QUrl('http://192.168.6.2'))
        self.left_browser.urlChanged.connect(self.log_url_change)
        self.right_browser = QWebEngineView()
        self.right_browser.setUrl(QUrl('http://192.168.6.2/IDE'))
        self.right_browser.urlChanged.connect(self.log_url_change)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_browser)
        splitter.addWidget(self.right_browser)
        self.setCentralWidget(splitter)
        self.showFullScreen()

        # Check status.log
        if os.path.exists('status.log'):
            with open('status.log', 'r') as f:
                last_status = f.readlines()[-1].strip()  # 去掉行尾的换行符
                if last_status:  # 检查字符串是否为空
                    last_time_str = last_status.split(',')[0]
                    last_time = datetime.strptime(last_time_str, "%Y.%m.%d.%H.%M.%S")
                    if (datetime.now() - last_time).total_seconds() > 10:
                        dialog = PasswordDialog(self)
                        self.password_dialog_open = True
                        while dialog.exec_() == QDialog.Accepted:
                            password = dialog.password()
                            if password != 'Jefery':
                                with open('status.log', 'a') as f:
                                    f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},password_fail\n')
                            else:
                                with open('status.log', 'a') as f:
                                    f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},password_correct\n')
                                self.password_dialog_open = False
                                break

        # Start status logging
        self.start_logging()
        
        # Start fullscreen status checking after 5 seconds
        QTimer.singleShot(5000, self.start_fullscreen_check)
    """    
    def eventFilter(self, source, event):
        if isinstance(event, QMouseEvent):
            if event.type() == QEvent.MouseButtonPress:
                self.log_mouse_event(event)
        elif isinstance(event, QKeyEvent):
            if event.type() == QEvent.KeyPress:
                self.log_key_event(event)
        return super(MainWindow, self).eventFilter(source, event)

    def log_mouse_event(self, event):
        with open('status.log', 'a') as f:
            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},mouse_event,{event.pos()}\n')

    def log_key_event(self, event):
        with open('status.log', 'a') as f:
            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},key_event,{event.text()}\n')
    """
    def log_url_change(self, url):
        with open('status.log', 'a') as f:
            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},url_changed,{url.toString()}\n')    
        
    def start_fullscreen_check(self):
        # Check if the application is in fullscreen mode
        if not self.isFullScreen():
            with open('status.log', 'a') as f:
                f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},not_fullscreen\n')
            # If not, show the password dialog
            dialog = PasswordDialog(self)
            self.password_dialog_open = True
            while dialog.exec_() == QDialog.Accepted:
                password = dialog.password()
                if password != 'Jefery':
                    with open('status.log', 'a') as f:
                        f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},password_fail\n')
                else:
                    with open('status.log', 'a') as f:
                        f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},password_correct\n')
                    self.password_dialog_open = False
                    break

        # Check if there is another window on top of the application
        if QApplication.activeWindow() != self:
            with open('status.log', 'a') as f:
                f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},not_uppest_windows\n')
            # If so, show the password dialog
            dialog = PasswordDialog(self)
            self.password_dialog_open = True
            while dialog.exec_() == QDialog.Accepted:
                password = dialog.password()
                if password != 'Jefery':
                    with open('status.log', 'a') as f:
                        f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},password_fail\n')
                else:
                    with open('status.log', 'a') as f:
                        f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},password_correct\n')
                    self.password_dialog_open = False
                    break

        # Continue checking every second
        QTimer.singleShot(1000, self.start_fullscreen_check)
    
    def start_logging(self):
        # Only log 'online' when the password dialog is not open
        if not self.password_dialog_open:
            with open('status.log', 'a') as f:
                f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},online\n')
        QTimer.singleShot(1000, self.start_logging)

app = QApplication(sys.argv)
#print(os.path.abspath('status.log'))  # Print log file path
window = MainWindow()
"""
window.installEventFilter(window)
"""
app.exec_()
uploader = LogUploader()
# 程序結束時停止上傳線程
import atexit
atexit.register(uploader.stop)