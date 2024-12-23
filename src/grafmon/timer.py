import time

import pyqtgraph as pg
from PyQt6 import QtCore

from .context            import Context
from .hoverablecurveitem import HoverableCurveItem
from .monitor            import Monitor

class Timer:
    def __init__(self, context: Context, *args, **kwargs):
        self.context = context
        self.context.timer = self
        self.timer = QtCore.QTimer()
        self.timer.setInterval(context.refresh_rate)
        self.timer.timeout.connect(self.tick)
        self.ticks = 0
        self.monitor = Monitor(context)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def tick(self):
        self.ticks += 1
        self.context.now = time.time()
        self.monitor.start()

    def update_interval(self):
        self.timer.setInterval(self.context.refresh_rate)
