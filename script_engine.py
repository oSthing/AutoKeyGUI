import time
from key_sender import key_down, key_up, tap_key
from keymap import KEY_MAP
from log_system import LogLevel


class ScriptEngine:
    def __init__(self, hwnd, pause_event, stop_event, speed=1.0,logger=None):
        self.hwnd = hwnd
        self.pause_event = pause_event
        self.stop_event = stop_event
        self.speed = speed
        self.logger = logger
    # 日志记录
    def log(self, level, msg):
        if self.logger:
            self.logger(level, msg)

    # 公共入口
    def run(self, script: str):
        lines = [l.strip() for l in script.splitlines() if l.strip()]
        self._exec(lines)

    # 线程控制
    def _check(self):
        self.pause_event.wait()
        if self.stop_event.is_set():
            raise RuntimeError("脚本被停止")

    def _wait(self, t):
        self.pause_event.wait()
        self.stop_event.wait(t / 1000)

    # 脚本执行
    def _exec(self, lines):
        i = 0
        while i < len(lines):
            self._check()

            parts = lines[i].split()
            cmd = parts[0].upper()

            # 单次按键
            if cmd == 'KEY':
                key = parts[1].upper()
                if key in KEY_MAP:
                    tap_key(self.hwnd, KEY_MAP[key])
                    self.logger(LogLevel.DEBUG, f"Tapped key: {key}")

            # 按下
            elif cmd == 'DOWN':
                key = parts[1].upper()
                if key in KEY_MAP:
                    key_down(self.hwnd, KEY_MAP[key])
                    self.logger(LogLevel.DEBUG, f"Key down: {key}")

            # 松开
            elif cmd == 'UP':
                key = parts[1].upper()
                if key in KEY_MAP:
                    key_up(self.hwnd, KEY_MAP[key])
                    self.logger(LogLevel.DEBUG, f"Key up: {key}")

            # 等待
            elif cmd == 'WAIT':
                t = float(parts[1]) / self.speed
                self._wait(t)
                self.logger(LogLevel.DEBUG, f"Waited for: {t} ms")

            # 循环
            elif cmd == 'LOOP':
                count = int(parts[1])
                block = []

                i += 1
                while i < len(lines) and not lines[i].startswith('}'):
                    block.append(lines[i])
                    i += 1
                n=0
                if count == 0:  # 无限循环
                    while not self.stop_event.is_set():
                        self._exec(block)
                        n+=1
                        self.logger(LogLevel.DEBUG, f"Completed infinite loop iteration: {n}")
                else:
                    for j in range(count):
                        if self.stop_event.is_set():
                            break
                        self._exec(block)
                        self.logger(LogLevel.DEBUG, f"Completed loop iteration: {j + 1}")


            #  未知指令
            else:

                raise ValueError(f"未知指令: {lines[i]}")

            i += 1
