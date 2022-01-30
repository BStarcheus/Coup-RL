from components import *
from coup_rl import Human_v_Agent

class Board(QWidget):
    def __init__(self, p_first_turn):
        '''
        p_first_turn: Which player goes first, 0-indexed
        '''
        super().__init__()
        self.layout = QVBoxLayout()

        self.top_menu = TopMenu()
        self.p1 = Player('Me', self)
        self.p2 = Player('Opponent', self)
        self.players = [self.p1, self.p2]

        self.actions = ActionSelector()
        self.actions.disable_all()
        for btn in self.actions.findChildren(ActionButton):
            btn.clicked.connect(self.action_btn_click)

        self.select_cards_instructions = QLabel('', self)

        self.confirm_btn = QPushButton('Confirm', self)
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setFixedSize(70, 30)
        self.confirm_btn.clicked.connect(self.card_select_confirm_click)

        self.layout.addWidget(self.top_menu)
        self.layout.addWidget(self.p2)
        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.select_cards_instructions, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.p1)
        self.layout.addWidget(self.confirm_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.confirm_btn.hide()

        self.setLayout(self.layout)
        self.game_setup(p_first_turn)

    def game_setup(self, p_first_turn):
        '''
        p_first_turn: Which player goes first, 0-indexed
        '''
        # agent and game env with RL algo
        self._game = Human_v_Agent(p_first_turn, log_level=logger.level)
        # gym env with game logic
        self.game = self._game.env.game

        self.refresh()

    def refresh(self):
        self.game.render()

        valid = []

        if self.game.game_over:
            self.actions.close()
            self.disable_card_select()
            # Check who won the game
            user_won = False in [x.is_face_up for x in self.game.players[0].cards]
            self.layout.replaceWidget(self.actions, GameOver(user_won))

        elif self.game.whose_action == 0:
            valid = self._game.env.get_valid_actions(text=True)
            valid = [x.replace('_', ' ').capitalize().strip() for x in valid]
            self.actions.enable(valid)

        for i in range(len(self.players)):
            p = self.players[i]
            p_env = self.game.players[i]

            # Refresh coins
            p.set_coins(p_env.coins)

            # Refresh last move
            if p_env.last_action is not None:
                a = self._game.env.actions[p_env.last_action].replace('_', ' ').capitalize().strip()
                p.set_move(a)

            # Replace all cards
            while len(p.cards):
                p.remove_card(0)
            for c in p_env.cards:
                new_c = Card(name=c.get_name(), parent=p)
                if c.is_face_up:
                    new_c.set_eliminated()
                elif i == 1:
                    # Hide player 2 cards unless eliminated
                    new_c.set_hidden()

                p.add_card(new_c)

            # If necessary, allow P1 cards to be selected
            if self.game.whose_action == 0 and i == 0:
                text = ''
                if 'Lose card 1' in valid or 'Lose card 2' in valid:
                    # Player will select which card to lose
                    p.num_selectable = 1

                    if self._game.env.actions[self.game.players[1].last_action] == 'assassinate':
                        # Opponent is assassinating
                        text = 'Choose a card to be eliminated and press Confirm\nOR\nBlock or Challenge the assassination'
                    else:
                        # Player's only option is losing a card
                        text = 'Choose a card to be eliminated and press Confirm.'
                elif 'Exchange return 34' in valid:
                    p.num_selectable = 2
                    text = 'Choose 2 cards to return to the deck and press Confirm.'
                else:
                    # Disable in the case that player chose block/challenge against assassinate
                    self.disable_card_select()

                if p.num_selectable > 0:
                    # Set cards to selectable
                    p.check_selected()

                    # Show confirm button
                    self.confirm_btn.show()

                    # Show instructions text
                    self.select_cards_instructions.setText(text)

    def action_btn_click(self):
        # Prevent more clicks
        self.actions.disable_all()

        sender = self.sender()
        action = sender.text().lower().replace(' ', '_')
        if action == 'pass':
            action += '_'

        self._game.step(action)
        self.refresh()

    def disable_card_select(self):
        # Hide confirm button
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.hide()

        # Hide instructions text
        self.select_cards_instructions.setText('')

        # Reset card selectable properties
        self.p1.num_selectable = 0
        self.p1.num_selected = 0

    def card_select_confirm_click(self):
        self.disable_card_select()

        # If it was lose_card for assassination, disable the other actions
        self.actions.disable_all()

        cards = self.p1.get_selected_cards_index()
        cards = [x+1 for x in cards]
        logger.debug(f'Selected cards: {cards}')
        action = ''

        if len(cards) == 1:
            action = f'lose_card_{cards[0]}'
        elif len(cards) == 2:
            action = f'exchange_return_{cards[0]}{cards[1]}'
        else:
            raise RuntimeError('Cannot select more than two cards')

        self._game.step(action)
        self.refresh()
