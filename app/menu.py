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
        sub.addWidget(self.select_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.file_name = QLineEdit('', self)
        self.file_name.setReadOnly(True)
        self.file_name.setMinimumWidth(200)
        sub.addWidget(self.file_name, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addRow(sub)

        # Radio buttons: training, no training
        sub = QHBoxLayout()
        self.rd1 = QRadioButton('Yes')
        self.rd2 = QRadioButton('No')
        sub.addWidget(self.rd1, alignment=Qt.AlignmentFlag.AlignCenter)
        sub.addWidget(self.rd2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addRow(QLabel('Train the agent?'), sub)
        self.rd_btn_group = QButtonGroup()
        self.rd_btn_group.addButton(self.rd1)
        self.rd_btn_group.addButton(self.rd2)
        self.rd_btn_group.button(-2).toggle()

        # Radio buttons: Who goes first P1/P2
        sub = QHBoxLayout()
        self.rd3 = QRadioButton('Me')
        self.rd4 = QRadioButton('Computer')
        sub.addWidget(self.rd3, alignment=Qt.AlignmentFlag.AlignCenter)
        sub.addWidget(self.rd4, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addRow(QLabel('Who goes first?'), sub)
        self.turn_btn_group = QButtonGroup()
        self.turn_btn_group.addButton(self.rd3)
        self.turn_btn_group.addButton(self.rd4)
        self.turn_btn_group.button(-2).toggle()

        self.start_btn = QPushButton('Start', self)
        self.layout.addRow(self.start_btn)
        self.layout.setAlignment(self.start_btn, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

    def get_form_data(self):
        return (
            self.file_name.text(),
            self.rd1.isChecked(),
            self.rd3.isChecked()
        )