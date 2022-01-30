from menu import *
from board import *
import sys
import argparse

class Coup(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Coup')
        self.quit_game()
        self.setFocus()

    def start_game(self):
        # Init from menu form
        agent_filename, is_training, user_first = self.menu_widget.get_form_data()

        self.board_widget = Board(int(not user_first))
        self.board_widget.top_menu.quit_btn.clicked.connect(self.quit_game)

        # TODO init rl agent
        if not user_first:
            # Agent has the first turn
            self.board_widget._game.agent_step()
            self.board_widget.actions.disable_all()
            self.board_widget.refresh()

        self.setCentralWidget(self.board_widget)

    def quit_game(self):
        self.menu_widget = Menu()
        self.menu_widget.start_btn.clicked.connect(self.start_game)
        self.setCentralWidget(self.menu_widget)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Coup RL Desktop App')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--info', action='store_true', help='Log at the info level')
    group.add_argument('-d', '--debug', action='store_true', help='Log at the debug level')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.info:
        logger.setLevel(logging.INFO)

    app = QApplication(sys.argv)
    main_app = Coup()
    main_app.show()
    sys.exit(app.exec())
