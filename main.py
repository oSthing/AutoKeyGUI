import sys
from gui import AutoKeyGUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from qfluentwidgets import FluentTranslator, setTheme, Theme


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # DPI 适配（推荐）
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Fluent 主题（亮 / 暗）
    setTheme(Theme.DARK)  # 或 Theme.LIGHT

    # 国际化（可选）
    translator = FluentTranslator()
    app.installTranslator(translator)

    w = AutoKeyGUI()
    w.show()

    sys.exit(app.exec_())
