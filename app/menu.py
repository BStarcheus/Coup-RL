from components import *

class Menu(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()

        self.lbl = QLabel('New Game', self)
        self.layout.addRow(self.lbl)
        self.layout.setAlignment(self.lbl, Qt.AlignmentFlag.AlignCenter)

        # Select RL agent opponent
        sub = QHBoxLayout()
        self.select_btn = QPushButton('Select Opponent Agent', self)
        sub.addWidget(self.select_btn)
        sub.setAlignment(self.select_btn, Qt.AlignmentFlag.AlignCenter)

        self.file_name = QLineEdit('', self)
        self.file_name.setReadOnly(True)
        self.file_name.setMinimumWidth(200)
        sub.addWidget(self.file_name)
        sub.setAlignment(self.file_name, Qt.AlignmentFlag.AlignCenter)
        self.layout.addRow(sub)

        # Radio buttons (training, no training)
        sub = QHBoxLayout()
        self.rd1 = QRadioButton('Training')
        self.rd2 = QRadioButton('No Training')
        sub.addWidget(self.rd1)
        sub.addWidget(self.rd2)
        sub.setAlignment(self.rd1, Qt.AlignmentFlag.AlignCenter)
        sub.setAlignment(self.rd2, Qt.AlignmentFlag.AlignCenter)
        self.layout.addRow(sub)
        
        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.rd1)
        self.btn_group.addButton(self.rd2)
        self.btn_group.button(-2).toggle()

        self.start_btn = QPushButton('Start', self)
        self.layout.addRow(self.start_btn)
        self.layout.setAlignment(self.start_btn, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)
