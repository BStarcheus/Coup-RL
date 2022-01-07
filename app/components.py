from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


# Cards
class Card(QWidget):
    name_colors = {
        'Assassin': 'black',
        'Ambassador': 'green',
        'Captain': 'blue',
        'Contessa': 'red',
        'Duke': 'purple',
    }

    def __init__(self, name=None):
        '''
        By default, no name given shows a face down card.
        If a name is given, show the (face up) card's name and color.
        '''
        super().__init__()
        self.setFixedSize(100, 150)

        self.hidden = name is None
        
        self.layout = QHBoxLayout()

        self.layout.addStretch()
        self.lbl = QLabel(name, self)
        self.layout.addWidget(self.lbl)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.setAutoFillBackground(True)

        if self.hidden:
            self.set_hidden()
        else:
            self.set_card(name)
        self.set_eliminated()

    def set_card(self, name=None):
        # Set the card text and color
        if name not in self.name_colors:
            print(f'Error: Cannot set to unknown card type {name}')
            return

        self.lbl.setText(name)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(self.name_colors[name]))
        self.setPalette(p)
        self.hidden = False

    def set_hidden(self):
        # Render a card hidden by the opponent
        self.lbl.setText('')
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor('lightGray'))
        self.setPalette(p)
        self.hidden = True

    def set_eliminated(self):
        # Indicate when card is eliminated
        if self.hidden:
            print('Show the card details before setting it as eliminated.')
            return
        
        self.elim_lbl = QLabel('ELIMINATED', self)
        self.elim_lbl.setStyleSheet('color: red; font-weight: bold;')
        self.elim_lbl.move(12, 0)


# Section of the board for all parts relating to a single player
class Player(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()

        self.move_lbl = QLabel('Last move:', self)
        self.move = QLabel('-', self)
        sub = QVBoxLayout()
        sub.addWidget(self.move_lbl)
        sub.addWidget(self.move)
        self.layout.addLayout(sub)

        self.cards = QHBoxLayout()
        self.layout.addLayout(self.cards)

        sub = QHBoxLayout()
        self.coin_lbl = QLabel('Coins:', self)
        self.coins = QLabel('-', self)
        sub.addWidget(self.coin_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        sub.addWidget(self.coins, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(sub)

        self.setLayout(self.layout)

    def add_card(self, name):
        card = Card(name)
        self.cards.addWidget(card)

    def remove_card(self, ind):
        self.cards.removeWidget(self.cards.itemAt(ind))

    def set_card(self, ind, name):
        if ind < 0 or ind > 1:
            print(f'Card index {ind} invalid')
            return
        
        card = Card(name)
        self.cards.replaceWidget(self.cards.itemAt(ind), card)

    def set_coins(self, num):
        self.coins.setText(str(num))

    def set_move(self, action):
        self.move.setText(action)
 

# Court Deck

# Treasury

# Action selector
# Gray out invalid options on turn

# Top menu bar
