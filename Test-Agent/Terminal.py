# Terminal.py
# Heart & Voice of Sunday
# Extend: TTS, emotion-based voice output

import sys
import threading
import time
import psutil
import random
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QProgressBar, QTabWidget, QTextEdit, QMessageBox, QPushButton
)

from PySide6.QtCore import (
    Qt, Signal, QObject, QTimer,
    QRectF, QPointF, QLineF, QSize
)

from PySide6.QtGui import (
    QPainter, QPen, QColor, QFont,
    QPainterPath, QIcon
)

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar,
    QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QObject , QTimer
import os
import json
import re
from collections import deque
import sys
sys.stdout.reconfigure(line_buffering=True)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
import math
import random
from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QIcon
import sounddevice as sd
import numpy as np
import core
import Memory
import nervous_system
import self_repair
import heart




# =========================
# SIGNALS
# =========================
class MonitorSignal(QObject):
    new_data = Signal(dict)
    log_line = Signal(str)
    comm_line = Signal(str)  # Kommunikation Logs

def start_llm_crawler_process(monitor_signal):
    llm_path = os.path.join(os.path.dirname(__file__), "llm.py")

    process = subprocess.Popen(
        [sys.executable, "-u", llm_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def read_stream(stream):
        for line in iter(stream.readline, ""):
            line = line.rstrip()
            if line:
                monitor_signal.comm_line.emit(line)

    threading.Thread(target=read_stream, args=(process.stdout,), daemon=True).start()
    threading.Thread(target=read_stream, args=(process.stderr,), daemon=True).start()

    return process

def start_self_repair_process(monitor_signal):
    path = os.path.join(os.path.dirname(__file__), "self_repair.py")

    process = subprocess.Popen(
        [sys.executable, "-u", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    def read_stream(stream):
        for line in iter(stream.readline, ""):
            line = line.rstrip()
            if line:
                monitor_signal.log_line.emit(line)

    threading.Thread(target=read_stream, args=(process.stdout,), daemon=True).start()
    threading.Thread(target=read_stream, args=(process.stderr,), daemon=True).start()

    return process


# =========================
# SELBSTÜBERWACHUNG
# =========================
def self_monitor(monitor_signal, stop_flag):
    while not stop_flag["stop"]:
        p = psutil.Process()
        cpu = psutil.cpu_percent(interval=0.5)
        mem = p.memory_info().rss / (1024 * 1024)
        threads = p.num_threads()
        disk = psutil.disk_usage(os.getcwd()).percent
        energy = random.uniform(1, 5)

        monitor_signal.new_data.emit({
            "CPU": cpu,
            "RAM": mem,
            "Threads": threads,
            "Disk": disk,
            "Energy": energy
        })

        time.sleep(1)


# =========================
# LLM CRAWLER PROCESS
# =========================



from PySide6.QtWidgets import (
    QWidget, QMessageBox, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer


# =========================
# 🧠 BODY MODULE NODE
# =========================
class BodyModuleNode:
    def __init__(self, module, pos, radius):
        self.module = module
        self.name = getattr(module, "NAME", module.__class__.__name__)
        self.pos = QPointF(*pos)
        self.radius = radius

        self.status = {}
        self.errors = []
        self.health = 1.0

    def update_status(self):
        self.errors.clear()

        try:
            if not hasattr(self.module, "status"):
                raise RuntimeError("Module has no status() function")

            data = self.module.status()
            if not isinstance(data, dict):
                raise ValueError("status() must return dict")

            self.status = data
            self.health = float(data.get("health", 1.0))

            if self.health < 0.7:
                self.errors.append("Health degraded")

            if self.health < 0.4:
                self.errors.append("Health critical")

        except Exception as e:
            self.health = 0.0
            self.errors.append(str(e))

    def contains(self, point):
        dx = point.x() - self.pos.x()
        dy = point.y() - self.pos.y()
        return dx * dx + dy * dy <= self.radius * self.radius


# =========================
# 🧍 BODY TAB
# =========================
class BodyTab(QWidget):
    def __init__(self, modules):
        super().__init__()
        self.setMinimumSize(900, 700)
        self.sleep_mode = False

        # -------- VALIDATION --------
        required = ["core", "memory", "nervous", "terminal", "self_repair"]
        for r in required:
            if r not in modules:
                raise RuntimeError(f"BodyTab: missing module '{r}'")

        # -------- MODULE NODES --------
        self.nodes = [
            BodyModuleNode(modules["core"],        (350, 140), 45),
            BodyModuleNode(modules["memory"],      (220, 300), 35),
            BodyModuleNode(modules["nervous"],     (480, 300), 35),
            BodyModuleNode(modules["terminal"],    (350, 520), 45),
            BodyModuleNode(modules["self_repair"], (520, 520), 30),
        ]

        self.connections = [
            (0, 1), (0, 2), (0, 3),
            (3, 4), (2, 0)
        ]

        # =========================
        # 📐 LAYOUT (RESPONSIVE)
        # =========================
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.setLayout(root)

        # ---- LEFT: BODY VIEW ----
        self.canvas = BodyCanvas(self)
        root.addWidget(self.canvas, 3)

        # ---- RIGHT: CONSOLE ----
        side = QVBoxLayout()
        root.addLayout(side, 1)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMinimumHeight(200)
        self.log_console.setStyleSheet(
            "background:#0f0f0f;color:#8fff8f;font-family:Consolas;"
        )

        side.addWidget(self.log_console)

        btns = QHBoxLayout()
        side.addLayout(btns)

        self.btn_check = QPushButton("System Check")
        self.btn_repair = QPushButton("Self Repair")

        btns.addWidget(self.btn_check)
        btns.addWidget(self.btn_repair)

        self.btn_sleep = QPushButton("Sleep Mode")
        side.addWidget(self.btn_sleep)

        # -------- SIGNALS --------
        self.btn_check.clicked.connect(self.run_check)
        self.btn_repair.clicked.connect(self.run_repair)
        self.btn_sleep.clicked.connect(self.toggle_sleep)

        # -------- TIMER --------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(1000)

        self.log("Body system initialized.")


    # =========================
    # 🔄 STATUS UPDATE
    # =========================
    def refresh_status(self):
        if self.sleep_mode:
            return

        for node in self.nodes:
            node.update_status()

            for err in node.errors:
                self.log(f"[{node.name.upper()}] {err}")

        self.canvas.update()

        # =========================
    # 📡 MONITOR SIGNAL INPUT
    # =========================
    def update_monitor(self, data: dict):
        """
        Receives live system data from self_monitor thread.
        This represents the physical body state.
        """

        # --- Sanity check ---
        if not isinstance(data, dict):
            self.log("[MONITOR] Invalid monitor payload")
            return

        # --- Store raw body state ---
        self.body_state = data

        # --- Log important anomalies ---
        cpu = data.get("CPU", 0)
        ram = data.get("RAM", 0)
        disk = data.get("Disk", 0)

        if cpu > 90:
            self.log(f"[BODY] ⚠ High CPU load: {cpu:.1f}%")

        if ram > 1500:  # MB, anpassbar
            self.log(f"[BODY] ⚠ High RAM usage: {ram:.1f} MB")

        if disk > 90:
            self.log(f"[BODY] ⚠ Disk nearly full: {disk:.1f}%")

        # --- Map physical state to nodes (optional, aber stark) ---
        for node in self.nodes:
            if node.name.lower() in ("terminal", "heart"):
                # Herz reagiert auf Energie
                node.health *= max(0.3, min(1.0, data.get("Energy", 1) / 5))

        # Trigger repaint
        self.update()

    # =========================
    # 🧪 ACTIONS
    # =========================
    def run_check(self):
        self.log("Running full diagnostic sweep...")
        for node in self.nodes:
            node.update_status()

        overall = self.calculate_global_health()
        self.log(f"System health: {overall:.2f}")

    def run_repair(self):
        self.log("Self-repair engaged")

        # Visuelles Feedback
        for node in self.nodes:
            if node.name.lower() == "selfrepair":
                node.health = 0.3

        self.canvas.update()

        # Prozess starten
        self.repair_process = start_self_repair_process(self.parent().monitor_signal)

        self.log("Self-repair process started")


    def toggle_sleep(self):
        self.sleep_mode = not self.sleep_mode
        self.log("Sleep mode ON" if self.sleep_mode else "Sleep mode OFF")


    # =========================
    # 🧠 HEALTH LOGIC
    # =========================
    def calculate_global_health(self):
        if not self.nodes:
            return 0.0
        return sum(n.health for n in self.nodes) / len(self.nodes)


    # =========================
    # 🖥️ LOG
    # =========================
    def log(self, text):
        self.log_console.append(text)


    # =========================
    # 🎨 DRAW
    # =========================
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1b1b1b"))

        self.draw_connections(painter)
        self.draw_nodes(painter)

    def draw_connections(self, painter):
        painter.setPen(QPen(QColor("#555"), 2))
        for a, b in self.connections:
            painter.drawLine(self.nodes[a].pos, self.nodes[b].pos)

    def draw_nodes(self, painter):
        for node in self.nodes:
            health = max(0.0, min(1.0, node.health))
            color = QColor(
                int(255 * (1 - health)),
                int(200 * health),
                80
            )

            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(color)
            painter.drawEllipse(node.pos, node.radius, node.radius)

            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(
                QRectF(
                    node.pos.x() - node.radius,
                    node.pos.y() - 10,
                    node.radius * 2,
                    20
                ),
                Qt.AlignCenter,
                node.name
            )


    # =========================
    # 🖱️ CLICK
    # =========================
    def mousePressEvent(self, event):
        p = event.position().toPoint()
        for node in self.nodes:
            if node.contains(p):
                self.open_node(node)
                return

    def open_node(self, node):
        msg = QMessageBox(self)
        msg.setWindowTitle(node.name)

        text = f"Health: {node.health:.2f}\n\nStatus:\n{node.status}"
        if node.errors:
            text += "\n\nErrors:\n" + "\n".join(node.errors)

        msg.setText(text)
        msg.exec()

# =========================
# 🎨 BODY CANVAS (RENDER)
# =========================
class BodyCanvas(QWidget):
    def __init__(self, body_tab):
        super().__init__()
        self.body_tab = body_tab
        self.setMinimumSize(500, 500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1b1b1b"))

        self.draw_connections(painter)
        self.draw_nodes(painter)

    def draw_connections(self, painter):
        painter.setPen(QPen(QColor("#555"), 2))
        for a, b in self.body_tab.connections:
            na = self.body_tab.nodes[a]
            nb = self.body_tab.nodes[b]
            painter.drawLine(na.pos, nb.pos)

    def draw_nodes(self, painter):
        for node in self.body_tab.nodes:
            health = max(0.0, min(1.0, node.health))
            color = QColor(
                int(255 * (1 - health)),
                int(200 * health),
                80
            )

            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(color)
            painter.drawEllipse(node.pos, node.radius, node.radius)

            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(
                QRectF(
                    node.pos.x() - node.radius,
                    node.pos.y() - 10,
                    node.radius * 2,
                    20
                ),
                Qt.AlignCenter,
                node.name
            )



# =========================
# KOMMUNIKATIONS TAB (LIVE LLM LOG)
# =========================
class ChatInput(QTextEdit):
        send_signal = Signal(str)

        def keyPressEvent(self, event):
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.NoModifier:
                text = self.toPlainText().strip()
                if text:
                    self.send_signal.emit(text)
                    self.clear()
                event.accept()
            else:
                super().keyPressEvent(event)
                
class CommTab(QWidget):
    def __init__(self, send_callback):
        super().__init__()
        self.send_callback = send_callback

        self.layout = QVBoxLayout()

        self.comm_view = QTextEdit()
        self.comm_view.setReadOnly(True)

        self.input_box = ChatInput()
        self.input_box.setFixedHeight(80)
        self.input_box.send_signal.connect(self.on_send)

        self.layout.addWidget(self.comm_view)
        self.layout.addWidget(QLabel("Eingabe an LLM:"))
        self.layout.addWidget(self.input_box)

        self.setLayout(self.layout)

    def on_send(self, text: str):
        self.comm_view.append(f">>> USER:\n{text}")
        self.send_callback(text)

    def append_comm(self, line: str):
        line = line.strip()
        if not line:
            return

        # nur JSON aus llm.py anzeigen
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                return

            t = data.get("type")
            if t == "chat":
                self.comm_view.append(f">>> LLM:\n{data.get('payload','')}")
            elif t == "status":
                # optional: Status NICHT in Chat anzeigen
                pass
            else:
                # alles andere ignorieren
                pass

            self.comm_view.verticalScrollBar().setValue(
                self.comm_view.verticalScrollBar().maximum()
            )
            return

        # alles Nicht-JSON ignorieren
        return



import sys, math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QIcon
import sounddevice as sd
import numpy as np

class VoiceTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.bubble = VoiceBubbleWidget()
        self.bubble.setMinimumHeight(300)

        self.mic_button = QPushButton()
        self.mic_button.setCheckable(True)
        self.mic_button.setChecked(True)
        self.mic_button.setIconSize(QSize(32, 32))
        self.mic_button.setToolTip("Microphone On/Off")
        self.mic_button.clicked.connect(self.toggle_mic)
        self.set_mic_icon(True)

        layout.addWidget(self.bubble)
        layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        self.stream = None
        self.is_recording = True
        self.start_recording()

    def toggle_mic(self, state):
        self.set_mic_icon(state)
        self.is_recording = state
        if state:
            self.start_recording()
        else:
            self.stop_recording()
            self.bubble.set_mode("idle")
            self.bubble.set_amplitude(0.0)

    def set_mic_icon(self, on):
        icon = "icons/mic_on.svg" if on else "icons/mic_off.svg"
        self.mic_button.setIcon(QIcon(icon))

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        volume = np.linalg.norm(indata) / np.sqrt(len(indata))
        # Sanft glätten (gleitender Mittelwert)
        self.bubble.amplitude = self.bubble.amplitude * 0.7 + volume * 0.3
        self.bubble.set_mode("speaking" if volume > 0.02 else "idle")

    def start_recording(self):
        if self.stream is None and self.is_recording:
            self.stream = sd.InputStream(callback=self.audio_callback, channels=1, samplerate=44100)
            self.stream.start()

    def stop_recording(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None


    def get_microphone_level(duration=0.1, fs=44100):
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()
        amplitude = np.linalg.norm(recording) / len(recording)
        return amplitude



class VoiceBubbleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0.0
        self.amplitude = 0.0
        self.mode = "idle"  # idle | thinking | speaking
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

    def set_amplitude(self, value: float):
        self.amplitude = value

    def set_mode(self, mode: str):
        self.mode = mode

    def animate(self):
        self.phase += 0.03  # langsamer gleitender Effekt
        # sanfte Übergänge bei idle -> speaking
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        lines = 6
        base_radius = min(w, h) * 0.25

        for i in range(lines):
            path = QPainterPath()
            angle_offset = (i / lines) * math.pi * 2
            points = 64

            for p in range(points):
                t = p / points * math.pi * 2
                wave = math.sin(t * 3 + self.phase + angle_offset)

                # Smooth deform: je nach mode
                if self.mode == "speaking":
                    deform = self.amplitude * 50  # Lautstärke beeinflusst Radius
                elif self.mode == "thinking":
                    deform = 6 + math.sin(self.phase * 2 + i) * 4
                else:
                    deform = 2

                r = base_radius + wave * deform
                x = cx + math.cos(t) * r
                y = cy + math.sin(t) * r

                if p == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)

            path.closeSubpath()

            # Farbe je Mode
            if self.mode == "speaking":
                pen = QPen(QColor(0, 200, 255, 200))
            elif self.mode == "thinking":
                pen = QPen(QColor(255, 200, 0, 180))
            else:
                pen = QPen(QColor(120, 180, 255, 150))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawPath(path)



class SoulTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.state_view = QTextEdit()
        self.state_view.setReadOnly(True)

        self.memory_view = QTextEdit()
        self.memory_view.setReadOnly(True)

        self.layout.addWidget(QLabel("🧠 Innerer Zustand"))
        self.layout.addWidget(self.state_view)
        self.layout.addWidget(QLabel("🧬 Gedächtnis (Auszug)"))
        self.layout.addWidget(self.memory_view)

        self.setLayout(self.layout)

        self.update_loop()

    def update_loop(self):
        self.load_state()
        self.load_memory()
        QTimer.singleShot(1500, self.update_loop)

    def load_state(self):
        try:
            with open("Storage/memory.json", "r") as f:
                self.state_view.setText(json.dumps(json.load(f), indent=2))
        except:
            self.state_view.setText("State unavailable")

    def load_memory(self):
        try:
            with open("Storage/Memory.json", "r") as f:
                mem = json.load(f)
                excerpt = mem.get("episodic", [])[-5:]
                self.memory_view.setText(json.dumps(excerpt, indent=2))
        except:
            self.memory_view.setText("Memory unavailable")



# =========================
# MAIN WINDOW
# =========================
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terminal & Intelligence Builder")
        self.resize(1000, 700)

        modules = {
            "core": core,                 # 🧠 Gehirn
            "memory": Memory,            # 🧬 Memory
            "nervous": nervous_system,   # ⚡ Nervensystem
            "terminal": heart,           # ❤️ Herz
            "self_repair": self_repair   # 🛠 Reparatur
        }


        # =========================
        # Stop-Flag & Signale zuerst
        # =========================
        self.stop_flag = {"stop": False}
        self.monitor_signal = MonitorSignal()

        # =========================
        # Tabs erstellen
        # =========================
        self.tabs = QTabWidget()
        self.monitor_tab = BodyTab(modules)
        
        self.comm_tab = CommTab(self.send_to_llm)


        self.tabs.addTab(self.monitor_tab, "Selbstmonitor")

        self.tabs.addTab(self.comm_tab, "Kommunikation Builder")
        self.voice_tab = VoiceTab()

        self.tabs.addTab(self.voice_tab, "Voice Mode")




        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # =========================
        # Signale verbinden
        # =========================
        self.monitor_signal.new_data.connect(self.monitor_tab.update_monitor)
        self.monitor_signal.comm_line.connect(self.comm_tab.append_comm)

        # =========================
        # Threads / Prozesse starten
        # =========================
        threading.Thread(target=self_monitor, args=(self.monitor_signal, self.stop_flag), daemon=True).start()
        self.llm_crawler_process = None
        QTimer.singleShot(300, self.start_llm_delayed)


        # =========================
        # Stylesheet
        # =========================
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; }
            QProgressBar { text-align: center; color: #d4d4d4; }
            QTextEdit { background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas; }
        """)

    def closeEvent(self, event):
        self.stop_flag["stop"] = True
        event.accept()

    def send_to_llm(self, text: str):
        if text.startswith("/"):
            self.handle_command(text)
            return
        proc = self.llm_crawler_process

        if not proc or not proc.stdin:
            self.comm_tab.append_comm("[ERROR] LLM Prozess nicht verfügbar")
            return

        try:
            proc.stdin.write(text + "\n")
            proc.stdin.flush()
        except BrokenPipeError:
            self.comm_tab.append_comm("[ERROR] LLM stdin geschlossen")
        except Exception as e:
            self.comm_tab.append_comm(f"[ERROR] stdin failed: {e}")

    def start_llm_delayed(self):
        self.comm_tab.append_comm("[SYSTEM] Starte LLM …")
        self.llm_crawler_process = start_llm_crawler_process(self.monitor_signal)

        if not self.llm_crawler_process:
            self.comm_tab.append_comm("[FATAL] LLM konnte nicht gestartet werden")



    def handle_command(self, cmd: str):
        if cmd == "/status":
            self.comm_tab.append_comm("[HEART] Status requested.")
            with open("self_state.json") as f:
                self.comm_tab.append_comm(f.read())

        elif cmd.startswith("/emotion"):
            _, emotion = cmd.split(" ", 1)
            with open("self_state.json", "r+") as f:
                state = json.load(f)
                state["emotion_state"] = emotion
                f.seek(0)
                json.dump(state, f, indent=2)
                f.truncate()
            self.comm_tab.append_comm(f"[HEART] Emotion set to {emotion}")

        elif cmd.startswith("/remember"):
            content = cmd.replace("/remember", "").strip()
            import Memory
            Memory.record_event(
                event_type="manual_memory",
                content=content,
                emotion="focus"
            )
            self.comm_tab.append_comm("[HEART] Memory stored.")

        else:
            self.comm_tab.append_comm("[HEART] Unknown command.")


# disk


# =========================
# START
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
