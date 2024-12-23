import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal as Signal

class HoverableCurveItem(pg.PlotCurveItem):
    sigHovered = Signal(object, object)
    sigNotHovered = Signal(object, object)

    def __init__(self, hoverable=True, *args, **kwargs):
        super(HoverableCurveItem, self).__init__(*args, **kwargs)
        self.xVals = None
        self.hoverable = hoverable
        self.setAcceptHoverEvents(True)

        self.basePen = self.opts['pen']
        #self.hoverPen = pg.mkPen(self.basePen.color(), width=3)
        self.scatterPen = pg.mkPen(self.basePen.color(), width=2)

        self.scatterItem = pg.ScatterPlotItem(pen=self.scatterPen, brush=self.basePen.color(), name=self.name())
        self.scatterItem.setParentItem(self)
        self.scatterItem.setVisible(False)
        self.scatterTick = 0

    def xValues(self, values):
        self.xVals = values

    def hideDot(self):
        self.scatterItem.setVisible(False)

    def hoverEvent(self, ev):
        if self.hoverable:
            if ev.exit == True:
                return
            if self.mouseShape().contains(ev.pos()):
                #self.setPen(self.hoverPen)
                x = int(round(ev.pos()[0]))
                y = self.yData[x]

                self.scatterItem.setData([x], [y])
                self.scatterItem.setVisible(True)

                self.scatterTick = x

                if self.xVals != None:
                    x = self.xVals[x]

                self.setToolTip(f"{self.name()}\n{x}: {y}")
                self.sigHovered.emit(self, ev)
            else:
                self.setToolTip('')
                #self.setPen(self.basePen)
                self.scatterItem.setVisible(False)
                self.sigNotHovered.emit(self, ev)
