from PyQt6.QtCore import (
        QObject,
        QThreadPool,
        QRunnable,
        pyqtSignal as Signal
)

from .context import Context
from .dialogs import ErrorDialog, AlertDialog

class FileMonitor:
    def __init__(self, context: Context):
        self.context = context
        context.monitor = self
        self.file = context.monitor_cmd
        self.threadpool = QThreadPool()
        self.reader = None

    def update(self):
        if self.reader == None:
            self.reader = Reader(self.file)
            self.reader.signal.data.connect(self.context.mainwindow.update_data)
            self.reader.signal.error.connect(self.error)
            self.reader.signal.done.connect(self.done)
            self.threadpool.start(self.reader)

    def error(self, exc, value):
        print(f"Monitor error: {exc}: {value}", file=sys.stderr)
        err = ErrorDialog()
        err.setText(f"Monitor error: {exc}")
        err.setInformativeText(value)
        err.show()
        self.context.app.exit(1)

    def done(self):
        if self.context.fatal_error:
            return
        self.context.timer.stop()
        d = AlertDialog()
        d.setText("File closed")
        d.setInformativeText("The file has signaled that all data has been consumed.")
        d.show()

    def stop(self):
        pass

class ReaderSignals(QObject):
    data = Signal(object)
    error = Signal(object, object)
    done = Signal()

class Reader(QRunnable):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.file = args[0]
        self.signal = ReaderSignals()

    def run(self):
        file = self.file
        try:
            while line := file.readline():
                data = line.strip().split(maxsplit=1)
                self.signal.data.emit(data)
        except:
            exc, value = sys.exc_info()[:2]
            self.signal.error.emit(exc, value)
        finally:
            self.signal.done.emit()
