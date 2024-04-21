import sys
import os
import time
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QInputDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView

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
                last_status = f.readlines()[-1]
                last_time = float(last_status.split(',')[0])
                if time.time() - last_time < 10:
                    password, ok = QInputDialog.getText(self, 'Password Input', 'Enter your password:')
                    if not ok or password != 'Jefery':
                        sys.exit()
        else:
            with open('status.log', 'w') as f:
                f.write(f'{time.time()},online\n')

        # Start status logging
        self.start_logging()
        print(os.path.abspath('status.log'))

    def start_logging(self):
        with open('status.log', 'a') as f:
            f.write(f'{time.time()},online\n')
        QTimer.singleShot(1000, self.start_logging)

app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
