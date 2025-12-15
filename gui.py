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

        self.speed = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed.setRange(1, 300)
        self.speed.setValue(100)
        layout.addWidget(QtWidgets.QLabel('速度 (%)'))
        layout.addWidget(self.speed)

        box1 = QtWidgets.QGroupBox('简单脚本')
        b1 = QtWidgets.QHBoxLayout(box1)
        self.simple_key = QtWidgets.QLineEdit('A')
        self.simple_interval = QtWidgets.QDoubleSpinBox()
        self.simple_interval.setValue(0.5)
        self.btn_simple = QtWidgets.QPushButton('开始')
        b1.addWidget(self.simple_key)
        b1.addWidget(self.simple_interval)
        b1.addWidget(self.btn_simple)
        layout.addWidget(box1)

        box2 = QtWidgets.QGroupBox('高级脚本')
        b2 = QtWidgets.QVBoxLayout(box2)
        self.script_edit = QtWidgets.QPlainTextEdit(
            'KEY A\nWAIT 0.5\nLOOP 3 {\n  KEY ENTER\n  WAIT 0.2\n}')
        self.btn_adv = QtWidgets.QPushButton('执行脚本')
        b2.addWidget(self.script_edit)
        b2.addWidget(self.btn_adv)
        layout.addWidget(box2)

        self.btn_refresh.clicked.connect(self.refresh_windows)
        self.btn_simple.clicked.connect(self.run_simple)
        self.btn_adv.clicked.connect(self.run_advanced)

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
        speed = self.speed.value() / 100
        key = self.simple_key.text().upper()
        interval = self.simple_interval.value()
        threading.Thread(
            target=run_simple,
            args=(hwnd, key, interval, speed),
            daemon=True
        ).start()

    def run_advanced(self):
        hwnd = self.current_hwnd()
        speed = self.speed.value() / 100
        self.engine = ScriptEngine(hwnd, speed)
        script = self.script_edit.toPlainText()
        threading.Thread(
            target=self.engine.run,
            args=(script,),
            daemon=True
        ).start()