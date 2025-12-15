import threading
from PyQt5 import QtWidgets, QtCore
from window_manager import list_windows
from simple_runner import run_simple
from script_engine import ScriptEngine

class AutoKeyGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AutoKey GUI')
        self.resize(720, 520)
        self.windows = []
        self.engine = None
        self.init_ui()
        self.refresh_windows()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

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

        # 简单模式（组合键）
        box1 = QtWidgets.QGroupBox('简单模式（按下你真实键盘组合）')
        b1 = QtWidgets.QHBoxLayout(box1)
        self.key_capture = QtWidgets.QLineEdit()
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

    def keyPressEvent(self, event):
        key = event.text().upper()
        if key:
            self.captured_keys.append(key)
            self.key_capture.setText('+'.join(self.captured_keys))

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
        threading.Thread(
            target=run_simple,
            args=(hwnd, keys, interval),
            daemon=True
        ).start()

    def run_advanced(self):
        hwnd = self.current_hwnd()
        self.engine = ScriptEngine(hwnd)
        script = self.script_edit.toPlainText()
        threading.Thread(
            target=self.engine.run,
            args=(script,),
            daemon=True
        ).start()