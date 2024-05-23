import asyncio
import os

from PyQt6.QtWidgets import QApplication, QDialog, QWidget, QGridLayout, QPushButton, QLineEdit, QTimeEdit
from PyQt6 import uic
from PySide6 import QtAsyncio

from src.GloriaVictis_bot.command_operations import CommOp
import sys


class UI(QDialog):
    def __init__(self):
        super(UI, self).__init__()

        path = os.path.dirname(__file__)
        ui_path = str(path + "\main_window.ui")

        uic.loadUi(ui_path, self)

        # Initiate object to run commands
        comm_op = CommOp()

        # Get the GUI items
        self.channel_button = self.findChild(QPushButton, "discord_channel_button")
        self.channel_input = self.findChild(QLineEdit, "discord_channel_input")
        self.token_button = self.findChild(QPushButton, "token_path_button")
        self.token_input = self.findChild(QLineEdit, "token_path_input")
        self.timer_button = self.findChild(QPushButton, "timer_button")
        self.timer_input = self.findChild(QTimeEdit, "timer_edit")
        self.manual_run_button = self.findChild(QPushButton, "manual_run_button")

        self.show()

        async def manual_run():
            # loop = QEventLoop()
            await asyncio.run(comm_op.gv_go())
            # loop.exit()

        # self.channel_button.clicked.connect(method)
        self.manual_run_button.clicked.connect(lambda: asyncio.ensure_future(manual_run))

def run_gui():
    app = QApplication(sys.argv)
    ui_window = UI()
    app.exec()
    QtAsyncio.run()