from PyQt6 import QtCore

from .context import Context
from .monitor import Monitor

class Timer:
    def __init__(self, context: Context, *args, **kwargs):
        self.context = context
        self.context.timer = self
        self.timer = QtCore.QTimer()
        self.timer.setInterval(context.refresh_rate)
        self.timer.timeout.connect(self.tick)
        self.ticks = 0

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def tick(self):
        self.context.mainwindow.zero_not_updated()
        self.ticks += 1
        self.context.update_tick()
        self.context.mainwindow.rgn.setRegion(
                (self.context.tick_index, self.context.tick_index)
        )
        self.context.monitor.update()

    def update_interval(self):
        self.timer.setInterval(self.context.refresh_rate)
