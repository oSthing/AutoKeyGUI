import win32gui


def list_windows():
    result = []

    def enum(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                result.append((hwnd, title))

    win32gui.EnumWindows(enum, None)
    return result