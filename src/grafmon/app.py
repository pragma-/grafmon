import sys

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .context     import Context, MonitorType
from .filemonitor import FileMonitor
from .mainwindow  import MainWindow
from .monitor     import Monitor
from .timer       import Timer

def exec():
    context = Context()
    context.initFromFile(str(Path.home() / '.grafmon.conf'))
    context.initFromArgs()

    if context.refresh_rate < 100:
        print("Error: Refresh rate cannot be less than 100 ms.", file=sys.stderr)
        sys.exit(1)

    if context.monitor_type == MonitorType.FILE:
        context.monitor = FileMonitor(context)
    else:
        context.monitor = Monitor(context)

    context.app = QApplication(sys.argv)
    w = MainWindow(context)
    w.show()
    t = Timer(context)
    # do a manual tick to show initial data immediately
    t.tick()
    t.start()
    sys.exit(context.app.exec())

if __name__ == '__main__':
    exec()
