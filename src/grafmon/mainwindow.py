import time

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import psutil as ps

from .context import Context
from .dialogs import ErrorDialog
from .hoverablecurveitem import HoverableCurveItem

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, context: Context, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.context = context
        self.context.mainwindow = self

        self.settings = QtCore.QSettings("pragmasoft", "grafmon")

        self.items = dict()
        self.item_last_update = dict()
        self.tree_items = dict()
        self.color_index = 0;
        self.selected_line = None

        self.create_window()
        self.create_x_axis()

    def create_window(self):
        self.cw = QtWidgets.QWidget()
        self.setCentralWidget(self.cw)
        self.setWindowTitle("grafmon")
        self.resize(1920, 512)

        self.menubar = QtWidgets.QMenuBar()
        self.menuHelp = QtWidgets.QMenu()
        self.menuHelp.setTitle("&Help")
        self.action_About = QtGui.QAction()
        self.action_About.setText("&About")
        self.action_About.triggered.connect(self.about)
        self.menuHelp.addAction(self.action_About)
        self.menubar.addAction(self.menuHelp.menuAction())
        self.setMenuBar(self.menubar)

        self.gridLayoutCW = QtWidgets.QGridLayout(self.cw)
        self.splitter = QtWidgets.QSplitter(self.cw)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.gridLayoutCW.addWidget(self.splitter, 1, 0, 1, 1)

        self.layoutWidgetL = QtWidgets.QWidget(self.splitter)
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidgetL)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.filter = QtWidgets.QLineEdit(self.layoutWidgetL)
        self.gridLayout.addWidget(self.filter, 0, 0, 1, 2)
        self.tree = QtWidgets.QTreeWidget(self.layoutWidgetL)
        self.tree.setHeaderLabels(["Item", "Value"])
        self.tree.setMinimumSize(275, 150)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)
        header = self.tree.header()
        header.setMinimumSectionSize(100)
        header.resizeSection(0, 200)
        header.resizeSection(1, 75)
        header.setStretchLastSection(True)
        self.gridLayout.addWidget(self.tree, 3, 0, 1, 2)

        self.layoutWidgetR = QtWidgets.QWidget(self.splitter)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidgetR)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.layoutWidgetT = QtWidgets.QWidget(self.layoutWidgetR)
        self.horizLayout = QtWidgets.QHBoxLayout(self.layoutWidgetT)
        self.horizLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addWidget(self.layoutWidgetT)

        self.spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizLayout.addItem(self.spacer)
        self.rateLabel = QtWidgets.QLabel("Refresh rate:")
        self.horizLayout.addWidget(self.rateLabel)
        self.rate = QtWidgets.QSpinBox()
        self.rate.setAccelerated(True)
        self.rate.setMinimum(100)
        self.rate.setMaximum(1000000)
        self.rate.setSingleStep(100)
        self.rate.setProperty("value", self.context.refresh_rate)
        self.rate.setSuffix(" ms")
        self.horizLayout.addWidget(self.rate)
        self.pause = QtWidgets.QPushButton()
        self.pause.setText("&Pause")
        self.pause.setCheckable(True)
        self.horizLayout.addWidget(self.pause)

        self.view = pg.GraphicsLayoutWidget()
        self.plot = self.view.addPlot()
        self.plot.setMouseEnabled(x=False, y=False)
        self.rgn = pg.LinearRegionItem(movable=False)
        self.plot.addItem(self.rgn)
        self.verticalLayout.addWidget(self.view)

        self.splitter.setStretchFactor(1, 1)

        self.status = QtWidgets.QLabel()
        self.status.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.status.setFrameStyle(QtWidgets.QFrame.Shape.Panel | QtWidgets.QFrame.Shadow.Sunken)
        self.statusBar().addPermanentWidget(self.status, 1)

        self.rate.valueChanged.connect(self.rate_changed)
        self.pause.clicked.connect(self.pause_clicked)
        self.tree.itemSelectionChanged.connect(self.tree_selection_changed)
        self.tree.itemChanged.connect(self.tree_item_changed)

        QtWidgets.QApplication.instance().aboutToQuit.connect(self.atexit)

        geometry = self.settings.value("geometry", None)
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, ev):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(ev)

    def atexit(self):
        self.context.timer.stop()
        self.context.monitor.stop()

    def about(self):
        QtWidgets.QMessageBox.about(
                self,
                "About grafmon",
                "<h1><center>grafmon 1.1.1</center></h1>"
                "<h2><p>Copyright &copy; 2024-2025 <a href='https://github.com/pragma-'>Pragmatic Software<a></h2>"
                "<hr>"
                "<h3><p><a href='https://github.com/pragma-/grafmon'>https://github.com/pragma-/grafmon</a>"
                "<p><a href='https://pypi.org/project/grafmon'>https://pypi.org/project/grafmon</a>"
        )

    def rate_changed(self, value):
        self.context.refresh_rate = value
        self.context.timer.update_interval()

    def pause_clicked(self, checked):
        if checked:
            self.pause.setText("&Resume")
            self.context.timer.stop()
        else:
            self.pause.setText("&Pause")
            self.context.timer.start()

    def tree_selection_changed(self):
        item = self.tree.selectedItems()[0]
        if self.selected_line is not None:
            pen = self.selected_line.opts['pen']
            self.selected_line.setPen(pg.mkPen(pen.color(), width=1))
        self.selected_line = self.items[item.text(0)]
        pen = self.selected_line.opts['pen']
        self.selected_line.setPen(pg.mkPen(pen.color(), width=self.context.selected_width))

    def tree_item_changed(self, item, column):
        if not column == 0:
            return
        line = self.items[item.text(0)]
        if item.checkState(column) == QtCore.Qt.CheckState.Checked:
            line.setVisible(True)
        else:
            line.setVisible(False)
        # force plot to redraw
        line.setData(x=line.xData, y=line.yData)

    def curve_clicked(self, curve):
        item = self.tree.findItems(curve.name(), QtCore.Qt.MatchFlag.MatchExactly)[0]
        self.tree.setCurrentItem(item)
        self.tree.scrollToItem(item)

    def curve_hovered(self, curve, ev):
        x = int(round(ev.pos()[0]))
        y = curve.yData[x]

        if curve.xVals != None:
            x = curve.xVals[x]

        self.status.setText(f"{curve.name()}: {x}: {y}")

        pen = curve.opts['pen']
        color = pen.color().name()
        self.status.setStyleSheet(f"color: {color}")

    def create_x_axis(self):
        xs = list(range(self.context.max_ticks))
        t = int(time.time())
        ticks = [t + x for x in xs]

        self.x_ticks = []
        for x in xs:
            if x % self.context.tick_mod == 0:
                self.x_ticks.append((x, time.strftime("%H:%M:%S", time.localtime(ticks[x] + 1))))

        self.plot.getAxis('bottom').setTicks([self.x_ticks])

    def add_tree_item(self, name, value, color_index):
        item = TreeWidgetItem([name, value])
        brush = pg.mkBrush(pg.intColor(color_index, hues=12))
        item.setForeground(0, brush)
        item.setCheckState(0, QtCore.Qt.CheckState.Checked)
        self.tree.invisibleRootItem().addChild(item)
        self.tree_items[name] = item

    def update_tree_item(self, name, value):
        item = self.tree_items[name]
        item.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, value)

    def remove_tree_item(self, name):
        item = self.tree_items[name]
        index = self.tree.indexOfTopLevelItem(item)
        self.tree.takeTopLevelItem(index)

    def update_data(self, data):
        try:
            val = float(data[0])
        except ValueError:
            self.context.timer.stop()
            self.context.fatal_error = 1
            err = ErrorDialog()
            err.setText(f"Invalid data")
            err.setInformativeText("The data must be in the format of:\n\n<float> <string>")
            err.setDetailedText(f"Invalid data:\n\n{data!r}")
            err.show()
            self.context.app.exit(1)
            return

        if data[1] not in self.items:
            if val == 0.0:
                return
            x = list(range(self.context.max_ticks))
            y = [0] * self.context.max_ticks
            y[self.context.tick_index] = val
            item = HoverableCurveItem(x=x, y=y, name=data[1],
                                      pen=pg.mkPen(pg.intColor(self.color_index, hues=12), width=1),
                                      skipFiniteCheck=True)
            item.setClickable(True, width=5)
            item.sigClicked.connect(self.curve_clicked)
            item.sigHovered.connect(self.curve_hovered)
            item.scatterItem.sigClicked.connect(self.curve_clicked)
            x_val = list(range(self.context.max_ticks))
            x_val[self.context.tick_index] = self.context.tick_time
            item.xValues(x_val)
            self.plot.addItem(item)
            self.items[item.name()] = item
            self.item_last_update[item.name()] = self.context.now
            self.add_tree_item(item.name(), data[0], self.color_index)
            self.color_index += 1
        else:
            item = self.items[data[1]]
            item.yData[self.context.tick_index] = val
            if item.scatterTick == self.context.tick_index:
                item.hideDot()
            item.setData(x=item.xData, y=item.yData)
            item.xVals[self.context.tick_index] = self.context.tick_time
            self.item_last_update[item.name()] = self.context.now
            self.update_tree_item(item.name(), data[0])

    def zero_not_updated(self):
        if self.context.tick_index % self.context.tick_mod == 0:
            self.x_ticks[self.context.tick_index // self.context.tick_mod] = (self.context.tick_index, self.context.tick_time)
            self.plot.getAxis('bottom').setTicks([self.x_ticks])

        update_remove = dict()
        for x in self.item_last_update:
            item = self.items[x]

            # remove items with zeroed values once graph has wrapped around
            if self.context.tick_index == 0:
                if not any(item.yData):
                    update_remove[x] = True
                    self.plot.removeItem(item)
                    del self.items[x]
                    self.remove_tree_item(x)
                    continue

            # set value to zero if item hasn't been updated this tick
            if self.item_last_update[x] < self.context.now:
                item.yData[self.context.tick_index] = 0.0
                self.update_tree_item(item.name(), "0.000")
                item.hideDot()
                item.setData(x=item.xData, y=item.yData)
                item.xVals[self.context.tick_index] = self.context.tick_time

        for x in update_remove:
            del self.item_last_update[x]

class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if column == 1:
            return float(self.text(column)) < float(otherItem.text(column))
        else:
            return self.text(column) < otherItem.text(column)

    def __gt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if column == 1:
            return float(self.text(column)) > float(otherItem.text(column))
        else:
            return self.text(column) > otherItem.text(column)
