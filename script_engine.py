import time
from key_sender import key_down, key_up, tap_key
from keymap import KEY_MAP

class ScriptEngine:
    def __init__(self, hwnd, speed=1.0):
        self.hwnd = hwnd
        self.speed = speed
        self.running = False

    def run(self, script: str):
        self.running = True
        lines = [l.strip() for l in script.splitlines() if l.strip()]
        self._exec(lines)

    def stop(self):
        self.running = False

    def _exec(self, lines):
        i = 0
        while i < len(lines) and self.running:
            parts = lines[i].split()
            cmd = parts[0]

            if cmd == 'KEY':
                key = parts[1].upper()
                if key in KEY_MAP:
                    tap_key(self.hwnd, KEY_MAP[key])

            elif cmd == 'DOWN':
                key = parts[1].upper()
                if key in KEY_MAP:
                    key_down(self.hwnd, KEY_MAP[key])

            elif cmd == 'UP':
                key = parts[1].upper()
                if key in KEY_MAP:
                    key_up(self.hwnd, KEY_MAP[key])

            elif cmd == 'WAIT':
                t = float(parts[1]) / self.speed
                time.sleep(t)

            elif cmd == 'LOOP':
                count = int(parts[1])
                block = []
                i += 1
                while not lines[i].startswith('}'):
                    block.append(lines[i])
                    i += 1
                if count == 0:  # 无限循环
                    while self.running:
                        self._exec(block)
                else:
                    for _ in range(count):
                        if not self.running:
                            break
                        self._exec(block)

            i += 1