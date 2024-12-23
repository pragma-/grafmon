import sys

from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .context    import Context
from .mainwindow import MainWindow
from .timer      import Timer

def exec():
    context = Context()
    context.initFromFile(str(Path.home() / '.grafmon.conf'))
    context.initFromArgs()

    if context.refresh_rate < 100:
        print("Error: Refresh rate cannot be less than 100 ms.", file=sys.stderr)
        sys.exit(1)

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
