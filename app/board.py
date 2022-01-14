from components import *
import gym
import gym_coup

class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.top_menu = TopMenu()
        self.p1 = Player('Me')
        self.p2 = Player('Opponent')
        self.players = [self.p1, self.p2]
        self.actions = ActionSelector()

        self.layout.addWidget(self.top_menu)
        self.layout.addWidget(self.p2)
        self.layout.addWidget(self.actions)
        self.layout.addWidget(self.p1)

        self.setLayout(self.layout)
        self.game_setup()

    def game_setup(self):
        self.env = gym.make('coup-v0')
        self.refresh()
        # Temp
        # self.p1.add_card('Assassin')
        # self.p1.add_card('Duke')
        # self.p2.add_card(None)
        # self.p2.add_card(None)
        # self.p1.set_coins(2)
        # self.p2.set_coins(2)

    def refresh(self):
        for i in range(len(self.players)):
            p = self.players[i]
            p_env = self.env.game.players[i]

            # Always refresh coins
            p.set_coins(p_env.coins)

            # Always refresh last move
            p.set_move(p_env.last_action)

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
