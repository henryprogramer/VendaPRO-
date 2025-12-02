import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import signal

class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            try:
                os.kill(self.process.pid, signal.SIGTERM)
            except:
                pass

        print("🔄 Iniciando aplicação...")
        self.process = subprocess.Popen(["python3", "-m", "main"])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("♻️ Código alterado → restart automático")
            self.start_app()

if __name__ == "__main__":
    handler = RestartHandler()

    observer = Observer()
    observer.schedule(handler, ".", recursive=True)
    observer.start()

    print("👀 Modo DEV ON — monitorando alterações em tempo real...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if handler.process:
            handler.process.terminate()

    observer.join()
