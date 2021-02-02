#coding:utf8
import sys

from PyQt5.QtWidgets import QMainWindow


from .UI.home import MainWindow


class Home(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)
        self.setupUI(self)
  