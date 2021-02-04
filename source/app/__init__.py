#coding:utf8
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from os import path
from configparser import ConfigParser


sys.path.append(path.join(path.dirname(__file__), "."))
from .communicator import MainWindow, Home