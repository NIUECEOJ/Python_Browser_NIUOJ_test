import sys
import os
import time
from datetime import datetime
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QDialog, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView

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
        super(MainWindow, self).__init__()
        self.left_browser = QWebEngineView()
        self.left_browser.setUrl(QUrl('http://192.168.6.2'))
        self.right_browser = QWebEngineView()
        self.right_browser.setUrl(QUrl('http://192.168.6.2/IDE'))
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
                        if dialog.exec_() == QDialog.Accepted:
                            password = dialog.password()
                            if password != 'Jefery':
                                sys.exit()
                        # Write 'entering_password' to status.log
                        with open('status.log', 'a') as f:
                            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},entering_password\n')
                    else:
                        with open('status.log', 'a') as f:
                            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},online\n')
                else:  # 如果字符串为空,则写入新的时间戳记
                    with open('status.log', 'a') as f:
                        f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},online\n')

        # Start status logging
        self.start_logging()

    def start_logging(self):
        with open('status.log', 'a') as f:
            f.write(f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},online\n')
        QTimer.singleShot(1000, self.start_logging)

app = QApplication(sys.argv)
print(os.path.abspath('status.log'))  # Print log file path
window = MainWindow()
app.exec_()
