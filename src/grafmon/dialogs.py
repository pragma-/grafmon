from PyQt6.QtWidgets import QMessageBox

class ErrorDialog(QMessageBox):
    def __init__(self, *args, **kwargs):
        super(ErrorDialog, self).__init__(*args, **kwargs)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setWindowTitle("Fatal error")
        self.setStandardButtons(QMessageBox.StandardButton.Close)

    def show(self):
        self.exec();


class AlertDialog(QMessageBox):
    def __init__(self, *args, **kwargs):
        super(AlertDialog, self).__init__(*args, **kwargs)
        self.setIcon(QMessageBox.Icon.Information)
        self.setWindowTitle("Alert")
        self.setStandardButtons(QMessageBox.StandardButton.Close)

    def show(self):
        self.exec();
