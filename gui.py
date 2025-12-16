from PyQt5 import QtCore, QtGui
from pynput import keyboard
import threading
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from qfluentwidgets import (
    FluentWindow,
    PushButton,
    PrimaryPushButton,
    ComboBox,
    PlainTextEdit,
    SubtitleLabel,
    BodyLabel,
    SpinBox,
    CardWidget,
    LineEdit,
    NavigationItemPosition,
    FluentIcon, CaptionLabel
)
from log_system import Logger, LogLevel
from key_sender import key_down, key_up
from window_manager import list_windows
from script_engine import ScriptEngine
from keymap import KEY_MAP

LOG_COLORS = {
    LogLevel.DEBUG: "#888888",
    LogLevel.INFO:  "#4FC1FF",
    LogLevel.WARN:  "#FFA500",
    LogLevel.ERROR: "#FF4C4C",
}

class AutoKeyGUI(FluentWindow):
    ui_log_signal = QtCore.pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle('AutoKey GUI')
        self.resize(900, 650)

        self.windows = []
        self.engine = None
        self.running_thread = None

        # 日志信号
        self.logger = Logger()
        self.current_log_level = LogLevel.INFO
        # 线程控制
        self.pause_event = threading.Event()
        self.stop_event = threading.Event()
        self.pause_event.set()
        self.stop_event.clear()

        # 全局热键
        self.hotkey_pause = keyboard.Key.f8
        self.hotkey_resume = keyboard.Key.f9

        self.hotkey_listener = keyboard.Listener(on_press=self.on_global_key)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

        self.init_ui()

        self.ui_log_signal.connect(self._append_log_ui)
        self.logger.add_handler(self._gui_log_handler)
        self.logger.info("应用初始化完成")

    # ---------------- UI ----------------

    def init_ui(self):
        self.root = QWidget(self)

        self.layout = QVBoxLayout(self.root)


        # 初始化两个页面
        self.page_main = self.init_main_tab()
        self.page_logs = self.init_logs_tab()
        self.page_main.setObjectName("main")
        self.page_logs.setObjectName("logs")

        # 添加到侧边栏
        self.addSubInterface(
            self.page_main,
            FluentIcon.HOME,
            "主功能",
            NavigationItemPosition.TOP
        )

        self.addSubInterface(
            self.page_logs,
            FluentIcon.DOCUMENT,
            "日志",
            NavigationItemPosition.TOP
        )

        # 默认显示主功能
        self.switchTo(self.page_main)

    def init_main_tab(self):
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTextEdit

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 窗口选择
        hl = QHBoxLayout()
        self.window_list = ComboBox()
        self.btn_refresh = PushButton("刷新窗口")
        hl.addWidget(self.window_list)
        hl.addWidget(self.btn_refresh)
        layout.addLayout(hl)

        # 速度
        layout.addWidget(BodyLabel("按键间隔（毫秒）[1000ms=1s]"))
        self.speed_spin = SpinBox()
        self.speed_spin.setRange(1, 100000)
        self.speed_spin.setValue(1000)
        layout.addWidget(self.speed_spin)

        # 状态
        self.status_label = SubtitleLabel("状态：Idle")
        font = self.status_label.font()
        font.setPointSize(12)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)

        # 控制按钮
        hl_ctrl = QHBoxLayout()
        self.btn_pause = PushButton("暂停")
        self.btn_reset = PushButton("重置")
        self.btn_pause.setEnabled(False)
        self.btn_reset.setEnabled(False)
        hl_ctrl.addWidget(self.btn_pause)
        hl_ctrl.addWidget(self.btn_reset)
        layout.addLayout(hl_ctrl)

        # 热键设置
        hotkey_box = CardWidget()
        hotkey_layout = QFormLayout(hotkey_box)

        self.combo_pause_key = ComboBox()
        self.combo_resume_key = ComboBox()

        for i in range(1, 13):
            self.combo_pause_key.addItem(f'F{i}')
            self.combo_resume_key.addItem(f'F{i}')

        self.combo_pause_key.setCurrentText('F8')
        self.combo_resume_key.setCurrentText('F9')

        self.label_pause = CaptionLabel("暂停")
        self.label_pause.setStyleSheet("color: #CCCCCC ;")

        self.label_resume = CaptionLabel("继续")
        self.label_resume.setStyleSheet("color: #CCCCCC ;")

        hotkey_layout.addRow(self.label_pause , self.combo_pause_key)
        hotkey_layout.addRow(self.label_resume , self.combo_resume_key)
        layout.addWidget(hotkey_box)

        # 简单模式
        simple_box = CardWidget()
        sb = QHBoxLayout(simple_box)
        self.key_capture = CustomKeyCapture()
        self.btn_simple = PrimaryPushButton("开始")
        sb.addWidget(self.key_capture)
        sb.addWidget(self.btn_simple)
        layout.addWidget(simple_box)

        # 高级脚本
        adv_box = CardWidget()
        vb = QVBoxLayout(adv_box)
        self.script_edit = PlainTextEdit()
        self.script_edit.setPlainText(
            "DOWN CTRL\nKEY C\nUP CTRL\nWAIT 0.5"
        )
        self.btn_adv = PrimaryPushButton("执行脚本")
        vb.addWidget(self.script_edit)
        vb.addWidget(self.btn_adv)
        layout.addWidget(adv_box)

        # 信号
        self.btn_refresh.clicked.connect(self.refresh_windows)
        self.btn_simple.clicked.connect(self.run_simple)
        self.btn_adv.clicked.connect(self.run_advanced)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_reset.clicked.connect(self.reset_task)

        layout.addStretch()
        return tab

    def init_logs_tab(self):
        from PyQt5.QtWidgets import QWidget, QVBoxLayout

        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setAcceptRichText(True)
        self.log_output.setPlaceholderText("日志输出...")
        self.log_output.setStyleSheet("""
        QTextEdit {
            background: transparent;
            border: none;
        }
        """)
        layout.addWidget(self.log_output)
        return tab

    # ---------------- 业务 ----------------

    def refresh_windows(self):
        self.window_list.clear()
        self.windows = list_windows()
        for _, title in self.windows:
            self.window_list.addItem(title)
        self.logger.info(f"刷新窗口列表，找到 {len(self.windows)} 个窗口")

    def current_hwnd(self):
        idx = self.window_list.currentIndex()
        return self.windows[idx][0] if idx >= 0 else None

    def run_simple(self):
        hwnd = self.current_hwnd()
        interval = self.speed_spin.value() / 1000
        keys = self.key_capture.text().split('+')

        if not hwnd or not keys:
            self.log_error("请选择窗口和按键组合")
            return

        self.stop_event.clear()
        self.pause_event.set()

        self.running_thread = threading.Thread(
            target=self.run_simple_thread,
            args=(hwnd, keys, interval),
            daemon=True
        )
        self.running_thread.start()
        self.logger.info(f"开始简单模式：窗口句柄={hwnd}，按键={keys}，间隔={interval}s")
        self.update_ui_running()

    def run_simple_thread(self, hwnd, keys, interval):
        try:
            while not self.stop_event.is_set():
                self.pause_event.wait()
                for k in keys:
                    if k in KEY_MAP:
                        key_down(hwnd, KEY_MAP[k])
                time.sleep(0.05)
                for k in reversed(keys):
                    if k in KEY_MAP:
                        key_up(hwnd, KEY_MAP[k])
                self.stop_event.wait(interval)
        except Exception as e:
            self.logger.error(f"简单模式执行异常：{e}")
        finally:
            self.update_ui_idle()

    def run_advanced(self):
        hwnd = self.current_hwnd()
        script = self.script_edit.toPlainText()

        self.stop_event.clear()
        self.pause_event.set()

        self.engine = ScriptEngine(hwnd, self.pause_event, self.stop_event, logger=self.logger.log)

        self.running_thread = threading.Thread(
            target=self.run_advanced_thread,
            args=(script,),
            daemon=True,
        )
        self.running_thread.start()
        self.logger.info(f"开始执行高级脚本：窗口句柄={hwnd}")
        self.update_ui_running()

    def run_advanced_thread(self, script):
        try:
            self.engine.run(script)
        except Exception as e:
            self.logger.error(f"脚本执行异常：{e}")
        finally:
            self.update_ui_idle()

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.btn_pause.setText("继续")
        else:
            self.pause_event.set()
            self.btn_pause.setText("暂停")

    def reset_task(self):
        self.stop_event.set()
        self.pause_event.set()
        self.update_ui_idle()

    # ---------------- UI 状态 ----------------

    def update_ui_running(self):
        self.status_label.setText("状态：Running")
        self.btn_pause.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.btn_simple.setEnabled(False)
        self.btn_adv.setEnabled(False)

    def update_ui_idle(self):
        self.status_label.setText("状态：Idle")
        self.btn_pause.setEnabled(False)
        self.btn_reset.setEnabled(False)
        self.btn_simple.setEnabled(True)
        self.btn_adv.setEnabled(True)

    # ---------------- 日志 ----------------
    def _gui_log_handler(self, level, text):
        if level < self.current_log_level:
            return

        color = LOG_COLORS.get(level, "#FFFFFF")
        html = f'<span style="color:{color}; font-family:Consolas;">{text}</span>'

        self.ui_log_signal.emit(html)

    @QtCore.pyqtSlot(str)
    def _append_log_ui(self, html: str):
        if not hasattr(self, "log_output"):
            return

        self.log_output.append(html)

        # 自动滚动到底部（可选，但推荐）
        bar = self.log_output.verticalScrollBar()
        bar.setValue(bar.maximum())

    # ---------------- 热键 ----------------

    def on_global_key(self, key):
        if key in (self.hotkey_pause, self.hotkey_resume):
            QtCore.QMetaObject.invokeMethod(
                self,
                "toggle_pause",
                QtCore.Qt.QueuedConnection
            )


class CustomKeyCapture(LineEdit):
    """
    Fluent 风格 · 专业组合键捕获控件
    - 使用 Qt.Key + modifiers
    - 不依赖 event.text()
    - 适用于全局热键 / GUI 配置
    """

    # 修饰键顺序
    KEY_ORDER = {
        'CTRL': 0,
        'SHIFT': 1,
        'ALT': 2,
        'META': 3
    }

    # Qt Key → 显示名
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

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setPlaceholderText("按下组合键")
        self._keys = set()

    def focusInEvent(self, event):
        """获得焦点时清空"""
        self._keys.clear()
        self.setText('')
        super().focusInEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        self._keys.clear()

        # ===== 修饰键 =====
        mods = event.modifiers()
        if mods & QtCore.Qt.ControlModifier:
            self._keys.add('CTRL')
        if mods & QtCore.Qt.ShiftModifier:
            self._keys.add('SHIFT')
        if mods & QtCore.Qt.AltModifier:
            self._keys.add('ALT')
        if mods & QtCore.Qt.MetaModifier:
            self._keys.add('META')

        # ===== 主键 =====
        key = event.key()

        # 忽略纯修饰键（避免只显示 CTRL）
        if key in (
            QtCore.Qt.Key_Control,
            QtCore.Qt.Key_Shift,
            QtCore.Qt.Key_Alt,
            QtCore.Qt.Key_Meta,
        ):
            event.accept()
            return

        if key in self.QT_KEY_MAP:
            self._keys.add(self.QT_KEY_MAP[key])

        elif QtCore.Qt.Key_A <= key <= QtCore.Qt.Key_Z:
            self._keys.add(chr(key))

        elif QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
            self._keys.add(chr(key))

        elif QtCore.Qt.Key_F1 <= key <= QtCore.Qt.Key_F12:
            self._keys.add(f'F{key - QtCore.Qt.Key_F1 + 1}')

        # ===== 排序 & 显示 =====
        ordered = sorted(
            self._keys,
            key=lambda k: self.KEY_ORDER.get(k, 100)
        )

        self.setText('+'.join(ordered))
        event.accept()

    def keyReleaseEvent(self, event):
        event.accept()

    def keySequence(self) -> str:
        """获取当前组合键字符串"""
        return self.text()