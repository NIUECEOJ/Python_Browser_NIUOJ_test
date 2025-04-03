import sys
import os
import time
import threading
import subprocess
import psutil
from datetime import datetime, timedelta
import requests
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QGuiApplication
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QSplitter, QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QWidget, QToolBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import keyboard  # 需要安裝 keyboard 模組: pip install keyboard
import win32clipboard  # 需要安裝 pywin32: pip install pywin32

# 設定常數
PASSWORD = "NIUeceJefery"  # 管理員密碼
SERVER_URL = "http://192.168.6.2:8000"  # 伺服器地址
WATCHDOG_BAT_PATH = "cmd.exe"  # 看門狗批處理文件路徑

# 要禁用的按鍵列表
BLOCKED_KEYS = [
    'esc', 'escape',
    'alt', 'alt+tab', 'alt+f4', 'alt+shift', 'alt+ctrl',
    'ctrl', 'ctrl+alt', 'ctrl+shift', 'ctrl+c', 'ctrl+v', 'ctrl+x', 'ctrl+a', 'ctrl+z', 'ctrl+y',
    'win', 'windows', 'left windows', 'right windows',
    'tab', 'alt+tab', 'shift+tab'
]

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
        #url = f'{SERVER_URL}/status'
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

class ClipboardManager:
    """剪貼簿管理類"""
    @staticmethod
    def clear_clipboard():
        """清除剪貼簿內容"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            print("剪貼簿已清空")
        except Exception as e:
            print(f"清空剪貼簿錯誤: {e}")
    
    @staticmethod
    def block_clipboard_thread():
        """持續監控並清空剪貼簿的線程"""
        while True:
            ClipboardManager.clear_clipboard()
            time.sleep(0.5)  # 每0.5秒清空一次剪貼簿

class KeyboardBlocker:
    """鍵盤按鍵禁用類"""
    @staticmethod
    def block_key(event):
        """攔截並禁用指定的按鍵"""
        # 返回False來禁止按鍵事件傳遞
        return False
    
    @staticmethod
    def setup_key_blocks():
        """設置所有要禁用的按鍵"""
        for key in BLOCKED_KEYS:
            try:
                keyboard.hook_key(key, KeyboardBlocker.block_key)
            except Exception as e:
                print(f"無法禁用按鍵 {key}: {e}")
        
        # 增強：直接攔截組合鍵
        keyboard.hook(KeyboardBlocker.enhanced_key_block)
        print("已禁用特殊按鍵")
    
    @staticmethod
    def enhanced_key_block(event):
        """進階按鍵阻擋函數"""
        # 如果是按下事件
        if event.event_type == keyboard.KEY_DOWN:
            # 檢查是否含有特殊功能鍵
            if (event.modifiers or 
                event.name.lower() in ['win', 'windows', 'left windows', 'right windows', 
                                      'esc', 'escape', 'tab', 
                                      'alt', 'ctrl', 'control']):
                return False  # 阻擋事件繼續傳遞
        return True  # 允許其他按鍵

class DialogKeyFilter:
    """對話框按鍵過濾器，用於限制只允許特定按鍵"""
    @staticmethod
    def is_allowed_key(key, modifiers):
        """檢查是否為允許的按鍵"""
        # 允許數字鍵 (Qt.Key_0 到 Qt.Key_9)
        if Qt.Key_0 <= key <= Qt.Key_9:
            return True
        
        # 允許字母鍵 (Qt.Key_A 到 Qt.Key_Z)
        if Qt.Key_A <= key <= Qt.Key_Z:
            return True
        
        # 允許回車鍵
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            return True
        
        # 允許退格鍵和刪除鍵（對密碼輸入有用）
        if key == Qt.Key_Backspace or key == Qt.Key_Delete:
            return True
        
        # 如果只有Shift修飾符被按下，允許該組合（用於大寫）
        if modifiers == Qt.ShiftModifier:
            return True
        
        # 其他所有按鍵和組合鍵都禁用
        return False

class UploadingMessageBox(QMessageBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setWindowTitle('上傳logs')
        self.setText('正在上傳考試資料，請勿關閉電腦')
        self.setStandardButtons(QMessageBox.NoButton)  # 移除所有標準按鈕
        # 確保訊息框在頂層
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)

    # 重寫 closeEvent 方法來禁止對話框被關閉
    def closeEvent(self, event):
        event.ignore()
        
    # 添加一個方法來關閉對話框
    def close_message_box(self):
        self.close()
        
    def keyPressEvent(self, event):
        """重寫按鍵事件，阻止所有按鍵輸入"""
        # 記錄嘗試使用的按鍵但不處理
        event.ignore()

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
        # 設置窗口標誌，確保在頂層且無法關閉
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | 
                           Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.logger = Logger('status.log')
        self.start_logging()
        
    def password(self):
        return self.password_edit.text()

    def start_logging(self):
        self.logger.log('entering_password')
        QTimer.singleShot(1000, self.start_logging)
        
    def showEvent(self, event):
        """重寫顯示事件，確保對話框顯示時主視窗仍然保持全螢幕"""
        super(PasswordDialog, self).showEvent(event)
        # 確保對話框在頂層
        self.activateWindow()
        self.raise_()
        
    def keyPressEvent(self, event):
        """重寫按鍵事件，只允許數字、字母、Shift和Enter鍵"""
        key = event.key()
        modifiers = event.modifiers()
        
        if DialogKeyFilter.is_allowed_key(key, modifiers):
            super(PasswordDialog, self).keyPressEvent(event)
        else:
            # 記錄嘗試使用的非法按鍵
            self.logger.log(f'password_dialog_blocked_key: {key} with modifiers: {modifiers}')
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
        self.pause_monitoring_until = None  # 新增一個變數來控制監控暫停時間
        
    def start_monitoring(self):
        threading.Thread(target=self._monitor_processes, daemon=True).start()
        
    def stop_monitoring(self):
        self.monitoring = False
        
    def pause_for_seconds(self, seconds):
        """暫停監控一段時間"""
        self.pause_monitoring_until = datetime.now() + timedelta(seconds=seconds)
        
    def _monitor_processes(self):
        forbidden_processes = ["taskmgr.exe", "processhacker.exe", "procexp.exe", "procmon.exe", "perfmon.exe"]
        while self.monitoring:
            # 檢查是否在暫停期內
            if self.pause_monitoring_until and datetime.now() < self.pause_monitoring_until:
                time.sleep(0.5)
                continue
                
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
        # *** 將 logger 初始化移到最前面 ***
        self.logger = Logger('status.log')
        
        super(MainWindow, self).__init__()
        self.password_dialog_open = False
        self.check_fullscreen_topest = True  # 新增一個標誌來控制全螢幕檢查、頂層
        self.grace_period_active = False  # 新增緩衝期狀態標記
        
        # 初始化剪貼簿
        self.init_clipboard()
        
        # 初始化鍵盤禁用
        self.init_keyboard_blocker()
        
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
        
        # 設定窗口屬性
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.showFullScreen()
        
        # 檢查是否需要鎖定（程式重開時）
        self.logger.log('program_started')
        # 程式啟動時立即鎖定，要求輸入密碼 - 確保重啟後的安全性
        #self.show_password_dialog()
            
        self.start_logging()
        QTimer.singleShot(500, self.start_fullscreen_check)  # 更快開始檢查全螢幕
        
    def init_clipboard(self):
        """初始化剪貼簿管理"""
        # 清空剪貼簿
        ClipboardManager.clear_clipboard()
        # 啟動剪貼簿監控線程
        threading.Thread(target=ClipboardManager.block_clipboard_thread, daemon=True).start()
        self.logger.log('clipboard_disabled')
        
    def init_keyboard_blocker(self):
        """初始化鍵盤禁用"""
        try:
            KeyboardBlocker.setup_key_blocks()
            self.logger.log('special_keys_disabled')
        except Exception as e:
            self.logger.log(f'keyboard_block_error: {e}')
    
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
        # 如果在緩衝期內，則不執行任何操作
        if self.grace_period_active:
            return
            
        self.logger.log('task_manager_detected')
        # 顯示密碼對話框
        self.show_password_dialog()
        
    def show_password_dialog(self):
        # 如果在緩衝期內或已經打開了密碼對話框，則不執行任何操作
        if self.grace_period_active or self.password_dialog_open:
            return
        
        # 在顯示密碼對話框前確保主視窗是全螢幕並且在最上層
        self.ensure_fullscreen_and_top()
            
        dialog = PasswordDialog(self)
        self.password_dialog_open = True
        
        while dialog.exec_() == QDialog.Accepted:
            password = dialog.password()
            if password != PASSWORD:
                self.logger.log('password_fail')
            else:
                self.logger.log('password_correct')
                self.password_dialog_open = False
                
                # 啟動緩衝期
                self.start_grace_period(3)  # 3秒緩衝期
                
                # 確保對話框關閉後主視窗仍然是全螢幕和最上層
                self.ensure_fullscreen_and_top()
                break
    
    def ensure_fullscreen_and_top(self):
        """確保視窗是全螢幕且在最上層"""
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.showFullScreen()
        self.activateWindow()
        self.raise_()
    
    def start_grace_period(self, seconds):
        """啟動緩衝期，在此期間內不會觸發作弊檢測和密碼輸入框"""
        self.grace_period_active = True
        self.logger.log(f'grace_period_started_{seconds}s')
        
        # 同時暫停進程監控
        self.process_monitor.pause_for_seconds(seconds)
        
        # 設定一個計時器，在緩衝期結束後恢復檢測
        QTimer.singleShot(seconds * 1000, self.end_grace_period)
        
    def end_grace_period(self):
        """結束緩衝期，恢復作弊檢測"""
        self.grace_period_active = False
        self.logger.log('grace_period_ended')
    
    # 攔截特定鍵盤按鍵
    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        
        # 檢查是否是特殊按鍵
        is_special_key = (key == Qt.Key_Escape or 
                         modifiers & Qt.AltModifier or 
                         modifiers & Qt.ControlModifier or 
                         modifiers & Qt.MetaModifier or
                         key == Qt.Key_Tab)
        
        if is_special_key:
            self.logger.log(f'detected_special_key: {key} with modifiers: {modifiers}')
            event.ignore()
            
            # 如果在緩衝期內，不執行任何操作
            if self.grace_period_active:
                return
            
            # 直接顯示密碼對話框
            self.show_password_dialog()
            return
            
        super(MainWindow, self).keyPressEvent(event)
    
    # 檢查是否為全螢幕或最頂層
    def start_fullscreen_check(self): 
        if self.check_fullscreen_topest:
            # 如果在緩衝期內，不進行全螢幕檢查
            if not self.grace_period_active and not self.password_dialog_open:
                if not self.isFullScreen():
                    self.logger.log('not_fullscreen')
                    self.ensure_fullscreen_and_top()
                    self.show_password_dialog()
                    
                if QApplication.activeWindow() != self:
                    self.logger.log('not_uppest_windows')
                    self.ensure_fullscreen_and_top()
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
                # 關閉所有cmd.exe進程
                self.logger.log('準備關閉所有cmd.exe進程')
                closed_count = 0
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] == 'cmd.exe':
                            pid = proc.info['pid']
                            self.logger.log(f'正在關閉cmd.exe進程 (PID: {pid})')
                            proc.kill()
                            closed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                        self.logger.log(f'無法關閉進程: {e}')
                self.logger.log(f'已關閉 {closed_count} 個cmd.exe進程')
                    
            except Exception as e:
                self.logger.log(f'關閉cmd.exe進程時發生錯誤: {e}')
        else:
            self.logger.log('User cancelled exit')
            event.ignore()  # 用戶選擇不退出，忽略關閉事件
            self.check_fullscreen_topest = True
            return
        
        # 如果用戶確認退出，則記錄日誌並關閉應用程式
        self.logger.log('logout')
        super(MainWindow, self).closeEvent(event)
        
        # 不再重新啟動看門狗，因為我們已經關閉了所有cmd.exe進程

# 程式入口點
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
