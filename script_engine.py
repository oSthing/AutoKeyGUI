import time
from key_sender import key_down, key_up, tap_key
from keymap import KEY_MAP


class ScriptEngine:
    def __init__(
        self,
        hwnd,
        pause_condition,
        is_paused_cb,
        stop_cb,
        speed=1.0
    ):
        """
        :param hwnd: 目标窗口句柄
        :param pause_condition: threading.Condition（来自主窗口）
        :param is_paused_cb: 回调，返回当前是否暂停
        :param stop_cb: 回调，返回是否应停止
        :param speed: 脚本速度倍率
        """
        self.hwnd = hwnd
        self.speed = speed
        self.pause_condition = pause_condition
        self.is_paused = is_paused_cb
        self.should_stop = stop_cb

    # 公共入口
    def run(self, script: str):
        lines = [l.strip() for l in script.splitlines() if l.strip()]
        self._exec(lines)

    # 线程控制
    def _check_control(self):
        # 停止优先
        if self.should_stop():
            raise RuntimeError("脚本被停止")

        # 暂停
        with self.pause_condition:
            while self.is_paused() and not self.should_stop():
                self.pause_condition.wait()

    def _wait(self, seconds: float):
        end = time.time() + seconds
        while time.time() < end:
            self._check_control()
            time.sleep(0.05)

    # 脚本执行
    def _exec(self, lines):
        i = 0
        while i < len(lines):
            self._check_control()

            parts = lines[i].split()
            cmd = parts[0].upper()

            # 单次按键
            if cmd == 'KEY':
                key = parts[1].upper()
                if key in KEY_MAP:
                    tap_key(self.hwnd, KEY_MAP[key])

            # 按下
            elif cmd == 'DOWN':
                key = parts[1].upper()
                if key in KEY_MAP:
                    key_down(self.hwnd, KEY_MAP[key])

            # 松开
            elif cmd == 'UP':
                key = parts[1].upper()
                if key in KEY_MAP:
                    key_up(self.hwnd, KEY_MAP[key])

            # 等待
            elif cmd == 'WAIT':
                t = float(parts[1]) / self.speed
                self._wait(t)

            # 循环
            elif cmd == 'LOOP':
                count = int(parts[1])
                block = []

                i += 1
                while i < len(lines) and not lines[i].startswith('}'):
                    block.append(lines[i])
                    i += 1

                if count == 0:  # 无限循环
                    while not self.should_stop():
                        self._exec(block)
                else:
                    for _ in range(count):
                        if self.should_stop():
                            break
                        self._exec(block)

            #  未知指令 
            else:
                raise ValueError(f"未知指令: {lines[i]}")

            i += 1
