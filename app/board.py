from components import *
from coup_rl import Human_v_Agent

class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.top_menu = TopMenu()
        self.p1 = Player('Me')
        self.p2 = Player('Opponent')
        self.players = [self.p1, self.p2]

        self.actions = ActionSelector()
        self.actions.disable_all()
        for btn in self.actions.findChildren(ActionButton):
            btn.clicked.connect(self.action_btn_click)

        self.layout.addWidget(self.top_menu)
        self.layout.addWidget(self.p2)
        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.p1)

        self.setLayout(self.layout)
        self.game_setup()

    def game_setup(self):
        # agent and game env with RL algo
        self._game = Human_v_Agent(logger.level)
        # gym env with game logic
        self.game = self._game.env.game

        self.refresh()

    def refresh(self):
        self.game.render()

        if not self.game.game_over and self.game.whose_action == 0:
            valid = self._game.env.get_valid_actions(text=True)
            valid = [x.replace('_', ' ').capitalize().strip() for x in valid]
            self.actions.enable(valid)

        for i in range(len(self.players)):
            p = self.players[i]
            p_env = self.game.players[i]

            # Always refresh coins
            p.set_coins(p_env.coins)

            # Always refresh last move
            if p_env.last_action is not None:
                a = self._game.env.actions[p_env.last_action].replace('_', ' ').capitalize().strip()
                p.set_move(a)

            # Only reload cards if change
            # Check if different card names
            # Updates to cards being hidden or eliminated happen in other functions
            if (len(p.cards) != len(p_env.cards) or
                p.get_card(0).lbl.text() != p_env.cards[0].get_name() or
                p.get_card(1).lbl.text() != p_env.cards[1].get_name()):
                
                # Remove all cards and add new ones
                while len(p.cards):
                    p.remove_card(0)
                for c in p_env.cards:
                    new_c = Card(c.get_name())
                    if c.is_face_up:
                        new_c.set_eliminated()
                    elif i == 1:
                        # Hide player 2 cards unless eliminated
                        new_c.set_hidden()

                    p.add_card(new_c)

    def action_btn_click(self):
        # Prevent more clicks
        self.actions.disable_all()

        sender = self.sender()
        action = sender.text().lower().replace(' ', '_')
        if action == 'pass':
            action += '_'

        self._game.step(action)
        self.refresh()

# TODO exhange return and lose card 1 / 2
# display game over