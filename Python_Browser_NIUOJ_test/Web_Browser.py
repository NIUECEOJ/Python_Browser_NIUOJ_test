import sys
import os
import time
from datetime import datetime
import requests
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QSplitter, QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
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
        self.setWindowTitle('Password Input')
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

    def log_url_change(self, url):
        self.logger.log(f'url_changed,{url.toString()}')

    def start_fullscreen_check(self):
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
    

app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
