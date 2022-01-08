from components import *

class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.top_menu = TopMenu()
        self.p1 = Player('Me')
        self.p2 = Player('Opponent')
        self.actions = ActionSelector()

        self.layout.addWidget(self.top_menu)
        self.layout.addWidget(self.p2)
        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.p1)

        self.setLayout(self.layout)
        self.game_setup()

    def game_setup(self):
        # Temp
        self.p1.add_card('Assassin')
        self.p1.add_card('Duke')
        self.p2.add_card(None)
        self.p2.add_card(None)
        self.p1.set_coins(2)
        self.p2.set_coins(2)
