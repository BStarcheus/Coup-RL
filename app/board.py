from components import *

class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
