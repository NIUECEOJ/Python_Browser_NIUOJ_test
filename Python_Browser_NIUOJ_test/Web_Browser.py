import sys
import os
import time
import threading
import subprocess
import psutil
from datetime import datetime, timedelta
import requests
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QMouseEvent, QKeyEvent
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QSplitter, QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QWidget, QToolBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# 設定常數
PASSWORD = "NIUeceJefery"  # 管理員密碼
SERVER_URL = "http://192.168.6.2:8000"  # 伺服器地址
WATCHDOG_BAT_PATH = "start.bat"  # 看門狗批處理文件路徑

class Logger:
    def __init__(self, filename):
        self.filename = filename
        self.last_logged_message = None
        self.last_online_time = None

    def log(self, message):
        timestamp = datetime.now().strftime("%Y.%m.%d.%H.%M.%S")
        log_entry = f'{timestamp},{message}\n'
        with open(self.filename, 'a') as f:
            f.write(log_entry)
        if message != self.last_logged_message:
            self.last_logged_message = message
            threading.Thread(target=self.upload_log, args=(log_entry,)).start()
            if message == 'online':
                self.last_online_time = datetime.now()
                # 啟動一個新線程來定時發送'online'
                threading.Thread(target=self.send_online_periodically).start()
            else:
                self.last_online_time = None
        elif message == 'online':
            if self.last_online_time and datetime.now() - self.last_online_time >= timedelta(seconds=10):
                threading.Thread(target=self.send_online_periodically).start()
            
    def upload_log(self, log_entry):
        url = f'{SERVER_URL}/status'
        try:
            # 實際上傳函數（目前僅打印日誌）
            print("日誌成功上傳。")
        except Exception as e:
            print(f"上傳錯誤: {e}")
                
    def send_online_periodically(self):
        while self.last_logged_message == 'online':
            if datetime.now() - self.last_online_time >= timedelta(seconds=10):
                log_entry = f'{datetime.now().strftime("%Y.%m.%d.%H.%M.%S")},online\n'
                self.upload_log(log_entry)
                time.sleep(5)  # 每五秒執行一次

class UploadingMessageBox(QMessageBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setWindowTitle('上傳logs')
        self.setText('正在上傳考試資料，請勿關閉電腦')
        self.setStandardButtons(QMessageBox.NoButton)  # 移除所有標準按鈕
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)  # 禁用關閉按鈕

    # 重寫 closeEvent 方法來禁止對話框被關閉
    def closeEvent(self, event):
        event.ignore()
        
    # 添加一個方法來關閉對話框
    def close_message_box(self):
        self.close()

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
        # 設置窗口標誌，禁用所有關閉選項
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.logger = Logger('status.log')
        self.start_logging()
        
    def password(self):
        return self.password_edit.text()

    def start_logging(self):
        self.logger.log('entering_password')
        QTimer.singleShot(1000, self.start_logging)
        
    # 禁用所有按鍵事件，包括Esc
    def keyPressEvent(self, event):
        event.ignore()
        
    # 重寫closeEvent來禁止對話框被關閉
    def closeEvent(self, event):
        event.ignore()

class WebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # 只允許訪問 'contest、ide' 開頭的網址
        if url.toString().startswith(("https://ecejudge.niu.edu.tw/contest", "https://ecejudge.niu.edu.tw/IDE")):
            return True
        return False

# 在創建 QWebEngineView 時，使用自定義的 WebEnginePage
class WebEngineView(QWebEngineView):
    def __init__(self, parent=None):
        super(WebEngineView, self).__init__(parent)
        self.setPage(WebEnginePage(self))

    def contextMenuEvent(self, event):
        # 不執行任何操作，從而禁用右鍵菜單
        pass

class ProcessMonitor(QObject):
    task_manager_detected = pyqtSignal()
    
    def __init__(self):
        super(ProcessMonitor, self).__init__()
        self.monitoring = True
        
    def start_monitoring(self):
        threading.Thread(target=self._monitor_processes, daemon=True).start()
        
    def stop_monitoring(self):
        self.monitoring = False
        
    def _monitor_processes(self):
        forbidden_processes = ["taskmgr.exe", "processhacker.exe", "procexp.exe", "procmon.exe", "perfmon.exe"]
        while self.monitoring:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in [p.lower() for p in forbidden_processes]:
                        # 直接嘗試終止進程
                        try:
                            proc.kill()
                        except:
                            pass
                        # 通知主視窗
                        self.task_manager_detected.emit()
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            time.sleep(0.5)  # 檢查頻率提高

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.password_dialog_open = False
        self.check_fullscreen_topest = True  # 新增一個標誌來控制全螢幕檢查、頂層
        
        # 初始化進程監控
        self.process_monitor = ProcessMonitor()
        self.process_monitor.task_manager_detected.connect(self.on_task_manager_detected)
        self.process_monitor.start_monitoring()
        
        # 初始化退出按鈕
        self.init_exit_button()
        self.left_browser = WebEngineView()
        self.left_browser.setUrl(QUrl('https://ecejudge.niu.edu.tw/contest'))
        self.left_browser.urlChanged.connect(self.log_url_change)
        self.right_browser = WebEngineView()
        self.right_browser.setUrl(QUrl('https://ecejudge.niu.edu.tw/IDE'))
        self.right_browser.urlChanged.connect(self.log_url_change)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_browser)
        splitter.addWidget(self.right_browser)
        self.setCentralWidget(splitter)
        self.showFullScreen()
        
        self.logger = Logger('status.log')
        # 檢查是否需要鎖定（程式重開時）
        self.logger.log('program_started')
        # 程式啟動時立即鎖定，要求輸入密碼 - 確保重啟後的安全性
        self.show_password_dialog()
            
        self.start_logging()
        QTimer.singleShot(1000, self.start_fullscreen_check)  # 更快開始檢查全螢幕
    
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
    
    def on_task_manager_detected(self):
        self.logger.log('task_manager_detected')
        # 顯示密碼對話框
        self.show_password_dialog()
        
    def show_password_dialog(self):
        if not self.password_dialog_open:
            dialog = PasswordDialog(self)
            self.password_dialog_open = True
            # 在對話框顯示之前，提高我們的窗口優先級
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
            
            while dialog.exec_() == QDialog.Accepted:
                password = dialog.password()
                if password != PASSWORD:
                    self.logger.log('password_fail')
                else:
                    self.logger.log('password_correct')
                    self.password_dialog_open = False
                    break
    
    # 檢查是否為全螢幕或最頂層
    def start_fullscreen_check(self): 
        if self.check_fullscreen_topest:
            if not self.isFullScreen():
                self.logger.log('not_fullscreen')
                self.showFullScreen()  # 直接嘗試恢復全螢幕
                self.show_password_dialog()
                
            if QApplication.activeWindow() != self:
                self.logger.log('not_uppest_windows')
                # 嘗試再次將窗口設置為頂層
                self.activateWindow()
                self.raise_()
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
                self.show()
                self.showFullScreen()
                self.show_password_dialog()
                
        QTimer.singleShot(500, self.start_fullscreen_check)  # 更頻繁地檢查

    def start_logging(self):
        if not self.password_dialog_open:
            self.logger.log('online')
        QTimer.singleShot(1000, self.start_logging)
    
    def find_watchdog_process(self):
        """查找看門狗進程"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # 檢查是否是CMD進程，並且命令行包含start.bat
                if proc.info['name'] == 'cmd.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if 'start.bat' in cmdline:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return None
    
    def closeEvent(self, event):
        # 在關閉視窗前輸出日誌
        self.logger.log('trylogout')
        self.check_fullscreen_topest = False
        self.process_monitor.stop_monitoring()

        # 顯示一個消息框詢問用戶是否確定要退出
        reply = QMessageBox.question(self, '確認退出考試？', 
                                    '您確定要退出考試，將無法重新進入考場？', 
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.logger.log('User confirmed exit')
            
            # 創建請等待對話框
            Uploading_msg_box = UploadingMessageBox()
            Uploading_msg_box.show()

            # 上傳日誌
            self.logger.log('upload_success')
            
            # 上傳完成關閉請等待對話框
            Uploading_msg_box.close_message_box()
            
            # 執行關閉前的清理工作
            try:
                # 關閉看門狗進程
                watchdog_proc = self.find_watchdog_process()
                if watchdog_proc:
                    self.logger.log(f'Found watchdog process (PID: {watchdog_proc.info["pid"]}), terminating...')
                    watchdog_proc.kill()
                    self.logger.log('Watchdog process terminated')
                else:
                    self.logger.log('No watchdog process found')
                    
            except Exception as e:
                self.logger.log(f'Failed to terminate watchdog: {e}')
        else:
            self.logger.log('User cancelled exit')
            event.ignore()  # 用戶選擇不退出，忽略關閉事件
            self.check_fullscreen_topest = True
            return
        
        # 如果用戶確認退出，則記錄日誌並關閉應用程式
        self.logger.log('logout')
        super(MainWindow, self).closeEvent(event)
        
        # 在主程序結束後，重新啟動看門狗，但不等待它完成
        try:
            # 在背景執行start.bat
            subprocess.Popen(WATCHDOG_BAT_PATH, shell=True, 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            print(f"Failed to restart watchdog: {e}")

# 程式入口點
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
