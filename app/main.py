from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys

class Coup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Coup')

        self.startBtn = QPushButton('Start', self)
        self.startBtn.clicked.connect(self.startGame)

        main_layout = QVBoxLayout()
        self.lbl = QLabel('New Game', self)
        main_layout.addWidget(self.lbl)
        main_layout.setAlignment(self.lbl, Qt.AlignmentFlag.AlignCenter)
        # add rl agent selector
        # add radio buttons (training, no training)
        main_layout.addWidget(self.startBtn)
        main_layout.setAlignment(self.startBtn, Qt.AlignmentFlag.AlignCenter)

        self.main_widget = QWidget()
        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)
        self.setFocus()

    def startGame(self):
        ...

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainApp = Coup()
    mainApp.show()
    sys.exit(app.exec())
