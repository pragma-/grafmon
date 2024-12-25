import shlex
import sys
import time

from PyQt6.QtCore import QProcess

import psutil as ps

from .context import Context, MonitorType
from .dialogs import ErrorDialog

class Monitor:
    def __init__(self, context: Context):
        self.context = context
        context.monitor = self
        self.process = None
        cmd = shlex.split(self.context.monitor_cmd)
        self.command = cmd.pop(0)
        self.args = cmd
        self.error_message = ''
        self.ignore_error = 0
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.started.connect(self.process_started)
        self.process.errorOccurred.connect(self.process_errored)
        self.process.finished.connect(self.process_finished)

    def update(self):
        if self.process.state() == QProcess.ProcessState.NotRunning:
            self.process.start(self.command, self.args)
        elif self.context.monitor_type != MonitorType.STREAM:
            print("Previous tick's monitor still running... skipping tick", file=sys.stderr)

    def stop(self):
        self.ignore_error = 1
        self.process.close()

    def handle_stdout(self):
        while self.process.canReadLine():
            line = self.process.readLine()
            line = bytes(line).decode("utf8")
            data = line.strip().split(maxsplit=1)
            try:
                pid, _ = data[1].split(maxsplit=1)
                pid = int(pid)
            except:
                pid = 0

            if pid not in self.ignore_pids:
                self.context.mainwindow.update_data(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        data = bytes(data).decode("utf8")
        self.error_message = data
        print(f"Stderr: {data!r}", file=sys.stderr)

    def process_started(self):
        pid = self.process.processId()
        self.ignore_pids = set()
        self.ignore_pids.add(pid)
        if self.context.monitor_type == MonitorType.BUILTIN:
            self.ignore_pids.add(pid + 1)
        # kludge to wait for child processes
        time.sleep(0.040)
        self.p = ps.Process(pid)
        self.children = self.p.children(recursive = True)
        for child in self.children:
            self.ignore_pids.add(child.pid)

    def process_errored(self, error):
        if self.ignore_error:
            return
        self.context.timer.stop()
        self.context.fatal_error = 1
        print(f"Monitor error: {error}: {self.process.errorString()}", file=sys.stderr)
        err = ErrorDialog()
        err.setText(f"Monitor error: {error}")
        err.setInformativeText(self.process.errorString())
        err.show()
        self.context.app.exit(1)

    def process_finished(self, exitcode):
        if exitcode != 0:
            if self.ignore_error:
                return
            self.context.timer.stop()
            self.context.fatal_error = 1
            err = ErrorDialog()
            err.setText("Monitor error")
            if len(self.error_message):
                err.setInformativeText(self.error_message)
            else:
                err.setInformativeText(f"Monitor exited with unsuccessful exit code {exitcode}.")
            err.show()
            self.context.app.exit(1)
