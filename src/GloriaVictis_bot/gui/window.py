from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit
import sys
import logging

logger = logging.getLogger("gv")

class MainWindow(QMainWindow):
    token_button = QPushButton
    token_field = QLineEdit
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gloria Victis bot")
        self.resize(600, 300)

        token_field = QLineEdit(text="Put your discord token here", parent=self)
        token_field.setFixedSize(300, 20)
        token_field.setAlignment()
        # token_field.hide()

        token_button = QPushButton(text="Add / update discord token", parent=self)
        token_button.setFixedSize(200, 20)
        token_button.clicked.connect(self.show_discord_token_field)

    def show_discord_token_field(self):
        self.token_field.show()

    def closeEvent(self) -> None:
        sys.exit(app.exec())


app = QApplication(sys.argv)

window = MainWindow()
window.show()

def run_gui():
    app.exec()