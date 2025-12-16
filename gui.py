from PyQt5 import QtWidgets, QtCore, QtGui

from pynput import keyboard
from key_sender import key_down, key_up
from window_manager import list_windows
from script_engine import ScriptEngine
import time
import threading
from keymap import KEY_MAP


class AutoKeyGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AutoKey GUI')
        self.resize(800, 600)
        self.windows = []
        self.engine = None
        self.running_thread = None

        # 全局热键
        self.hotkey_pause = keyboard.Key.f8
        self.hotkey_resume = keyboard.Key.f9

        self.hotkey_listener = keyboard.Listener(on_press=self.on_global_key)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

        # 初始化UI
        self.init_ui()

        self.stop_thread = False
        self.is_paused = False
        self.pause_condition = threading.Condition()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # 创建选项卡控件
        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs)

        # 第一个选项卡：主功能
        self.tab_main = QtWidgets.QWidget()
        self.init_main_tab()
        self.tabs.addTab(self.tab_main, "主功能")

        # 第二个选项卡：日志输出
        self.tab_logs = QtWidgets.QWidget()
        self.init_logs_tab()
        self.tabs.addTab(self.tab_logs, "日志输出")

    def init_main_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_main)

        self.window_list = QtWidgets.QComboBox()
        self.btn_refresh = QtWidgets.QPushButton('刷新窗口')
        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(self.window_list)
        hl.addWidget(self.btn_refresh)
        layout.addLayout(hl)

        # 速度（秒）
        self.speed_spin = QtWidgets.QDoubleSpinBox()
        self.speed_spin.setRange(0.01, 10.0)
        self.speed_spin.setValue(0.5)
        self.speed_spin.setSuffix(' s')
        layout.addWidget(QtWidgets.QLabel('按键间隔（秒）'))
        layout.addWidget(self.speed_spin)

        # 状态显示
        self.status_label = QtWidgets.QLabel('状态：Idle')
        self.status_label.setStyleSheet('font-weight: bold; color: gray;')
        layout.addWidget(self.status_label)

        # 暂停/重置 按钮
        hl_ctrl = QtWidgets.QHBoxLayout()

        self.btn_pause = QtWidgets.QPushButton('暂停')
        self.btn_pause.setEnabled(False)

        self.btn_reset = QtWidgets.QPushButton('重置')
        self.btn_reset.setEnabled(False)

        hl_ctrl.addWidget(self.btn_pause)
        hl_ctrl.addWidget(self.btn_reset)

        layout.addLayout(hl_ctrl)

        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_reset.clicked.connect(self.reset_task)

        # 全局热键暂停设置
        hotkey_box = QtWidgets.QGroupBox('全局热键设置')
        hotkey_layout = QtWidgets.QHBoxLayout(hotkey_box)
        hotkey_box.setMaximumHeight(120)
        self.combo_pause_key = QtWidgets.QComboBox()
        self.combo_resume_key = QtWidgets.QComboBox()

        for i in range(1, 13):
            self.combo_pause_key.addItem(f'F{i}')
            self.combo_resume_key.addItem(f'F{i}')

        self.combo_pause_key.setCurrentText('F8')
        self.combo_resume_key.setCurrentText('F9')

        hotkey_layout.addWidget(QtWidgets.QLabel('暂停'))
        hotkey_layout.addWidget(self.combo_pause_key)
        hotkey_layout.addWidget(QtWidgets.QLabel('继续'))
        hotkey_layout.addWidget(self.combo_resume_key)

        layout.addWidget(hotkey_box)

        # 简单模式（组合键）
        box1 = QtWidgets.QGroupBox('简单模式（按下你真实键盘组合）')
        b1 = QtWidgets.QHBoxLayout(box1)

        # 创建自定义输入框
        self.key_capture = CustomKeyCapture()
        self.key_capture.setPlaceholderText('点击后直接按组合键，如 Ctrl+Shift+A')
        self.key_capture.setReadOnly(True)

        self.btn_simple = QtWidgets.QPushButton('开始')
        b1.addWidget(self.key_capture)
        b1.addWidget(self.btn_simple)
        layout.addWidget(box1)

        # 高级脚本
        box2 = QtWidgets.QGroupBox('高级脚本')
        b2 = QtWidgets.QVBoxLayout(box2)
        self.script_edit = QtWidgets.QPlainTextEdit('''DOWN CTRL
KEY C
UP CTRL
WAIT 0.5''')
        self.btn_adv = QtWidgets.QPushButton('执行脚本')
        b2.addWidget(self.script_edit)
        b2.addWidget(self.btn_adv)
        layout.addWidget(box2)

        self.btn_refresh.clicked.connect(self.refresh_windows)
        self.btn_simple.clicked.connect(self.run_simple)
        self.btn_adv.clicked.connect(self.run_advanced)

        self.captured_keys = []

    def init_logs_tab(self):
        layout = QtWidgets.QVBoxLayout(self.tab_logs)

        self.log_output = QtWidgets.QPlainTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

    def refresh_windows(self):
        self.window_list.clear()
        self.windows = list_windows()
        for _, title in self.windows:
            self.window_list.addItem(title)

    def current_hwnd(self):
        idx = self.window_list.currentIndex()
        return self.windows[idx][0] if idx >= 0 else None

    def run_simple(self):
        hwnd = self.current_hwnd()
        interval = self.speed_spin.value()
        keys = self.key_capture.text().split('+')

        if not hwnd or not keys:
            self.log_error("请选择窗口和按键组合")
            return

        if self.running_thread and self.running_thread.is_alive():
            self.log_info("已存在运行任务，停止当前任务")
            self.stop_current_task()

        self.log_info(f"启动简单模式: 窗口={hwnd}, 按键={keys}, 间隔={interval}s")
        self.running_thread = threading.Thread(target=self.run_simple_thread, args=(hwnd, keys, interval))
        self.running_thread.daemon = True
        self.running_thread.start()
        self.update_ui_running()

    def run_simple_thread(self, hwnd, keys, interval):
        """带暂停功能的运行线程"""
        self.is_paused = False
        self.stop_thread = False
        try:
            while not self.stop_thread:  # 检查标志位
                with self.pause_condition:
                    while self.is_paused and not self.stop_thread:
                        self.pause_condition.wait()
                if self.stop_thread:
                    break
                for k in keys:
                    if k in KEY_MAP:
                        key_down(hwnd, KEY_MAP[k])
                        self.log_debug(f"DOWN: {k}")
                time.sleep(0.05)
                for k in reversed(keys):
                    if k in KEY_MAP:
                        key_up(hwnd, KEY_MAP[k])
                        self.log_debug(f"UP: {k}")
                time.sleep(interval)
        except Exception as e:
            self.log_error(f"运行错误: {str(e)}")
        finally:
            self.log_info("简单模式运行完成")
            self.update_ui_idle()

    def run_advanced(self):
        hwnd = self.current_hwnd()
        script = self.script_edit.toPlainText()

        if not hwnd or not script.strip():
            self.log_error("请选择窗口和有效脚本")
            return

        self.stop_thread = False
        self.is_paused = False

        self.engine = ScriptEngine(
            hwnd,
            self.pause_condition,
            lambda: self.is_paused,
            lambda: self.stop_thread
        )

        self.running_thread = threading.Thread(
            target=self.run_advanced_thread,
            args=(script,)
        )
        self.running_thread.daemon = True
        self.running_thread.start()
        self.update_ui_running()

    def run_advanced_thread(self, script):
        try:
            self.engine.run(script)
        except RuntimeError as e:
            self.log_info(str(e))
        except Exception as e:
            self.log_error(f"脚本执行错误: {str(e)}")
        finally:
            self.log_info("高级脚本执行完成")
            self.update_ui_idle()

    def toggle_pause(self):
        if not self.running_thread or not self.running_thread.is_alive():
            return

        if self.is_paused:
            self.is_paused = False
            self.btn_pause.setText('暂停')
            self.log_info("恢复运行")
        else:
            self.is_paused = True
            self.btn_pause.setText('继续')
            self.log_info("已暂停运行")

        # 通知线程继续
        with self.pause_condition:
            self.pause_condition.notify_all()

    def stop_current_task(self):
        """停止当前运行任务"""
        if self.running_thread and self.running_thread.is_alive():
            self.log_info("正在停止运行任务...")
            self.stop_thread = True  # 设置标志位通知线程停止
            self.is_paused = True  # 防止线程卡在暂停状态
            with self.pause_condition:
                self.pause_condition.notify_all()  # 唤醒线程
            self.running_thread.join(timeout=1.0)  # 等待线程结束
            if self.running_thread.is_alive():
                self.log_warning("任务停止超时，线程未完全退出")
            else:
                self.log_info("任务已成功停止")
        self.running_thread = None
        self.stop_thread = False  # 重置标志位

    def reset_task(self):
        self.log_info("重置任务")

        # 停止线程
        self.stop_current_task()

        # 状态恢复
        self.is_paused = False
        self.update_ui_idle()

    def update_ui_running(self):
        """更新UI为运行状态"""
        self.status_label.setText('状态：Running')
        self.status_label.setStyleSheet('font-weight: bold; color: green;')
        self.btn_simple.setEnabled(False)
        self.btn_adv.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_pause.setText('暂停')
        self.btn_reset.setEnabled(True)

    def update_ui_idle(self):
        """更新UI为空闲状态"""
        self.status_label.setText('状态：Idle')
        self.status_label.setStyleSheet('font-weight: bold; color: gray;')
        self.btn_simple.setEnabled(True)
        self.btn_adv.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText('暂停')
        self.btn_reset.setEnabled(False)

    def on_hotkey_pause(self):
        if self.running_thread and self.running_thread.is_alive() and not self.is_paused:
            self.log_info("【全局热键】暂停 (F8)")
            self.toggle_pause()

    def on_hotkey_resume(self):
        if self.running_thread and self.running_thread.is_alive() and self.is_paused:
            self.log_info("【全局热键】继续 (F9)")
            self.toggle_pause()

    def on_global_key(self, key):
        try:
            if key == self.hotkey_pause:
                self.on_hotkey_pause()
            elif key == self.hotkey_resume:
                self.on_hotkey_resume()
        except Exception:
            pass
    # 日志方法
    def log_info(self, msg):
        self.append_log(f"[INFO] {msg}")
        self.status_label.setText(f"状态：{msg}")

    def log_debug(self, msg):
        self.append_log(f"[DEBUG] {msg}")

    def log_error(self, msg):
        self.append_log(f"[ERROR] {msg}")
        self.status_label.setText(f"状态：错误: {msg}")
        self.status_label.setStyleSheet('font-weight: bold; color: red;')

    def log_warning(self, msg):
        self.append_log(f"[WARNING] {msg}")
        self.status_label.setText(f"状态：警告: {msg}")
        self.status_label.setStyleSheet('font-weight: bold; color: #FFA500;')

    def append_log(self, msg):
        QtCore.QMetaObject.invokeMethod(
            self.log_output,
            "appendPlainText",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, msg)
        )
        max_lines = 1000
        if self.log_output.blockCount() > max_lines:
            cursor = self.log_output.textCursor()
            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()

class CustomKeyCapture(QtWidgets.QLineEdit):
    """
    专业级组合键捕获：
    - 使用 Qt.Key + modifiers
    - 不依赖 event.text()
    """
    KEY_ORDER = {
        'CTRL': 0,
        'SHIFT': 1,
        'ALT': 2,
        'META': 3
    }
    QT_KEY_MAP = {
        QtCore.Qt.Key_Control: 'CTRL',
        QtCore.Qt.Key_Shift: 'SHIFT',
        QtCore.Qt.Key_Alt: 'ALT',
        QtCore.Qt.Key_Meta: 'META',

        QtCore.Qt.Key_Return: 'ENTER',
        QtCore.Qt.Key_Enter: 'ENTER',
        QtCore.Qt.Key_Tab: 'TAB',
        QtCore.Qt.Key_Escape: 'ESC',
        QtCore.Qt.Key_Backspace: 'BACKSPACE',
        QtCore.Qt.Key_Delete: 'DELETE',

        QtCore.Qt.Key_Up: 'UP',
        QtCore.Qt.Key_Down: 'DOWN',
        QtCore.Qt.Key_Left: 'LEFT',
        QtCore.Qt.Key_Right: 'RIGHT',
    }

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._keys = set()

    def focusInEvent(self, event):
        self._keys.clear()
        self.setText('')
        super().focusInEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        self._keys.clear()

        # 修饰键
        mods = event.modifiers()
        if mods & QtCore.Qt.ControlModifier:
            self._keys.add('CTRL')
        if mods & QtCore.Qt.ShiftModifier:
            self._keys.add('SHIFT')
        if mods & QtCore.Qt.AltModifier:
            self._keys.add('ALT')

        # 主键
        key = event.key()

        if key in self.QT_KEY_MAP:
            self._keys.add(self.QT_KEY_MAP[key])
        elif QtCore.Qt.Key_A <= key <= QtCore.Qt.Key_Z:
            self._keys.add(chr(key))
        elif QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
            self._keys.add(chr(key))
        elif QtCore.Qt.Key_F1 <= key <= QtCore.Qt.Key_F12:
            self._keys.add(f'F{key - QtCore.Qt.Key_F1 + 1}')

        ordered = sorted(
            self._keys,
            key=lambda k: self.KEY_ORDER.get(k, 100)
        )
        self.setText('+'.join(ordered))
        event.accept()

    def keyReleaseEvent(self, event):
        event.accept()
