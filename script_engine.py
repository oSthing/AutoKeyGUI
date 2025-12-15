import time
from key_sender import send_key
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
            line = lines[i]


            if line.startswith('KEY'):
                key = line.split()[1].upper()
                if key in KEY_MAP:
                    send_key(self.hwnd, KEY_MAP[key])
            elif line.startswith('WAIT'):
                t = float(line.split()[1]) / self.speed
                time.sleep(t)
            elif line.startswith('LOOP'):
                count = int(line.split()[1])
                block = []
                i += 1
                while not lines[i].startswith('}'):
                    block.append(lines[i])
                    i += 1
                for _ in range(count):
                    self._exec(block)
        i += 1