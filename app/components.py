from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import logging

logging.basicConfig()
logger = logging.getLogger('app')


class Card(QFrame):
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
        self.setLineWidth(3)
        self.setFixedSize(100, 150)

        # Highlight on hover and press
        self.is_hidden = name is None
        self.is_highlighted = False
        self.is_selected = False
        self.is_selectable = False
        
        self.layout = QHBoxLayout()

        self.layout.addStretch()
        self.lbl = QLabel(name, self)
        self.layout.addWidget(self.lbl)
        self.layout.addStretch()

        self.setLayout(self.layout)

        self.setAutoFillBackground(True)

        if self.is_hidden:
            self.set_hidden()
        else:
            self.set_card(name)

    def set_card(self, name):
        # Set the card text and color
        if name not in self.name_colors:
            raise RuntimeError(f'Cannot set to unknown card type {name}')

        self.lbl.setText(name)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(self.name_colors[name]))
        self.setPalette(p)
        self.is_hidden = False

    def set_hidden(self):
        # Render a card hidden by the opponent
        self.lbl.setText('')
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor('darkGray'))
        self.setPalette(p)
        self.is_hidden = True

    def set_eliminated(self):
        # Indicate when card is eliminated
        if self.is_hidden:
            logger.warning('Show the card details before setting it as eliminated.')
            return

        self.elim_lbl = QLabel('ELIMINATED', self)
        self.elim_lbl.setStyleSheet('color: red; font-weight: bold; background-color: black;')
        self.elim_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.elim_lbl.move(0, 0)

    def set_highlighted(self, val):
        # val: True or False
        self.is_highlighted = val
        if val:
            self.setFrameShape(QFrame.Shape.Panel)
        else:
            self.setFrameShape(QFrame.Shape.NoFrame)

    def set_selected(self, val):
        # val: True or False
        self.is_selected = val
        if val:
            self.setFrameShadow(QFrame.Shadow.Sunken)
        else:
            self.setFrameShadow(QFrame.Shadow.Plain)

    def enterEvent(self, event):
        # Highlight on hover
        if self.is_selectable and not self.is_selected:
            self.set_highlighted(True)

    def leaveEvent(self, event):
        # Unhighlight
        if self.is_highlighted and not self.is_selected:
            self.set_highlighted(False)

    def mousePressEvent(self, event):
        # Select a card
        if self.is_selectable:
            self.set_selected(not self.is_selected)


# Section of the board for all parts relating to a single player
class Player(QWidget):
    def __init__(self, name):
        super().__init__()
        self.layout = QVBoxLayout()
        self.msg = QLabel(name)
        self.layout.addWidget(self.msg)

        self._layout = QHBoxLayout()

        self.move_lbl = QLabel('Last move:', self)
        self.move = QLabel('-', self)
        sub = QVBoxLayout()
        sub.addWidget(self.move_lbl)
        sub.addWidget(self.move)
        self._layout.addLayout(sub)

        self.cards = QHBoxLayout()
        self._layout.addLayout(self.cards)

        sub = QHBoxLayout()
        self.coin_lbl = QLabel('Coins:', self)
        self.coins = QLabel('-', self)
        sub.addWidget(self.coin_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        sub.addWidget(self.coins, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addLayout(sub)

        self.layout.addLayout(self._layout)
        self.setLayout(self.layout)

    def get_card(self, ind):
        return self.cards.itemAt(ind).widget()

    def add_card(self, card):
        if isinstance(card, str):
            card = Card(card)
            self.cards.addWidget(card)
        elif isinstance(card, Card):
            self.cards.addWidget(card)
        else:
            raise TypeError(f'add_card does not accept param type {type(card)}')

    def remove_card(self, ind):
        self.cards.removeWidget(self.cards.itemAt(ind).widget())

    def set_card(self, ind, name):
        card = Card(name)
        self.cards.replaceWidget(self.cards.itemAt(ind), card)

    def set_coins(self, num):
        self.coins.setText(str(num))

    def set_move(self, action):
        self.move.setText(action)


class ActionSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.msg = QLabel('Select an action below')
        self.layout.addWidget(self.msg)

        self.main_actions = QGridLayout()
        self.counter_actions = QGridLayout()

        # Main actions
        actions = ['Income', 'Foreign aid', 'Coup', 'Tax', 'Assassinate', 'Exchange', 'Steal']
        colors = [None, None, None, 'purple', 'black', 'green', 'blue']
        for x in range(len(actions)):
            per_row = 4
            r = x // per_row
            c = x % per_row
            self.main_actions.addWidget(ActionButton(actions[x], colors[x]), r, c)

        # Counter actions
        actions = ['Pass', 'Block', 'Challenge']
        colors = [None, '#00856f', '#a33c00']
        for x in range(len(actions)):
            per_row = 4
            r = x // per_row
            c = x % per_row
            self.counter_actions.addWidget(ActionButton(actions[x], colors[x]), r, c)        

        self.layout.addLayout(self.main_actions)
        self.layout.addLayout(self.counter_actions)
        self.setLayout(self.layout)

    def disable_all(self):
        for btn in self.findChildren(ActionButton):
            btn.disable()
    
    def enable(self, lst):
        for btn in self.findChildren(ActionButton):
            if btn.text() in lst:
                btn.enable()


class ActionButton(QPushButton):
    default = '#606060'
    grayedOut = '#909090'

    def __init__(self, name, color=None):
        super().__init__(name)
        self.setFixedSize(100, 100)
        self.color = color if color is not None else ActionButton.default
        self.setStyleSheet(f'background-color: {self.color};')

    def disable(self):
        self.setEnabled(False)
        self.setStyleSheet(f'background-color: {ActionButton.grayedOut};')

    def enable(self):
        self.setEnabled(True)
        self.setStyleSheet(f'background-color: {self.color};')


class TopMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setFixedSize(150, 40)

        self.quit_btn = QPushButton('Quit', self)
        self.rules_btn = QPushButton('Rules', self)
        self.rules = Rules()
        self.rules_btn.clicked.connect(self.rules.show)

        self.layout.addWidget(self.quit_btn)
        self.layout.addWidget(self.rules_btn)
        self.setLayout(self.layout)


class Rules(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Rules')
        self.setFixedSize(580, 350)
        
        self.text = QTextEdit()
        self.text.setHtml('''
        <style type="text/css">
        table  {border-collapse:collapse;border-spacing:0;}
        table td {border:1px solid grey;padding:10px 5px;}
        table th {border:1px solid grey;padding:10px 5px;}
        </style>
        <table>
        <thead>
        <tr>
            <th>Character</th>
            <th>Action</th>
            <th>Effect</th>
            <th>Counteraction</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td>-</td>
            <td>Income</td>
            <td>Take 1 coin</td>
            <td>X</td>
        </tr>
        <tr>
            <td>-</td>
            <td>Foreign Aid</td>
            <td>Take 2 coins</td>
            <td>X</td>
        </tr>
        <tr>
            <td>-</td>
            <td>Coup</td>
            <td>Pay 7 coins. Choose player to lose a card.</td>
            <td>X</td>
        </tr>
        <tr>
            <td style="background-color:purple">Duke</td>
            <td>Tax</td>
            <td>Take 3 coins</td>
            <td>Blocks foreign aid</td>
        </tr>
        <tr>
            <td style="background-color:black">Assassin</td>
            <td>Assassinate</td>
            <td>Pay 3 coins. Choose player to lose a card.</td>
            <td>X</td>
        </tr>
        <tr>
            <td style="background-color:green">Ambassador</td>
            <td>Exchange</td>
            <td>Exchange cards with deck</td>
            <td>Blocks stealing</td>
        </tr>
        <tr>
            <td style="background-color:blue">Captain</td>
            <td>Steal</td>
            <td>Take 2 coins from another player</td>
            <td>Blocks stealing</td>
        </tr>
        <tr>
            <td style="background-color:red">Contessa</td>
            <td>X</td>
            <td>X</td>
            <td>Blocks assassination</td>
        </tr>
        </tbody>
        </table>
        ''')
        self.text.setReadOnly(True)
        self.setCentralWidget(self.text)