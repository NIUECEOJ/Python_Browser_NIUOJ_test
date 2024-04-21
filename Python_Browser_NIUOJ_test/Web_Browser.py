import sys
import os
import time
from datetime import datetime
import requests
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QSplitter, QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QWidget, QToolBar
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Logger:
    def __init__(self, filename):
        self.filename = filename

    def log(self, message):
        with open(self.filename, 'a') as f:
            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},{message}\n')

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super(PasswordDialog, self).__init__(parent)
        self.setWindowTitle('偵測到作弊請聯絡助教與教授')
        self.layout = QVBoxLayout(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_edit)
        self.ok_button = QPushButton('OK', self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.logger = Logger('status.log')
        self.start_logging()

    def password(self):
        return self.password_edit.text()

    def start_logging(self):
        self.logger.log('entering_password')
        QTimer.singleShot(1000, self.start_logging)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.password_dialog_open = False
        self.check_fullscreen_topest = True  # 新增一個標誌來控制全螢幕檢查、頂層
        # 初始化退出按鈕
        self.init_exit_button()
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
        
        

        self.logger = Logger('status.log')
        if os.path.exists('status.log'):
            with open('status.log', 'r') as f:
                last_status = f.readlines()[-1].strip()
                if last_status:
                    last_time_str = last_status.split(',')[0]
                    last_time = datetime.strptime(last_time_str, "%Y.%m.%d.%H.%M.%S")
                    if (datetime.now() - last_time).total_seconds() > 10:
                        dialog = PasswordDialog(self)
                        self.password_dialog_open = True
                        while dialog.exec_() == QDialog.Accepted:
                            password = dialog.password()
                            if password != 'NIUeceJefery':
                                self.logger.log('password_fail')
                            else:
                                self.logger.log('password_correct')
                                self.password_dialog_open = False
                                break
        self.start_logging()
        QTimer.singleShot(5000, self.start_fullscreen_check)
    
    def init_exit_button(self):
        # 創建退出按鈕並設定其屬性
        self.exit_button = QPushButton('退出', self)
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setFixedSize(80, 40)  # 為按鈕設定固定大小

        # 創建一個工具欄並將退出按鈕添加到其中
        exit_toolbar = QToolBar("Exit Toolbar", self)
        exit_toolbar.addWidget(self.exit_button)
        exit_toolbar.setMovable(False)  # 防止工具欄被移動
        exit_toolbar.setFloatable(False)  # 防止工具欄浮動
        exit_toolbar.setStyleSheet("QToolBar { border: 0px }")  # 隱藏工具欄的邊框

        # 將工具欄添加到主視窗的右上角
        self.addToolBar(Qt.TopToolBarArea, exit_toolbar)
        self.insertToolBarBreak(exit_toolbar)
    
    def log_url_change(self, url):
        self.logger.log(f'url_changed,{url.toString()}')
    
    # 檢查是否為全螢幕或最頂層
    def start_fullscreen_check(self): 
        if self.check_fullscreen_topest:
            if not self.isFullScreen():
                self.logger.log('not_fullscreen')
                dialog = PasswordDialog(self)
                self.password_dialog_open = True
                while dialog.exec_() == QDialog.Accepted:
                    password = dialog.password()
                    if password != 'NIUeceJefery':
                        self.logger.log('password_fail')
                    else:
                        self.logger.log('password_correct')
                        self.password_dialog_open = False
                        break
            if QApplication.activeWindow() != self:
                self.logger.log('not_uppest_windows')
                dialog = PasswordDialog(self)
                self.password_dialog_open = True
                while dialog.exec_() == QDialog.Accepted:
                    password = dialog.password()
                    if password != 'NIUeceJefery':
                        self.logger.log('password_fail')
                    else:
                        self.logger.log('password_correct')
                        self.password_dialog_open = False
                        break
        QTimer.singleShot(1000, self.start_fullscreen_check)


    def start_logging(self):
        if not self.password_dialog_open:
            self.logger.log('online')
        QTimer.singleShot(1000, self.start_logging)
    
    def closeEvent(self, event):
        # 在關閉視窗前輸出日誌
        self.logger.log('trylogout')
        self.check_fullscreen_topest = False

        # 顯示一個消息框詢問用戶是否確定要重啟電腦
        reply = QMessageBox.question(self, '確認退出考試？', '您確定要退出考試，將無法重新進入考場？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.logger.log('User confirmed reboot')
            try:
                # Windows 系統重啟命令
                os.system('shutdown /r /t 1')
            except Exception as e:
                self.logger.log(f'Failed to reboot: {e}')
                QMessageBox.warning(self, '警告', '無法重啟電腦。')
                event.ignore()  # 忽略關閉事件，不關閉應用程式
                return  # 提前返回，不執行下面的關閉代碼
        else:
            self.logger.log('User cancelled reboot')
            event.ignore()  # 用戶選擇不重啟，忽略關閉事件
            return  # 提前返回，不執行下面的關閉代碼

        # 如果用戶確認重啟，則記錄日誌並關閉應用程式
        self.logger.log('logout')
        super(MainWindow, self).closeEvent(event)  # 繼續執行預設的關閉事件
        self.check_fullscreen_topest = True

app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
