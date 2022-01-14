from menu import *
from board import *
import sys

class Coup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Coup')
        self.quit_game()
        self.setFocus()

    def start_game(self):
        self.board_widget = Board()
        self.board_widget.top_menu.quit_btn.clicked.connect(self.quit_game)

        # Init from menu form
        agent_filename, is_training, user_first = self.menu_widget.get_form_data()
        # TODO init rl agent
        if not user_first:
            self.board_widget.env.game.whose_turn = 1
            self.board_widget.env.game.whose_action = 1

        self.setCentralWidget(self.board_widget)

    def quit_game(self):
        self.menu_widget = Menu()
        self.menu_widget.start_btn.clicked.connect(self.start_game)
        self.setCentralWidget(self.menu_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = Coup()
    main_app.show()
    sys.exit(app.exec())
